from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from environment.messages import send_message as environment_send_message
from environment.state import EnvironmentState, MemoryEntry, Session, User
from target.config import MemoryWriteMode
from target.permissions import PermissionPolicy
from target.tool_schemas import (
    LOOKUP_CUSTOMER,
    MEMORY_READ,
    MEMORY_WRITE,
    READ_TICKET,
    SEARCH_KNOWLEDGE_BASE,
    SEND_MESSAGE,
    TOOL_SCHEMAS_BY_NAME,
    UPDATE_TICKET,
    ToolSchema,
)


@dataclass(frozen=True)
class ToolContext:
    """
    Runtime-only context available during tool execution.

    The LLM never receives this object.
    """

    environment: EnvironmentState
    user: User
    session: Session
    permissions: PermissionPolicy
    memory_write_mode: MemoryWriteMode


ToolHandler = Callable[[ToolContext, dict[str, Any]], Any]


class ToolRegistry:
    """Maps public tool schemas to their runtime handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}

    def register(
        self,
        schema: ToolSchema,
        handler: ToolHandler,
    ) -> None:
        if schema.name in self._handlers:
            raise ValueError(
                f"Tool already registered: {schema.name}"
            )

        self._handlers[schema.name] = handler

    def get_handler(self, name: str) -> ToolHandler:
        try:
            return self._handlers[name]
        except KeyError:
            raise KeyError(f"Unknown tool: {name}") from None

    def get_schema(self, name: str) -> ToolSchema:
        try:
            return TOOL_SCHEMAS_BY_NAME[name]
        except KeyError:
            raise KeyError(f"Unknown tool: {name}") from None

    def schemas(self) -> Iterable[ToolSchema]:
        return tuple(
            TOOL_SCHEMAS_BY_NAME[name]
            for name in self._handlers
        )

    def execute(
        self,
        name: str,
        context: ToolContext,
        arguments: dict[str, Any],
    ) -> Any:
        return self.get_handler(name)(context, arguments)


def create_tool_registry() -> ToolRegistry:
    """Create the complete registry of target-agent tools."""

    registry = ToolRegistry()

    registry.register(
        SEARCH_KNOWLEDGE_BASE,
        search_knowledge_base,
    )
    registry.register(
        LOOKUP_CUSTOMER,
        lookup_customer,
    )
    registry.register(
        READ_TICKET,
        read_ticket,
    )
    registry.register(
        UPDATE_TICKET,
        update_ticket,
    )
    registry.register(
        SEND_MESSAGE,
        send_message,
    )
    registry.register(
        MEMORY_READ,
        memory_read,
    )
    registry.register(
        MEMORY_WRITE,
        memory_write,
    )

    return registry


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

def search_knowledge_base(
    context: ToolContext,
    arguments: dict[str, Any],
) -> list[dict[str, str]]:
    """Search the support knowledge base."""

    if not context.permissions.can_search_knowledge_base(
        context.user
    ):
        raise PermissionError(
            "User is not permitted to search the knowledge base."
        )

    query = arguments["query"].strip().lower()

    if not query:
        return []

    query_terms = set(query.split())
    results: list[dict[str, str]] = []

    for document in context.environment.knowledge_base.values():
        searchable_text = (
            f"{document.title} {document.content}"
        ).lower()

        document_terms = set(searchable_text.split())

        if query_terms.intersection(document_terms):
            results.append(
                {
                    "document_id": document.document_id,
                    "title": document.title,
                    "content": document.content,
                }
            )

    return results


# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------

def lookup_customer(
    context: ToolContext,
    arguments: dict[str, Any],
) -> dict[str, str]:
    """Look up a customer after resource-level authorization."""

    customer_id = arguments["customer_id"]

    customer = context.environment.customers.get(customer_id)

    if customer is None:
        raise KeyError(
            f"Customer not found: {customer_id}"
        )

    if not context.permissions.can_lookup_customer(
        context.user,
        customer,
    ):
        raise PermissionError(
            "User is not permitted to access this customer."
        )

    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
    }


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

def read_ticket(
    context: ToolContext,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Read a ticket after resource-level authorization."""

    ticket_id = arguments["ticket_id"]

    ticket = context.environment.tickets.get(ticket_id)

    if ticket is None:
        raise KeyError(
            f"Ticket not found: {ticket_id}"
        )

    if not context.permissions.can_read_ticket(
        context.user,
        ticket,
    ):
        raise PermissionError(
            "User is not permitted to read this ticket."
        )

    return {
        "ticket_id": ticket.ticket_id,
        "customer_id": ticket.customer_id,
        "status": ticket.status,
        "note": ticket.note,
    }


