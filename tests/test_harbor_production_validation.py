from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_script():
    path = Path(__file__).parents[1] / "scripts/harbor_production_validation.py"
    spec = importlib.util.spec_from_file_location("harbor_production_validation", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gate = _load_script()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _artifact(path: Path, root: Path) -> dict[str, str]:
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": gate.sha256_file(path),
    }


def _grading(expected: int, reward: float) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "valid": True,
        "reward": reward,
        "expected_total": expected,
        "counts": {"collected": expected, "passed": round(expected * reward)},
        "collection": {"collection_errors": []},
        "failure_reason": None,
    }


def _network() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "public_network_available": False,
        "probes": {"pypi.org:443": False, "1.1.1.1:443": False},
    }


def test_frozen_input_validates_canonical_digest_without_git(tmp_path: Path) -> None:
    rows = [
        {"task_id": "alpha", "source_tree_sha1": "a" * 40},
        {"task_id": "beta", "source_tree_sha1": "b" * 40},
    ]
    payload = {
        "schema_version": "1.0",
        "campaign_id": "fixture",
        "base_commit": "c" * 40,
        "source_root": "catalog/sources",
        "source_count": 2,
        "sources": rows,
    }
    payload["content_sha256"] = gate.canonical_sha256(payload)
    path = tmp_path / "input.json"
    _write_json(path, payload)
    loaded, loaded_rows = gate.validate_frozen_input(
        path, repository_root=tmp_path, expected_sources=2, verify_git=False
    )
    assert loaded["content_sha256"] == payload["content_sha256"]
    assert loaded_rows == rows


def test_frozen_input_rejects_duplicate_task_ids(tmp_path: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "base_commit": "c" * 40,
        "source_root": "catalog/sources",
        "source_count": 2,
        "sources": [
            {"task_id": "alpha", "source_tree_sha1": "a" * 40},
            {"task_id": "alpha", "source_tree_sha1": "b" * 40},
        ],
    }
    payload["content_sha256"] = gate.canonical_sha256(payload)
    path = tmp_path / "input.json"
    _write_json(path, payload)
    with pytest.raises(gate.ProductionGateError, match="duplicate"):
        gate.validate_frozen_input(
            path, repository_root=tmp_path, expected_sources=2, verify_git=False
        )


