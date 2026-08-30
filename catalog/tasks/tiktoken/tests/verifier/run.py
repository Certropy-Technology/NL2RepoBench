from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SCENARIOS: dict[str, Any] = {
    "exports": {"encoding": "Encoding", "get": True, "model": True, "names": True},
    "encoding_repr": {"repr": "<Encoding 'fixture'>", "max": 300, "n_vocab": 301},
    "bpe_merge": {"bytes": "hello", "text": "hello", "tokens": [259]},
    "special_guard": {"allowed": [300], "blocked": "builtins.ValueError"},
    "single_token": {"known": 259, "missing": "builtins.KeyError"},
    "decode_errors": {"replacement": "�", "strict": "builtins.UnicodeDecodeError"},
    "offsets": {"offsets": [0, 5, 6, 7, 8, 9, 10], "text": "hello world", "tokens": [259, 32, 119, 111, 114, 108, 100]},
    "batch_order": {"decoded": ["hello", "world", "hello world"], "encoded": [[259], [119, 111, 114, 108, 100], [259, 32, 119, 111, 114, 108, 100]]},
    "surrogate_replace": True,
    "pickle": {"repr": "<Encoding 'fixture'>", "same": True},
    "explicit_vocab": "builtins.AssertionError",
    "registry_names": ["gpt2", "r50k_base", "p50k_base", "p50k_edit", "cl100k_base", "o200k_base", "o200k_harmony"],
    "model_exact": "cl100k_base",
    "model_prefix": "cl100k_base",
    "model_unknown": "builtins.KeyError",
    "load_bpe": {"b": 1, "a": 0},
    "load_hash_mismatch": "builtins.ValueError",
    "dump_bpe": "YQ== 0\nYWI= 1\nYg== 2\n",
    "data_gym_local": {"size": 256, "space": 220, "zero": 188},
    "educational_bpe": [257],
    "educational_train": {"new": 256, "size": 257},
    "educational_wrapper": {"text": "ab", "tokens": [256]},
    "unknown_encoding": "builtins.ValueError",
    "offline_local_loader": "offline",
}


def invoke(scenario: str) -> dict[str, Any]:
    adapter = Path(__file__).with_name("adapter.py")
    command = [
        "runuser", "-u", "candidate", "--", "env",
        "HOME=/tmp", "TMPDIR=/tmp", "PATH=/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1",
        sys.executable, "-I", "-B", "-",
        "--candidate-site", "/tmp/candidate-site",
        "--dependency-site", "/opt/candidate-dependencies/site",
        "--scenario", scenario,
    ]
    try:
        completed = subprocess.run(
            command,
            input=adapter.read_text(encoding="utf-8"),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": completed.stderr[-1000:]}
    try:
        value = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return value if isinstance(value, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def matches(actual: dict[str, Any], expected: Any) -> bool:
    if actual.get("ok") is not True:
        return actual.get("exception_type") == expected
    return actual.get("value") == expected


def main() -> int:
    leaves = []
    for scenario, expected in SCENARIOS.items():
        actual = invoke(scenario)
        passed = matches(actual, expected)
        leaves.append({
            "id": f"tiktoken/{scenario}",
            "status": "passed" if passed else "failed",
            "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1000],
        })
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
