"""Unprivileged child-side scenarios for the frozen filelock contract.

This process imports the candidate package. It deliberately reports only
normalized observations; expected values remain in the trusted parent runner.
Contention helpers emit readiness only after acquiring their lock and wait for
an explicit release byte, so no result depends on host scheduling races.
"""

from __future__ import annotations

import asyncio
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def _configure_candidate_import() -> None:
    candidate_root = os.environ["CANDIDATE_ROOT"]
    dependency_root = os.environ["NL2REPO_CANDIDATE_DEPENDENCIES"]
    for entry in (dependency_root, candidate_root):
        while entry in sys.path:
            sys.path.remove(entry)
        sys.path.insert(0, entry)


_configure_candidate_import()

import filelock  # noqa: E402


SCENARIO_ROOT = Path(os.environ["FILELOCK_SCENARIO_ROOT"])
HELPER = r'''
from __future__ import annotations

import os
import sys

for entry in (os.environ["NL2REPO_CANDIDATE_DEPENDENCIES"], os.environ["CANDIDATE_ROOT"]):
    while entry in sys.path:
        sys.path.remove(entry)
    sys.path.insert(0, entry)

import filelock

kind, lock_file = sys.argv[1:]
lock = None
try:
    if kind == "native":
        lock = filelock.FileLock(lock_file, timeout=1.0, poll_interval=0.02)
        lock.acquire()
    elif kind == "soft":
        lock = filelock.SoftFileLock(lock_file, timeout=1.0, poll_interval=0.02)
        lock.acquire()
    elif kind == "read-write":
        lock = filelock.ReadWriteLock(lock_file, timeout=1.0, is_singleton=False)
        lock.acquire_write()
    else:
        raise ValueError(f"unknown helper kind: {kind}")
    print("ready", flush=True)
    sys.stdin.readline()
finally:
    if lock is not None:
        try:
            lock.release(force=True)
        except TypeError:
            lock.release()
        if hasattr(lock, "close"):
            lock.close()
'''


def _path(name: str) -> Path:
    return SCENARIO_ROOT / f"{name}.lock"


def _start_holder(kind: str, lock_file: Path) -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [sys.executable, "-I", "-B", "-c", HELPER, kind, os.fspath(lock_file)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=dict(os.environ),
    )
    assert process.stdout is not None
    ready, _, _ = select.select([process.stdout], [], [], 3.0)
    if not ready:
        _finish_holder(process)
        raise RuntimeError(f"{kind} holder did not signal readiness")
    if process.stdout.readline().strip() != "ready":
        stderr = process.stderr.read() if process.stderr is not None else ""
        _finish_holder(process)
        raise RuntimeError(f"{kind} holder failed: {stderr[-1000:]}")
    return process


