"""Regenerate verifier-only parts of the flat Harbor projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tomllib
from pathlib import Path

from nl2repobench.harbor.task_writer import copy_python_verifier_runtime


def _refresh_manifest(task: Path) -> None:
    manifest_path = task / "bundle.manifest.json"
    if not manifest_path.is_file():
        return
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = []
    for path in sorted(p for p in task.rglob("*") if p.is_file() and p != manifest_path):
        data = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(task).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            }
        )
    payload["files"] = files
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _projection_dockerfile(existing: str, *, node_image: str, python_image: str) -> str:
    body_start = existing.find("COPY dependencies /opt/npm-bundle")
    rest = existing[body_start:] if body_start >= 0 else existing.split("\n", 1)[1]
    needle = (
        "RUN useradd --uid 10001 --create-home candidate \\\n"
        "  && chmod -R 0500 /tests/private \\\n"
        "  && chmod -R 0555 /tests/runtime"
    )
    replacement = (
        "RUN useradd --uid 10001 --create-home candidate \\\n"
        "  && chmod -R 0555 /opt/nl2repobench-runtime \\\n"
        "  && chmod -R 0500 /tests/private \\\n"
        "  && chmod -R 0555 /tests/runtime"
    )
    rest = rest.replace(needle, replacement)
    header = f"""FROM {node_image} AS node-runtime
FROM {python_image}

COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \\
  && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
COPY python-runtime /opt/nl2repobench-runtime
COPY verifier-requirements.lock.txt /tmp/verifier-requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \\
  -r /tmp/verifier-requirements.lock.txt
"""
    return header + rest


def _sync_projection_test_script(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "network_check" not in text:
        marker = "rm -rf /tmp/candidate-source /tmp/candidate-site /tmp/npm-cache\n"
        if marker not in text:
            marker = "rm -rf /tmp/candidate-source /tmp/candidate-site /tmp/pnpm-store\n"
        check = (
            "NETWORK_CHECK='import sys; sys.path.insert(0, \"/opt/nl2repobench-runtime\");'\n"
            "NETWORK_CHECK+='from nl2repobench.verification.network_check import main; main()'\n"
            "if ! python3 -I -c \"$NETWORK_CHECK\" --output /logs/verifier/network.json; then\n"
            "  node /tests/runtime/node/grade-report.mjs --expected 0 "
            "--reason verifier-network-available --output /logs/verifier\n"
            "  exit 0\n"
            "fi\n"
        )
        text = text.replace(marker, marker + check, 1)
    if "--reason candidate-call-failed" not in text and "runner_exit_code=0" in text:
        command = "  --output /logs/verifier/report.json || runner_exit_code=$?\n"
        if command in text:
            text = text.replace(
                command,
                command
                + "if [[ \"$runner_exit_code\" -eq 70 ]]; then\n"
                "  node /tests/runtime/node/grade-report.mjs --expected 0 "
                "--reason candidate-call-failed --output /logs/verifier\n"
                "  exit 0\n"
                "fi\n",
                1,
            )
    path.write_text(text, encoding="utf-8")


def sync(root: Path) -> list[str]:
    canonical_grader = root / "src/nl2repobench/verification/node/grade-report.mjs"
    requirements = root / "verifier/requirements.lock.txt"
    node_image = (
        "docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848"
    )
    python_image = (
        "python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a"
    )
    changed: list[str] = []
    for task in sorted(path for path in (root / "catalog/tasks").iterdir() if path.is_dir()):
        task_toml = task / "task.toml"
        if not task_toml.is_file():
            continue
        data = tomllib.loads(task_toml.read_text(encoding="utf-8"))
        metadata = data.get("metadata", {})
        if not isinstance(metadata, dict) or metadata.get("language") != "node":
            continue
        updated_task = False
        text = task_toml.read_text(encoding="utf-8")
        updated = text.replace(
            'metric_contract = "node-test-leaf-pass-rate-v1"',
            'metric_contract = "fixed-test-pass-rate-v1"',
        )
        grader = task / "tests/runtime/node/grade-report.mjs"
        if grader.is_file() and canonical_grader.is_file():
            grader.write_bytes(canonical_grader.read_bytes())
            updated_task = True
        if grader.is_file() and requirements.is_file():
            runtime = task / "tests/python-runtime"
            if runtime.exists():
                shutil.rmtree(runtime)
            copy_python_verifier_runtime(runtime)
            shutil.copy2(requirements, task / "tests/verifier-requirements.lock.txt")
            dockerfile = task / "tests/Dockerfile"
            if dockerfile.is_file():
                dockerfile.write_text(
                    _projection_dockerfile(
                        dockerfile.read_text(encoding="utf-8"),
                        node_image=node_image,
                        python_image=python_image,
                    ),
                    encoding="utf-8",
                )
                updated_task = True
            test_script = task / "tests/test.sh"
            if test_script.is_file():
                _sync_projection_test_script(test_script)
                updated_task = True
            readme = task / "README.md"
            if readme.is_file():
                readme_text = readme.read_text(encoding="utf-8")
                readme.write_text(
                    readme_text.replace(
                        "node-test-leaf-pass-rate-v1", "fixed-test-pass-rate-v1"
                    ),
                    encoding="utf-8",
                )
                updated_task = True
        if updated != text:
            task_toml.write_text(updated, encoding="utf-8")
            updated_task = True
        if updated_task:
            _refresh_manifest(task)
            changed.append(task.name)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    changed = sync(args.root.resolve())
    print(json.dumps({"changed_tasks": changed, "count": len(changed)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
