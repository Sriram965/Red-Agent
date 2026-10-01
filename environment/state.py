from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PermissionTier(str, Enum):
    """Authorization level of the user operating the agent."""

    GUEST = "guest"
    VERIFIED = "verified"
    SUPPORT_TIER_2 = "support_tier_2"


class TrustLevel(str, Enum):
    """Trust classification for data entering the agent."""

    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"


@dataclass
class User:
    user_id: str
    name: str
    email: str
    tier: PermissionTier
    customer_id: Optional[str] = None


@dataclass
class Session:
    session_id: str
    user_id: str
    task: str


@dataclass
class Customer:
    customer_id: str
    name: str
    email: str


@dataclass
class Ticket:
    ticket_id: str
    customer_id: str
    status: str
    note: str
    restricted: bool = False


@dataclass
class KnowledgeDocument:
    document_id: str
    title: str
    content: str
    trust_level: TrustLevel = TrustLevel.UNTRUSTED


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
    Mutable state of one sandbox instance.

    The target agent never accesses this object directly.
    It interacts with the environment through tools.
    """

    users: Dict[str, User] = field(default_factory=dict)
    customers: Dict[str, Customer] = field(default_factory=dict)
    sessions: Dict[str, Session] = field(default_factory=dict)
    tickets: Dict[str, Ticket] = field(default_factory=dict)
    knowledge_base: Dict[str, KnowledgeDocument] = field(default_factory=dict)
    memory: Dict[str, MemoryEntry] = field(default_factory=dict)
    messages: List[Message] = field(default_factory=list)
    secrets: Dict[str, str] = field(default_factory=dict)

    next_message_id: int = 1

    def add_user(self, user: User) -> None:
        self.users[user.user_id] = user

    def add_customer(self, customer: Customer) -> None:
        self.customers[customer.customer_id] = customer

    def add_session(self, session: Session) -> None:
        self.sessions[session.session_id] = session

    def add_ticket(self, ticket: Ticket) -> None:
        self.tickets[ticket.ticket_id] = ticket

    def add_knowledge_document(self, document: KnowledgeDocument) -> None:
        self.knowledge_base[document.document_id] = document

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