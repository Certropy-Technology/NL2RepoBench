"""Scoped cleanup for terminal Harbor compose projects."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

TRIAL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def trial_dirs(jobs_dir: Path) -> tuple[Path, ...]:
    """Find Harbor trial directories containing a lock record."""

    if not jobs_dir.is_dir():
        return ()
    found = {
        path.parent
        for path in jobs_dir.rglob("lock.json")
        if path.is_file() and path.parent.is_dir()
    }
    return tuple(sorted(found))


def project_for_trial(trial_dir: Path) -> str | None:
    """Convert a Harbor trial directory name to its exact env project name."""

    name = trial_dir.name
    if not TRIAL_NAME.fullmatch(name):
        return None
    suffix = name.removeprefix("harbor__")
    if not suffix or not TRIAL_NAME.fullmatch(suffix):
        return None
    return f"harbor__{suffix.lower()}__env"


def cleanup(jobs_dir: Path, *, dry_run: bool = False) -> list[str]:
    """Remove matching projects and return actions, never performing a global prune."""

    actions: list[str] = []
    for trial_dir in trial_dirs(jobs_dir):
        project = project_for_trial(trial_dir)
        if project is None:
            actions.append(f"skip invalid trial directory: {trial_dir}")
            continue
        inspect = subprocess.run(
            ["docker", "ps", "-aq", "--filter", f"label=com.docker.compose.project={project}"],
            check=False,
            capture_output=True,
            text=True,
        )
        container_ids = tuple(line for line in inspect.stdout.splitlines() if line)
        if not container_ids:
            continue
        if dry_run:
            actions.append(f"would remove {project}: {','.join(container_ids)}")
            continue
        result = subprocess.run(
            ["docker", "compose", "-p", project, "down", "--remove-orphans", "--volumes"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            actions.append(f"removed {project}: {','.join(container_ids)}")
        else:
            actions.append(
                f"cleanup failed {project} rc={result.returncode}: "
                f"{result.stderr.strip()[-500:]}"
            )
    return actions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    for action in cleanup(args.jobs_dir, dry_run=args.dry_run):
        print(action)
    return 0


__all__ = ["cleanup", "main", "project_for_trial", "trial_dirs"]
