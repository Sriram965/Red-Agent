from target.configurations import (
    MEMORY_TARGET,
    RETRIEVAL_TARGET,
    STANDARD_TARGET,
    STRICT_TARGET,
    TARGET_CONFIGS,
)


def test_target_configurations_are_unique():
    configs = (
        STANDARD_TARGET,
        RETRIEVAL_TARGET,
        MEMORY_TARGET,
        STRICT_TARGET,
    )

    assert len({config.name for config in configs}) == 4


def test_target_configuration_registry_contains_all_targets():
    assert set(TARGET_CONFIGS) == {
        "standard_target",
        "retrieval_target",
        "memory_target",
        "strict_target",
    }


def test_target_configurations_have_different_tool_surfaces():
    assert set(STANDARD_TARGET.exposed_tools) != set(
        RETRIEVAL_TARGET.exposed_tools
    )

    assert set(MEMORY_TARGET.exposed_tools) != set(
        STANDARD_TARGET.exposed_tools
    )


def test_target_configurations_have_different_memory_behaviors():
    assert (
        STANDARD_TARGET.memory_write_mode
        != STRICT_TARGET.memory_write_mode
    )

    assert (
        MEMORY_TARGET.memory_write_mode
        != STANDARD_TARGET.memory_write_mode
    )
