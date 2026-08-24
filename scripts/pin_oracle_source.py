#!/usr/bin/env python3
"""Rewrite Oracle ``solve.sh`` to verify the frozen source against a digest.

The historical scripts fetched the upstream revision and copied it into the
workspace with no integrity check, so a silently changed remote would be
accepted. This rewrites them to the pattern ``autojump`` and ``pss`` already
use:

1. fetch the pinned revision,
2. assert ``rev-parse HEAD`` equals that revision,
3. build ``git archive --format=tar <revision>`` and check it against the
   ``source_digest`` recorded in ``catalog/sources/<task>/task.toml``,
4. extract into a cleaned ``/workspace``.

``git archive`` of a fixed revision is byte-reproducible, and the digest is
already stored per task, so no new artifact has to be published. Only the
Oracle runs this script: ``harbor/solution/`` is uploaded exclusively by the
Oracle agent and is not part of the agent image build context, so the reference
implementation never reaches the model agent.

Egress stays denied in task metadata. Authorize the source host for an Oracle
run only::

    harbor run -p <task> -a oracle --allow-agent-hosts codeload.github.com

Usage::

    python scripts/pin_oracle_source.py --task aiofiles --task asteval
    python scripts/pin_oracle_source.py --all --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = REPO_ROOT / "catalog" / "sources"
TASKS_ROOT = REPO_ROOT / "catalog" / "tasks"

_SHA256_PREFIXED = re.compile(r"^sha256:([0-9a-f]{64})$")
_FETCHES_SOURCE = re.compile(r"\bgit\b[^\n]{0,120}?\b(?:fetch|clone)\b")
_VERIFIES_DIGEST = re.compile(r"sha256sum\s+(?:--check|-c)\b")

TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is not part of the
# agent image build context, so this never reaches the model agent. Task
# metadata still declares no-network; authorize the source host for an Oracle
# run only, e.g. `harbor run -a oracle --allow-agent-hosts codeload.github.com`.
#
# SOURCE_ARCHIVE_SHA256 is source_digest from catalog/sources/{task}/task.toml and
# equals sha256(git archive --format=tar {revision}), which is byte-reproducible
# for a fixed revision. A changed remote fails the check instead of being used.

UPSTREAM_URL="{url}"
UPSTREAM_REVISION="{revision}"
SOURCE_ARCHIVE_SHA256="{digest}"
SOURCE_DIR="/tmp/{task}-source"
SOURCE_ARCHIVE="/tmp/{task}-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"

git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD

resolved_revision="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "unexpected source revision: $resolved_revision" >&2
    exit 1
fi

git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {{}} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
"""

_GITHUB_CLEANUP = "rm -rf /workspace/.github\n"

#: Tasks whose upstream marks a file ``export-subst`` in ``.gitattributes`` and
#: derives its package version from git (hatch-vcs / setuptools-scm).
#:
#: Two problems appear when such a repository is fetched by commit SHA alone:
#:
#: 1. ``git archive`` substitutes ``describe-name``/``ref-names``, which depend on
#:    which refs the local clone has, so the tarball is not byte-reproducible. For
#:    structlog at f5cbae43 a SHA-only shallow fetch yields digest 544ccd2c while
#:    the recorded value is c9127121.
#: 2. ``--depth 1 <sha>`` fetches no tags, so the version resolves to ``0.0``.
#:    structlog's own ``tests/test_packaging.py`` asserts
#:    ``metadata.version("structlog") == structlog.__version__``, so the Oracle
#:    would fail a real test for a packaging reason.
#:
#: Fetching the tag ref fixes both: the tag is present, so the substitution and
#: the derived version match the frozen release, and the digest reproduces the
#: recorded ``source_digest`` exactly. The commit SHA is still asserted, so a
#: moved tag is rejected rather than silently accepted.
#:
#: The working tree is deliberately never checked out. ``git checkout --detach``
#: adds ``HEAD`` to the ref list that ``export-subst`` writes into
#: ``.git_archival.txt`` (``grafted, HEAD, tag: 23.2.0`` instead of
#: ``grafted, tag: 23.2.0``), which changes the tarball and breaks the digest.
#: ``git archive`` reads the object database, so no checkout is needed.
#:
#: Verified for structlog: three independent fetches each reproduce c9127121,
#: and the installed package reports version 23.2.0.
_TAG_REFS: dict[str, str] = {
    "structlog": "23.2.0",
}

TAG_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is not part of the
# agent image build context, so this never reaches the model agent. Task
# metadata still declares no-network; authorize the source host for an Oracle
# run only, e.g. `harbor run -a oracle --allow-agent-hosts codeload.github.com`.
#
# This upstream marks a file 'export-subst' in .gitattributes and derives its
# version from git, so the tag ref is fetched rather than the bare commit:
#
#   * a SHA-only shallow fetch carries no tags, so `git archive` substitutes an
#     empty describe-name and the tarball digest does not reproduce;
#   * the package version would resolve to 0.0, failing the upstream packaging
#     test that compares metadata.version() with __version__.
#
# The commit SHA is asserted after fetching, so a moved tag is rejected.

