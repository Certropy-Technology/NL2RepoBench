"""Run one candidate operation in an unprivileged subprocess.

This module is the only process that imports candidate code. Hidden tests and
pytest remain in the root-owned verifier process and treat this process's output
as the implementation response under test.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import os
import resource
import runpy
import sys
from pathlib import Path
from typing import Any, NoReturn

MAX_REQUEST_BYTES = 1024 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
RESULT_PREFIX = "NL2REPO_CANDIDATE_RESULT="


def _apply_limits() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_BYTES, MAX_OUTPUT_BYTES))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))


def _candidate_site(value: str) -> Path:
    path = Path(value).resolve()
    if path != Path("/tmp/candidate-site") or not path.is_dir():
        raise ValueError("candidate site is unavailable")
    sys.path.append(str(path))
    dependency_root = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    if dependency_root:
        dependency_path = Path(dependency_root).resolve()
        if not dependency_path.is_dir() or not dependency_path.is_relative_to(Path("/opt")):
            raise ValueError("candidate dependency site is unavailable")
        sys.path.insert(1, str(dependency_path))
    return path


def _read_request() -> dict[str, Any]:
    data = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
    if len(data) > MAX_REQUEST_BYTES:
        raise ValueError("candidate request exceeds size limit")
    payload = json.loads(data)
    if not isinstance(payload, dict):
        raise ValueError("candidate request must be an object")
    return payload


def _emit(payload: dict[str, Any], exit_code: int = 0) -> NoReturn:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    os.write(1, RESULT_PREFIX.encode() + encoded + b"\n")
    os._exit(exit_code)


def _call() -> NoReturn:
    request = _read_request()
    if set(request) != {"args", "attribute", "kwargs", "module", "operation"}:
        raise ValueError("invalid call request fields")
    if request["operation"] not in {"call", "get"}:
        raise ValueError("invalid call operation")
    module_name = request["module"]
    attribute = request["attribute"]
    args = request["args"]
    kwargs = request["kwargs"]
    if not isinstance(module_name, str) or not isinstance(attribute, str):
        raise ValueError("module and attribute must be strings")
    if not isinstance(args, list) or not isinstance(kwargs, dict):
        raise ValueError("args and kwargs have invalid shapes")
    try:
        target: Any = importlib.import_module(module_name)
        for part in attribute.split("."):
            target = getattr(target, part)
        value = target(*args, **kwargs) if request["operation"] == "call" else target
        payload = {"ok": True, "value": value}
    except BaseException as exc:  # candidate exceptions are test observations
        payload = {
            "exception_message": str(exc),
            "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "ok": False,
        }
    _emit(payload)


def _script() -> NoReturn:
    """Run a trusted JSON scenario inside the isolated candidate process."""

    request = _read_request()
    if set(request) != {"source"} or not isinstance(request["source"], str):
        raise ValueError("invalid script request")
    namespace: dict[str, Any] = {"__name__": "__main__"}
    try:
        exec(compile(request["source"], "<candidate-scenario>", "exec"), namespace)
        payload = {"ok": True, "value": namespace["result"]}
    except BaseException as exc:  # scenario failures are verifier observations
        payload = {
            "exception_message": str(exc),
            "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "ok": False,
        }
    _emit(payload)


def _metadata_requires(site: Path, distribution: str) -> NoReturn:
    normalized = distribution.casefold().replace("_", "-")
    for candidate in importlib.metadata.distributions(path=[str(site)]):
        try:
            metadata_name = candidate.metadata["Name"]
        except KeyError:
            metadata_name = ""
        name = metadata_name.casefold().replace("_", "-")
        if name == normalized:
            _emit({"ok": True, "value": candidate.requires})
    _emit(
        {
            "exception_message": f"distribution not found: {distribution}",
            "exception_type": "importlib.metadata.PackageNotFoundError",
            "ok": False,
        }
    )


def _run_module(module: str, arguments: list[str]) -> NoReturn:
    sys.argv = [module, *arguments]
    runpy.run_module(module, run_name="__main__", alter_sys=True)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


def _run_console(site: Path, name: str, arguments: list[str]) -> NoReturn:
    matches = [
        entry
        for distribution in importlib.metadata.distributions(path=[str(site)])
        for entry in distribution.entry_points
        if entry.group == "console_scripts" and entry.name == name
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected one console entry point {name!r}, found {len(matches)}")
    sys.argv = [name, *arguments]
    result = matches[0].load()()
    raise SystemExit(result if isinstance(result, int) else 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    subcommands = parser.add_subparsers(dest="operation", required=True)
    subcommands.add_parser("call")
    subcommands.add_parser("script")
    metadata = subcommands.add_parser("metadata-requires")
    metadata.add_argument("distribution")
    module = subcommands.add_parser("module")
    module.add_argument("module")
    module.add_argument("arguments", nargs=argparse.REMAINDER)
    console = subcommands.add_parser("console")
    console.add_argument("name")
    console.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    _apply_limits()
    site = _candidate_site(args.candidate_site)
    if args.operation == "call":
        _call()
    if args.operation == "script":
        _script()
    if args.operation == "metadata-requires":
        _metadata_requires(site, args.distribution)
    if args.operation == "module":
        _run_module(args.module, args.arguments)
    if args.operation == "console":
        _run_console(site, args.name, args.arguments)
    raise AssertionError("unreachable candidate operation")


if __name__ == "__main__":
    main()
