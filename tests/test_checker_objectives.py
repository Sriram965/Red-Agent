from checker.objectives import UnauthorizedTicketAccessObjective


def test_unauthorized_ticket_access_objective() -> None:
    objective = UnauthorizedTicketAccessObjective(
        ticket_id="TKT-005",
    )

    assert objective.ticket_id == "TKT-005"
