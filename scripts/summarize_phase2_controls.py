"""Validate and summarize the Harbor Phase 2 control matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from pathlib import Path
from typing import Any


def latest_job(root: Path) -> Path:
    jobs = [path for path in root.iterdir() if path.is_dir()]
    if not jobs:
        raise ValueError(f"no Harbor job found under {root}")
    return max(jobs, key=lambda path: path.stat().st_mtime)


def verifier_artifact(job: Path, name: str) -> Path:
    matches = [path for path in job.rglob(name) if path.parent.name == "verifier"]
    if len(matches) != 1:
        raise ValueError(f"expected one verifier/{name} under {job}, found {matches}")
    return matches[0]


def read_control(root: Path) -> dict[str, Any]:
    job = latest_job(root)
    result = json.loads((job / "result.json").read_text(encoding="utf-8"))
    evaluation = next(iter(result["stats"]["evals"].values()))
    metric = evaluation["metrics"][0]
    grading_path = verifier_artifact(job, "grading.json")
    grading = json.loads(grading_path.read_text(encoding="utf-8"))
    network = json.loads(verifier_artifact(job, "network.json").read_text(encoding="utf-8"))
    if grading["reward"] != metric["reward"]:
        raise ValueError(f"Harbor/grading reward mismatch under {job}")
    if grading["valid"] and grading.get("failure_reason") is None:
        expected_reward = grading["counts"]["passed"] / grading["expected_total"]
        if grading["reward"] != expected_reward:
            raise ValueError(f"fixed-denominator reward mismatch under {job}")
    return {
        "reward": metric["reward"],
        "test_pass_rate": metric["test_pass_rate"],
        "exceptions": evaluation["n_errors"],
        "grading_valid": grading["valid"],
        "failure_class": grading.get("failure_class"),
        "failure_reason": grading.get("failure_reason"),
        "public_network_available": network["public_network_available"],
        "job": str(job),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jobs", type=Path)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--toolchain", type=Path, default=Path("toolchain.lock.toml"))
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    names = [
        "oracle-1",
        "oracle-2",
        "oracle-3",
        "nop",
        "stub",
        "forgery",
        "install-hang",
        "workspace-invalid",
        "call-hang",
    ]
    controls = {name: read_control(args.jobs / name) for name in names}
    for name in ("oracle-1", "oracle-2", "oracle-3"):
        assert controls[name]["reward"] == 1.0, controls[name]
        assert controls[name]["grading_valid"] is True, controls[name]
        assert controls[name]["public_network_available"] is False, controls[name]
    assert controls["nop"]["reward"] == 0.0, controls["nop"]
    assert controls["stub"]["reward"] <= 0.2, controls["stub"]
    assert controls["forgery"]["reward"] <= 0.2, controls["forgery"]
    assert controls["stub"]["grading_valid"] is True, controls["stub"]
    assert controls["forgery"]["grading_valid"] is True, controls["forgery"]
    assert controls["install-hang"]["reward"] == 0.0, controls["install-hang"]
    assert controls["install-hang"]["grading_valid"] is True, controls["install-hang"]
    assert controls["install-hang"]["failure_reason"] == "candidate-installation-failed"
    assert controls["workspace-invalid"]["reward"] == 0.0, controls["workspace-invalid"]
    assert controls["workspace-invalid"]["grading_valid"] is True
    assert controls["workspace-invalid"]["failure_reason"] == "candidate-workspace-rejected"
    assert controls["call-hang"]["reward"] <= 0.2, controls["call-hang"]
    assert controls["call-hang"]["grading_valid"] is True, controls["call-hang"]
    assert all(control["exceptions"] == 0 for control in controls.values()), controls
    assert all(control["public_network_available"] is False for control in controls.values()), (
        controls
    )

    bundle_manifest_data = (args.bundle / "bundle.manifest.json").read_bytes()
    bundle_manifest = json.loads(bundle_manifest_data)
    toolchain = tomllib.loads(args.toolchain.read_text(encoding="utf-8"))

    def common(control: dict[str, Any]) -> dict[str, Any]:
        return {
            "reward": control["reward"],
            "test_pass_rate": control["test_pass_rate"],
            "grading_valid": control["grading_valid"],
            "exceptions": control["exceptions"],
            "public_network_available": control["public_network_available"],
        }

    empty = common(controls["nop"])
    empty["failure_class"] = controls["nop"]["failure_class"]
    empty["failure_reason"] = controls["nop"]["failure_reason"]
    evidence = {
        "schema_version": "1.0",
        "harbor_version": toolchain["harbor"]["version"],
        "task_schema": toolchain["harbor"]["task_schema"],
        "canonical_manifest_digest": bundle_manifest["canonical_manifest_digest"],
        "bundle_manifest_sha256": hashlib.sha256(bundle_manifest_data).hexdigest(),
        "toolchain_digest": bundle_manifest["toolchain_lock_digest"],
        "harbor_lock_sha256": toolchain["harbor"]["lock_sha256"],
        "verifier_requirements_sha256": toolchain["verifier"]["requirements_sha256"],
        "controls": {
            "oracle": [
                {"attempt": attempt, **common(controls[f"oracle-{attempt}"])}
                for attempt in (1, 2, 3)
            ],
            "empty": empty,
            "stub": common(controls["stub"]),
            "forgery": common(controls["forgery"]),
            "install_hang": {
                **common(controls["install-hang"]),
                "failure_class": controls["install-hang"]["failure_class"],
                "failure_reason": controls["install-hang"]["failure_reason"],
            },
            "workspace_invalid": {
                **common(controls["workspace-invalid"]),
                "failure_class": controls["workspace-invalid"]["failure_class"],
                "failure_reason": controls["workspace-invalid"]["failure_reason"],
            },
            "call_hang": common(controls["call-hang"]),
        },
    }
    if args.reference is not None:
        reference = json.loads(args.reference.read_text(encoding="utf-8"))
        reference.pop("recorded_at", None)
        if reference != evidence:
            raise ValueError("control evidence does not match the checked reference report")

    payload = {
        "schema_version": "1.0",
        "evidence": evidence,
        "jobs": {name: control["job"] for name, control in controls.items()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
