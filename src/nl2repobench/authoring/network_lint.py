"""Catalog-wide network egress lint.

Schema validation rejects a bad policy only when a task is compiled. This lint
answers the broader question a reviewer actually needs: across every catalog
task, is run-time egress restricted, and can any task still reach the frozen
upstream source it is supposed to reproduce?

It checks four things:

1. Every task with a Harbor bundle declares an explicit
   ``[environment.network_policy]``. A missing policy is a finding, so the
   default is never an accident.
2. Declared modes and allowlists satisfy the domain contract, and
   ``[environment].network_mode`` / ``[harbor].agent_network_mode`` do not
   contradict the policy.
3. No instruction, solution or compiled bundle acquires reference source over
   the network (``git clone``, ``pip install git+``, curl/wget of GitHub).
4. No task points a fetchable URL at a code host, raw file endpoint or generic
   source mirror.

The lint reads files only, so it is safe to run in CI and on a dirty worktree.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

from nl2repobench.domain.network_policy import (
    NetworkPolicyViolation,
    host_category,
    scan_forbidden_hosts,
    scan_reference_source_acquisition,
    validate_allowed_hosts,
)

Severity = Literal["error", "warning"]

#: Files scanned for reference-source acquisition and forbidden endpoints.
_SCANNED_SUFFIXES = (".md", ".sh", ".toml", ".dockerfile", ".yaml", ".yml")
_SCANNED_NAMES = ("Dockerfile",)

#: Directories that hold historical evidence rather than executable task
#: content. A blocker write-up may legitimately quote an upstream URL.
_EVIDENCE_DIRS = frozenset({"evidence", "provenance", "audit", "source"})
_EVIDENCE_FILES = frozenset(
    {
        "blocked.md",
        "blocker.md",
        "audit.md",
        "provenance.md",
        "provenance-audit.md",
        "api-inventory.md",
    }
)

#: ``task.toml`` records the frozen upstream URL on purpose: provenance requires
#: it, and the agent never reads task metadata. Only executable or
#: agent-visible content is scanned for endpoints.
_PROVENANCE_FILES = frozenset({"task.toml", "dataset.toml"})

#: The Oracle solution runs inside the agent environment, but ``solution/`` is
#: uploaded by the Oracle agent alone and is not part of the agent image build
#: context, so the reference implementation never reaches the model agent.
#: Fetching upstream source there is therefore legitimate *when it is verified*:
#: the script must assert the frozen revision against a recorded digest, and the
#: source host must be authorized per run via ``--allow-agent-hosts`` rather
#: than by loosening task metadata.
_SOLUTION_MARKERS = ("solution/", "solve.sh")

#: Proof that a solution verifies what it downloaded against a recorded digest.
_DIGEST_VERIFICATION = re.compile(r"(?:sha256sum|shasum|sha256)\s+[^\n]*(?:--check|--strict|-c)\b")

#: Proof that a solution verifies the git tree object hash instead of a tar
#: digest. Some upstreams mark a file ``export-subst`` in ``.gitattributes``, so
#: ``git archive`` substitutes values that depend on clone depth and local ref
#: state and the tarball is not byte-reproducible. The tree hash is the
#: depth-independent content identity of a revision, so checking it is an
#: equally strong guarantee. Both the expected value and the lookup must appear.
_TREE_VERIFICATION_EXPECTED = re.compile(r"EXPECTED_TREE=[\"']?[0-9a-f]{40}")
_TREE_VERIFICATION_LOOKUP = re.compile(r"\^\{tree\}")

#: Proof that a solution pins an exact revision rather than a moving ref.
_REVISION_PIN = re.compile(r"\b[0-9a-f]{40}\b")


@dataclass(frozen=True)
class Finding:
    task_id: str
    rule: str
    severity: Severity
    detail: str
    location: str | None = None

    def as_dict(self) -> dict[str, str]:
        payload = {
            "task_id": self.task_id,
            "rule": self.rule,
            "severity": self.severity,
            "detail": self.detail,
        }
        if self.location is not None:
            payload["location"] = self.location
        return payload


@dataclass
class LintReport:
    findings: list[Finding] = field(default_factory=list)
    tasks_scanned: int = 0
    tasks_with_bundle: int = 0
    tasks_with_policy: int = 0

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    def as_dict(self) -> dict[str, object]:
        return {
            "tasks_scanned": self.tasks_scanned,
            "tasks_with_harbor_bundle": self.tasks_with_bundle,
            "tasks_with_explicit_policy": self.tasks_with_policy,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "findings": [f.as_dict() for f in self.findings],
        }


#: Path fragments that indicate a URL serves raw source or a repository
#: snapshot rather than a human-facing project page.
_SOURCE_SERVING_MARKERS = (
    "/raw/",
    "raw.",
    "codeload.",
    "/archive/",
    "/tarball/",
    "/zipball/",
    "/releases/download/",
    ".git",
)


def _upstream_identity(data: dict[str, Any]) -> tuple[str, str] | None:
    """Return ``(owner, repo)`` for the frozen upstream, when recorded."""

    url = ((data.get("source") or {}).get("upstream_url") or "").strip()
    match = re.search(r"[/@]([^/\s:]+)/([^/\s.]+?)(?:\.git)?/?$", url)
    if not match:
        return None
    return match.group(1).lower(), match.group(2).lower()


def _targets_own_upstream(text: str, upstream: tuple[str, str] | None) -> bool:
    """True when ``text`` names the task's own upstream repository."""

    if upstream is None:
        return False
    owner, repo = upstream
    return bool(re.search(rf"{re.escape(owner)}/{re.escape(repo)}\b", text, re.IGNORECASE))


