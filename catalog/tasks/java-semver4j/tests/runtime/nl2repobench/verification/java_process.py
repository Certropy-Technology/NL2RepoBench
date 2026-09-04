"""Bounded Java process execution for the separate verifier environment."""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .subprocess_supervisor import ProcessLimits, ProcessResult, run_supervised_process

MAX_OUTPUT_BYTES = 8 * 1024 * 1024
MAX_TIMEOUT_SEC = 600.0
DEFAULT_ADDRESS_SPACE_BYTES = 4 * 1024 * 1024 * 1024
DEFAULT_NOFILE = 128
DEFAULT_NPROC = 256
SAFE_ENVIRONMENT_NAMES = frozenset(
    {"PATH", "JAVA_HOME", "MAVEN_HOME", "HOME", "LANG", "LC_ALL", "MAVEN_OPTS"}
)


@dataclass(frozen=True)
class JavaProcessResult:
    """Bounded result of one JVM or compiler process."""

    return_code: int | None
    signal: int | None
    timed_out: bool
    spawn_error: str | None
    stdout: str
    stderr: str
    stdout_bytes: int
    stderr_bytes: int
    stdout_truncated: bool
    stderr_truncated: bool


def _as_java_result(result: ProcessResult) -> JavaProcessResult:
    return JavaProcessResult(**asdict(result))


def run_java_process(
    command: list[str],
    *,
    cwd: Path,
    uid: int,
    timeout_sec: float,
    address_space_bytes: int = DEFAULT_ADDRESS_SPACE_BYTES,
    environment: dict[str, str] | None = None,
) -> JavaProcessResult:
    """Run argv without a shell and clean its complete process group."""

    if not command or any(not isinstance(item, str) or not item for item in command):
        raise ValueError("Java process command must be a non-empty argv")
    if not math.isfinite(timeout_sec) or not 0 < timeout_sec <= MAX_TIMEOUT_SEC:
        raise ValueError(f"Java process timeout must be within (0, {MAX_TIMEOUT_SEC}]")
    if address_space_bytes <= 0:
        raise ValueError("Java process address space limit must be positive")
    if uid != os.getuid() and os.geteuid() != 0:
        raise ValueError("dropping to a different UID requires root")
    if environment is not None and not set(environment).issubset(SAFE_ENVIRONMENT_NAMES):
        raise ValueError("Java process environment contains an unsafe variable")
    process_environment = {
        name: os.environ[name]
        for name in SAFE_ENVIRONMENT_NAMES
        if name in os.environ and name != "MAVEN_OPTS"
    }
    process_environment.setdefault("PATH", "/usr/local/bin:/usr/bin:/bin")
    process_environment["HOME"] = "/root" if uid == 0 else "/home/candidate"
    if environment is not None:
        process_environment.update(environment)

    result = run_supervised_process(
        command,
        cwd=cwd,
        uid=uid,
        limits=ProcessLimits(
            timeout_sec=timeout_sec,
            max_output_bytes=MAX_OUTPUT_BYTES,
            address_space_bytes=address_space_bytes,
            max_open_files=DEFAULT_NOFILE,
            max_processes=DEFAULT_NPROC,
        ),
        environment=process_environment,
    )
    return _as_java_result(result)


def _write_text(path: str | None, value: str) -> None:
    if path is not None:
        Path(path).write_text(value, encoding="utf-8")


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--stdout-path")
    parser.add_argument("--stderr-path")
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--uid", type=int, required=True)
    parser.add_argument("--timeout-sec", type=float, required=True)
    parser.add_argument("--address-space-bytes", type=int, default=DEFAULT_ADDRESS_SPACE_BYTES)
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("--source-root", type=Path, action="append", default=[])
    parser.add_argument("--classes-dir", type=Path)
    parser.add_argument("--release", type=int, choices=(8, 11, 17, 21), default=21)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if args.source_root:
        if args.classes_dir is None or command:
            parser.error("--source-root requires --classes-dir and no command")
        java_files = sorted(
            path
            for source_root in args.source_root
            for path in source_root.rglob("*.java")
            if path.is_file()
        )
        if not java_files:
            parser.error("--source-root contains no Java files")
        command = [
            "/opt/java/openjdk/bin/javac",
            "-encoding",
            "UTF-8",
            "--release",
            str(args.release),
            "-d",
            str(args.classes_dir),
            *(str(path) for path in java_files),
        ]
    if not command:
        parser.error("a Java process command is required")
    environment = {
        name: os.environ[name]
        for name in ("PATH", "JAVA_HOME", "MAVEN_HOME", "LANG", "LC_ALL")
        if name in os.environ
    }
    environment.setdefault("PATH", "/usr/local/bin:/usr/bin:/bin")
    environment["HOME"] = "/root" if args.uid == 0 else "/home/candidate"
    for item in args.env:
        name, separator, value = item.partition("=")
        if not separator or not name:
            parser.error("--env values must use NAME=VALUE")
        environment[name] = value
    result = run_java_process(
        command,
        cwd=args.cwd,
        uid=args.uid,
        timeout_sec=args.timeout_sec,
        address_space_bytes=args.address_space_bytes,
        environment=environment,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(asdict(result), sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    _write_text(args.stdout_path, result.stdout)
    _write_text(args.stderr_path, result.stderr)
    if result.spawn_error is not None:
        return 3
    if result.timed_out:
        return 2
    if result.return_code != 0 or result.signal is not None:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())


__all__ = ["JavaProcessResult", "run_java_process"]
