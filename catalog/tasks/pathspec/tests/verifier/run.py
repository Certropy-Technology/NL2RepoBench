from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


LEAF_IDS = (
    "exports.root", "exports.version", "exports.factory",
    "pattern.include", "pattern.abstract", "regex.match", "regex.no-match",
    "regex.precompiled", "regex.value-semantics",
    "wildmatch.star", "wildmatch.negation", "wildmatch.comment",
    "wildmatch.escape-comment", "wildmatch.double-star",
    "wildmatch.character-class", "wildmatch.escape-api", "wildmatch.invalid",
    "pathspec.length", "pathspec.match-file", "pathspec.match-files-order",
    "pathspec.check-file", "pathspec.check-files", "pathspec.negate",
    "pathspec.generator-lines", "pathspec.reject-string-lines", "pathspec.add",
    "pathspec.iadd", "pathspec.equality", "pathspec.repr",
    "gitignore.default-factory", "gitignore.directory", "gitignore.reinclude",
    "gitignore.last-rule", "gitignore.reject-basic",
    "util.normalize", "util.match-file", "util.check-last", "util.details",
    "util.registration", "filesystem.files", "filesystem.entries",
    "filesystem.append-dir", "runtime.uid",
)


def fail_all(message: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "leaves": [
            {"id": leaf_id, "status": "failed", "message": message[:500]}
            for leaf_id in LEAF_IDS
        ],
    }


def main() -> None:
    candidate_site = pathlib.Path(os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"))
    source_adapter = pathlib.Path(__file__).with_name("adapter.py")
    work = pathlib.Path(tempfile.mkdtemp(prefix="pathspec-verifier-", dir="/tmp"))
    adapter = work / "adapter.py"
    try:
        shutil.copyfile(source_adapter, adapter)
        os.chmod(work, 0o755)
        os.chmod(adapter, 0o500)
        if os.geteuid() == 0:
            os.chown(work, 10001, 10001)
            os.chown(adapter, 10001, 10001)
            command = [
                "runuser", "-u", "candidate", "--", "env",
                "HOME=/home/candidate", "PYTHONDONTWRITEBYTECODE=1",
                sys.executable, "-I", str(adapter), str(candidate_site),
            ]
        else:
            command = [sys.executable, "-I", str(adapter), str(candidate_site)]
        completed = subprocess.run(
            command,
            cwd=work,
            capture_output=True,
            text=True,
            timeout=40,
            check=False,
            start_new_session=True,
        )
        if completed.returncode != 0:
            report = fail_all(f"candidate adapter failed ({completed.returncode}): {completed.stderr[-300:]}")
        else:
            lines = [line for line in completed.stdout.splitlines() if line.strip()]
            payload = json.loads(lines[-1])
            results = payload["results"]
            leaves = []
            for leaf_id in LEAF_IDS:
                value = results.get(leaf_id)
                if value is True:
                    leaves.append({"id": leaf_id, "status": "passed"})
                else:
                    leaves.append({"id": leaf_id, "status": "failed", "message": repr(value)[:500]})
            report = {"schema_version": "1.0", "leaves": leaves}
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, json.JSONDecodeError) as exc:
        report = fail_all(f"verifier orchestration failed: {type(exc).__name__}: {exc}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