def _is_source_serving(url: str) -> bool:
    lowered = url.lower()
    return any(marker in lowered for marker in _SOURCE_SERVING_MARKERS)


def _is_evidence_path(path: Path, task_dir: Path) -> bool:
    if path.name in _EVIDENCE_FILES:
        return True
    relative = path.relative_to(task_dir)
    return any(part in _EVIDENCE_DIRS for part in relative.parts[:-1])


def _scannable_files(task_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(task_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in _SCANNED_NAMES or path.suffix.lower() in _SCANNED_SUFFIXES:
            files.append(path)
    return files


def _check_policy_table(task_id: str, policy: object, source: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(policy, dict):
        return [
            Finding(
                task_id, "policy-malformed", "error", "network_policy must be a table", str(source)
            )
        ]

    mode = policy.get("mode")
    if mode not in {"no-network", "allowlist"}:
        findings.append(
            Finding(
                task_id,
                "policy-mode-invalid",
                "error",
                f"mode must be 'no-network' or 'allowlist', got {mode!r}",
                str(source),
            )
        )

    if policy.get("reference_source_fetch", "forbidden") != "forbidden":
        findings.append(
            Finding(
                task_id,
                "reference-source-fetch-allowed",
                "error",
                "reference_source_fetch must remain 'forbidden'",
                str(source),
            )
        )

    hosts = policy.get("allowed_hosts", []) or []
    if mode == "allowlist":
        try:
            validated = validate_allowed_hosts(hosts)
        except NetworkPolicyViolation as exc:
            findings.append(
                Finding(task_id, "allowlist-host-forbidden", "error", str(exc), str(source))
            )
        else:
            if not validated:
                findings.append(
                    Finding(
                        task_id,
                        "allowlist-empty",
                        "error",
                        "allowlist mode requires at least one host",
                        str(source),
                    )
                )
            registry = [h for h in validated if host_category(h) == "registry"]
            if registry:
                findings.append(
                    Finding(
                        task_id,
                        "runtime-registry-egress",
                        "warning",
                        "registry hosts "
                        f"{', '.join(registry)} are reachable at run time; prefer installing "
                        "the dependency closure during the Docker build phase",
                        str(source),
                    )
                )
            if not (policy.get("reason") or "").strip():
                findings.append(
                    Finding(
                        task_id,
                        "allowlist-reason-missing",
                        "error",
                        "allowlist mode requires a reason",
                        str(source),
                    )
                )
    elif hosts:
        findings.append(
            Finding(
                task_id,
                "allowed-hosts-without-allowlist",
                "error",
                "allowed_hosts is only valid when mode='allowlist'",
                str(source),
            )
        )

    if policy.get("offline_dependencies") == "missing":
        findings.append(
            Finding(
                task_id,
                "offline-dependencies-missing",
                "warning",
                "dependency closure is not baked into the image yet; task cannot run "
                "offline until it is frozen or a private artifact is attached",
                str(source),
            )
        )
    return findings


def lint_task(task_dir: Path) -> tuple[list[Finding], bool, bool]:
    """Lint one catalog task. Returns (findings, has_bundle, has_policy)."""

    task_id = task_dir.name
    findings: list[Finding] = []
    source = task_dir / "task.toml"
    has_bundle = (task_dir / "harbor" / "task.toml").exists()

    try:
        data = tomllib.loads(source.read_text())
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return (
            [Finding(task_id, "task-toml-unreadable", "error", str(exc), str(source))],
            has_bundle,
            False,
        )

    environment = data.get("environment", {}) or {}
    policy = environment.get("network_policy")
    has_policy = policy is not None

    if has_policy:
        findings.extend(_check_policy_table(task_id, policy, source))
        declared_mode = policy.get("mode") if isinstance(policy, dict) else None
        env_mode = environment.get("network_mode")
        if env_mode is not None and declared_mode is not None and env_mode != declared_mode:
            findings.append(
                Finding(
                    task_id,
                    "network-mode-contradiction",
                    "error",
                    f"environment.network_mode={env_mode!r} contradicts "
                    f"policy mode={declared_mode!r}",
                    str(source),
                )
            )
    elif has_bundle:
        findings.append(
            Finding(
                task_id,
                "policy-missing",
                "error",
                "task has a Harbor bundle but no [environment.network_policy]",
                str(source),
            )
        )
    else:
        findings.append(
            Finding(
                task_id,
                "policy-missing",
                "warning",
                "no [environment.network_policy]; declare one before compiling a bundle",
                str(source),
            )
        )

    # Checked regardless of whether a policy table exists: a task that declares
    # an unrestricted agent must not escape review just because it has not
    # written a policy yet.
    if (data.get("harbor", {}) or {}).get("agent_network_mode") == "public":
        findings.append(
            Finding(
                task_id,
                "agent-network-public",
                "error" if has_bundle else "warning",
                "harbor.agent_network_mode='public' leaves the agent unrestricted",
                str(source),
            )
        )

    restricted = True
    if isinstance(policy, dict):
        restricted = policy.get("mode") in {"no-network", "allowlist"}
    upstream = _upstream_identity(data)

    for path in _scannable_files(task_dir):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        where = str(path.relative_to(task_dir))
        # Provenance metadata must name the frozen upstream revision, and the
        # agent never sees task.toml. Evidence write-ups may quote it too.
        if path.name in _PROVENANCE_FILES or _is_evidence_path(path, task_dir):
            continue
        is_solution = any(marker in where for marker in _SOLUTION_MARKERS)

        if is_solution:
            # The Oracle is the reference implementation, so acquiring source is
            # allowed. What matters is that it cannot silently accept a changed
            # remote, and that egress is granted per run instead of in metadata.
            if scan_reference_source_acquisition(text):
                tree_verified = bool(
                    _TREE_VERIFICATION_EXPECTED.search(text)
                    and _TREE_VERIFICATION_LOOKUP.search(text)
                )
                verified = _DIGEST_VERIFICATION.search(text) is not None or tree_verified
                pinned = _REVISION_PIN.search(text) is not None
                if not verified:
                    findings.append(
                        Finding(
                            task_id,
                            "oracle-source-unverified",
                            "error",
                            f"{where} downloads reference source without checking it against a "
                            "recorded digest; pin the revision and verify with "
                            "'sha256sum --check --strict', or verify the git tree hash when the "
                            "upstream uses export-subst (see scripts/pin_oracle_source.py)",
                            where,
                        )
                    )
                elif not pinned:
                    findings.append(
                        Finding(
                            task_id,
                            "oracle-source-unpinned-revision",
                            "error",
                            f"{where} verifies a digest but does not pin a full 40-character "
                            "commit SHA",
                            where,
                        )
                    )
                elif restricted:
                    findings.append(
                        Finding(
                            task_id,
                            "oracle-requires-host-authorization",
                            "warning",
                            f"{where} fetches digest-verified reference source, so an Oracle run "
                            "needs the source host authorized explicitly, e.g. "
                            "'harbor run -a oracle --allow-agent-hosts codeload.github.com'; "
                            "model-agent runs stay denied",
                            where,
                        )
                    )
            continue

        for reason in scan_reference_source_acquisition(text):
            findings.append(
                Finding(
                    task_id,
                    "reference-source-acquisition",
                    "error",
                    f"{reason} in {where}",
                    where,
                )
            )

        # A code-host URL is only a leak when it can actually serve the frozen
        # implementation: either it names this task's own upstream repository,
        # or it is a raw/archive endpoint. Many specs legitimately describe a
        # library whose own domain is code hosting (cookiecutter expands 'gh:'
        # into a GitHub URL; emoji reads api.github.com/emojis), so a bare
        # third-party mention is documentation, not an escape hatch.
        for url_match in re.finditer(r"https?://[^\s\"'()<>\]]+", text):
            url = url_match.group(0)
            if not scan_forbidden_hosts(url):
                continue
            own = _targets_own_upstream(url, upstream)
            serving = _is_source_serving(url)
            if not (own or serving):
                continue
            # A URL only hands over the implementation when it actually serves
            # source: raw files, an archive, or a clonable remote. A project or
            # issue page for the same repository is provenance prose, and
            # sometimes the library's own documented API constant, so it is
            # reported for review rather than failed outright.
            if own and serving:
                rule, severity, note = (
                    "upstream-source-endpoint",
                    "error",
                    "serves this task's own upstream source",
                )
            elif own:
                rule, severity, note = (
                    "upstream-repo-reference",
                    "warning",
                    "references this task's own upstream repository",
                )
            else:
                rule, severity, note = (
                    "source-serving-endpoint",
                    "warning",
                    "is a raw/archive source endpoint",
                )
            findings.append(
                Finding(
                    task_id,
                    rule,
                    cast(Severity, severity),
                    f"{url[:110]} in {where} {note}",
                    where,
                )
            )

    return findings, has_bundle, has_policy


def lint_catalog(tasks_root: Path) -> LintReport:
    """Lint every task directory under ``tasks_root``."""

    report = LintReport()
    if not tasks_root.is_dir():
        report.findings.append(
            Finding("<catalog>", "tasks-root-missing", "error", f"not a directory: {tasks_root}")
        )
        return report

    for task_dir in sorted(p for p in tasks_root.iterdir() if p.is_dir()):
        if not (task_dir / "task.toml").exists():
            continue
        report.tasks_scanned += 1
        findings, has_bundle, has_policy = lint_task(task_dir)
        report.findings.extend(findings)
        report.tasks_with_bundle += int(has_bundle)
        report.tasks_with_policy += int(has_policy)
    return report
