import json
from dataclasses import dataclass
from typing import Any, Protocol, cast

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionFunctionToolParam,
    ChatCompletionMessageParam,
    ChatCompletionToolUnionParam,
)

from environment.state import EnvironmentState, Session, User
from target.config import MemoryWriteMode
from target.permissions import PermissionPolicy
from target.tool_schemas import (
    TOOL_SCHEMAS_BY_NAME,
    ToolSchema,
)
from target.tools import (
    ToolContext,
    ToolRegistry,
    create_tool_registry,
)


@dataclass(frozen=True)
class TargetConfig:
    """Configuration for one target-agent variant."""

    name: str
    system_prompt: str
    exposed_tools: tuple[str, ...]
    permissions: PermissionPolicy
    memory_write_mode: MemoryWriteMode = MemoryWriteMode.FULL
    max_tool_steps: int = 8


@dataclass(frozen=True)
class ToolCall:
    """Normalized tool call produced by an LLM."""

    call_id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ModelResponse:
    """Normalized response returned by an LLM adapter."""

    content: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()


class TargetModel(Protocol):
    """Provider-neutral model interface."""

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: tuple[ToolSchema, ...],
    ) -> ModelResponse:
        ...


class OpenAIChatModel:
    """OpenAI Chat Completions adapter."""

    def __init__(
        self,
        model: str,
        client: OpenAI | None = None,
    ) -> None:
        self.model = model
        self.client = client or OpenAI()

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: tuple[ToolSchema, ...],
    ) -> ModelResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._convert_messages(messages),
            tools=self._convert_tools(tools),
            reasoning_effort="none",
        )

        message = response.choices[0].message

        tool_calls: list[ToolCall] = []

        for tool_call in message.tool_calls or []:
            if tool_call.type != "function":
                continue

            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Model returned invalid JSON tool arguments."
                ) from exc

            if not isinstance(arguments, dict):
                raise ValueError(
                    "Tool arguments must decode to a JSON object."
                )

            tool_calls.append(
                ToolCall(
                    call_id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=arguments,
                )
            )

        return ModelResponse(
            content=message.content,
            tool_calls=tuple(tool_calls),
        )

    @staticmethod
    def _convert_tools(
        tools: tuple[ToolSchema, ...],
    ) -> list[ChatCompletionToolUnionParam]:
        converted: list[ChatCompletionToolUnionParam] = []

        for tool in tools:
            function_tool = cast(
                ChatCompletionFunctionToolParam,
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                        "strict": True,
                    },
                },
            )

            converted.append(function_tool)

        return converted

    @staticmethod
    def _convert_messages(
        messages: list[dict[str, Any]],
    ) -> list[ChatCompletionMessageParam]:
        converted: list[ChatCompletionMessageParam] = []

        for message in messages:
            role = message["role"]

            if role in {"system", "user"}:
                converted.append(
                    cast(
                        ChatCompletionMessageParam,
                        {
                            "role": role,
                            "content": message["content"],
                        },
                    )
                )
                continue

            if role == "assistant":
                converted.append(
                    cast(
                        ChatCompletionMessageParam,
                        {
                            "role": "assistant",
                            "content": message.get("content"),
                            "tool_calls": [
                                {
                                    "id": call["call_id"],
                                    "type": "function",
                                    "function": {
                                        "name": call["name"],
                                        "arguments": json.dumps(
                                            call["arguments"]
                                        ),
                                    },
                                }
                                for call in message.get(
                                    "tool_calls",
                                    [],
                                )
                            ],
                        },
                    )
                )
                continue

            if role == "tool":
                converted.append(
                    cast(
                        ChatCompletionMessageParam,
                        {
                            "role": "tool",
                            "tool_call_id": message["call_id"],
                            "content": json.dumps(
                                message["content"],
                            ),
                        },
                    )
                )
                continue

            raise ValueError(
                f"Unsupported message role: {role}"
            )

        return converted


@dataclass(frozen=True)
class TargetRunResult:
    """Result of one target-agent interaction."""

    final_response: str
    messages: tuple[dict[str, Any], ...]
    tool_steps: int


class TargetAgent:
    """Reusable multi-step tool-using target-agent runtime."""

    def __init__(
        self,
        model: TargetModel,
        config: TargetConfig,
        environment: EnvironmentState,
        user: User,
        session: Session,
        registry: ToolRegistry | None = None,
    ) -> None:
        if session.user_id != user.user_id:
            raise ValueError(
                "Session user does not match the current user."
            )

        if config.max_tool_steps <= 0:
            raise ValueError(
                "max_tool_steps must be greater than zero."
            )

        self.model = model
        self.config = config
        self.environment = environment
        self.user = user
        self.session = session
        self.registry = registry or create_tool_registry()

        self._validate_exposed_tools()

        self.context = ToolContext(
            environment=environment,
            user=user,
            session=session,
            permissions=config.permissions,
            memory_write_mode=config.memory_write_mode,
        )

    def _validate_exposed_tools(self) -> None:
        """Ensure every configured tool exists."""

        unknown_tools = [
            name
            for name in self.config.exposed_tools
            if name not in TOOL_SCHEMAS_BY_NAME
        ]

        if unknown_tools:
            raise ValueError(
                f"Unknown exposed tools: {unknown_tools}"
            )

    @property
    def tool_schemas(self) -> tuple[ToolSchema, ...]:
        """Return only the schemas exposed to this target."""

        return tuple(
            TOOL_SCHEMAS_BY_NAME[name]
            for name in self.config.exposed_tools
        )

    def run(
        self,
        user_message: str,
    ) -> TargetRunResult:
        """Run one user interaction through the tool loop."""

        if not user_message.strip():
            raise ValueError(
                "user_message cannot be empty."
            )

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": self.config.system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        tool_steps = 0

        while True:
            response = self.model.generate(
                messages=messages,
                tools=self.tool_schemas,
            )

            if not response.tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": response.content,
                    }
                )

                return TargetRunResult(
                    final_response=response.content or "",
                    messages=tuple(messages),
                    tool_steps=tool_steps,
                )

            if (
                tool_steps + len(response.tool_calls)
                > self.config.max_tool_steps
            ):
                raise RuntimeError(
                    "Target agent exceeded its maximum "
                    "number of tool steps."
                )

            messages.append(
                {
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": [
                        {
                            "call_id": call.call_id,
                            "name": call.name,
                            "arguments": call.arguments,
                        }
                        for call in response.tool_calls
                    ],
                }
            )

            for call in response.tool_calls:
                result = self._execute_tool_call(call)

                messages.append(
                    {
                        "role": "tool",
                        "call_id": call.call_id,
                        "name": call.name,
                        "content": result,
                    }
                )

                tool_steps += 1

    def _execute_tool_call(
        self,
        call: ToolCall,
    ) -> Any:
        """Execute one model-generated tool call."""

        if call.name not in self.config.exposed_tools:
            raise PermissionError(
                f"Tool is not exposed to this target: {call.name}"
            )

        return self.registry.execute(
            name=call.name,
            context=self.context,
            arguments=call.arguments,
        )
