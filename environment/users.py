from environment.state import PermissionTier, User


def create_users() -> list[User]:
    return [
        User(
            user_id="USER-001",
            name="Alice Rao",
            email="alice@example.com",
            tier=PermissionTier.GUEST,
            customer_id="CUST-001",
        ),
        User(
            user_id="USER-002",
            name="Daniel Kim",
            email="daniel@example.com",
            tier=PermissionTier.VERIFIED,
            customer_id="CUST-002",
        ),
        User(
            user_id="USER-003",
            name="Priya Support",
            email="priya-support@example.com",
            tier=PermissionTier.SUPPORT_TIER_2,
        ),
        User(
            user_id="USER-004",
            name="Michael Chen",
            email="michael@example.com",
            tier=PermissionTier.VERIFIED,
            customer_id="CUST-004",
        ),
    ]