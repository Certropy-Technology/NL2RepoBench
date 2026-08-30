from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_pinned_openhands_fork_uses_the_canonical_root_submodule() -> None:
    gitmodules = (ROOT / ".gitmodules").read_text(encoding="utf-8")
    build_script = (ROOT / "scripts/build_openhands_runtime.sh").read_text(
        encoding="utf-8"
    )

    assert '[submodule "openhands"]' in gitmodules
    assert "path = openhands" in gitmodules
    assert "vendor/openhands-software-agent-sdk" not in gitmodules
    assert 'CONTEXT="$ROOT/openhands"' in build_script
    assert "vendor/openhands-software-agent-sdk" not in build_script


def test_removed_openhands_056_runner_does_not_return() -> None:
    removed = (
        "main.py",
        "only_test.py",
        "test_data_service.py",
        "logging_config.py",
        "config.json",
        "docker_self",
        "legacy",
        "template",
        "tests/legacy",
    )

    assert [path for path in removed if (ROOT / path).exists()] == []
