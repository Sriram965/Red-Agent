from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from environment.state import EnvironmentState, Session, User
from target.permissions import PermissionPolicy


class ToolSideEffect(str, Enum):
    """Security-relevant effect produced by a tool."""

    READ_ONLY = "read_only"
    STATE_MUTATION = "state_mutation"
    EXTERNAL_SIDE_EFFECT = "external_side_effect"
    PERSISTENT_MEMORY = "persistent_memory"


@dataclass(frozen=True)
class ToolSpec:
    """
    Description and metadata for one target-agent tool.

    The LLM receives the public schema/description.
    Internal implementation details remain hidden.
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    permission_action: str
    side_effect: ToolSideEffect
    accepts_untrusted_data: bool = False

    handler: Callable[
        ["ToolContext", dict[str, Any]],
        Any,
    ] | None = None

    def public_schema(self) -> dict[str, Any]:
        """Return the tool description exposed to the target LLM."""

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass
class ToolContext:
    """
    Controlled execution context available to a tool.

    Tools can access environment state only through this context.
    """

    state: EnvironmentState
    user: User
    session: Session
    permission_policy: PermissionPolicy


class ToolRegistry:
    """Registry and execution layer for target-agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        if tool.handler is None:
            raise ValueError(f"Tool has no handler: {tool.name}")

        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def list_tools(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def public_schemas(self) -> list[dict[str, Any]]:
        return [
            tool.public_schema()
            for tool in self._tools.values()
        ]

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        context: ToolContext,
    ) -> Any:
        tool = self.get(name)

        authorized = context.permission_policy.authorize(
            action=tool.permission_action,
            user=context.user,
            state=context.state,
            arguments=arguments,
        )

        if not authorized:
            raise PermissionError(
                f"Permission denied for tool: {name}"
            )

        return tool.handler(context, arguments) # type: ignore