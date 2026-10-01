from environment.bootstrap import create_environment
from target.permissions import PermissionPolicy
from target.tools import (
    ToolContext,
    ToolRegistry,
    ToolSideEffect,
    ToolSpec,
)


def test_tool_registration_and_schema():
    registry = ToolRegistry()

    tool = ToolSpec(
        name="test_tool",
        description="A test tool.",
        input_schema={
            "type": "object",
            "properties": {},
        },
        permission_action="search_knowledge_base",
        side_effect=ToolSideEffect.READ_ONLY,
        handler=lambda context, arguments: "ok",
    )

    registry.register(tool)

    assert registry.get("test_tool").name == "test_tool"
    assert len(registry.list_tools()) == 1


def test_tool_execution():
    state = create_environment()

    user = state.users["USER-002"]
    session = state.sessions["SESSION-001"]

    context = ToolContext(
        state=state,
        user=user,
        session=session,
        permission_policy=PermissionPolicy(),
    )

    registry = ToolRegistry()

    registry.register(
        ToolSpec(
            name="test_tool",
            description="A test tool.",
            input_schema={
                "type": "object",
                "properties": {},
            },
            permission_action="search_knowledge_base",
            side_effect=ToolSideEffect.READ_ONLY,
            handler=lambda context, arguments: "success",
        )
    )

    result = registry.execute(
        "test_tool",
        {},
        context,
    )

    assert result == "success"