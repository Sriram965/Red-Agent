from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolSchema:
    """Public description of a tool exposed to the target LLM."""

    name: str
    description: str
    parameters: dict[str, Any]


SEARCH_KNOWLEDGE_BASE = ToolSchema(
    name="search_knowledge_base",
    description=(
        "Search the support knowledge base for information relevant "
        "to the current task."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query.",
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
)


LOOKUP_CUSTOMER = ToolSchema(
    name="lookup_customer",
    description="Look up a customer record using the customer ID.",
    parameters={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The ID of the customer to look up.",
            }
        },
        "required": ["customer_id"],
        "additionalProperties": False,
    },
)


READ_TICKET = ToolSchema(
    name="read_ticket",
    description="Read a support ticket using the ticket ID.",
    parameters={
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "string",
                "description": "The ID of the ticket to read.",
            }
        },
        "required": ["ticket_id"],
        "additionalProperties": False,
    },
)


UPDATE_TICKET = ToolSchema(
    name="update_ticket",
    description="Update the status and note of a support ticket.",
    parameters={
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "string",
                "description": "The ID of the ticket to update.",
            },
            "status": {
                "type": "string",
                "description": "The new ticket status.",
            },
            "note": {
                "type": "string",
                "description": "The new ticket note.",
            },
        },
        "required": ["ticket_id", "status", "note"],
        "additionalProperties": False,
    },
)


SEND_MESSAGE = ToolSchema(
    name="send_message",
    description="Send an outbound message to a recipient.",
    parameters={
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "The message recipient.",
            },
            "body": {
                "type": "string",
                "description": "The message body.",
            },
        },
        "required": ["to", "body"],
        "additionalProperties": False,
    },
)


MEMORY_READ = ToolSchema(
    name="memory_read",
    description=(
        "Read persistent memory associated with the current user."
    ),
    parameters={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "The memory key to retrieve.",
            }
        },
        "required": ["key"],
        "additionalProperties": False,
    },
)


MEMORY_WRITE = ToolSchema(
    name="memory_write",
    description=(
        "Create or update persistent memory associated with the current user."
    ),
    parameters={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "The memory key.",
            },
            "value": {
                "type": "string",
                "description": "The value to store.",
            },
        },
        "required": ["key", "value"],
        "additionalProperties": False,
    },
)


ALL_TOOL_SCHEMAS: tuple[ToolSchema, ...] = (
    SEARCH_KNOWLEDGE_BASE,
    LOOKUP_CUSTOMER,
    READ_TICKET,
    UPDATE_TICKET,
    SEND_MESSAGE,
    MEMORY_READ,
    MEMORY_WRITE,
)


TOOL_SCHEMAS_BY_NAME: dict[str, ToolSchema] = {
    schema.name: schema
    for schema in ALL_TOOL_SCHEMAS
}
