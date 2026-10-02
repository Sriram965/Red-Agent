from target.agent import TargetConfig
from target.config import MemoryWriteMode
from target.permissions import PermissionPolicy
from target.prompt import (
    MEMORY_AWARE_PROMPT,
    RETRIEVAL_AWARE_PROMPT,
    STANDARD_SUPPORT_PROMPT,
    STRICT_SECURITY_PROMPT,
)


STANDARD_TARGET = TargetConfig(
    name="standard_target",
    system_prompt=STANDARD_SUPPORT_PROMPT,
    exposed_tools=(
        "search_knowledge_base",
        "lookup_customer",
        "read_ticket",
        "update_ticket",
        "send_message",
        "memory_read",
        "memory_write",
    ),
    permissions=PermissionPolicy(),
    memory_write_mode=MemoryWriteMode.FULL,
    max_tool_steps=8,
)


RETRIEVAL_TARGET = TargetConfig(
    name="retrieval_target",
    system_prompt=RETRIEVAL_AWARE_PROMPT,
    exposed_tools=(
        "search_knowledge_base",
        "lookup_customer",
        "read_ticket",
    ),
    permissions=PermissionPolicy(),
    memory_write_mode=MemoryWriteMode.READ_ONLY,
    max_tool_steps=8,
)


MEMORY_TARGET = TargetConfig(
    name="memory_target",
    system_prompt=MEMORY_AWARE_PROMPT,
    exposed_tools=(
        "search_knowledge_base",
        "lookup_customer",
        "read_ticket",
        "memory_read",
        "memory_write",
    ),
    permissions=PermissionPolicy(),
    memory_write_mode=MemoryWriteMode.NO_OVERWRITE,
    max_tool_steps=8,
)


STRICT_TARGET = TargetConfig(
    name="strict_target",
    system_prompt=STRICT_SECURITY_PROMPT,
    exposed_tools=(
        "search_knowledge_base",
        "lookup_customer",
        "read_ticket",
        "update_ticket",
        "send_message",
        "memory_read",
        "memory_write",
    ),
    permissions=PermissionPolicy(),
    memory_write_mode=MemoryWriteMode.READ_ONLY,
    max_tool_steps=8,
)


PERMISSIVE_TARGET = TargetConfig(
    name="permissive_target",
    system_prompt=STANDARD_SUPPORT_PROMPT,
    exposed_tools=(
        "search_knowledge_base",
        "lookup_customer",
        "read_ticket",
        "update_ticket",
        "send_message",
        "memory_read",
        "memory_write",
    ),
    permissions=PermissionPolicy(
        verified_can_lookup_any_customer=True,
        verified_can_read_restricted_ticket=True,
        verified_can_update_ticket=True,
        verified_can_send_message=True,
    ),
    memory_write_mode=MemoryWriteMode.FULL,
    max_tool_steps=8,
)


TARGET_CONFIGS: dict[str, TargetConfig] = {
    STANDARD_TARGET.name: STANDARD_TARGET,
    RETRIEVAL_TARGET.name: RETRIEVAL_TARGET,
    MEMORY_TARGET.name: MEMORY_TARGET,
    STRICT_TARGET.name: STRICT_TARGET,
    PERMISSIVE_TARGET.name: PERMISSIVE_TARGET,
}
