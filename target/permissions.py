from dataclasses import dataclass

from environment.state import (
    Customer,
    EnvironmentState,
    MemoryEntry,
    PermissionTier,
    Ticket,
    User,
)


@dataclass(frozen=True)
class PermissionPolicy:
    """
    Resource-aware authorization policy.

    Authorization depends on:
    - the user
    - the resource
    - the requested operation
    """

    def can_search_knowledge_base(self, user: User) -> bool:
        return True

    def can_lookup_customer(
        self,
        user: User,
        customer: Customer,
    ) -> bool:
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
        return user.tier == PermissionTier.SUPPORT_TIER_2

    def can_send_message(
        self,
        user: User,
        recipient: str,
    ) -> bool:
        if user.tier == PermissionTier.SUPPORT_TIER_2:
            return True

        if user.tier == PermissionTier.VERIFIED:
            return (
                user.customer_id is not None
                and recipient
                == f"customer-{user.customer_id.lower()}@example.com"
            )

        return False

    def can_memory_read(
        self,
        user: User,
        entry: MemoryEntry,
    ) -> bool:
        if entry.protected:
            return user.tier == PermissionTier.SUPPORT_TIER_2

        return user.tier in {
            PermissionTier.VERIFIED,
            PermissionTier.SUPPORT_TIER_2,
        }

    def can_memory_write(
        self,
        user: User,
        entry: MemoryEntry,
    ) -> bool:
        if entry.protected:
            return user.tier == PermissionTier.SUPPORT_TIER_2

        return user.tier in {
            PermissionTier.VERIFIED,
            PermissionTier.SUPPORT_TIER_2,
        }

    def authorize(
        self,
        action: str,
        user: User,
        state: EnvironmentState,
        arguments: dict,
    ) -> bool:
        """Central authorization entry point for tool execution."""

        if action == "search_knowledge_base":
            return self.can_search_knowledge_base(user)

        if action == "lookup_customer":
            customer = state.customers.get(arguments.get("customer_id"))
            return customer is not None and self.can_lookup_customer(
                user,
                customer,
            )

        if action == "read_ticket":
            ticket = state.tickets.get(arguments.get("ticket_id"))
            return ticket is not None and self.can_read_ticket(
                user,
                ticket,
            )

        if action == "update_ticket":
            ticket = state.tickets.get(arguments.get("ticket_id"))
            return ticket is not None and self.can_update_ticket(
                user,
                ticket,
            )

        if action == "send_message":
            return self.can_send_message(
                user,
                arguments.get("recipient", ""),
            )

        if action == "memory_read":
            entry = state.memory.get(arguments.get("key"))
            return entry is not None and self.can_memory_read(
                user,
                entry,
            )

        if action == "memory_write":
            entry = state.memory.get(arguments.get("key"))
            if entry is None:
                return False

            return self.can_memory_write(
                user,
                entry,
            )

        raise ValueError(f"Unknown permission action: {action}")