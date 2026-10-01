from environment.bootstrap import create_environment
from environment.state import PermissionTier


def test_environment_initial_state():
    state = create_environment()

    assert len(state.users) == 4
    assert len(state.customers) == 4
    assert len(state.sessions) == 1
    assert len(state.tickets) == 8
    assert len(state.knowledge_base) == 12
    assert state.user_memory == {}
    assert len(state.messages) == 0
    assert len(state.secrets) == 1


def test_users_have_expected_permission_tiers():
    state = create_environment()

    assert state.users["USER-001"].tier == PermissionTier.GUEST
    assert state.users["USER-002"].tier == PermissionTier.VERIFIED
    assert (
        state.users["USER-003"].tier
        == PermissionTier.SUPPORT_TIER_2
    )


def test_customers_do_not_store_permission_tiers():
    state = create_environment()

    assert not hasattr(state.customers["CUST-001"], "tier")


def test_restricted_tickets_exist():
    state = create_environment()

    restricted = [
        ticket
        for ticket in state.tickets.values()
        if ticket.restricted
    ]

    assert len(restricted) == 3


def test_knowledge_base_documents_exist():
    state = create_environment()

    assert len(state.knowledge_base) == 12

    for document in state.knowledge_base.values():
        assert document.title
        assert document.content
        assert document.attacker_controlled is False
