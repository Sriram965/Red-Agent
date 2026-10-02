from collections.abc import Callable, Iterable
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from benchmark.attacks import StaticAttack
from benchmark.logging import EpisodeLogger, EpisodeRecord
from checker.checker import CheckContext, GroundTruthChecker
from environment.bootstrap import create_environment
from environment.state import EnvironmentState
from target.agent import TargetAgent, TargetConfig, TargetModel


ModelFactory = Callable[[], TargetModel]
EnvironmentFactory = Callable[[], EnvironmentState]


@dataclass
class EpisodeRunner:
    """
    Runs complete benchmark episodes.

    Every episode receives a fresh environment.
    """

    model_factory: ModelFactory
    checker: GroundTruthChecker
    environment_factory: EnvironmentFactory = create_environment
    logger: EpisodeLogger | None = None

    _episode_counter: int = 0

    def run(
        self,
        attack: StaticAttack,
        target_config: TargetConfig,
    ) -> EpisodeRecord:

        self._episode_counter += 1

        episode_id = (
            f"EP-{self._episode_counter:06d}"
        )

        state = self.environment_factory()

        if attack.environment_setup is not None:
            attack.environment_setup(state)

        initial_state = deepcopy(state)

        if attack.user_id not in state.users:
            raise ValueError(
                f"Unknown attack user: {attack.user_id}"
            )

        if attack.session_id not in state.sessions:
            raise ValueError(
                f"Unknown attack session: {attack.session_id}"
            )

        user = state.users[attack.user_id]
        session = state.sessions[attack.session_id]

        if session.user_id != user.user_id:
            raise ValueError(
                "Attack session user does not match attack user."
            )

        agent = TargetAgent(
            model=self.model_factory(),
            config=target_config,
            environment=state,
            user=user,
            session=session,
        )

        run_result = agent.run(
            attack.user_message
        )

        check_result = self.checker.check(
            CheckContext(
                initial_state=initial_state,
                final_state=state,
                user=user,
                session=session,
                run_result=run_result,
            ),
            attack.objective,
        )

        record = EpisodeRecord(
            episode_id=episode_id,
            attack_id=attack.attack_id,
            attack_family=attack.family.value,
            target_name=target_config.name,
            user_id=user.user_id,
            tool_steps=run_result.tool_steps,
            success=check_result.success,
            violation=check_result.violation,
            evidence=check_result.evidence,
            final_response=run_result.final_response,
            trajectory=run_result.messages,
        )

        if self.logger is not None:
            self.logger.log(record)

        return record

    def run_suite(
        self,
        attacks: Iterable[StaticAttack],
        target_configs: Iterable[TargetConfig],
    ) -> list[EpisodeRecord]:

        results: list[EpisodeRecord] = []

        for target_config in target_configs:
            for attack in attacks:
                results.append(
                    self.run(
                        attack=attack,
                        target_config=target_config,
                    )
                )

        return results
