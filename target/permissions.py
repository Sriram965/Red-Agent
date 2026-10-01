from dataclasses import dataclass

from environment.state import PermissionTier


@dataclass(frozen=True)
class PermissionPolicy:
    """
    Defines which operations are allowed for each permission tier.
    """

    def can_search_knowledge_base(self, tier: PermissionTier) -> bool:
        return True

    def can_lookup_customer(self, tier: PermissionTier) -> bool:
        return tier in {
            PermissionTier.VERIFIED,
            PermissionTier.SUPPORT_TIER_2,
        }

    def can_read_ticket(self, tier: PermissionTier) -> bool:
        return True

    def can_update_ticket(self, tier: PermissionTier) -> bool:
        return tier == PermissionTier.SUPPORT_TIER_2

    def can_send_message(self, tier: PermissionTier) -> bool:
        return tier == PermissionTier.SUPPORT_TIER_2

    def can_memory_read(self, tier: PermissionTier) -> bool:
        return tier in {
            PermissionTier.VERIFIED,
            PermissionTier.SUPPORT_TIER_2,
        }

    def can_memory_write(self, tier: PermissionTier) -> bool:
        return tier == PermissionTier.SUPPORT_TIER_2