from dataclasses import dataclass

from environment.state import (
    Customer,
    PermissionTier,
    Ticket,
    User,
)


@dataclass(frozen=True)
class PermissionPolicy:
    """
    Resource-aware authorization policy foundation.

    Phase 1 defines authorization rules separately from the environment.
    Tool-specific dispatch belongs to Phase 2.
    """

    def can_search_knowledge_base(self, user: User) -> bool:
        """Whether this user may use the knowledge-base capability."""
        return True

    def can_lookup_customer(
        self,
        user: User,
        customer: Customer,
    ) -> bool:
        """Whether this user may access a specific customer record."""
        if user.tier == PermissionTier.SUPPORT_TIER_2:
            return True

        return (
            user.tier == PermissionTier.VERIFIED
            and user.customer_id == customer.customer_id
        )

    def can_read_ticket(
        self,
        user: User,
        ticket: Ticket,
    ) -> bool:
        """Whether this user may read a specific ticket."""
        if user.tier == PermissionTier.SUPPORT_TIER_2:
            return True

        if ticket.restricted:
            return False

        return user.customer_id == ticket.customer_id

    def can_update_ticket(
        self,
        user: User,
        ticket: Ticket,
    ) -> bool:
        """Whether this user may update a specific ticket."""
        return user.tier == PermissionTier.SUPPORT_TIER_2

    def can_send_message(self, user: User) -> bool:
        """Whether this user may perform an outbound message action."""
        return user.tier == PermissionTier.SUPPORT_TIER_2
