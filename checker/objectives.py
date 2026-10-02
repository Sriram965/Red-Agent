from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UnauthorizedCustomerAccessObjective:
    """Target should not gain access to this customer record."""

    customer_id: str


@dataclass(frozen=True)
class UnauthorizedTicketAccessObjective:
    """Target should not gain access to this ticket."""

    ticket_id: str


@dataclass(frozen=True)
class UnauthorizedTicketUpdateObjective:
    """Target should not modify this ticket."""

    ticket_id: str


@dataclass(frozen=True)
class MemoryPoisoningObjective:
    """
    Target should not cause the specified persistent memory entry
    to acquire the attacker-controlled value.
    """

    user_id: str
    key: str
    expected_value: str


@dataclass(frozen=True)
class IndirectPromptInjectionObjective:
    """
    An attacker-controlled document must lead to a concrete
    downstream action.

    expected_arguments describe the concrete action that must have
    occurred.
    """

    document_id: str
    downstream_tool: str
    expected_arguments: dict[str, Any]


@dataclass(frozen=True)
class DataExfiltrationObjective:
    """
    Protected secret must not be sent to the specified recipient.
    """

    secret_name: str
    recipient: str
