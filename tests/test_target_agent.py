from target.agent import (
    ModelResponse,
    TargetAgent,
    TargetConfig,
    ToolCall,
)
from target.config import MemoryWriteMode
from target.permissions import PermissionPolicy
from target.prompt import STANDARD_SUPPORT_PROMPT
from environment.bootstrap import create_environment


class FakeModel:
    """Deterministic model used to test the target-agent loop."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate(self, messages, tools):
        self.calls.append(
            {
                "messages": messages,
                "tools": tools,
            }
        )

        if not self.responses:
            raise AssertionError(
                "FakeModel has no response left."
            )

        return self.responses.pop(0)


def make_target_config() -> TargetConfig:
    return TargetConfig(
        name="test_target",
        system_prompt=STANDARD_SUPPORT_PROMPT,
        exposed_tools=(
            "search_knowledge_base",
            "lookup_customer",
            "read_ticket",
        ),
        permissions=PermissionPolicy(),
        memory_write_mode=MemoryWriteMode.FULL,
        max_tool_steps=4,
    )


def test_target_can_return_normal_response():
    state = create_environment()
    user = state.users["USER-002"]
    session = state.sessions["SESSION-001"]

    model = FakeModel(
        [
            ModelResponse(
                content="I can help with your support issue."
            )
        ]
    )

    agent = TargetAgent(
        model=model,
        config=make_target_config(),
        environment=state,
        user=user,
        session=session,
    )

    result = agent.run(
        "Help me with my support issue."
    )

    assert result.final_response == (
        "I can help with your support issue."
    )
    assert result.tool_steps == 0

    assert len(model.calls) == 1
    assert len(model.calls[0]["tools"]) == 3

    assert result.messages[-1] == {
        "role": "assistant",
        "content": "I can help with your support issue.",
    }


def test_target_can_execute_tool_and_continue():
    state = create_environment()
    user = state.users["USER-002"]
    session = state.sessions["SESSION-001"]

    model = FakeModel(
        [
            ModelResponse(
                content=None,
                tool_calls=(
                    ToolCall(
                        call_id="call-1",
                        name="read_ticket",
                        arguments={
                            "ticket_id": "TKT-002",
                        },
                    ),
                ),
            ),
            ModelResponse(
                content="The ticket is currently pending."
            ),
        ]
    )

    agent = TargetAgent(
        model=model,
        config=make_target_config(),
        environment=state,
        user=user,
        session=session,
    )

    result = agent.run(
        "What is the status of ticket TKT-002?"
    )

    assert result.final_response == (
        "The ticket is currently pending."
    )
    assert result.tool_steps == 1
    assert len(model.calls) == 2

    first_call = model.calls[0]

    tool_names = {
        schema.name
        for schema in first_call["tools"]
    }

    assert tool_names == {
        "search_knowledge_base",
        "lookup_customer",
        "read_ticket",
    }

    second_messages = model.calls[1]["messages"]

    assert any(
        message["role"] == "tool"
        and message["name"] == "read_ticket"
        and message["call_id"] == "call-1"
        for message in second_messages
    )


def test_target_only_exposes_configured_tools():
    state = create_environment()
    user = state.users["USER-002"]
    session = state.sessions["SESSION-001"]

    config = TargetConfig(
        name="minimal_target",
        system_prompt=STANDARD_SUPPORT_PROMPT,
        exposed_tools=(
            "search_knowledge_base",
            "read_ticket",
        ),
        permissions=PermissionPolicy(),
    )

    model = FakeModel(
        [
            ModelResponse(
                content="Done."
            )
        ]
    )

    agent = TargetAgent(
        model=model,
        config=config,
        environment=state,
        user=user,
        session=session,
    )

    agent.run("Help me.")

    exposed_names = {
        schema.name
        for schema in model.calls[0]["tools"]
    }

    assert exposed_names == {
        "search_knowledge_base",
        "read_ticket",
    }

    assert "lookup_customer" not in exposed_names
    assert "update_ticket" not in exposed_names
    assert "send_message" not in exposed_names
    assert "memory_read" not in exposed_names
    assert "memory_write" not in exposed_names


def test_target_rejects_call_to_unexposed_tool():
    state = create_environment()
    user = state.users["USER-002"]
    session = state.sessions["SESSION-001"]

    config = TargetConfig(
        name="restricted_target",
        system_prompt=STANDARD_SUPPORT_PROMPT,
        exposed_tools=("read_ticket",),
        permissions=PermissionPolicy(),
    )

    model = FakeModel(
        [
            ModelResponse(
                tool_calls=(
                    ToolCall(
                        call_id="call-1",
                        name="send_message",
                        arguments={
                            "to": "external@example.com",
                            "body": "Should not execute.",
                        },
                    ),
                ),
            ),
            ModelResponse(
                content="I cannot use that tool.",
            ),
        ]
    )

    agent = TargetAgent(
        model=model,
        config=config,
        environment=state,
        user=user,
        session=session,
    )

    result = agent.run("Send a message.")

    assert result.tool_steps == 1
    assert result.final_response == "I cannot use that tool."

    tool_messages = [
        message
        for message in result.messages
        if message.get("role") == "tool"
    ]

    assert len(tool_messages) == 1

    assert tool_messages[0]["content"] == {
        "error_type": "PermissionError",
        "error": "Tool is not exposed to this target: send_message",
    }

    assert state.messages == []


def test_target_rejects_invalid_exposed_tool():
    state = create_environment()
    user = state.users["USER-002"]
    session = state.sessions["SESSION-001"]

    config = TargetConfig(
        name="invalid_target",
        system_prompt=STANDARD_SUPPORT_PROMPT,
        exposed_tools=("does_not_exist",),
        permissions=PermissionPolicy(),
    )

    model = FakeModel([])

    try:
        TargetAgent(
            model=model,
            config=config,
            environment=state,
            user=user,
            session=session,
        )
    except ValueError as exc:
        assert "Unknown exposed tools" in str(exc)
    else:
        raise AssertionError(
            "Invalid tool configuration should have failed."
        )


def test_target_rejects_session_for_different_user():
    state = create_environment()
    user = state.users["USER-001"]
    session = state.sessions["SESSION-001"]

    model = FakeModel([])

    try:
        TargetAgent(
            model=model,
            config=make_target_config(),
            environment=state,
            user=user,
            session=session,
        )
    except ValueError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError(
            "Mismatched user/session should have failed."
        )


def test_target_config_can_select_memory_write_mode():
    config = TargetConfig(
        name="read_only_target",
        system_prompt=STANDARD_SUPPORT_PROMPT,
        exposed_tools=(
            "memory_read",
            "memory_write",
        ),
        permissions=PermissionPolicy(),
        memory_write_mode=MemoryWriteMode.READ_ONLY,
    )

    assert config.memory_write_mode == (
        MemoryWriteMode.READ_ONLY
    )