def update_ticket(
    context: ToolContext,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Update a ticket after resource-level authorization."""

    ticket_id = arguments["ticket_id"]

    ticket = context.environment.tickets.get(ticket_id)

    if ticket is None:
        raise KeyError(
            f"Ticket not found: {ticket_id}"
        )

    if not context.permissions.can_update_ticket(
        context.user,
        ticket,
    ):
        raise PermissionError(
            "User is not permitted to update this ticket."
        )

    ticket.status = arguments["status"]
    ticket.note = arguments["note"]

    return {
        "ticket_id": ticket.ticket_id,
        "customer_id": ticket.customer_id,
        "status": ticket.status,
        "note": ticket.note,
    }


# ---------------------------------------------------------------------------
# Messaging
# ---------------------------------------------------------------------------

def send_message(
    context: ToolContext,
    arguments: dict[str, Any],
) -> dict[str, str]:
    """Send an outbound message after authorization."""

    if not context.permissions.can_send_message(
        context.user
    ):
        raise PermissionError(
            "User is not permitted to send messages."
        )

    message = environment_send_message(
        state=context.environment,
        sender=context.user.user_id,
        recipient=arguments["to"],
        body=arguments["body"],
    )

    return {
        "message_id": message.message_id,
        "sender": message.sender,
        "recipient": message.recipient,
        "body": message.body,
    }


# ---------------------------------------------------------------------------
# Persistent user memory
# ---------------------------------------------------------------------------

def memory_read(
    context: ToolContext,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Read persistent memory belonging to the current user."""

    if not context.permissions.can_read_memory(
        context.user
    ):
        raise PermissionError(
            "User is not permitted to read persistent memory."
        )

    key = arguments["key"].strip()

    if not key:
        raise ValueError("Memory key cannot be empty.")

    user_memory = context.environment.user_memory.get(
        context.user.user_id,
        {},
    )

    entry = user_memory.get(key)

    if entry is None:
        return {
            "found": False,
            "key": key,
        }

    return {
        "found": True,
        "memory_id": entry.memory_id,
        "key": entry.key,
        "value": entry.value,
    }


def memory_write(
    context: ToolContext,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Create or update persistent memory for the current user."""

    if not context.permissions.can_write_memory(
        context.user
    ):
        raise PermissionError(
            "User is not permitted to write persistent memory."
        )

    if (
        context.memory_write_mode
        == MemoryWriteMode.READ_ONLY
    ):
        raise PermissionError(
            "Persistent memory is read-only for this target."
        )

    key = arguments["key"].strip()
    value = arguments["value"]

    if not key:
        raise ValueError("Memory key cannot be empty.")

    user_id = context.user.user_id

    user_memory = context.environment.user_memory.setdefault(
        user_id,
        {},
    )

    existing = user_memory.get(key)

    if (
        existing is not None
        and context.memory_write_mode
        == MemoryWriteMode.NO_OVERWRITE
    ):
        raise PermissionError(
            "Existing persistent memory cannot be overwritten."
        )

    if existing is None:
        entry = MemoryEntry(
            memory_id=_next_memory_id(context.environment),
            key=key,
            value=value,
            user_id=user_id,
            created_by_session=context.session.session_id,
            updated_by_session=context.session.session_id,
        )

        user_memory[key] = entry
    else:
        existing.value = value
        existing.updated_by_session = (
            context.session.session_id
        )
        entry = existing

    return {
        "memory_id": entry.memory_id,
        "key": entry.key,
        "value": entry.value,
    }


def _next_memory_id(
    state: EnvironmentState,
) -> str:
    """Generate a deterministic memory ID within one sandbox."""

    count = sum(
        len(entries)
        for entries in state.user_memory.values()
    )

    return f"MEM-{count + 1:04d}"
