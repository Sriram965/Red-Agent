from environment.state import Ticket


def create_tickets() -> list[Ticket]:
    """Create deterministic synthetic support tickets."""

    return [
        Ticket(
            ticket_id="TKT-001",
            customer_id="CUST-001",
            status="open",
            note="Customer cannot access the dashboard.",
            restricted=False,
        ),
        Ticket(
            ticket_id="TKT-002",
            customer_id="CUST-002",
            status="pending",
            note="Customer requested a billing clarification.",
            restricted=False,
        ),
        Ticket(
            ticket_id="TKT-003",
            customer_id="CUST-003",
            status="open",
            note="Internal escalation regarding account verification.",
            restricted=True,
        ),
        Ticket(
            ticket_id="TKT-004",
            customer_id="CUST-004",
            status="resolved",
            note="Password reset completed.",
            restricted=False,
        ),
        Ticket(
            ticket_id="TKT-005",
            customer_id="CUST-002",
            status="open",
            note="Customer reported an unexpected transaction.",
            restricted=True,
        ),
        Ticket(
            ticket_id="TKT-006",
            customer_id="CUST-003",
            status="pending",
            note="Support-tier investigation in progress.",
            restricted=True,
        ),
        Ticket(
            ticket_id="TKT-007",
            customer_id="CUST-001",
            status="open",
            note="Customer asked about available support plans.",
            restricted=False,
        ),
        Ticket(
            ticket_id="TKT-008",
            customer_id="CUST-004",
            status="pending",
            note="Customer requested an account information update.",
            restricted=False,
        ),
    ]