def test_repository_relative_rejects_external_gate_input(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()

    with pytest.raises(gate.ProductionGateError, match="must be inside the repository"):
        gate.repository_relative(tmp_path / "outside.json", repository, "production input")


def test_current_source_freeze_rejects_head_or_worktree_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sources = tmp_path / "catalog/sources"
    sources.mkdir(parents=True)
    frozen = [{"task_id": "alpha", "source_tree_sha1": "a" * 40}]

    def clean_git(_root: Path, *args: str) -> str:
        if args[0] == "ls-tree":
            return f"040000 tree {'a' * 40}\talpha"
        return ""

    monkeypatch.setattr(gate, "_git_output", clean_git)
    gate.validate_current_source_freeze(
        frozen, repository_root=tmp_path, sources_root=sources
    )

    def changed_git(_root: Path, *args: str) -> str:
        if args[0] == "ls-tree":
            return f"040000 tree {'b' * 40}\talpha"
        return ""

    monkeypatch.setattr(gate, "_git_output", changed_git)
    with pytest.raises(gate.ProductionGateError, match="current HEAD source trees differ"):
        gate.validate_current_source_freeze(
            frozen, repository_root=tmp_path, sources_root=sources
        )

    def dirty_git(_root: Path, *args: str) -> str:
        if args[0] == "ls-tree":
            return f"040000 tree {'a' * 40}\talpha"
        return " M catalog/sources/alpha/task.toml"

    monkeypatch.setattr(gate, "_git_output", dirty_git)
    with pytest.raises(gate.ProductionGateError, match="source worktree differs"):
        gate.validate_current_source_freeze(
            frozen, repository_root=tmp_path, sources_root=sources
        )


def _runtime_fixture(
    root: Path, *, language: str = "python"
) -> tuple[dict[str, object], Path]:
    task_root = root / "task"
    files = {
        "environment/Dockerfile": "FROM python:3.12-slim\n",
        "instruction.md": "# Task\n",
        "solution/solve.sh": "#!/bin/sh\n",
        "tests/test.sh": "#!/bin/sh\n",
        "tests/verifier/run.py": "print('ok')\n",
        "task.toml": """schema_version = "1.4"
[metadata]
expected_test_count = 3
canonical_manifest_digest = "sha256:abc"
[environment]
network_mode = "no-network"
[verifier]
environment_mode = "separate"
network_mode = "no-network"
""",
    }
    for relative, content in files.items():
        path = task_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    rows = []
    for relative, (digest, size) in gate._file_inventory(task_root).items():
        rows.append({"path": relative, "sha256": digest, "size_bytes": size})
    _write_json(
        task_root / "bundle.manifest.json",
        {
            "schema_version": "1.0" if language == "python" else "2.0",
            "mode": "production",
            "canonical_manifest_digest": "sha256:abc",
            "files": rows,
        },
    )
    source = {
        "schema_version": "1.0" if language == "python" else "2.0",
        "metadata": {"language": language},
        "environment": {"network_policy": {"mode": "no-network"}},
        "tests": {"expected_total": 3},
    }
    return source, task_root


def test_runtime_shape_accepts_python_v1_bundle_manifest_and_validates_hashes(
    tmp_path: Path,
) -> None:
    source, task_root = _runtime_fixture(tmp_path)
    result = gate._validate_runtime_shape("fixture", source, task_root)
    assert result["schema_version"] == "1.4"
    (task_root / "instruction.md").write_text("changed\n", encoding="utf-8")
    with pytest.raises(gate.ProductionGateError, match="bundle manifest mismatch"):
        gate._validate_runtime_shape("fixture", source, task_root)


def test_runtime_shape_accepts_node_v2_bundle_manifest(tmp_path: Path) -> None:
    source, task_root = _runtime_fixture(tmp_path, language="node")

    result = gate._validate_runtime_shape("node-fixture", source, task_root)

    assert result["schema_version"] == "1.4"


def test_runtime_shape_rejects_bundle_manifest_schema_for_source_language(
    tmp_path: Path,
) -> None:
    source, task_root = _runtime_fixture(tmp_path, language="node")
    manifest_path = task_root / "bundle.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["schema_version"] = "1.0"
    _write_json(manifest_path, manifest)

    with pytest.raises(gate.ProductionGateError, match="node bundle manifest schema must be 2.0"):
        gate._validate_runtime_shape("node-fixture", source, task_root)


def _valid_gate_report(root: Path) -> tuple[Path, dict[str, object]]:
    expected = 5
    oracle_grading = root / "evidence/oracle/grading.json"
    oracle_network = root / "evidence/oracle/network.json"
    _write_json(oracle_grading, _grading(expected, 1.0))
    _write_json(oracle_network, _network())
    controls: dict[str, object] = {}
    for name in ("empty", "stub", "forgery"):
        grading = root / f"evidence/{name}/grading.json"
        network = root / f"evidence/{name}/network.json"
        _write_json(grading, _grading(expected, 0.0))
        _write_json(network, _network())
        controls[name] = {
            "command": f"run {name}",
            "exit_code": 0,
            "grading": _artifact(grading, root),
            "network": _artifact(network, root),
            **({"verifier_owned_reward": True} if name == "forgery" else {}),
        }
    offline_network = root / "evidence/offline/network.json"
    _write_json(offline_network, _network())
    controls["offline"] = {
        "command": "run offline",
        "exit_code": 0,
        "completed": True,
        "network": _artifact(offline_network, root),
    }
    evidence = {
        "schema_version": "1.0",
        "task_id": "fixture",
        "terminal_kind": "valid",
        "oracle": {
            "command": "harbor run -a oracle",
            "exit_code": 0,
            "harbor_version": "0.21.0",
            "grading": _artifact(oracle_grading, root),
            "network": _artifact(oracle_network, root),
        },
        "controls": controls,
    }
    report: dict[str, object] = {
        "schema_version": "1.0",
        "report_kind": "harbor-production-gate",
        "repository_root": ".",
        "ok": True,
        "tasks": [
            {
                "task_id": "fixture",
                "category": "valid",
                "expected_total": expected,
                "evidence": evidence,
            }
        ],
        "errors": [],
    }
    report["content_sha256"] = gate.canonical_sha256(report)
    path = root / "reports/gate.json"
    _write_json(path, report)
    return path, report


def test_oracle_and_control_evidence_are_hash_bound_and_fail_closed(tmp_path: Path) -> None:
    report_path, _report = _valid_gate_report(tmp_path)
    assert gate.validate_evidence(report_path, "oracle")["ok"] is True
    assert gate.validate_evidence(report_path, "controls")["ok"] is True
    grading = tmp_path / "evidence/stub/grading.json"
    _write_json(grading, _grading(5, 1.0))
    result = gate.validate_evidence(report_path, "controls")
    assert result["ok"] is False
    assert "hash mismatch" in result["errors"][0]["message"]


def test_grading_accepts_go_frozen_total_denominator() -> None:
    grading = _grading(1, 1.0)
    grading.pop("expected_total")
    grading["frozen_total"] = 1

    gate._validate_grading(
        "go-fixture",
        grading,
        expected_total=1,
        minimum_reward=0.8,
        maximum_reward=1.0,
    )


def test_blocked_evidence_requires_hashed_real_command_log(tmp_path: Path) -> None:
    log = tmp_path / "evidence/blocked.log"
    log.parent.mkdir(parents=True)
    log.write_text("compiler exited 1: missing artifact\n", encoding="utf-8")
    evidence = {
        "schema_version": "1.0",
        "task_id": "blocked-task",
        "terminal_kind": "blocked",
        "blocked": {
            "failure_class": "verifier",
            "next_step": "Materialize the missing private verifier bundle.",
            "source_freeze": {"status": "known"},
            "commands": [
                {
                    "command": "uv run nl2repo harbor compile ...",
                    "tool_version": "nl2repobench 0.1.0",
                    "exit_code": 1,
                    "log": _artifact(log, tmp_path),
                }
            ],
        },
    }
    report: dict[str, object] = {
        "schema_version": "1.0",
        "report_kind": "harbor-production-gate",
        "repository_root": ".",
        "ok": True,
        "tasks": [
            {"task_id": "blocked-task", "category": "blocked", "evidence": evidence}
        ],
        "errors": [],
    }
    report["content_sha256"] = gate.canonical_sha256(report)
    path = tmp_path / "reports/gate.json"
    _write_json(path, report)
    result = gate.validate_evidence(path, "blocked")
    assert result == {
        "schema_version": "1.0",
        "report_kind": "harbor-production-blocked-evidence",
        "tasks_checked": 1,
        "errors": [],
        "ok": True,
    }
