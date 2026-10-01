from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PermissionTier(str, Enum):
    """Permission level assigned to a user/session."""

    GUEST = "guest"
    VERIFIED = "verified"
    SUPPORT_TIER_2 = "support_tier_2"


@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    tier: PermissionTier


@dataclass
class Ticket:
    ticket_id: str
    customer_id: str
    status: str
    note: str
    restricted: bool = False


@dataclass
class MemoryEntry:
    key: str
    value: str
    protected: bool = False


@dataclass
class Message:
    message_id: str
    sender: str
    recipient: str
    body: str


@dataclass
class EnvironmentState:
    """
    Complete mutable state of one target-agent environment.

    The target agent never accesses this object directly.
    Tools will interact with the environment through controlled APIs.
    """

    customers: Dict[str, Customer] = field(default_factory=dict)
    tickets: Dict[str, Ticket] = field(default_factory=dict)
    memory: Dict[str, MemoryEntry] = field(default_factory=dict)
    messages: List[Message] = field(default_factory=list)

    secrets: Dict[str, str] = field(default_factory=dict)

    next_message_id: int = 1

    def add_customer(self, customer: Customer) -> None:
        self.customers[customer.customer_id] = customer

    def add_ticket(self, ticket: Ticket) -> None:
        self.tickets[ticket.ticket_id] = ticket

    def add_memory(self, entry: MemoryEntry) -> None:
        self.memory[entry.key] = entry

    def add_secret(self, name: str, value: str) -> None:
        self.secrets[name] = value

    def add_message(
        self,
        sender: str,
        recipient: str,
        body: str,
    ) -> Message:
        message = Message(
            message_id=f"MSG-{self.next_message_id:04d}",
            sender=sender,
            recipient=recipient,
            body=body,
        )

        self.messages.append(message)
        self.next_message_id += 1

        return message