UPSTREAM_URL="{url}"
UPSTREAM_REVISION="{revision}"
UPSTREAM_TAG="{tag}"
SOURCE_ARCHIVE_SHA256="{digest}"
SOURCE_DIR="/tmp/{task}-source"
SOURCE_ARCHIVE="/tmp/{task}-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"

git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin \
    "refs/tags/${{UPSTREAM_TAG}}:refs/tags/${{UPSTREAM_TAG}}"

# Intentionally no checkout: it would add HEAD to the substituted ref list and
# change the archive. git archive reads the object database directly.
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse "refs/tags/${{UPSTREAM_TAG}}^{{commit}}")"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "tag ${{UPSTREAM_TAG}} resolved to $resolved_revision, expected $UPSTREAM_REVISION" >&2
    exit 1
fi

git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {{}} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
"""


class ConversionError(RuntimeError):
    """Raised when a task cannot be converted safely."""


def _load_source(task: str) -> tuple[str, str, str]:
    """Return ``(upstream_url, revision, bare_digest)`` for ``task``."""

    task_toml = SOURCE_ROOT / task / "task.toml"
    if not task_toml.is_file():
        raise ConversionError(f"{task}: missing task.toml")
    source = tomllib.loads(task_toml.read_text()).get("source") or {}
    url = (source.get("upstream_url") or "").strip()
    revision = (source.get("revision") or "").strip()
    digest = (source.get("source_digest") or "").strip()
    if not url:
        raise ConversionError(f"{task}: source.upstream_url is missing")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ConversionError(
            f"{task}: source.revision must be a full commit SHA, got {revision!r}"
        )
    matched = _SHA256_PREFIXED.match(digest)
    if not matched:
        raise ConversionError(
            f"{task}: source.source_digest must be sha256:<64 hex>, got {digest!r}"
        )
    return url, revision, matched.group(1)


def render(task: str) -> str:
    """Render the pinned solve.sh for ``task``, preserving .github cleanup."""

    url, revision, digest = _load_source(task)
    tag = _TAG_REFS.get(task)
    if tag is not None:
        script = TAG_TEMPLATE.format(task=task, url=url, revision=revision, tag=tag, digest=digest)
    else:
        script = TEMPLATE.format(task=task, url=url, revision=revision, digest=digest)
    existing = TASKS_ROOT / task / "solution" / "solve.sh"
    if existing.is_file() and "/workspace/.github" in existing.read_text():
        script += _GITHUB_CLEANUP
    return script


def convert(task: str, *, dry_run: bool = False, force: bool = False) -> str:
    """Convert one task. Returns a short status string."""

    solve = TASKS_ROOT / task / "solution" / "solve.sh"
    if not solve.is_file():
        raise ConversionError(f"{task}: missing harbor/solution/solve.sh")
    current = solve.read_text()
    if not _FETCHES_SOURCE.search(current):
        return "skipped (no network fetch)"
    needs_tag = task in _TAG_REFS
    already = _VERIFIES_DIGEST.search(current) and not (
        needs_tag and "UPSTREAM_TAG=" not in current
    )
    if already and not force:
        return "skipped (already digest-verified)"
    rendered = render(task)
    if rendered == current:
        return "unchanged"
    if dry_run:
        return "would rewrite" if already else "would convert"
    solve.write_text(rendered)
    solve.chmod(0o755)
    return "rewritten" if already else "converted"


def candidates() -> list[str]:
    """Return tasks whose Oracle fetches source without verifying a digest."""

    found: list[str] = []
    for directory in sorted(p for p in TASKS_ROOT.iterdir() if p.is_dir()):
        solve = directory / "solution" / "solve.sh"
        if not solve.is_file():
            continue
        body = solve.read_text()
        if _FETCHES_SOURCE.search(body) and not _VERIFIES_DIGEST.search(body):
            found.append(directory.name)
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", action="append", default=[], help="Task id (repeatable).")
    parser.add_argument("--all", action="store_true", help="Convert every unverified task.")
    parser.add_argument("--dry-run", action="store_true", help="Report without writing.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even when already verified, for template changes.",
    )
    parser.add_argument("--list", action="store_true", help="List candidates and exit.")
    args = parser.parse_args(argv)

    if args.list:
        for task in candidates():
            print(task)
        return 0
    tasks = candidates() if args.all else args.task
    if not tasks:
        parser.error("pass --task <id>, --all, or --list")

    failures = 0
    for task in tasks:
        try:
            print(f"{task}: {convert(task, dry_run=args.dry_run, force=args.force)}")
        except ConversionError as exc:
            print(f"{task}: FAILED {exc}", file=sys.stderr)
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
