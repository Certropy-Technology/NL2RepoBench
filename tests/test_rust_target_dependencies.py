from __future__ import annotations

import json
from pathlib import Path

import pytest

from nl2repobench.runtimes.rust import evaluate_target_selector, normalize_target_selector

ROOT = Path(__file__).parent


@pytest.mark.parametrize(
    ("selector", "selected"),
    [
        ("x86_64-unknown-linux-gnu", True),
        ('cfg(target_os="linux")', True),
        ('cfg(all(target_arch="x86_64",target_env="gnu"))', True),
        ('cfg(not(target_os="linux"))', False),
        ('cfg(any(target_os="linux",target_family="unix"))', True),
    ],
)
def test_target_selector_uses_the_frozen_grammar_and_target(
    selector: str,
    selected: bool,
) -> None:
    assert normalize_target_selector(selector) == selector
    assert evaluate_target_selector(selector) is selected


@pytest.mark.parametrize(
    "selector",
    [
        'cfg(target_os = "linux")',
        'cfg(target_os="windows")',
        'cfg(unix)',
        'cfg(feature="std")',
        "aarch64-unknown-linux-gnu",
        'cfg(all(target_os="linux"))',
    ],
)
def test_target_selector_rejects_noncanonical_or_host_dependent_syntax(
    selector: str,
) -> None:
    with pytest.raises(ValueError, match="target selector"):
        normalize_target_selector(selector)


def test_target_selector_public_fixture_covers_true_false_and_rejected_branches() -> None:
    fixture = json.loads(
        (ROOT / "fixtures/rust-cargo-r0/target-selectors.json").read_text(encoding="utf-8")
    )
    assert [
        evaluate_target_selector(entry["selector"]) for entry in fixture["accepted"]
    ] == [entry["selected"] for entry in fixture["accepted"]]
    for selector in fixture["rejected"]:
        with pytest.raises(ValueError):
            normalize_target_selector(selector)
