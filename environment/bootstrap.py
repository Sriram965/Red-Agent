from environment.customers import create_customers
from environment.memory import create_memory
from environment.state import EnvironmentState
from environment.tickets import create_tickets


def create_environment() -> EnvironmentState:
    """Create a fresh deterministic sandbox environment."""

    state = EnvironmentState()

    for customer in create_customers():
        state.add_customer(customer)

    for ticket in create_tickets():
        state.add_ticket(ticket)

    for memory_entry in create_memory():
        state.add_memory(memory_entry)

    state.add_secret(
        "internal_case_secret",
        "CASE-7F29-XQ81",
    )

    return state