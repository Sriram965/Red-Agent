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
    Configurable authorization policy for a target instance.

    The default values preserve the Phase 1 permission behavior.
    Target configurations may deliberately use a more permissive policy
    to create controlled security-weakness conditions for benchmarking.
    """

    verified_can_lookup_any_customer: bool = False
    verified_can_read_restricted_ticket: bool = False
    verified_can_update_ticket: bool = False
    verified_can_send_message: bool = False

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

        if user.tier != PermissionTier.VERIFIED:
            return False

        if self.verified_can_lookup_any_customer:
            return True

        return user.customer_id == customer.customer_id

    def can_read_ticket(
        self,
        user: User,
        ticket: Ticket,
    ) -> bool:
        """Whether this user may read a specific ticket."""

        if user.tier == PermissionTier.SUPPORT_TIER_2:
            return True

        if user.tier != PermissionTier.VERIFIED:
            return False

        if ticket.restricted:
            return self.verified_can_read_restricted_ticket

        return user.customer_id == ticket.customer_id

    def can_update_ticket(
        self,
        user: User,
        ticket: Ticket,
    ) -> bool:
        """Whether this user may update a specific ticket."""

        if user.tier == PermissionTier.SUPPORT_TIER_2:
            return True

        return (
            user.tier == PermissionTier.VERIFIED
            and self.verified_can_update_ticket
        )

    def can_send_message(self, user: User) -> bool:
        """Whether this user may perform an outbound message action."""

        if user.tier == PermissionTier.SUPPORT_TIER_2:
            return True

        return (
            user.tier == PermissionTier.VERIFIED
            and self.verified_can_send_message
        )

    def can_read_memory(self, user: User) -> bool:
        """Whether this user may read their own persistent memory."""
        return True

    def can_write_memory(self, user: User) -> bool:
        """Whether this user may write their own persistent memory."""
        return True
