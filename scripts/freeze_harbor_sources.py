#!/usr/bin/env python3
"""Freeze provenance for the Harbor pilot tasks.

This is intentionally explicit: a task is not allowed to silently move when
an upstream default branch changes.  The script records the exact checkout
used to create the checked-in fixture and rewrites the Oracle checkout to
fetch that immutable commit.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

TASKS = {
    "aiofiles": ("https://github.com/Tinche/aiofiles", "Apache-2.0"),
    "arguably": ("https://github.com/treykeown/arguably", "MIT"),
    "boltons": ("https://github.com/mahmoud/boltons", "BSD-3-Clause"),
    "cerberus": ("https://github.com/pyeve/cerberus", "ISC"),
    "decouple": ("https://github.com/HBNetwork/python-decouple", "MIT"),
    "ftfy": ("https://github.com/rspeer/python-ftfy", "Apache-2.0"),
    "humanize": ("https://github.com/python-humanize/humanize", "MIT"),
    "parse": ("https://github.com/r1chardj0n3s/parse", "MIT"),
    "pytz": ("https://github.com/stub42/pytz", "MIT"),
    "six": ("https://github.com/benjaminp/six", "MIT"),
    "jsonlines": ("https://github.com/wbolster/jsonlines", "BSD-3-Clause"),
    "freezegun": ("https://github.com/spulec/freezegun", "Apache-2.0"),
    "tinydb": ("https://github.com/msiemens/tinydb", "MIT"),
    "tenacity": ("https://github.com/jd/tenacity", "Apache-2.0"),
}

BASE_IMAGE = "python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a"


def replace_section(text: str, section: str, replacement: str) -> str:
    pattern = rf"(?ms)^\[{re.escape(section)}\]\n.*?(?=^\[|\Z)"
    if not re.search(pattern, text):
        raise ValueError(f"missing [{section}] section")
    return re.sub(pattern, replacement.rstrip() + "\n\n", text, count=1)


def update_task(task: str, root: Path, cache: Path) -> None:
    import hashlib
    import subprocess

    repo = cache / f"{task}-upstream"
    if not (repo / ".git").is_dir():
        raise ValueError(f"missing upstream checkout: {repo}")
    revision = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    source_digest = (
        "sha256:"
        + hashlib.sha256(
            subprocess.check_output(["git", "-C", str(repo), "archive", "HEAD"])
        ).hexdigest()
    )
    url, license_spdx = TASKS[task]
    task_dir = root / task
    source_path = task_dir / "task.toml"
    text = source_path.read_text(encoding="utf-8")
    text = replace_section(
        text,
        "source",
        f"""[source]
status = "known"
upstream_url = {url!r}
revision = {revision!r}
license_spdx = {license_spdx!r}
source_digest = {source_digest!r}""",
    )
    text = replace_section(
        text,
        "environment",
        '''[environment]
status = "known"
python_version = "3.12"
os_name = "debian-12"
base_image = {image!r}
base_image_digest = {digest!r}
network_mode = "no-network"'''.format(image="python:3.12-slim", digest=BASE_IMAGE.split("@", 1)[1]),
    )
    source_path.write_text(text, encoding="utf-8")

    solve = task_dir / "harbor/solution/solve.sh"
    solve_text = f"""#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL={url!r}
UPSTREAM_REVISION={revision!r}
SOURCE_DIR=/tmp/{task}-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
"""
    solve.write_text(solve_text, encoding="utf-8")
    solve.chmod(0o755)
    print(task, revision, source_digest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("catalog/tasks"))
    parser.add_argument("--cache", type=Path, default=Path("/tmp"))
    parser.add_argument("tasks", nargs="*", default=list(TASKS))
    args = parser.parse_args()
    for task in args.tasks:
        if task not in TASKS:
            raise SystemExit(f"unknown pilot task: {task}")
        update_task(task, args.root, args.cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
