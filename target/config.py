from enum import Enum


class MemoryWriteMode(str, Enum):
    """How persistent-memory writes are handled by a target."""

    FULL = "full"
    NO_OVERWRITE = "no_overwrite"
    READ_ONLY = "read_only"
