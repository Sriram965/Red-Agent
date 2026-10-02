import pytest

from environment.bootstrap import create_environment
from environment.state import Session
from target.config import MemoryWriteMode
from target.permissions import PermissionPolicy
from target.tool_schemas import ALL_TOOL_SCHEMAS
from target.tools import (
    ToolContext,
    create_tool_registry,
)


def make_context(
    state,
    user_id: str = "USER-002",
    memory_write_mode: MemoryWriteMode = MemoryWriteMode.FULL,
) -> ToolContext:
    user = state.users[user_id]

    session = state.sessions.get("SESSION-001")

    if session is None or session.user_id != user_id:
        session = Session(
            session_id=f"TEST-{user_id}",
            user_id=user_id,
            task="Test support task",
        )

    return ToolContext(
        environment=state,
        user=user,
        session=session,
        permissions=PermissionPolicy(),
        memory_write_mode=memory_write_mode,
    )


def test_registry_contains_all_tools():
    registry = create_tool_registry()

    registered_names = {
        schema.name
        for schema in registry.schemas()
    }

    expected_names = {
        schema.name
        for schema in ALL_TOOL_SCHEMAS
    }

    assert registered_names == expected_names


def test_search_knowledge_base_returns_public_fields_only():
    state = create_environment()
    context = make_context(state)

    registry = create_tool_registry()

    results = registry.execute(
        "search_knowledge_base",
        context,
        {"query": "dashboard"},
    )

    assert results

    assert all(
        set(result) == {
            "document_id",
            "title",
            "content",
        }
        for result in results
    )

    assert all(
        "attacker_controlled" not in result
        for result in results
    )


def test_verified_user_can_read_own_customer():
    state = create_environment()
    context = make_context(state)

    registry = create_tool_registry()

    result = registry.execute(
        "lookup_customer",
        context,
        {"customer_id": "CUST-002"},
    )

    assert result["customer_id"] == "CUST-002"
    assert result["name"] == "Daniel Kim"


def test_verified_user_cannot_read_other_customer():
    state = create_environment()
    context = make_context(state)

    registry = create_tool_registry()

    with pytest.raises(PermissionError):
        registry.execute(
            "lookup_customer",
            context,
            {"customer_id": "CUST-003"},
        )


def test_verified_user_can_read_own_ticket():
    state = create_environment()
    context = make_context(state)

    registry = create_tool_registry()

    result = registry.execute(
        "read_ticket",
        context,
        {"ticket_id": "TKT-002"},
    )

    assert result["ticket_id"] == "TKT-002"
    assert result["status"] == "pending"


def test_verified_user_cannot_read_restricted_ticket():
    state = create_environment()
    context = make_context(state)

    registry = create_tool_registry()

    with pytest.raises(PermissionError):
        registry.execute(
            "read_ticket",
            context,
            {"ticket_id": "TKT-005"},
        )


def test_support_user_can_update_ticket():
    state = create_environment()
    context = make_context(
        state,
        "USER-003",
    )

    registry = create_tool_registry()

    result = registry.execute(
        "update_ticket",
        context,
        {
            "ticket_id": "TKT-002",
            "status": "resolved",
            "note": "Resolved during test.",
        },
    )

    assert result["status"] == "resolved"
    assert result["note"] == "Resolved during test."

    assert state.tickets["TKT-002"].status == "resolved"
    assert state.tickets["TKT-002"].note == "Resolved during test."


def test_verified_user_cannot_update_ticket():
    state = create_environment()
    context = make_context(state)

    registry = create_tool_registry()

    with pytest.raises(PermissionError):
        registry.execute(
            "update_ticket",
            context,
            {
                "ticket_id": "TKT-002",
                "status": "resolved",
                "note": "Unauthorized update.",
            },
        )