def _finish_holder(process: subprocess.Popen[str]) -> bool:
    try:
        stdout, stderr = process.communicate("release\n", timeout=3.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return False
    return process.returncode == 0 and not stderr and not stdout


def _exception_name(callable_: Any) -> str | None:
    try:
        callable_()
    except BaseException as error:
        return type(error).__name__
    return None


def root_surface() -> dict[str, Any]:
    names = (
        "FileLock",
        "SoftFileLock",
        "StrictSoftFileLock",
        "SoftFileLease",
        "ReadWriteLock",
        "SoftReadWriteLock",
        "AsyncFileLock",
        "Timeout",
        "OwnerRecord",
        "lock_descriptor",
        "unlock_descriptor",
    )
    modules = (
        "filelock.asyncio",
        "filelock._api",
        "filelock._descriptor",
        "filelock._error",
        "filelock._identity",
        "filelock._lease",
        "filelock._marker",
        "filelock._read_write",
        "filelock._soft",
        "filelock._soft_rw",
        "filelock._strict",
        "filelock._util",
    )
    for module in modules:
        __import__(module)
    return {
        "version": filelock.__version__,
        "names": {name: hasattr(filelock, name) for name in names},
        "all_names": all(name in filelock.__all__ for name in names),
        "module_count": len(modules),
    }


def native_reentrant() -> dict[str, Any]:
    lock = filelock.FileLock(_path("native-reentrant"), timeout=0.25, poll_interval=0.02)
    with lock.acquire() as entered:
        first = (entered is lock, lock.is_locked, lock.lock_counter)
        with lock.acquire() as nested:
            second = (nested is lock, lock.is_locked, lock.lock_counter)
        after_nested = (lock.is_locked, lock.lock_counter)
    return {
        "first": first,
        "second": second,
        "after_nested": after_nested,
        "after_outer": (lock.is_locked, lock.lock_counter),
    }


def native_timeout() -> dict[str, Any]:
    lock_file = _path("native-timeout")
    holder = _start_holder("native", lock_file)
    try:
        contender = filelock.FileLock(lock_file, timeout=0.15, poll_interval=0.02)
        started = time.monotonic()
        outcome = _exception_name(contender.acquire)
        elapsed = time.monotonic() - started
    finally:
        released = _finish_holder(holder)
    followup = filelock.FileLock(lock_file, timeout=0.25, poll_interval=0.02)
    with followup.acquire():
        acquired_after_release = followup.is_locked
    return {
        "outcome": outcome,
        "elapsed": elapsed,
        "holder_released": released,
        "acquired_after_release": acquired_after_release,
    }


def soft_marker() -> dict[str, Any]:
    lock_file = _path("soft-marker")
    lock = filelock.SoftFileLock(lock_file, timeout=0.25, poll_interval=0.02)
    with lock.acquire():
        held = {
            "exists": lock_file.exists(),
            "pid": lock.pid == os.getpid(),
            "ours": lock.is_lock_held_by_us,
            "counter": lock.lock_counter,
        }
    return {"held": held, "removed": not lock_file.exists()}


def soft_timeout() -> dict[str, Any]:
    lock_file = _path("soft-timeout")
    holder = _start_holder("soft", lock_file)
    try:
        contender = filelock.SoftFileLock(lock_file, timeout=0.0, poll_interval=0.02)
        outcome = _exception_name(contender.acquire)
    finally:
        released = _finish_holder(holder)
    return {"outcome": outcome, "holder_released": released}


def strict_claims() -> dict[str, Any]:
    lock = filelock.StrictSoftFileLock(_path("strict-claims"), timeout=0.5, poll_interval=0.02)
    with lock.acquire():
        claims = lock.claims
        held = {
            "count": len(claims),
            "states": sorted(claim.state for claim in claims),
            "pid_matches": all(claim.pid == os.getpid() for claim in claims),
            "names_unique": len({claim.name for claim in claims}) == len(claims),
        }
    return {"held": held, "after_count": len(lock.claims)}


def lease_lifecycle() -> dict[str, Any]:
    lock = filelock.SoftFileLease(
        _path("lease-lifecycle"),
        lease_duration=0.45,
        heartbeat_interval=0.12,
        timeout=0.25,
        poll_interval=0.02,
    )
    with lock.acquire():
        held = {
            "token_length": len(lock.token or ""),
            "compromise": lock.compromise is None,
            "locked": lock.is_locked,
        }
    return {"held": held, "token_cleared": lock.token is None, "locked": lock.is_locked}


def lease_mismatch() -> dict[str, Any]:
    lock_file = _path("lease-mismatch")
    owner = filelock.SoftFileLease(
        lock_file,
        lease_duration=0.5,
        heartbeat_interval=0.15,
        timeout=0.25,
        poll_interval=0.02,
    )
    other = filelock.SoftFileLease(
        lock_file,
        lease_duration=0.7,
        heartbeat_interval=0.2,
        timeout=0.0,
        poll_interval=0.02,
    )
    with owner.acquire():
        outcome = _exception_name(other.acquire)
    return {"outcome": outcome}


def read_write_modes() -> dict[str, Any]:
    lock = filelock.ReadWriteLock(_path("read-write-modes"), timeout=0.25, is_singleton=False)
    try:
        with lock.read_lock():
            with lock.read_lock():
                nested_read = True
            upgrade = _exception_name(lambda: lock.acquire_write(timeout=0.0))
        with lock.write_lock():
            write = True
    finally:
        lock.close()
    return {"nested_read": nested_read, "upgrade": upgrade, "write": write}


def read_write_timeout() -> dict[str, Any]:
    lock_file = _path("read-write-timeout")
    holder = _start_holder("read-write", lock_file)
    contender = filelock.ReadWriteLock(lock_file, timeout=0.0, is_singleton=False)
    try:
        outcome = _exception_name(lambda: contender.acquire_read(timeout=0.0))
    finally:
        contender.close()
        released = _finish_holder(holder)
    return {"outcome": outcome, "holder_released": released}


def soft_read_write_modes() -> dict[str, Any]:
    lock = filelock.SoftReadWriteLock(
        _path("soft-read-write-modes"),
        timeout=0.25,
        is_singleton=False,
        heartbeat_interval=0.05,
        stale_threshold=0.16,
        poll_interval=0.02,
    )
    try:
        with lock.read_lock():
            read = True
        with lock.write_lock():
            write = True
    finally:
        lock.close()
    return {"read": read, "write": write}


def descriptor_lifecycle() -> dict[str, Any]:
    lock_file = _path("descriptor-lifecycle")
    descriptor = os.open(lock_file, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        acquired = filelock.lock_descriptor(descriptor, blocking=False)
        filelock.unlock_descriptor(descriptor)
        retained = os.fstat(descriptor).st_size == 0
    finally:
        os.close(descriptor)
    return {"acquired": acquired, "retained": retained}


def descriptor_timeout() -> dict[str, Any]:
    lock_file = _path("descriptor-timeout")
    holder = _start_holder("native", lock_file)
    descriptor = os.open(lock_file, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        contended = filelock.lock_descriptor(descriptor, blocking=False)
    finally:
        os.close(descriptor)
        released = _finish_holder(holder)
    return {"contended": contended, "holder_released": released}


async def _async_lifecycle_inner() -> dict[str, Any]:
    lock = filelock.AsyncFileLock(_path("async-lifecycle"), timeout=0.25, poll_interval=0.02)
    async with lock:
        held = (lock.is_locked, lock.lock_counter)
    return {"held": held, "after": (lock.is_locked, lock.lock_counter)}


def async_lifecycle() -> dict[str, Any]:
    return asyncio.run(_async_lifecycle_inner())


async def _async_timeout_inner(lock_file: Path) -> str | None:
    contender = filelock.AsyncFileLock(lock_file, timeout=0.15, poll_interval=0.02)
    try:
        await contender.acquire()
    except BaseException as error:
        return type(error).__name__
    return None


def async_timeout() -> dict[str, Any]:
    lock_file = _path("async-timeout")
    holder = _start_holder("native", lock_file)
    try:
        outcome = asyncio.run(_async_timeout_inner(lock_file))
    finally:
        released = _finish_holder(holder)
    return {"outcome": outcome, "holder_released": released}


def marker_codec() -> dict[str, Any]:
    from filelock._marker import encode_marker, parse_marker

    record = filelock.OwnerRecord(
        pid=os.getpid(),
        hostname="scenario-host",
        mode="lease",
        token="scenario-token",
        lease_duration=1.5,
        start=42,
    )
    parsed = parse_marker(encode_marker(record).decode("utf-8"))
    return {
        "round_trip": parsed == record,
        "unknown_mode": getattr(parse_marker("filelock/2\npid=1\nhost=x\nmode=future\n"), "mode", None),
        "malformed": parse_marker("not-a-marker") is None,
    }


def singleton_configuration() -> dict[str, Any]:
    lock_file = _path("singleton")
    first = filelock.FileLock(lock_file, timeout=0.25, is_singleton=True)
    second = filelock.FileLock(lock_file, timeout=0.25, is_singleton=True)
    mismatch = _exception_name(lambda: filelock.FileLock(lock_file, timeout=0.5, is_singleton=True))
    return {"same_instance": first is second, "mismatch": mismatch}


SCENARIOS = {
    name: value
    for name, value in globals().items()
    if callable(value)
    and not name.startswith("_")
    and name not in {"Any", "Path"}
}


def main() -> None:
    SCENARIO_ROOT.mkdir(parents=True, exist_ok=True)
    observations: dict[str, Any] = {}
    for name in sorted(SCENARIOS):
        try:
            observations[name] = {"ok": True, "value": SCENARIOS[name]()}
        except BaseException as error:
            observations[name] = {
                "ok": False,
                "error_type": type(error).__name__,
                "message": str(error)[-1000:],
            }
    print(json.dumps({"schema_version": "1.0", "observations": observations}, sort_keys=True))


if __name__ == "__main__":
    main()
