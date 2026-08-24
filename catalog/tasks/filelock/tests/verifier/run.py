"""Trusted `custom-json-v1` verifier for deterministic filelock scenarios.

The candidate is imported only by ``adapter.py`` in an unprivileged child.
Every contended scenario uses a ready/release pipe and an explicit finite
timeout. The trusted verifier owns expected values and produces the leaf
report consumed by the generic grader.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable


ROOT = Path("/tests/verifier")
CANDIDATE_UID = 10001


def _equals(expected: Any) -> Callable[[Any], bool]:
    return lambda value: value == expected


def _native_timeout(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("outcome") == "Timeout"
        and value.get("holder_released") is True
        and value.get("acquired_after_release") is True
        and isinstance(value.get("elapsed"), (float, int))
        and 0.10 <= value["elapsed"] <= 1.0
    )


CHECKS: tuple[tuple[str, str, Callable[[Any], bool]], ...] = (
    (
        "root-public-surface",
        "root_surface",
        _equals(
            {
                "version": "3.32.3",
                "names": {
                    "FileLock": True,
                    "SoftFileLock": True,
                    "StrictSoftFileLock": True,
                    "SoftFileLease": True,
                    "ReadWriteLock": True,
                    "SoftReadWriteLock": True,
                    "AsyncFileLock": True,
                    "Timeout": True,
                    "OwnerRecord": True,
                    "lock_descriptor": True,
                    "unlock_descriptor": True,
                },
                "all_names": True,
                "module_count": 12,
            }
        ),
    ),
    (
        "native-reentrant-context",
        "native_reentrant",
        _equals(
            {
                "first": [True, True, 1],
                "second": [True, True, 2],
                "after_nested": [True, 1],
                "after_outer": [False, 0],
            }
        ),
    ),
    ("native-bounded-contention", "native_timeout", _native_timeout),
    (
        "soft-marker-lifecycle",
        "soft_marker",
        _equals(
            {
                "held": {"exists": True, "pid": True, "ours": True, "counter": 1},
                "removed": True,
            }
        ),
    ),
    (
        "soft-ready-contention",
        "soft_timeout",
        _equals({"outcome": "Timeout", "holder_released": True}),
    ),
    (
        "strict-claim-lifecycle",
        "strict_claims",
        _equals(
            {
                "held": {
                    "count": 2,
                    "states": ["held", "intent"],
                    "pid_matches": True,
                    "names_unique": True,
                },
                "after_count": 0,
            }
        ),
    ),
    (
        "lease-lifecycle",
        "lease_lifecycle",
        _equals(
            {
                "held": {"token_length": 32, "compromise": True, "locked": True},
                "token_cleared": True,
                "locked": False,
            }
        ),
    ),
    ("lease-duration-mismatch", "lease_mismatch", _equals({"outcome": "LeaseSettingsMismatch"})),
    (
        "sqlite-reader-writer-modes",
        "read_write_modes",
        _equals({"nested_read": True, "upgrade": "RuntimeError", "write": True}),
    ),
    (
        "sqlite-reader-writer-contention",
        "read_write_timeout",
        _equals({"outcome": "Timeout", "holder_released": True}),
    ),
    (
        "soft-reader-writer-modes",
        "soft_read_write_modes",
        _equals({"read": True, "write": True}),
    ),
    (
        "descriptor-lifecycle",
        "descriptor_lifecycle",
        _equals({"acquired": True, "retained": True}),
    ),
    (
        "descriptor-contention",
        "descriptor_timeout",
        _equals({"contended": False, "holder_released": True}),
    ),
    (
        "async-lifecycle",
        "async_lifecycle",
        _equals({"held": [True, 1], "after": [False, 0]}),
    ),
    (
        "async-bounded-contention",
        "async_timeout",
        _equals({"outcome": "Timeout", "holder_released": True}),
    ),
    (
        "marker-codec",
        "marker_codec",
        _equals({"round_trip": True, "unknown_mode": "unknown", "malformed": True}),
    ),
    (
        "singleton-configuration",
        "singleton_configuration",
        _equals({"same_instance": True, "mismatch": "ValueError"}),
    ),
)


def _run_adapter() -> dict[str, Any]:
    work = Path(tempfile.mkdtemp(prefix="filelock-scenarios-"))
    os.chown(work, CANDIDATE_UID, CANDIDATE_UID)
    os.chmod(work, 0o700)
    adapter = work / "adapter.py"
    shutil.copy2(ROOT / "adapter.py", adapter)
    os.chown(adapter, CANDIDATE_UID, CANDIDATE_UID)
    os.chmod(adapter, 0o500)
    environment = {
        "HOME": os.fspath(work),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "CANDIDATE_ROOT": "/tmp/candidate-site",
        "NL2REPO_CANDIDATE_DEPENDENCIES": os.environ["NL2REPO_CANDIDATE_DEPENDENCIES"],
        "FILELOCK_SCENARIO_ROOT": os.fspath(work),
    }
    try:
        completed = subprocess.run(
            [
                "runuser",
                "-u",
                "candidate",
                "--",
                "env",
                *[f"{key}={value}" for key, value in environment.items()],
                "/usr/local/bin/python",
                "-I",
                "-B",
                os.fspath(adapter),
            ],
            cwd="/workspace",
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if completed.returncode != 0:
        raise RuntimeError(f"adapter exited {completed.returncode}: {completed.stderr[-2000:]}")
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"adapter emitted no report: {completed.stderr[-2000:]}")
    report = json.loads(lines[-1])
    if report.get("schema_version") != "1.0" or not isinstance(report.get("observations"), dict):
        raise RuntimeError("adapter report has an invalid schema")
    return report["observations"]


def main() -> None:
    try:
        observations = _run_adapter()
    except BaseException as error:
        print(f"filelock verifier infrastructure error: {type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(70) from None
    leaves = []
    for identifier, observation_name, predicate in CHECKS:
        observation = observations.get(observation_name)
        passed = (
            isinstance(observation, dict)
            and observation.get("ok") is True
            and predicate(observation.get("value"))
        )
        message = "" if passed else json.dumps(observation, sort_keys=True)[-1000:]
        leaves.append({"id": identifier, "status": "passed" if passed else "failed", "message": message})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
