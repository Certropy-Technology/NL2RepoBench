"""Network egress policy primitives for NL2RepoBench tasks.

The benchmark measures 0-to-1 repository generation from a natural language
specification. A task is only trustworthy when the agent cannot reach the
upstream implementation it is supposed to reproduce, so egress is restricted by
construction rather than by convention.

The dependency closure is installed at **image build time**, where Docker still
has network access. Run-time egress therefore does not need a package registry
in the normal case:

1. ``no-network`` is the preferred run-time mode. Build and test dependencies
   are baked into the task image (``RUN pip install ...``) or supplied as a
   private artifact (wheelhouse, npm cache).
2. ``allowlist`` exists for what genuinely cannot be preinstalled. In practice
   that is the **model provider endpoint**: Harbor runs "installed" agents such
   as OpenHands inside the task environment, so a restricted agent still has to
   reach its own inference API. A package registry host is the narrower
   exception, added per task only when a specific dependency resists baking.
3. Code hosting, raw file endpoints, wildcard suffixes and generic source
   mirrors are always rejected, because each of them can serve the frozen
   upstream source.
4. Acquiring reference source during an agent run (for example ``git clone`` of
   the upstream repository) is always forbidden.

Model provider hosts serve inference, not source code, so allowing one does not
leak the implementation the agent is asked to reproduce.

This module intentionally contains no Pydantic models. ``domain.models``
defines the persisted ``NetworkPolicy`` record on top of these helpers, which
keeps the lint tooling importable without pulling in the whole model layer.
"""

from __future__ import annotations

import re
from typing import Final, Literal

NetworkPolicyMode = Literal["no-network", "allowlist"]

#: Modes a task may declare. ``public`` is deliberately absent: an unrestricted
#: agent can download the upstream repository and defeat the benchmark.
NETWORK_POLICY_MODES: Final[tuple[str, ...]] = ("no-network", "allowlist")

#: How the build/test dependency closure is provisioned. ``preinstalled-image``
#: is the intended default: install during the Docker build, which has network,
#: so the run phase needs none. ``missing`` is an honest placeholder for tasks
#: whose closure has not been baked yet and must record a blocker reason.
OFFLINE_DEPENDENCY_SOURCES: Final[tuple[str, ...]] = (
    "preinstalled-image",
    "private-artifact",
    "missing",
)

#: Exact dependency registry hostnames. These are the *exception* path: the
#: default is to install the dependency closure at image build time, where the
#: Docker build phase still has network. A task only needs a registry host at
#: run time when a specific package genuinely cannot be preinstalled.
ALLOWED_REGISTRY_HOSTS: Final[frozenset[str]] = frozenset(
    {
        # Python
        "pypi.org",
        "files.pythonhosted.org",
        # Node
        "registry.npmjs.org",
        # Go
        "proxy.golang.org",
        "sum.golang.org",
        # Rust
        "crates.io",
        "index.crates.io",
        "static.crates.io",
    }
)

#: Exact model provider API hostnames. Harbor runs "installed" agents (OpenHands,
#: Claude Code, Codex) *inside* the task environment, so a restricted agent still
#: needs to reach its own model endpoint. These hosts serve model inference, not
#: source code, so allowing them does not leak the frozen upstream repository.
ALLOWED_MODEL_PROVIDER_HOSTS: Final[frozenset[str]] = frozenset(
    {
        "api.openai.com",
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        "api.deepseek.com",
        "api.mistral.ai",
        "api.cohere.com",
        "api.groq.com",
        "api.together.xyz",
        "api.fireworks.ai",
        "openrouter.ai",
        "api.x.ai",
        "dashscope.aliyuncs.com",
        "dashscope-intl.aliyuncs.com",
        "ark.cn-beijing.volces.com",
        "bedrock-runtime.us-east-1.amazonaws.com",
    }
)


def admissible_hosts() -> frozenset[str]:
    """Return every hostname that may appear in an allowlist."""

    return ALLOWED_REGISTRY_HOSTS | ALLOWED_MODEL_PROVIDER_HOSTS


def host_category(host: str) -> str | None:
    """Return ``"registry"`` or ``"model-provider"`` for an admissible host."""

    normalized = host.strip().lower()
    if normalized in ALLOWED_REGISTRY_HOSTS:
        return "registry"
    if normalized in ALLOWED_MODEL_PROVIDER_HOSTS:
        return "model-provider"
    return None