def test_support_user_can_send_message():
    state = create_environment()
    context = make_context(
        state,
        "USER-003",
    )

    registry = create_tool_registry()

    result = registry.execute(
        "send_message",
        context,
        {
            "to": "external@example.com",
            "body": "Test message.",
        },
    )

    assert result["message_id"] == "MSG-0001"
    assert result["sender"] == "USER-003"
    assert result["recipient"] == "external@example.com"
    assert result["body"] == "Test message."

    assert len(state.messages) == 1


def test_verified_user_cannot_send_message():
    state = create_environment()
    context = make_context(state)

    registry = create_tool_registry()

    with pytest.raises(PermissionError):
        registry.execute(
            "send_message",
            context,
            {
                "to": "external@example.com",
                "body": "Unauthorized message.",
            },
        )

    assert state.messages == []


def test_memory_starts_empty():
    state = create_environment()

    assert state.user_memory == {}


def test_memory_write_then_read():
    state = create_environment()
    context = make_context(state)

    registry = create_tool_registry()

    write_result = registry.execute(
        "memory_write",
        context,
        {
            "key": "preferred_language",
            "value": "English",
        },
    )

    assert write_result["key"] == "preferred_language"
    assert write_result["value"] == "English"

    read_result = registry.execute(
        "memory_read",
        context,
        {"key": "preferred_language"},
    )

    assert read_result["found"] is True
    assert read_result["key"] == "preferred_language"
    assert read_result["value"] == "English"


def test_memory_is_scoped_to_current_user():
    state = create_environment()

    verified_context = make_context(
        state,
        "USER-002",
    )
    guest_context = make_context(
        state,
        "USER-001",
    )

    registry = create_tool_registry()

    registry.execute(
        "memory_write",
        verified_context,
        {
            "key": "note",
            "value": "private user memory",
        },
    )

    guest_result = registry.execute(
        "memory_read",
        guest_context,
        {"key": "note"},
    )

    assert guest_result["found"] is False


def test_memory_write_updates_existing_entry():
    state = create_environment()
    context = make_context(state)

    registry = create_tool_registry()

    first = registry.execute(
        "memory_write",
        context,
        {
            "key": "customer_preference",
            "value": "email",
        },
    )

    second = registry.execute(
        "memory_write",
        context,
        {
            "key": "customer_preference",
            "value": "phone",
        },
    )

    assert second["memory_id"] == first["memory_id"]

    result = registry.execute(
        "memory_read",
        context,
        {"key": "customer_preference"},
    )

    assert result["value"] == "phone"
    assert len(state.user_memory["USER-002"]) == 1


def test_read_only_memory_rejects_writes():
    state = create_environment()
    context = make_context(
        state,
        memory_write_mode=MemoryWriteMode.READ_ONLY,
    )

    registry = create_tool_registry()

    with pytest.raises(PermissionError):
        registry.execute(
            "memory_write",
            context,
            {
                "key": "note",
                "value": "should not be stored",
            },
        )

    assert state.user_memory == {}


def test_no_overwrite_memory_rejects_existing_key_update():
    state = create_environment()

    full_context = make_context(state)

    registry = create_tool_registry()

    first = registry.execute(
        "memory_write",
        full_context,
        {
            "key": "preference",
            "value": "email",
        },
    )

    restricted_context = make_context(
        state,
        memory_write_mode=MemoryWriteMode.NO_OVERWRITE,
    )

    with pytest.raises(PermissionError):
        registry.execute(
            "memory_write",
            restricted_context,
            {
                "key": "preference",
                "value": "phone",
            },
        )

    result = registry.execute(
        "memory_read",
        restricted_context,
        {"key": "preference"},
    )

    assert result["memory_id"] == first["memory_id"]
    assert result["value"] == "email"


def test_no_overwrite_memory_allows_new_key():
    state = create_environment()

    context = make_context(
        state,
        memory_write_mode=MemoryWriteMode.NO_OVERWRITE,
    )

    registry = create_tool_registry()

    result = registry.execute(
        "memory_write",
        context,
        {
            "key": "new_key",
            "value": "new value",
        },
    )

    assert result["key"] == "new_key"
    assert result["value"] == "new value"
