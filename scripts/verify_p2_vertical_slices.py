"""Run deterministic adapter vertical checks and report external blockers."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path
from typing import Any


def _diff_measure(root: Path, base: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "diff", base, "--numstat"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    allowed_fragments = (
        "package_managers/",
        "harbor/pnpm_compiler.py",
        "harbor/go_compiler.py",
        "harbor/registry.py",
        "verification/go_",
        "verification/node_pnpm",
        "tests/test_package_managers.py",
        "tests/test_go_adapter.py",
        "docs/",
    )
    outside = 0
    rows: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        row = {"path": path, "added": int(added or 0), "deleted": int(deleted or 0)}
        rows.append(row)
        if not any(fragment in path for fragment in allowed_fragments):
            outside += row["added"] + row["deleted"]
    return {"outside_allowed_lines": outside, "files": rows}


def _pnpm(root: Path, base: str) -> dict[str, Any]:
    from nl2repobench.harbor.pnpm_compiler import PnpmHarborCompiler
    from nl2repobench.package_managers.pnpm import PnpmPackageManager

    fixture = root / "catalog/sources/node-pnpm-synthetic"
    adapter = PnpmPackageManager()
    lock = fixture / "harbor/solution/pnpm-lock.yaml"
    lock_summary = adapter.validate_lock(lock, expected_version="9.15.0")
    with tempfile.TemporaryDirectory(prefix="nl2repo-pnpm-slice-") as tmp:
        output = PnpmHarborCompiler(root / "toolchain.node.dev.lock.toml").compile_task(
            fixture, Path(tmp), allow_incomplete=True
        )
        task = output / "task.toml"
        compiled = task.is_file() and 'package_manager = "pnpm"' in task.read_text()
    result = {
        "runtime": "node",
        "package_manager": "pnpm",
        "abstract_gate": "pass" if compiled else "fail",
        "lock_summary": lock_summary.__dict__,
        "oracle_runs_requested": 1,
        "status": "blocked",
        "release_status": "blocked",
        "release_blocked_reason": (
            "source lifecycle/image/store artifacts are not approved for publication"
        ),
        "blocked_reason": (
            "no reviewed pnpm store artifact or Harbor job evidence exists at this checkout"
        ),
        "controls": "not-run: requires locked Harbor pnpm image and offline store",
        "diff_measure": _diff_measure(root, base),
    }
    archived = root / "reports/node-pnpm-synthetic-controls-v1/pnpm-evidence.json"
    compiled = root / "reports/node-pnpm-synthetic-compiled-v1"
    required = (
        compiled / "task.toml",
        compiled / "verifier.Dockerfile",
        compiled / "bundle.manifest.json",
    )
    if archived.is_file() and all(path.is_file() for path in required):
        evidence = json.loads(archived.read_text(encoding="utf-8"))
        manifest = json.loads((compiled / "bundle.manifest.json").read_text(encoding="utf-8"))
        if (
            evidence.get("archive_contract") == "p2-vertical-slice-v1"
            and evidence.get("oracle_reward") == 1.0
            and evidence.get("empty_reward") == 0.0
            and isinstance(manifest.get("files"), list)
            and manifest.get("files")
        ):
            result["status"] = "pass"
            result["blocked_reason"] = None
            result["controls"] = "pass"
    return result


def _go(root: Path) -> dict[str, Any]:
    from nl2repobench.harbor.go_compiler import GoHarborCompiler
    from nl2repobench.package_managers.go_modules import GoModulesPackageManager
    from nl2repobench.verification.go_supervisor import run_go_bridge

    fixture = root / "catalog/sources/go-google-uuid"
    compiler = GoHarborCompiler(root / "toolchain.go.dev.lock.toml")
    build_status = "not-run"
    controls: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="nl2repo-go-slice-") as tmp:
        output = compiler.compile_task(fixture, Path(tmp), allow_incomplete=True)
        compiled = (output / "tests/private/bridge.go").is_file()
        candidate = Path(tmp) / "candidate"
        candidate.mkdir()
        solved = subprocess.run(
            ["bash", str(fixture / "harbor/solution/solve.sh")],
            cwd=candidate,
            capture_output=True,
            text=True,
            check=False,
        )
        if solved.returncode == 0:
            bridge = candidate / "cmd/bridge"
            bridge.mkdir(parents=True)
            shutil.copy2(output / "tests/private/bridge.go", bridge / "main.go")
            built = subprocess.run(
                ["go", "build", "-o", str(candidate / "bridge"), "./cmd/bridge"],
                cwd=candidate,
                env={**os.environ, "GOPROXY": "off", "GOSUMDB": "off", "GOTOOLCHAIN": "local"},
                capture_output=True,
                text=True,
                check=False,
            )
            build_status = "pass" if built.returncode == 0 else "fail: " + built.stderr[-500:]
            if built.returncode == 0:
                contract = run_go_bridge(
                    (str(candidate / "bridge"),),
                    b'{"operation":"parse","args":["550e8400-e29b-41d4-a716-446655440000"]}\n',
                )
                controls["oracle"] = (
                    "pass"
                    if contract.returncode == 0
                    and json.loads(contract.stdout) == {
                        "value": "550e8400-e29b-41d4-a716-446655440000"
                    }
                    else "fail"
                )
                controls["offline"] = "pass"
            else:
                controls["oracle"] = "fail"
                controls["offline"] = "fail"
        else:
            controls["oracle"] = "fail"
            controls["offline"] = "fail"
        controls["empty"] = "model-zero"
        controls["stub"] = "model-zero"
        controls["forgery"] = "ignored-by-trusted-result"
        controls["hang"] = "timeout-guarded"
        source = tomllib.loads((fixture / "task.toml").read_text(encoding="utf-8"))
    return {
        "runtime": "go",
        "package_manager": "go-modules",
        "abstract_gate": "pass" if compiled else "fail",
        "source_revision": source["source"]["revision"],
        "source_digest": source["source"]["source_digest"],
        "real_bridge_build": build_status,
        "local_controls": controls,
        "lock_validator": GoModulesPackageManager().identity,
        "oracle_runs_requested": 1,
        "status": "blocked",
        "release_status": "blocked",
        "release_blocked_reason": (
            "source lifecycle/environment publication evidence is not complete"
        ),
        "blocked_reason": (
            "no frozen real Go source revision, locked image, or Harbor job artifact "
            "exists at this checkout"
        ),
        "controls": "not-run: requires a real candidate and locked verifier image",
    }


def _latest_job(root: Path) -> Path:
    jobs = sorted(path for path in root.iterdir() if path.is_dir())
    if not jobs:
        raise ValueError(f"no Harbor job under {root}")
    return jobs[-1]


def _harbor_controls(jobs_root: Path) -> dict[str, Any]:
    names = ("oracle", "empty", "stub", "forgery", "install-failure", "call-hang")
    controls: dict[str, Any] = {}
    for name in names:
        job = _latest_job(jobs_root / name)
        trials = sorted(path for path in job.iterdir() if path.is_dir())
        if len(trials) != 1:
            raise ValueError(f"expected one trial for {name}, found {trials}")
        trial = trials[0]
        result = json.loads((job / "result.json").read_text(encoding="utf-8"))
        evaluation = next(iter(result["stats"]["evals"].values()))
        metric = evaluation["metrics"][0]
        grading = json.loads((trial / "verifier/grading.json").read_text(encoding="utf-8"))
        controls[name] = {
            "reward": metric["reward"],
            "exceptions": evaluation["n_errors"],
            "valid": grading.get("valid"),
            "failure_class": grading.get("failure_class"),
            "failure_reason": grading.get("failure_reason"),
            "job": str(job),
        }
    expected = {
        "oracle": controls["oracle"]["valid"] is True and controls["oracle"]["reward"] >= 0.8,
        "empty": controls["empty"]["reward"] == 0.0,
        "stub": controls["stub"]["reward"] <= 0.2,
        "forgery": controls["forgery"]["reward"] >= 0.8,
        "install-failure": controls["install-failure"]["valid"] is True,
        "call-hang": controls["call-hang"]["valid"] is True,
    }
    return {"controls": controls, "gates": expected, "all_pass": all(expected.values())}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=("node", "go"), required=True)
    parser.add_argument("--package-manager", required=True)
    parser.add_argument("--oracle-runs", type=int, default=1)
    parser.add_argument("--base", default="1d2927a")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--jobs-dir", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.runtime == "node" and args.package_manager != "pnpm":
        raise SystemExit("node vertical slice only supports pnpm in P2")
    if args.runtime == "go" and args.package_manager != "go-modules":
        raise SystemExit("go vertical slice only supports go-modules")
    result = (
        _pnpm(root, args.base)
        if args.runtime == "node"
        else _go(root)
    )
    if args.jobs_dir is not None:
        harbor = _harbor_controls(args.jobs_dir)
        result["harbor_controls"] = harbor
        if harbor["all_pass"]:
            result["status"] = "pass"
            result["blocked_reason"] = None
            result["controls"] = "pass"
            result["archive_contract"] = "p2-vertical-slice-v1"
    elif args.runtime == "go":
        archived = root / "reports/go-google-uuid-controls-v1/summary.json"
        if archived.is_file():
            evidence = json.loads(archived.read_text(encoding="utf-8"))
            harbor_controls = evidence.get("harbor_controls", {})
            compiled = root / "reports/go-google-uuid-compiled-v1"
            manifest_path = compiled / "bundle.manifest.json"
            if (
                evidence.get("status") == "pass"
                and evidence.get("archive_contract") == "p2-vertical-slice-v1"
                and harbor_controls.get("all_pass") is True
                and manifest_path.is_file()
            ):
                result["harbor_controls"] = harbor_controls
                result["status"] = "pass"
                result["blocked_reason"] = None
                result["controls"] = "pass"
                result["archive_contract"] = "p2-vertical-slice-v1"
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
