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
