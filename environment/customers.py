from environment.state import Customer


def create_customers() -> list[Customer]:
    return [
        Customer(
            customer_id="CUST-001",
            name="Alice Rao",
            email="alice@example.com",
        ),
        Customer(
            customer_id="CUST-002",
            name="Daniel Kim",
            email="daniel@example.com",
        ),
        Customer(
            customer_id="CUST-003",
            name="Priya Shah",
            email="priya@example.com",
        ),
        Customer(
            customer_id="CUST-004",
            name="Michael Chen",
            email="michael@example.com",
        ),
    ]