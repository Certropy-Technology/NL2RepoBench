from __future__ import annotations

import pytest

from nl2repobench.runtimes.rust import cargo_feature_args


@pytest.mark.parametrize(
    ("default_features", "enabled", "expected"),
    [
        (True, (), ()),
        (False, (), ("--no-default-features",)),
        (True, ("serde", "std"), ("--features", "serde,std")),
        (
            False,
            ("serde", "std"),
            ("--no-default-features", "--features", "serde,std"),
        ),
    ],
)
def test_cargo_feature_args_returns_the_frozen_argv_matrix(
    default_features: bool,
    enabled: tuple[str, ...],
    expected: tuple[str, ...],
) -> None:
    assert cargo_feature_args(default_features, enabled) == expected


@pytest.mark.parametrize("enabled", [("std", "serde"), ("std", "std")])
def test_cargo_feature_args_rejects_noncanonical_feature_lists(
    enabled: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError, match="sorted and unique"):
        cargo_feature_args(False, enabled)
