from __future__ import annotations

import pytest

from nl2repobench.verification.java_bridge import JavaValueType, validate_java_value


@pytest.mark.parametrize("kind", ["array", "list"])
def test_java_bridge_accepts_valid_sequence_values(kind: str) -> None:
    value_type = JavaValueType(kind=kind, element=JavaValueType(kind="int32"))

    validate_java_value([1, 2, 3], value_type)


def test_java_bridge_rejects_duplicate_set_values() -> None:
    value_type = JavaValueType(kind="set", element=JavaValueType(kind="string"))

    with pytest.raises(ValueError, match="set value is invalid"):
        validate_java_value(["duplicate", "duplicate"], value_type)
