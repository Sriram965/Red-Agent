from environment.state import Customer, PermissionTier


def create_customers() -> list[Customer]:
    """Create deterministic synthetic customer records."""

    return [
        Customer(
            customer_id="CUST-001",
            name="Alice Rao",
            email="alice@example.com",
            tier=PermissionTier.GUEST,
        ),
        Customer(
            customer_id="CUST-002",
            name="Daniel Kim",
            email="daniel@example.com",
            tier=PermissionTier.VERIFIED,
        ),
        Customer(
            customer_id="CUST-003",
            name="Priya Shah",
            email="priya@example.com",
            tier=PermissionTier.SUPPORT_TIER_2,
        ),
        Customer(
            customer_id="CUST-004",
            name="Michael Chen",
            email="michael@example.com",
            tier=PermissionTier.VERIFIED,
        ),
    ]