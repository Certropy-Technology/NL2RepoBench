#!/usr/bin/env python3
"""Claim package candidates and run independent top-level Pi authoring sessions.

The loop owns concurrency and queue leases.  Each claimed package is handled by
one direct ``pi`` process in its own disk-backed git worktree and session
directory.  This driver intentionally does not use ``pi-subagents`` to create
the authoring workers; a child Pi session may only use that capability when a
future policy explicitly enables it.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import threading
import tomllib
from collections.abc import Iterator
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any, cast

SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MAX_CONCURRENCY = 8
DEFAULT_EXCLUDED_TOOLS = "subagent,subagent_supervisor,subagent_wait"
TMPFS_ROOTS = (Path("/tmp"), Path("/dev/shm"))
SCRIPT_ROOT = Path(__file__).resolve().parent
PI_AGENT_DIR = Path.home() / ".pi/agent"
PI_SETTINGS_PATH = PI_AGENT_DIR / "settings.json"
AUTHORING_RETRY_SETTINGS = {
    "retry": {
        "enabled": True,
        "maxRetries": 10,
        "baseDelayMs": 5000,
        "provider": {"maxRetries": 5, "maxRetryDelayMs": 120000},
    }
}
QUEUE_OUTPUT_LOCK = threading.Lock()
GO_RUNTIME_LOCK_FILES = (
    "src/nl2repobench/verification/go_bridge.py",
    "src/nl2repobench/verification/go_bridge_proxy.py",
    "src/nl2repobench/verification/go_contract_runner.py",
    "src/nl2repobench/verification/go_grader.py",
    "src/nl2repobench/verification/go_supervisor.py",
    "src/nl2repobench/verification/normalize/go_json.py",
    "src/nl2repobench/package_managers/go_modules.py",
)


def _load_queue_loop() -> Any:
    path = Path(__file__).with_name("package_queue_loop.py")
    spec = importlib.util.spec_from_file_location("package_queue_loop_driver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load queue loop: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_author_planner() -> Any:
    path = Path(__file__).with_name("author_package_loop.py")
    spec = importlib.util.spec_from_file_location("author_package_loop_driver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load author planner: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _ensure_disk_root(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if any(resolved == root or root in resolved.parents for root in TMPFS_ROOTS):
        raise ValueError(f"authoring root must not use tmpfs: {resolved}")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _claim(
    queue: Path,
    state: Path,
    candidate_id: str,
    owner: str,
    language: str,
    lease: int,
    attempts: int,
    remediation_plan: Path | None = None,
) -> dict[str, Any] | None:
    loop = _load_queue_loop()
    args = type(
        "ClaimArgs",
        (),
        {
            "queue": queue,
            "state": state,
            "owner": owner,
            "limit": 1,
            "lease_seconds": lease,
            "max_attempts": attempts,
            "language": language,
            "candidate_id": [candidate_id],
            "remediation_plan": remediation_plan,
        },
    )()
    output = StringIO()
    with QUEUE_OUTPUT_LOCK, redirect_stdout(output):
        result = loop.command_claim(args)
    if result == 2:
        return None
    if result != 0:
        raise RuntimeError(f"queue claim failed for {candidate_id}: rc={result}")
    payload = json.loads(output.getvalue())
    claimed = payload.get("claimed")
    if not isinstance(claimed, list) or len(claimed) != 1:
        raise RuntimeError(f"queue claim returned unexpected payload for {candidate_id}")
    return cast(dict[str, Any], claimed[0])


def _queue_transition(
    action: str,
    *,
    queue: Path,
    state: Path,
    owner: str,
    candidate_id: str,
    reason: str,
    artifacts: list[str] | None = None,
) -> dict[str, Any]:
    loop = _load_queue_loop()
    values: dict[str, Any] = {
        "queue": queue,
        "state": state,
        "owner": owner,
        "candidate_id": candidate_id,
    }
    if action == "record":
        values.update(
            {
                "status": "complete",
                "reason": reason,
                "failure_class": None,
                "artifact": artifacts or [],
            }
        )
        handler = loop.command_record
    elif action == "release":
        values["reason"] = reason
        handler = loop.command_release
    else:
        raise ValueError(f"unsupported queue transition: {action}")
    output = StringIO()
    with QUEUE_OUTPUT_LOCK, redirect_stdout(output):
        result = handler(type("QueueArgs", (), values)())
    if result != 0:
        raise RuntimeError(f"queue {action} failed for {candidate_id}: rc={result}")
    parsed = json.loads(output.getvalue())
    return parsed if isinstance(parsed, dict) else {"raw": parsed}


def _worktree(path: Path) -> str:
    if path.exists():
        if not (path / ".git").exists():
            raise RuntimeError(f"worker path exists and is not a git worktree: {path}")
        return "reused"
    path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        ["git", "worktree", "add", "--detach", str(path), "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git worktree add failed: {completed.stderr[-1000:]}")
    return "created"


def _configured_credential_env(models_file: Path, provider: str) -> str | None:
    """Resolve a Pi provider's ``$ENV`` apiKey reference without reading its value."""

    payload = _load_json(models_file)
    providers = payload.get("providers", payload)
    record = providers.get(provider) if isinstance(providers, dict) else None
    if not isinstance(record, dict):
        return None
    api_key = record.get("apiKey")
    if not isinstance(api_key, str):
        return None
    match = re.fullmatch(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?", api_key)
    return match.group(1) if match else None


def _agent_environment(args: argparse.Namespace) -> dict[str, str]:
    environment = os.environ.copy()
    if args.credential_env:
        if not ENV_NAME.fullmatch(args.credential_env):
            raise ValueError(f"unsafe credential environment name: {args.credential_env}")
        credential = environment.get(args.credential_env)
        if not credential:
            raise ValueError(f"credential environment variable is empty: {args.credential_env}")
        provider_env = _configured_credential_env(args.models_file, args.provider)
        if provider_env is None:
            raise ValueError(
                f"Pi provider {args.provider} does not use an environment-backed credential"
            )
        environment[provider_env] = credential
    if args.model == "claude-fable-5" or "fable" in args.provider.casefold():
        environment.setdefault("LLM_ANTHROPIC_THINKING_MODE", "adaptive")
        # The Harbor adapter has a separate relay workaround that disables
        # native tools. Direct Pi sessions must keep native tools enabled so
        # the authoring agent can edit and validate its worktree.
        environment.pop("LLM_ANTHROPIC_NATIVE_TOOLS", None)
    environment["NL2REPO_AUTHORING_TOP_LEVEL"] = "1"
    return environment


def _task_catalog_paths(task: dict[str, Any], package: str) -> tuple[Path, Path]:
    expected_source = Path("catalog/sources") / package
    expected_harbor = Path("catalog/tasks") / package
    source = Path(str(task.get("source_root") or expected_source))
    harbor = Path(str(task.get("harbor_task_root") or expected_harbor))
    if source != expected_source or harbor != expected_harbor:
        raise ValueError(f"task catalog paths must be {expected_source} and {expected_harbor}")
    return source, harbor


def _language_guidance(language: str) -> str:
    if language != "go":
        return ""
    return """
Go first-lane constraints are strict. Use one go.mod module on Linux/amd64,
pure Go only, no cgo/plugin/unsafe-heavy behavior, no go generate, no workspace
or external replace directive, and no toolchain auto-download. Freeze GOOS,
GOARCH, GOWORK=off, GOPROXY=off, GOSUMDB=off, and GOTOOLCHAIN=local for offline
validation. Inventory the real package with go/packages/go/types and dynamic
go test evidence. Build a reviewed typed bridge that contains only public API
mapping and serialization; hidden inputs, assertions, expected values, and the
grader belong in a private verifier artifact. The Oracle and offline module
closure must also be private content-addressed artifacts. Run the candidate
bridge as UID 10001 under the bounded supervisor. Production handoff requires
three stable Oracle runs plus empty, stub, forgery, install-failure, panic,
hang, oversized-output, background-process, and offline controls.
""".strip()


def _agent_prompt(
    *,
    plan: dict[str, Any],
    task: dict[str, Any],
    brief_path: Path,
    worktree: Path,
    handoff_path: Path,
    allow_internal_subagent: bool,
) -> str:
    package = task["package"]
    source_root, harbor_task_root = _task_catalog_paths(task, package)
    language_guidance = _language_guidance(str(plan["language"]))
    remediation_context = (
        "This is an existing-source remediation lane. Read the current source, "
        "production evidence, blocked reason, and any generated runtime before editing. "
        "Preserve valid evidence, repair the declarative source, and regenerate the "
        "Harbor task; do not restart from a blank task."
        if task.get("remediation_mode")
        else "This is a new-source authoring lane."
    )
    subagent_guidance = (
        "You may use subagent only for bounded read-only probes or independent analysis; "
        "the Loop still owns task concurrency and you remain the sole writer."
        if allow_internal_subagent
        else (
            "Do not invoke any subagent; this process is the top-level Pi Agent "
            "selected by the Loop."
        )
    )
    return f"""You are the independent top-level Pi Agent for one NL2RepoBench authoring lane.

Work only in this existing detached worktree:
{worktree}

Read these files first:
- AGENTS.md
- {worktree / ".nl2repo/authoring-claim.json"}
- {brief_path}
- {worktree / "docs/authoring-agent-remediation-guide.zh-CN.md"}

Your package is {package!r}, language is {plan["language"]!r}, and your only
authoring source target is {source_root.as_posix()}/ plus task-local private
artifacts and evidence under .nl2repo/. `{harbor_task_root.as_posix()}/` is generated
compiler output: do not hand-edit it. You are the sole writer for this worktree.
Do not edit the parent checkout, another worktree, shared catalog/dataset files,
or OSS data. Do not start a Harbor Agent Run from this lane.
{subagent_guidance}
{remediation_context}
{language_guidance}

Turn the candidate into a real, testable Harbor task. Freeze and verify the
exact source revision, inventory the public API and tests, debug the actual
build/install/test behavior, and create instruction, environment, verifier,
solution, controls, and traceability evidence. Missing image digests,
dependency pins, hash-locked closures, build backends, or complete closure
are remediation work: try to repair and prove them before deciding status.
Risky cloud, database, native, browser, or network behavior needs a bounded
deterministic adaptation when the contract permits it; do not mechanically
translate a README and do not lower tests to hide failures.

Network policy is a security gate. The future Harbor Agent Run must not be
able to clone or download the reference implementation from GitHub. Set
an explicit `[environment.network_policy]` with `mode = "no-network"` for
normal tasks. Python tasks must use a hash-locked `lock_artifact` installed at
Docker build time and must not vendor a wheelhouse. Node tasks use the pinned
npm lock/cache contract. Do not make the evaluation Agent run
`pip install`, `npm install`, `git clone`, `curl`, or `wget` to discover or
install dependencies. If a special package needs an extra system library or
runtime dependency, declare and freeze it in the source contract, then compile
and test the generated bundle; do not rely on a later model run to fetch it.

The LLM Provider is injected by the model runner as a run-scoped exact
`--allow-agent-host` hostname. The trusted Oracle run is different: Oracle is
the reference implementation and may fetch the frozen upstream revision from
the exact hostname in `[source].upstream_url`; the Oracle runner supplies that
host only for `-a oracle`. This exception is for Oracle, not for the model
Agent. Do not add source hosts, PyPI/npm/package-registry hosts, or the LLM
Provider to task metadata. Keep `agent_network_mode = "no-network"` and leave
`agent_allowed_hosts` empty. Never use `public`, wildcard hosts, GitHub, raw
GitHub, GitHubusercontent, or generic source mirrors for a model run. Agent
Compose files must not declare `network_mode` or `networks`, because that would
bypass Harbor's egress sidecar and break run-scoped Provider/Oracle allowlists.

Before handoff, run these gates from the worktree and fix every task-local
finding:
- `uv run nl2repo task validate-source {source_root.as_posix()}`
- `uv run nl2repo task lint-network --tasks-root catalog/sources`
- a production `uv run nl2repo harbor compile` using the language toolchain,
  `.nl2repo/artifacts`, `--allow-private`, and a task-local output directory
The Loop repeats source validation, network lint, and a production compile
before it records the claim as complete. Git source acquisition is allowed only
inside the Oracle solution, which is uploaded exclusively to the trusted Oracle
run and receives a run-scoped source-host override.

Shared verifier/compiler remediation is allowed only when it is a minimal
generic change needed by this task; keep that change in this worktree for
integrator review and never modify the parent/shared checkout directly.
Run the strongest available syntax, build, collection, Oracle, empty/stub,
forgery, timeout, and offline controls. A hard blocked/excluded result must
include attempted commands, tool versions, exit codes, failure logs, failure
class, and next_unblock_action. Do not classify missing environment material
or this tool boundary as Block.

Before finishing, write a concise machine-readable handoff to:
{handoff_path}
including status, changed files, commands, versions, exit codes, artifacts,
Oracle/control outcomes, residual risks, and any evidence-backed blocker.
"""


def _pi_command(
    args: argparse.Namespace,
    *,
    prompt: str,
    session_dir: Path,
    session_id: str,
) -> list[str]:
    command = shlex.split(args.pi_command)
    if not command:
        raise ValueError("pi-command must not be empty")
    excluded_tools = args.exclude_tools
    if getattr(args, "allow_internal_subagent", False):
        excluded_tools = ",".join(
            name
            for name in args.exclude_tools.split(",")
            if name.strip() not in {"subagent", "subagent_supervisor"}
        )
    command.extend(
        [
            "--print",
            "--provider",
            args.provider,
            "--model",
            args.model,
            "--thinking",
            args.thinking,
            "--approve",
            "--session-dir",
            str(session_dir),
            "--session-id",
            session_id,
            "--exclude-tools",
            excluded_tools,
            "--append-system-prompt",
            (
                "This is a direct top-level authoring session. "
                + (
                    "Use subagent only for a genuinely necessary, bounded parallel "
                    "probe; the Loop still owns task concurrency."
                    if getattr(args, "allow_internal_subagent", False)
                    else "Do not call subagent, subagent_supervisor, or subagent_wait."
                )
            ),
        ]
    )
    command.append(prompt)
    return command


def _write_authoring_settings(worktree: Path) -> Path:
    settings = worktree / ".pi/settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    global_settings = _load_json(PI_SETTINGS_PATH)
    packages = global_settings.get("packages", [])
    if not isinstance(packages, list):
        raise ValueError(f"Pi global settings packages must be a list: {PI_SETTINGS_PATH}")
    filtered_packages = [
        package
        for package in packages
        if not (
            package == "npm:pi-lark-notify"
            or (isinstance(package, dict) and package.get("source") == "npm:pi-lark-notify")
        )
    ]
    authoring_settings = {
        "packages": filtered_packages,
        "lark-notify": {"enabled": False},
        **AUTHORING_RETRY_SETTINGS,
    }
    settings.write_text(
        json.dumps(authoring_settings, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return settings


def _terminate_process(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            process.kill()
        process.wait()


def _launch_agent(
    args: argparse.Namespace,
    *,
    plan: dict[str, Any],
    task: dict[str, Any],
    brief_path: Path,
    worktree: Path,
    session_dir: Path,
    log_path: Path,
    handoff_path: Path,
    attempt: int,
) -> dict[str, Any]:
    session_dir.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    session_id = f"{plan['batch_id']}-{task['package']}-attempt-{attempt}"
    if not SAFE_NAME.fullmatch(session_id):
        raise ValueError(f"unsafe Pi session id: {session_id}")
    prompt = _agent_prompt(
        plan=plan,
        task=task,
        brief_path=brief_path,
        worktree=worktree,
        handoff_path=handoff_path,
        allow_internal_subagent=getattr(args, "allow_internal_subagent", False),
    )
    command = _pi_command(
        args,
        prompt=prompt,
        session_dir=session_dir,
        session_id=session_id,
    )
    environment = _agent_environment(args)
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            command,
            cwd=worktree,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        try:
            returncode = process.wait(timeout=args.agent_timeout_sec)
            status = "exited"
        except subprocess.TimeoutExpired:
            _terminate_process(process)
            returncode = 124
            status = "timeout"
    return {
        "status": status,
        "exit_code": returncode,
        "command": command,
        "session_id": session_id,
        "session_dir": str(session_dir),
        "log": str(log_path),
        "handoff": str(handoff_path),
    }


def _run_network_policy_check(worktree: Path, task_root: Path) -> dict[str, Any]:
    report = worktree / ".nl2repo/evidence/network-policy.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [
            "uv",
            "run",
            "nl2repo",
            "task",
            "lint-network",
            "--tasks-root",
            str(task_root.parent),
        ],
        cwd=worktree,
        capture_output=True,
        text=True,
        check=False,
    )
    report.write_text(
        completed.stdout
        if completed.stdout.strip()
        else json.dumps(
            {
                "status": "failed",
                "exit_code": completed.returncode,
                "stderr": completed.stderr[-4000:],
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + ("" if completed.stdout.endswith("\n") else "\n"),
        encoding="utf-8",
    )
    return {
        "status": "passed" if completed.returncode == 0 else "failed",
        "exit_code": completed.returncode,
        "report": str(report),
        "output": (completed.stdout or completed.stderr).strip()[-4000:],
    }


def _authoring_toolchain(worktree: Path, language: str | None) -> Path:
    if language == "node":
        return worktree / "toolchain.node.lock.toml"
    if language == "go":
        return worktree / "toolchain.go.lock.toml"
    return worktree / "toolchain.lock.toml"


def _private_artifact(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    digest = value.get("digest")
    return (
        isinstance(digest, str)
        and re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is not None
        and value.get("visibility") == "private"
        and value.get("uri") == f"artifact://private/{digest}"
        and isinstance(value.get("size_bytes"), int)
        and not isinstance(value.get("size_bytes"), bool)
        and value["size_bytes"] >= 0
    )


def _go_runtime_digest(repository_root: Path) -> str:
    digest = hashlib.sha256()
    for relative in GO_RUNTIME_LOCK_FILES:
        path = repository_root / relative
        digest.update(relative.removeprefix("src/nl2repobench/").encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return f"sha256:{digest.hexdigest()}"


def _go_toolchain_errors(toolchain: Path) -> list[str]:
    errors: list[str] = []
    try:
        lock = tomllib.loads(toolchain.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return [f"invalid production Go toolchain lock: {exc}"]
    repository_root = toolchain.parent
    if lock.get("status") != "locked":
        errors.append("toolchain.go.lock.toml status must be locked")
    if lock.get("schema_version") != "1.0":
        errors.append("Go toolchain schema must be 1.0")
    if lock.get("go_report_schema") != "go-test-json-v1":
        errors.append("Go report schema must be go-test-json-v1")
    go = lock.get("go")
    if not isinstance(go, dict) or not re.fullmatch(r"1\.[0-9]+\.[0-9]+", str(go.get("version"))):
        errors.append("Go toolchain version must be exact")
    elif re.fullmatch(r"[A-Za-z0-9._/-]+@sha256:[0-9a-f]{64}", str(go.get("base_image"))) is None:
        errors.append("Go toolchain base image must be digest pinned")
    elif go.get("platform") != "linux/amd64" or go.get("executable") != "/usr/local/go/bin/go":
        errors.append("Go toolchain platform or executable is invalid")
    try:
        runtime_digest = _go_runtime_digest(repository_root)
    except OSError as exc:
        errors.append(f"cannot hash Go runtime: {exc}")
    else:
        if lock.get("go_runtime_sha256") != runtime_digest:
            errors.append("Go runtime digest does not match toolchain lock")
    for table_name, path_field, digest_field in (
        (None, "verifier_requirements_lock", "verifier_requirements_sha256"),
        ("harbor", "lock_file", "lock_sha256"),
    ):
        table = lock if table_name is None else lock.get(table_name)
        if not isinstance(table, dict):
            errors.append(f"Go toolchain {table_name or 'root'} table is invalid")
            continue
        relative = table.get(path_field)
        expected = table.get(digest_field)
        if (
            not isinstance(relative, str)
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
        ):
            errors.append(f"Go toolchain {path_field} is unsafe")
            continue
        path = repository_root / relative
        try:
            actual = f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
        except OSError as exc:
            errors.append(f"cannot hash Go toolchain file {relative}: {exc}")
            continue
        if expected != actual:
            errors.append(f"Go toolchain {digest_field} does not match {relative}")
    harbor = lock.get("harbor")
    if isinstance(harbor, dict) and (
        harbor.get("version") != "0.21.0" or harbor.get("task_schema") != "1.4"
    ):
        errors.append("Go Harbor contract must be 0.21.0/task 1.4")
    return errors


def _go_production_contract(
    task_root: Path,
    source: dict[str, Any],
    compiled_root: Path,
    toolchain: Path,
) -> dict[str, Any]:
    errors = _go_toolchain_errors(toolchain)
    environment = source.get("environment")
    if not isinstance(environment, dict) or environment.get("status") != "known":
        errors.append("Go environment.status must be known")
    elif not environment.get("runtime_version"):
        errors.append("Go environment.runtime_version is required")
    dependencies = source.get("dependencies")
    if not isinstance(dependencies, dict) or dependencies.get("status") != "known":
        errors.append("Go dependencies.status must be known")
    elif not _private_artifact(dependencies.get("module_bundle")):
        errors.append("Go dependencies.module_bundle must be a private CAS artifact")
    verifier = source.get("verifier")
    if not isinstance(verifier, dict) or not _private_artifact(verifier.get("bundle")):
        errors.append("Go verifier.bundle must be a private CAS artifact")
    if not _private_artifact(source.get("oracle_bundle")):
        errors.append("Go oracle_bundle must be a private CAS artifact")
    public_bridge = task_root / "harbor/tests/bridge.go"
    tests_root = task_root / "harbor/tests"
    if tests_root.exists() and any(
        path.is_file() and path != public_bridge for path in tests_root.rglob("*")
    ):
        errors.append("public Go source retains private verifier material")
    for relative in ("harbor/dependencies", "harbor/solution"):
        if (task_root / relative).exists():
            errors.append(f"public Go source retains private material: {relative}")
    manifest_path = compiled_root / "bundle.manifest.json"
    generated_task_path = compiled_root / "task.toml"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        generated = tomllib.loads(generated_task_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"invalid generated Go Harbor task: {exc}")
    else:
        metadata = generated.get("metadata")
        if manifest.get("mode") != "production":
            errors.append("generated Go Harbor manifest must be production")
        rows = manifest.get("files")
        declared: dict[str, tuple[str, int]] = {}
        if not isinstance(rows, list) or not rows:
            errors.append("generated Go Harbor manifest files must be non-empty")
        else:
            for row in rows:
                if not isinstance(row, dict):
                    errors.append("generated Go Harbor manifest contains a non-object row")
                    break
                row_path = row.get("path")
                digest = row.get("sha256")
                size = row.get("size_bytes")
                if (
                    not isinstance(row_path, str)
                    or Path(row_path).is_absolute()
                    or ".." in Path(row_path).parts
                    or row_path in declared
                    or not isinstance(digest, str)
                    or re.fullmatch(r"[0-9a-f]{64}", digest) is None
                    or isinstance(size, bool)
                    or not isinstance(size, int)
                    or size < 0
                ):
                    errors.append("generated Go Harbor manifest contains an invalid file row")
                    break
                declared[row_path] = (digest, size)
            if any(path.is_symlink() for path in compiled_root.rglob("*")):
                errors.append("generated Go Harbor task contains a symlink")
            else:
                actual = {
                    path.relative_to(compiled_root).as_posix(): (
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                        path.stat().st_size,
                    )
                    for path in compiled_root.rglob("*")
                    if path.is_file() and path != manifest_path
                }
                if declared != actual:
                    errors.append("generated Go Harbor manifest inventory does not match files")
        if not isinstance(metadata, dict) or metadata.get("language") != "go":
            errors.append("generated Harbor task metadata.language must be go")
        elif metadata.get("package_manager") != "go-modules":
            errors.append("generated Harbor task package_manager must be go-modules")
    return {"status": "passed" if not errors else "failed", "errors": errors}


def _run_authoring_task_lint(worktree: Path, task_root: Path) -> dict[str, Any]:
    report = worktree / ".nl2repo/evidence/authoring-task-lint.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    validation = subprocess.run(
        [
            "uv",
            "run",
            "nl2repo",
            "task",
            "validate-source",
            str(task_root),
        ],
        cwd=worktree,
        capture_output=True,
        text=True,
        check=False,
    )
    compile_result: subprocess.CompletedProcess[str] | None = None
    compile_output: Path | None = None
    language: str | None = None
    if validation.returncode == 0:
        source = tomllib.loads((task_root / "task.toml").read_text(encoding="utf-8"))
        metadata = source.get("metadata")
        language = metadata.get("language") if isinstance(metadata, dict) else None
        toolchain = _authoring_toolchain(worktree, language)
        compile_parent = worktree / ".nl2repo/authoring-gate"
        compile_parent.mkdir(parents=True, exist_ok=True)
        compile_output = Path(tempfile.mkdtemp(prefix=f"{task_root.name}-", dir=compile_parent))
        compile_result = subprocess.run(
            [
                "uv",
                "run",
                "nl2repo",
                "harbor",
                "compile",
                str(task_root),
                "--output",
                str(compile_output),
                "--toolchain",
                str(toolchain),
                "--artifact-root",
                str(worktree / ".nl2repo/artifacts"),
                "--allow-private",
            ],
            cwd=worktree,
            capture_output=True,
            text=True,
            check=False,
        )
    go_contract: dict[str, Any] | None = None
    if (
        language == "go"
        and compile_result is not None
        and compile_result.returncode == 0
        and compile_output is not None
    ):
        go_contract = _go_production_contract(
            task_root,
            source,
            compile_output / str(source.get("task_id") or task_root.name),
            toolchain,
        )
    payload = {
        "status": (
            "passed"
            if validation.returncode == 0
            and compile_result is not None
            and compile_result.returncode == 0
            and (go_contract is None or go_contract["status"] == "passed")
            else "failed"
        ),
        "language": language,
        "source_validation": {
            "exit_code": validation.returncode,
            "stdout": validation.stdout[-4000:],
            "stderr": validation.stderr[-4000:],
        },
        "harbor_compile": (
            {
                "exit_code": compile_result.returncode,
                "stdout": compile_result.stdout[-4000:],
                "stderr": compile_result.stderr[-4000:],
                "output": str(compile_output),
            }
            if compile_result is not None
            else None
        ),
        "go_production_contract": go_contract,
    }
    report.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "status": payload["status"],
        "exit_code": 1
        if go_contract is not None and go_contract["status"] != "passed"
        else (
            validation.returncode
            if validation.returncode != 0 or compile_result is None
            else compile_result.returncode
        ),
        "report": str(report),
        "output": (
            "\n".join(go_contract["errors"])
            if go_contract is not None and go_contract["status"] != "passed"
            else (
                validation.stdout
                or validation.stderr
                or (compile_result.stdout if compile_result else "")
                or (compile_result.stderr if compile_result else "")
            )
        ).strip()[-4000:],
    }


def _prepare_task(
    args: argparse.Namespace,
    *,
    plan: dict[str, Any],
    task: dict[str, Any],
    claims_root: Path,
    worktree_root: Path,
) -> dict[str, Any] | None:
    package = task.get("package")
    candidate_id = task.get("candidate_id")
    language = plan["language"]
    if not isinstance(package, str) or not SAFE_NAME.fullmatch(package):
        raise ValueError(f"unsafe package name: {package!r}")
    if not isinstance(candidate_id, str):
        raise ValueError(f"missing candidate id for {package}")
    source_root, harbor_task_root = _task_catalog_paths(task, package)
    remediation_mode = bool(
        plan.get("remediation_mode") or getattr(args, "remediation_mode", False)
    )
    raw_reclaim = task.get("queue_reclaim_statuses", []) if remediation_mode else []
    if not isinstance(raw_reclaim, list) or any(
        status not in {"blocked", "complete"} for status in raw_reclaim
    ):
        raise ValueError(f"invalid queue reclaim statuses for {package}")
    claimed = _claim(
        args.queue,
        args.queue_state,
        candidate_id,
        args.owner,
        language,
        args.lease_seconds,
        args.max_attempts,
        remediation_plan=args.plan if raw_reclaim else None,
    )
    if claimed is None:
        return None
    worktree = worktree_root / package
    worktree_status = _worktree(worktree)
    authoring_settings = _write_authoring_settings(worktree)
    batch_id = plan["batch_id"]
    brief = {
        "schema_version": "1.0",
        "batch_id": batch_id,
        "package": package,
        "candidate_id": candidate_id,
        "language": language,
        "claim": claimed,
        "worktree": str(worktree),
        "task_scope": f"{source_root.as_posix()}/** plus task-local .nl2repo artifacts",
        "stages": plan.get("stages", []),
        "remediation_policy": plan.get("remediation_policy", {}),
        "worker_guidance": plan.get("worker_guidance"),
        "remediation_mode": remediation_mode,
        "remediation_reasons": task.get("remediation_reasons", []),
        "existing_source_status": task.get("existing_source_status"),
        "existing_source_reason": task.get("existing_source_reason"),
        "existing_harbor_task_state": task.get("existing_harbor_task_state"),
        "blocked_reason_kind": task.get("blocked_reason_kind"),
        "source_root": source_root.as_posix(),
        "harbor_task_root": harbor_task_root.as_posix(),
        "agent_run_boundary": "direct top-level pi CLI session; no pi-subagents",
        "must_not": [
            "start a Harbor Agent Run",
            *([] if getattr(args, "allow_internal_subagent", False) else ["invoke subagent tools"]),
            "edit shared datasets/reports or the parent checkout",
            "publish without integrator",
        ],
    }
    brief_path = claims_root / f"{package}.json"
    brief_path.write_text(
        json.dumps(brief, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    worktree_claim = worktree / ".nl2repo" / "authoring-claim.json"
    worktree_claim.parent.mkdir(parents=True, exist_ok=True)
    worktree_claim.write_text(
        json.dumps(brief, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    attempt = int(claimed.get("attempts", 1))
    session_root = _ensure_disk_root(args.session_root) / batch_id / package
    log_path = _ensure_disk_root(args.state_root / batch_id / "agent-logs") / (
        f"{package}.attempt-{attempt}.log"
    )
    handoff_path = worktree / ".nl2repo" / "authoring-handoff.json"
    return {
        "package": package,
        "candidate_id": candidate_id,
        "claim": claimed,
        "worktree": str(worktree),
        "worktree_status": worktree_status,
        "brief": str(brief_path),
        "worktree_claim": str(worktree_claim),
        "authoring_settings": str(authoring_settings),
        "session_root": str(session_root),
        "log": str(log_path),
        "handoff": str(handoff_path),
        "task_root": str(worktree / source_root),
        "plan": plan,
        "task": task,
    }


def _run_claimed(args: argparse.Namespace, context: dict[str, Any]) -> dict[str, Any]:
    agent = _launch_agent(
        args,
        plan=context["plan"],
        task=context["task"],
        brief_path=Path(context["brief"]),
        worktree=Path(context["worktree"]),
        session_dir=Path(context["session_root"]),
        log_path=Path(context["log"]),
        handoff_path=Path(context["handoff"]),
        attempt=int(context["claim"].get("attempts", 1)),
    )
    task_root = Path(context["task_root"])
    handoff = Path(context["handoff"])
    artifacts = [context["brief"], context["worktree_claim"], agent["log"]]
    if handoff.is_file():
        artifacts.append(str(handoff))
    ready = (task_root / "task.toml").is_file() and (task_root / "instruction.md").is_file()
    network = _run_network_policy_check(Path(context["worktree"]), task_root)
    artifacts.append(network["report"])
    lint = _run_authoring_task_lint(Path(context["worktree"]), task_root)
    artifacts.append(lint["report"])
    if (
        agent["exit_code"] == 0
        and ready
        and handoff.is_file()
        and network["status"] == "passed"
        and lint["status"] == "passed"
    ):
        transition = _queue_transition(
            "record",
            queue=args.queue,
            state=args.queue_state,
            owner=args.owner,
            candidate_id=context["candidate_id"],
            reason="top-level Pi Agent exited successfully with task handoff",
            artifacts=artifacts,
        )
        return {
            **context,
            **agent,
            "status": "complete",
            "queue_transition": transition,
            "artifacts": artifacts,
        }
    reason = (
        f"top-level Pi Agent {agent['status']} with exit_code={agent['exit_code']}"
        if agent["exit_code"] != 0
        else (
            "authoring network policy check failed: " + network["output"]
            if network["status"] != "passed"
            else "authoring task lint failed: " + lint["output"]
            if lint["status"] != "passed"
            else "Pi Agent exited without complete task.toml/instruction/handoff"
        )
    )
    transition = _queue_transition(
        "release",
        queue=args.queue,
        state=args.queue_state,
        owner=args.owner,
        candidate_id=context["candidate_id"],
        reason=reason,
    )
    return {
        **context,
        **agent,
        "status": "released",
        "reason": reason,
        "queue_transition": transition,
        "artifacts": artifacts,
    }


def _next_tasks(tasks: list[Any]) -> Iterator[dict[str, Any]]:
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("author plan task must be an object")
        yield task


def _catalog_packages(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {path.name for path in root.iterdir() if path.is_dir() and not path.name.startswith(".")}


def _queue_refill_tasks(
    queue_path: Path,
    *,
    language: str,
    scheduled: set[str],
    source_root: Path,
    tasks_root: Path,
    remediation_mode: bool,
) -> Iterator[dict[str, Any]]:
    queue = _load_json(queue_path)
    records = queue.get("queue")
    if not isinstance(records, list):
        raise ValueError("authoring queue requires a queue list for refill")
    existing_catalog = _catalog_packages(source_root)
    planner = _load_author_planner() if remediation_mode else None
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("authoring queue candidate must be an object")
        candidate_id = record.get("candidate_id")
        package = record.get("package")
        if not isinstance(candidate_id, str) or not isinstance(package, str):
            raise ValueError("authoring queue candidate requires candidate_id and package")
        if candidate_id in scheduled:
            continue
        scheduled.add(candidate_id)
        if record.get("language") != language:
            continue
        if remediation_mode:
            assert planner is not None
            if record.get("status") not in {
                "candidate",
                "needs-evidence",
                "existing",
                "blocked",
                "needs-remediation",
            }:
                continue
            selected, _skip_reason = planner.classify_existing_remediation(
                record,
                source_root=source_root / package,
                task_root=tasks_root / package,
            )
            if selected is None:
                continue
            selected["source_root"] = f"catalog/sources/{package}"
            selected["harbor_task_root"] = f"catalog/tasks/{package}"
            selected["remediation_mode"] = True
            selected["remediation_reasons"] = sorted(
                set(planner._remediation_reasons(selected))
                | set(selected.pop("existing_task_remediation_reasons", []))
            )
            # Refill candidates are not present in the signed/bound plan. They may
            # consume pending queue records, but terminal reopen requires a new plan.
            selected["queue_reclaim_statuses"] = []
            yield selected
            continue
        if record.get("status") not in {"candidate", "needs-evidence"}:
            continue
        if package not in existing_catalog:
            yield record


def _task_stream(
    tasks: list[Any],
    *,
    refill_queue: bool,
    queue_path: Path,
    language: str,
    source_root: Path,
    tasks_root: Path,
    remediation_mode: bool,
) -> Iterator[dict[str, Any]]:
    scheduled: set[str] = set()
    for task in _next_tasks(tasks):
        candidate_id = task.get("candidate_id")
        if isinstance(candidate_id, str):
            scheduled.add(candidate_id)
        yield task
    if refill_queue:
        yield from _queue_refill_tasks(
            queue_path,
            language=language,
            scheduled=scheduled,
            source_root=source_root,
            tasks_root=tasks_root,
            remediation_mode=remediation_mode,
        )


def run(args: argparse.Namespace) -> dict[str, Any]:
    if not 1 <= args.max_concurrency <= MAX_CONCURRENCY:
        raise ValueError(f"max-concurrency must be between 1 and {MAX_CONCURRENCY}")
    if args.agent_timeout_sec < 1:
        raise ValueError("agent-timeout-sec must be positive")
    plan = _load_json(args.plan)
    tasks = plan.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("author plan requires tasks")
    language = plan.get("language")
    if language not in {"python", "node", "go"}:
        raise ValueError("author plan language must be python, node, or go")
    batch_id = plan.get("batch_id")
    if not isinstance(batch_id, str) or not SAFE_NAME.fullmatch(batch_id):
        raise ValueError("author plan requires a safe batch_id")
    refill_queue = getattr(args, "refill_queue", True)
    remediation_mode = bool(
        plan.get("remediation_mode") or getattr(args, "remediation_mode", False)
    )
    configured_source_root = getattr(args, "source_root", None)
    if configured_source_root is None:
        configured_source_root = getattr(args, "catalog_root", None) or Path("catalog/sources")
    source_root = Path(configured_source_root)
    tasks_root = Path(getattr(args, "tasks_root", Path("catalog/tasks")))
    if not source_root.is_absolute():
        source_root = (Path.cwd() / source_root).resolve()
    if not tasks_root.is_absolute():
        tasks_root = (Path.cwd() / tasks_root).resolve()
    state_root = _ensure_disk_root(args.state_root)
    worktree_root = _ensure_disk_root(args.worktree_root) / batch_id
    claims_root = state_root / batch_id / "claims"
    claims_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    pending = iter(
        _task_stream(
            tasks,
            refill_queue=refill_queue,
            queue_path=args.queue,
            language=language,
            source_root=source_root,
            tasks_root=tasks_root,
            remediation_mode=remediation_mode,
        )
    )
    active: dict[Any, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=args.max_concurrency) as executor:
        exhausted = False
        while active or not exhausted:
            while not exhausted and len(active) < args.max_concurrency:
                try:
                    task = next(pending)
                except StopIteration:
                    exhausted = True
                    break
                package = task.get("package")
                candidate_id = task.get("candidate_id")
                context = _prepare_task(
                    args,
                    plan=plan,
                    task=task,
                    claims_root=claims_root,
                    worktree_root=worktree_root,
                )
                if context is None:
                    results.append(
                        {
                            "package": package,
                            "candidate_id": candidate_id,
                            "status": "already-claimed-or-terminal",
                        }
                    )
                    continue
                future = executor.submit(_run_claimed, args, context)
                active[future] = context
            if not active:
                continue
            done, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in done:
                context = active.pop(future)
                try:
                    results.append(future.result())
                except BaseException as exc:
                    reason = f"top-level Pi launch failed: {type(exc).__name__}: {exc}"
                    try:
                        transition = _queue_transition(
                            "release",
                            queue=args.queue,
                            state=args.queue_state,
                            owner=args.owner,
                            candidate_id=context["candidate_id"],
                            reason=reason,
                        )
                    except BaseException as transition_exc:
                        transition = {"error": f"{type(transition_exc).__name__}: {transition_exc}"}
                    results.append(
                        {
                            **context,
                            "status": "released",
                            "reason": reason,
                            "queue_transition": transition,
                        }
                    )
    return {
        "schema_version": "2.0",
        "batch_id": batch_id,
        "language": language,
        "owner": args.owner,
        "agent_mode": "top-level-pi-cli",
        "agent_runs_started": any(
            result.get("status") in {"complete", "released", "exited", "timeout"}
            for result in results
        ),
        "model_runs_started": False,
        "provider": args.provider,
        "model": args.model,
        "max_concurrency": args.max_concurrency,
        "queue_refill": refill_queue,
        "remediation_mode": remediation_mode,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--queue-state", type=Path, required=True)
    parser.add_argument(
        "--source-root",
        "--catalog-root",
        dest="source_root",
        type=Path,
        default=Path("catalog/sources"),
        help="Human-maintained declarative source root.",
    )
    parser.add_argument(
        "--tasks-root",
        type=Path,
        default=Path("catalog/tasks"),
        help="Generated production Harbor task root.",
    )
    parser.add_argument("--state-root", type=Path, default=Path(".nl2repo/authoring"))
    parser.add_argument(
        "--worktree-root",
        type=Path,
        default=Path(".nl2repo/authoring-work/worktrees"),
        help="Disk-backed worktree root; do not use tmpfs for source/build artifacts.",
    )
    parser.add_argument("--owner", required=True)
    parser.add_argument("--max-concurrency", type=int, default=3)
    parser.add_argument("--lease-seconds", type=int, default=7200)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument(
        "--refill-queue",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Continue with pending queue candidates after plan tasks are exhausted.",
    )
    parser.add_argument(
        "--remediation-mode",
        action="store_true",
        help=(
            "Refill from existing incomplete sources and explicitly reopen only "
            "targeted blocked/complete queue records selected for remediation."
        ),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pi-command", default=os.environ.get("PI_COMMAND", "pi"))
    parser.add_argument(
        "--provider",
        default=os.environ.get("PI_PROVIDER", "z-open-api-gpt-openai-responses"),
    )
    parser.add_argument("--model", default=os.environ.get("PI_MODEL", "gpt-5.6-sol"))
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--models-file", type=Path, default=Path.home() / ".pi/agent/models.json")
    parser.add_argument(
        "--credential-env",
        help="Parent environment variable to map to the Pi provider's $ENV apiKey reference.",
    )
    parser.add_argument(
        "--session-root",
        type=Path,
        default=Path(".nl2repo/authoring/sessions"),
        help="Persistent session root; must not be on tmpfs.",
    )
    parser.add_argument("--agent-timeout-sec", type=int, default=3600)
    parser.add_argument(
        "--exclude-tools",
        default=DEFAULT_EXCLUDED_TOOLS,
        help="Comma-separated Pi tools denied to direct authoring sessions.",
    )
    parser.add_argument(
        "--allow-internal-subagent",
        action="store_true",
        help=("Allow a child Pi Agent to use subagent for bounded parallel probes."),
    )
    args = parser.parse_args()
    try:
        result = run(args)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"authoring loop execution failed: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "agent_mode": result["agent_mode"],
                "started": result["agent_runs_started"],
                "completed": sum(x.get("status") == "complete" for x in result["results"]),
                "released": sum(x.get("status") == "released" for x in result["results"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
