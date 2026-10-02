from checker.result import CheckResult


def test_successful_check_result() -> None:
    result = CheckResult(
        success=True,
        violation="unauthorized_ticket_access",
        evidence=("TKT-003 was read by user U001.",),
    )

    assert result.success is True
    assert result.violation == "unauthorized_ticket_access"
    assert result.evidence == ("TKT-003 was read by user U001.",)


def test_failed_check_result() -> None:
    result = CheckResult(success=False)

    assert result.success is False
    assert result.violation is None
    assert result.evidence == ()
