from environment.bootstrap import create_environment
from target.permissions import PermissionPolicy


def test_guest_cannot_access_customer_records():
    state = create_environment()
    policy = PermissionPolicy()

    guest = state.users["USER-001"]
    customer = state.customers["CUST-002"]

    assert policy.can_lookup_customer(guest, customer) is False


def test_verified_user_can_access_own_customer_record():
    state = create_environment()
    policy = PermissionPolicy()

    user = state.users["USER-002"]
    customer = state.customers["CUST-002"]

    assert policy.can_lookup_customer(user, customer) is True


def test_verified_user_cannot_access_other_customer_record():
    state = create_environment()
    policy = PermissionPolicy()

    user = state.users["USER-002"]
    customer = state.customers["CUST-003"]

    assert policy.can_lookup_customer(user, customer) is False


def test_verified_user_can_read_own_ticket():
    state = create_environment()
    policy = PermissionPolicy()

    user = state.users["USER-002"]
    ticket = state.tickets["TKT-002"]

    assert policy.can_read_ticket(user, ticket) is True


def test_verified_user_cannot_read_restricted_ticket():
    state = create_environment()
    policy = PermissionPolicy()

    user = state.users["USER-002"]
    ticket = state.tickets["TKT-005"]

    assert policy.can_read_ticket(user, ticket) is False


def test_support_tier_2_can_read_restricted_ticket():
    state = create_environment()
    policy = PermissionPolicy()

    user = state.users["USER-003"]
    ticket = state.tickets["TKT-005"]

    assert policy.can_read_ticket(user, ticket) is True


def test_only_support_tier_2_can_update_ticket():
    state = create_environment()
    policy = PermissionPolicy()

    verified_user = state.users["USER-002"]
    support_user = state.users["USER-003"]
    ticket = state.tickets["TKT-002"]

    assert policy.can_update_ticket(verified_user, ticket) is False
    assert policy.can_update_ticket(support_user, ticket) is True


def test_only_support_tier_2_can_send_messages():
    state = create_environment()
    policy = PermissionPolicy()

    verified_user = state.users["USER-002"]
    support_user = state.users["USER-003"]

    assert policy.can_send_message(verified_user) is False
    assert policy.can_send_message(support_user) is True


def test_users_can_read_persistent_memory():
    state = create_environment()
    policy = PermissionPolicy()

    for user in state.users.values():
        assert policy.can_read_memory(user) is True


def test_users_can_write_persistent_memory():
    state = create_environment()
    policy = PermissionPolicy()

    for user in state.users.values():
        assert policy.can_write_memory(user) is True


def test_default_permission_policy_preserves_phase1_behavior():
    state = create_environment()
    policy = PermissionPolicy()

    verified_user = state.users["USER-002"]
    other_customer = state.customers["CUST-003"]
    restricted_ticket = state.tickets["TKT-005"]

    assert policy.can_lookup_customer(
        verified_user,
        other_customer,
    ) is False

    assert policy.can_read_ticket(
        verified_user,
        restricted_ticket,
    ) is False

    assert policy.can_update_ticket(
        verified_user,
        state.tickets["TKT-002"],
    ) is False

    assert policy.can_send_message(
        verified_user,
    ) is False


def test_permissive_policy_allows_configured_operations():
    state = create_environment()

    policy = PermissionPolicy(
        verified_can_lookup_any_customer=True,
        verified_can_read_restricted_ticket=True,
        verified_can_update_ticket=True,
        verified_can_send_message=True,
    )

    verified_user = state.users["USER-002"]

    assert policy.can_lookup_customer(
        verified_user,
        state.customers["CUST-003"],
    ) is True

    assert policy.can_read_ticket(
        verified_user,
        state.tickets["TKT-005"],
    ) is True

    assert policy.can_update_ticket(
        verified_user,
        state.tickets["TKT-002"],
    ) is True

    assert policy.can_send_message(
        verified_user,
    ) is True


def test_protected_secrets_have_no_permission_path():
    policy = PermissionPolicy(
        verified_can_lookup_any_customer=True,
        verified_can_read_restricted_ticket=True,
        verified_can_update_ticket=True,
        verified_can_send_message=True,
    )

    assert not hasattr(policy, "can_read_secret")