#: Hostnames that can serve frozen upstream source directly.
FORBIDDEN_HOSTS: Final[frozenset[str]] = frozenset(
    {
        "github.com",
        "www.github.com",
        "api.github.com",
        "raw.github.com",
        "raw.githubusercontent.com",
        "githubusercontent.com",
        "objects.githubusercontent.com",
        "codeload.github.com",
        "gist.github.com",
        "gist.githubusercontent.com",
        "gitlab.com",
        "bitbucket.org",
        "codeberg.org",
        "git.sr.ht",
        "sourceforge.net",
        "downloads.sourceforge.net",
        "git.kernel.org",
        "hg.python.org",
    }
)

#: Substrings that identify code hosting or generic mirror infrastructure even
#: when the concrete hostname is not enumerated above.
FORBIDDEN_HOST_MARKERS: Final[tuple[tuple[str, str], ...]] = (
    ("githubusercontent", "raw GitHub content host"),
    ("github", "GitHub code host"),
    ("gitlab", "GitLab code host"),
    ("bitbucket", "Bitbucket code host"),
    ("sourceforge", "SourceForge code host"),
    ("gitea", "Gitea code host"),
    ("gogs", "Gogs code host"),
    ("mirror", "generic source mirror"),
    ("tuna.tsinghua.edu.cn", "generic source mirror"),
    ("npmmirror", "generic source mirror"),
    ("cdn.jsdelivr.net", "generic source CDN"),
    ("unpkg.com", "generic source CDN"),
    ("statically.io", "generic source CDN"),
)

#: Tail that proves a git subcommand names an actual remote: a URL, a shell
#: variable, ``origin``, or a flag. Without this guard, prose describing a
#: library whose own domain is repositories -- "Git repository to clone" in the
#: gitingest spec -- would be misread as an instruction to fetch the answer.
_REMOTE_TAIL: Final[str] = (
    r"(?:https?://|git@|ssh://|git\+|\$[A-Za-z_]|\$\{|\borigin\b|--?[a-z]+[ =\"']|<[a-z_]+>)"
)


def _git_remote_subcommand(subcommand: str) -> str:
    """Regex for ``git ... <subcommand> ... <remote>``.

    Intervening flags are tolerated so ``git -C "$SRC" fetch --depth 1`` matches,
    and ``[^\\n]`` is used instead of ``\\s`` so a line break between unrelated
    words cannot match.
    """

    return r"\bgit\b[^\n]{0,120}?\b" + subcommand + r"\b[^\n]{0,40}?" + _REMOTE_TAIL


#: Reference-source acquisition patterns that must not appear in a public
#: instruction or in an unverified solution.
REFERENCE_SOURCE_PATTERNS: Final[tuple[tuple[str, str], ...]] = (
    (_git_remote_subcommand("clone"), "git clone of reference source"),
    (_git_remote_subcommand("fetch"), "git fetch of reference source"),
    (_git_remote_subcommand("pull"), "git pull of reference source"),
    (
        r"\bgit\b[^\n]{0,120}?\bsubmodule\b[^\n]{0,40}\b(?:update|add)\b",
        "git submodule reference source",
    ),
    (r"\bpip\b[^\n]{0,80}\binstall\b[^\n]{0,120}git\+", "pip install from a git remote"),
    (r"\bnpm\b[^\n]{0,80}\b(?:install|i)\b[^\n]{0,120}git\+", "npm install from a git remote"),
    (r"\bgo\b[^\n]{0,40}\bget\b[^\n]{0,120}\S+\.git\b", "go get from a git remote"),
    (r"\bcurl\b[^\n]{0,160}\b(?:github|githubusercontent)\b", "curl of GitHub content"),
    (r"\bwget\b[^\n]{0,160}\b(?:github|githubusercontent)\b", "wget of GitHub content"),
)

_HOSTNAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^(?=.{1,253}$)[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
)


class NetworkPolicyViolation(ValueError):
    """Raised when a declared egress policy is not admissible."""


