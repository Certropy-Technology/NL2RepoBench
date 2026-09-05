#!/usr/bin/env python3
"""Static quality gate for public task instructions.

This checks the structure and minimum information density required by the task
authoring standard. It does not attempt to judge whether the API contract is
semantically correct; reviewers and traceability gates still do that.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path


REQUIRED = {
    "project_description": re.compile(r"project description", re.I),
    "natural_language_instruction": re.compile(
        r"natural language instruction|natural-language instruction", re.I
    ),
    "supports_or_environment": re.compile(
        r"supports|environment configuration", re.I
    ),
    "directory_structure": re.compile(r"project directory structure", re.I),
    "api_usage": re.compile(r"api usage guide", re.I),
    "implementation": re.compile(
        r"implementation notes|detailed implementation nodes", re.I
    ),
}
FORBIDDEN = re.compile(
    r"VERIFIER_DIGEST|ORACLE_DIGEST|candidate[_ -]?site|/tests/verifier|"
    r"artifact://private|sha256:[0-9a-f]{64}",
    re.I,
)
SIGNATURE = re.compile(
    r"(?:def\s+[A-Za-z_]\w*\s*\(|class\s+[A-Za-z_]\w*|"
    r"(?:func\s+)?[A-Za-z_][\w.]*\s*\([^\n]{0,240}\))"
)
IMPORT = re.compile(r"(?:from\s+[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\s+import|"
                    r"import\s+[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)")


def is_blocked(task_dir: Path) -> bool:
    try:
        data = tomllib.loads((task_dir / "task.toml").read_text())
    except (OSError, tomllib.TOMLDecodeError):
        return False
    return data.get("lifecycle", {}).get("status") in {"blocked", "excluded"}


def check(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()
    task_id = path.parent.name
    try:
        tomllib.loads((path.parent / "task.toml").read_text())
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [f"{task_id}: cannot read task.toml: {exc}"]
    if is_blocked(path.parent):
        return errors
    for name, pattern in REQUIRED.items():
        if not pattern.search(text):
            errors.append(f"{task_id}: missing required section {name}")
    if len(text.splitlines()) < 120:
        errors.append(f"{task_id}: instruction is too short (<120 lines)")
    trees = re.findall(r"```(?:text|plain|plaintext)?\s*(.*?)```", text, re.I | re.S)
    if not any("workspace/" in tree for tree in trees):
        errors.append(f"{task_id}: directory structure must be a workspace/ code fence")
    if len(SIGNATURE.findall(text)) < 3:
        errors.append(f"{task_id}: API guide has fewer than three signatures/classes")
    if len(IMPORT.findall(text)) < 1:
        errors.append(f"{task_id}: API guide has no import path or module example")
    if text.count("```") < 6:
        errors.append(f"{task_id}: instruction needs at least three fenced examples")
    forbidden = FORBIDDEN.search(text)
    if forbidden:
        errors.append(f"{task_id}: forbidden internal detail: {forbidden.group(0)!r}")
    # Distribution and import names are not normalized in the current catalog
    # (for example, python-json-logger imports as pythonjsonlogger). Their
    # semantic consistency is reviewed from task metadata and inventories.
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources-root", type=Path, default=Path("catalog/sources"))
    args = parser.parse_args()
    errors: list[str] = []
    for task_dir in sorted(p for p in args.sources_root.iterdir() if p.is_dir()):
        instruction = task_dir / "instruction.md"
        if instruction.is_file():
            errors.extend(check(instruction))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"instruction quality failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("instruction quality passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
