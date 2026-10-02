from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    """
    Final episode-level result produced by the deterministic checker.
    """

    success: bool
    violation: str | None = None
    evidence: tuple[str, ...] = ()
