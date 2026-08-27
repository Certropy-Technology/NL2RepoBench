from __future__ import annotations

import json
import os
import select
import signal
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/tests/verifier")
DRAFTS = {
    "draft4": "http://json-schema.org/draft-04/schema",
    "draft6": "http://json-schema.org/draft-06/schema",
    "draft7": "http://json-schema.org/draft-07/schema",
    "draft2019-09": "http://json-schema.org/draft-2019-09/schema",
}


def cases():
    for draft, version in DRAFTS.items():
        for path in sorted((ROOT / "suite" / draft).glob("*.json")):
            for group in json.loads(path.read_text(encoding="utf-8")):
                for test in group["tests"]:
                    yield {
                        "operation": "validate",
                        "draft": version,
                        "schema": group["schema"],
                        "data": test["data"],
                    }, test["valid"], f"{draft}/{path.name}/{test['description']}"


def all_cases():
    yield from cases()
    special = [
        ({"operation": "validate", "schema": {"type": "object", "properties": {"x": {"type": "integer", "default": 3}}}, "data": {}}, {"ok": True, "value": {"x": 3}}, "default"),
        ({"operation": "validate", "schema": {"type": "object", "properties": {"x": {"type": "integer"}}, "required": ["x"]}, "data": {}}, False, "required"),
        ({"operation": "validate", "schema": {"$ref": "http://example.test/number"}, "remote_schemas": {"http://example.test/number": {"type": "number"}}, "data": 4}, True, "remote-valid"),
        ({"operation": "validate", "schema": {"$ref": "http://example.test/number"}, "remote_schemas": {"http://example.test/number": {"type": "number"}}, "data": "4"}, False, "remote-invalid"),
        ({"operation": "generated", "schema": {"type": "object", "properties": {"x": {"type": "integer"}}}, "data": {"x": 4}}, True, "generated-valid"),
        ({"operation": "generated", "schema": {"type": "object", "properties": {"x": {"type": "integer"}}}, "data": {"x": "4"}}, False, "generated-invalid"),
        ({"operation": "validate", "schema": {"type": "string", "format": "identifier"}, "formats": {"identifier": "is_identifier"}, "data": "valid_name"}, True, "callback-recipe"),
        ({"operation": "metadata"}, {"ok": True, "version_is_string": True, "callables_present": True, "exception_hierarchy": True}, "public-api-surface"),
    ]
    yield from special


def main() -> None:
    adapter = Path("/tmp/fjs-candidate-rpc.py")
    shutil.copyfile(ROOT / "candidate_rpc.py", adapter)
    adapter.chmod(0o555)
    remote_root = Path("/tmp/fjs-remotes")
    meta_root = Path("/tmp/fjs-metaschemas")
    for source, target in ((ROOT / "remotes", remote_root), (ROOT / "metaschemas", meta_root)):
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        target.chmod(0o555)
        for directory in target.rglob("*"):
            directory.chmod(0o555 if directory.is_dir() else 0o444)
    env = {
        **os.environ,
        "FJS_REMOTE_ROOT": str(remote_root),
        "FJS_META_ROOT": str(meta_root),
    }
    process = subprocess.Popen(
        ["runuser", "-u", "candidate", "--", "env", *[f"{k}={v}" for k, v in env.items() if k.startswith("FJS_")], "/usr/local/bin/python", "-I", str(adapter), "--candidate", "/tmp/candidate-site"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        start_new_session=True,
    )
    leaves = []
    seen = {}
    candidate_unavailable = False
    try:
        assert process.stdin and process.stdout
        for request, expected, name in all_cases():
            count = seen.get(name, 0)
            seen[name] = count + 1
            leaf_id = name if count == 0 else f"{name}#{count}"
            if candidate_unavailable:
                leaves.append(
                    {
                        "id": leaf_id,
                        "status": "failed",
                        "message": "candidate unavailable after timeout or exit",
                    }
                )
                continue
            process.stdin.write(json.dumps(request, ensure_ascii=False, allow_nan=False) + "\n")
            process.stdin.flush()
            ready, _, _ = select.select([process.stdout], [], [], 15.0)
            if not ready:
                leaves.append(
                    {"id": leaf_id, "status": "failed", "message": "candidate timeout"}
                )
                candidate_unavailable = True
                os.killpg(process.pid, signal.SIGTERM)
                continue
            response_line = process.stdout.readline()
            if not response_line:
                leaves.append(
                    {"id": leaf_id, "status": "failed", "message": "candidate exited"}
                )
                candidate_unavailable = True
                continue
            response = json.loads(response_line)
            if isinstance(expected, dict):
                passed = "error" not in response and all(
                    response.get(key) == value for key, value in expected.items()
                )
            else:
                passed = "error" not in response and response.get("ok") is expected
            leaves.append(
                {
                    "id": leaf_id,
                    "status": "passed" if passed else "failed",
                    "message": "" if passed else json.dumps(response, sort_keys=True)[:512],
                }
            )
    finally:
        if process.stdin:
            process.stdin.close()
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=10)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
