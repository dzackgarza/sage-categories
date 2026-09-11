"""The two open Python special-method input positions (POL-TYPE-004)."""

from typing import Any

__all__ = ["ContainmentInput", "EqualityInput"]

# These are the only permitted aliases of ``Any``. They name Python protocol input
# positions rather than mathematical value types (D131, POL-TYPE-004/014/015).
type EqualityInput = Any
type ContainmentInput = Any
