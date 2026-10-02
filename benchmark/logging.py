import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EpisodeRecord:
    """One final record for one benchmark episode."""

    episode_id: str
    attack_id: str
    attack_family: str
    target_name: str
    user_id: str
    tool_steps: int
    success: bool
    violation: str | None
    evidence: tuple[str, ...]
    final_response: str
    trajectory: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence"] = list(self.evidence)
        data["trajectory"] = list(self.trajectory)
        return data


class EpisodeLogger:
    """Append completed episode records as JSON Lines."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(self, record: EpisodeRecord) -> None:
        with self.path.open(
            "a",
            encoding="utf-8",
        ) as file:
            json.dump(
                record.to_dict(),
                file,
                sort_keys=True,
            )
            file.write("\n")