def normalize_exact_host(value: str) -> str:
    """Return a normalized exact hostname, or raise on anything ambiguous.

    Only bare, fully qualified, lowercase hostnames are accepted. Schemes,
    paths, ports, credentials, IP literals and wildcards are all rejected so
    that an allowlist entry cannot silently widen at runtime.
    """

    host = value.strip().lower()
    if not host:
        raise NetworkPolicyViolation("allowed host must not be empty")
    if host.startswith("*") or "*" in host:
        raise NetworkPolicyViolation(
            f"wildcard allowlist entry is forbidden: {value!r}; "
            "declare each exact registry hostname instead"
        )
    for marker in ("://", "/", "@", "?", "#"):
        if marker in host:
            raise NetworkPolicyViolation(
                f"allowed host must be a bare hostname without {marker!r}: {value!r}"
            )
    if ":" in host:
        raise NetworkPolicyViolation(f"allowed host must not carry a port: {value!r}")
    if host != host.strip("."):
        raise NetworkPolicyViolation(
            f"allowed host must not have a leading or trailing dot: {value!r}"
        )
    if not _HOSTNAME_PATTERN.fullmatch(host):
        raise NetworkPolicyViolation(
            f"allowed host must be an exact fully qualified hostname: {value!r}"
        )
    return host


def describe_forbidden_host(host: str) -> str | None:
    """Return why ``host`` is forbidden, or ``None`` when it is not."""

    normalized = host.strip().lower()
    if normalized in FORBIDDEN_HOSTS:
        return "code hosting or raw source host"
    for marker, reason in FORBIDDEN_HOST_MARKERS:
        if marker in normalized:
            return reason
    return None


def validate_allowed_host(value: str) -> str:
    """Validate one allowlist entry against the exact-host contract.

    An explicitly admissible host wins, so a provider endpoint that merely looks
    like shared cloud infrastructure is not rejected by a substring marker. Every
    other host is reported with the most specific reason available.
    """

    host = normalize_exact_host(value)
    if host_category(host) is not None:
        return host
    forbidden = describe_forbidden_host(host)
    if forbidden is not None:
        raise NetworkPolicyViolation(
            f"host {host!r} is forbidden ({forbidden}); reference source must not be reachable"
        )
    raise NetworkPolicyViolation(
        f"host {host!r} is not a recognized dependency registry or model provider "
        "hostname; preinstall the dependency at image build time, or extend "
        "ALLOWED_REGISTRY_HOSTS/ALLOWED_MODEL_PROVIDER_HOSTS deliberately"
    )


def validate_allowed_hosts(values: object) -> tuple[str, ...]:
    """Validate and de-duplicate an allowlist while preserving declared order."""

    if isinstance(values, str):
        raise NetworkPolicyViolation("allowed_hosts must be a list of hostnames, not a string")
    if not isinstance(values, (list, tuple)):
        raise NetworkPolicyViolation("allowed_hosts must be a list of hostnames")
    seen: dict[str, None] = {}
    for entry in values:
        if not isinstance(entry, str):
            raise NetworkPolicyViolation("allowed_hosts entries must be strings")
        seen.setdefault(validate_allowed_host(entry), None)
    return tuple(seen)


def scan_reference_source_acquisition(text: str) -> tuple[str, ...]:
    """Return reasons why ``text`` acquires reference source over the network."""

    findings: dict[str, None] = {}
    for pattern, reason in REFERENCE_SOURCE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.setdefault(reason, None)
    return tuple(findings)


def scan_forbidden_hosts(text: str) -> tuple[str, ...]:
    """Return forbidden hostnames referenced as fetchable URLs in ``text``.

    Only ``scheme://host`` occurrences are reported. A task may legitimately
    name its upstream project in prose, so a bare mention is not a violation;
    a resolvable endpoint is.
    """

    findings: dict[str, None] = {}
    for match in re.finditer(r"\b[a-z][a-z0-9+.-]*://([^/\s\"'<>)\]]+)", text, flags=re.IGNORECASE):
        authority = match.group(1)
        host = authority.rsplit("@", 1)[-1].split(":", 1)[0].strip().lower()
        if not host:
            continue
        reason = describe_forbidden_host(host)
        if reason is not None:
            findings.setdefault(f"{host} ({reason})", None)
    return tuple(findings)
