from __future__ import annotations

import argparse
import importlib.metadata
import json
import multiprocessing
import os
import pathlib
import tempfile
import time
from typing import Any

PREFIX = "PORTALOCKER_RESULT="


def child_contender(path: str, queue: Any, timeout: float, fail: bool) -> None:
    import portalocker
    try:
        with portalocker.Lock(path, timeout=timeout, fail_when_locked=fail):
            queue.put({"acquired": True})
    except BaseException as exc:
        queue.put({"acquired": False, "type": f"{type(exc).__module__}.{type(exc).__qualname__}"})


def hold_lock(path: str, ready: Any, release: Any, queue: Any) -> None:
    import portalocker
    try:
        with portalocker.Lock(path, timeout=1):
            ready.set()
            release.wait(3)
            queue.put({"acquired": True})
    except BaseException as exc:
        queue.put({"acquired": False, "type": f"{type(exc).__module__}.{type(exc).__qualname__}"})


def scenario(name: str) -> Any:
    import portalocker
    from portalocker import constants, exceptions, utils

    if name == "exports-version-flags":
        return {"version": portalocker.__version__, "exclusive": int(portalocker.LOCK_EX), "shared": int(portalocker.LOCK_SH), "nonblocking": int(portalocker.LOCK_NB), "unblock": int(portalocker.LOCK_UN), "flags": [m.name for m in constants.LockFlags]}
    if name == "package-metadata":
        return {"distribution": importlib.metadata.version("portalocker"), "description": portalocker.__description__}
    if name == "module-exports":
        return {"all": sorted(portalocker.__all__), "modules": [portalocker.constants.__name__, portalocker.exceptions.__name__, portalocker.portalocker.__name__, portalocker.types.__name__, portalocker.utils.__name__]}
    if name == "lock-context-persistence":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "lock"
            before = p.exists()
            with portalocker.Lock(p, "a") as fh:
                inside = [fh.name == str(p), p.exists(), not fh.closed]
            return {"before": before, "inside": inside, "after": p.exists()}
    if name == "lock-write-read":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "value"
            with portalocker.Lock(p, "w") as fh:
                fh.write("payload")
            return p.read_text()
    if name in {"nonblocking-contention", "timeout-contention"}:
        with tempfile.TemporaryDirectory() as d:
            p = str(pathlib.Path(d) / "lock")
            ctx = multiprocessing.get_context("fork")
            q, ready, release = ctx.Queue(), ctx.Event(), ctx.Event()
            holder = ctx.Process(target=hold_lock, args=(p, ready, release, q))
            holder.start(); assert ready.wait(2)
            timeout, fail = ((0, True) if name == "nonblocking-contention" else (0.15, False))
            started = time.monotonic()
            contender = ctx.Process(target=child_contender, args=(p, q, timeout, fail))
            contender.start(); contender.join(3)
            elapsed = time.monotonic() - started
            result = q.get(timeout=2)
            release.set(); holder.join(3)
            result["waited"] = elapsed >= 0.1
            return result
    if name == "blocking-contention":
        with tempfile.TemporaryDirectory() as d:
            p = str(pathlib.Path(d) / "lock")
            ctx = multiprocessing.get_context("fork")
            q, ready, release = ctx.Queue(), ctx.Event(), ctx.Event()
            holder = ctx.Process(target=hold_lock, args=(p, ready, release, q)); holder.start(); assert ready.wait(2)
            contender = ctx.Process(target=child_contender, args=(p, q, 1, False)); contender.start(); time.sleep(0.2); release.set()
            contender.join(3); holder.join(3); results = [q.get(timeout=2), q.get(timeout=2)]
            return {"acquired": sum(bool(x.get("acquired")) for x in results), "exits": [holder.exitcode, contender.exitcode]}
    if name == "lock-release":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "lock"; fh = p.open("a"); portalocker.lock(fh, portalocker.LOCK_EX); portalocker.unlock(fh); fh.close(); return p.exists()
    if name == "lock-exception":
        try: raise exceptions.LockException("bad")
        except exceptions.LockException as exc: return {"type": type(exc).__name__, "strerror": exc.strerror}
    if name == "rlock-reentry":
        with tempfile.TemporaryDirectory() as d:
            lock = portalocker.RLock(pathlib.Path(d) / "rlock", timeout=1); first = lock.acquire(); second = lock.acquire(); count = lock._acquire_count; lock.release(); mid = lock._acquire_count; lock.release()
            return {"same": [first is lock, second is lock], "count": count, "mid": mid}
    if name == "temporary-file-lock":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "tmp.lock"
            with portalocker.TemporaryFileLock(p): inside = p.exists()
            return {"inside": inside, "after": not p.exists()}
    if name == "pid-file-lock":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "pid.lock"
            with portalocker.PidFileLock(p): value = int(p.read_text())
            return {"positive": value > 0, "same": value == os.getpid(), "removed": not p.exists()}
    if name == "pid-file-read-missing":
        with tempfile.TemporaryDirectory() as d: return portalocker.PidFileLock(pathlib.Path(d) / "missing").read_pid() is None
    if name == "semaphore-slots":
        with tempfile.TemporaryDirectory() as d:
            first = portalocker.BoundedSemaphore(1, name="slots", directory=d, timeout=0.1); second = portalocker.BoundedSemaphore(1, name="slots", directory=d, timeout=0.1); a = first.acquire()
            try: b = second.acquire()
            except BaseException as exc: b = f"{type(exc).__module__}.{type(exc).__qualname__}"
            first.release()
            return {"first": a is not None, "second": b, "files": len(first.get_filenames())}
    if name == "named-semaphore":
        with tempfile.TemporaryDirectory() as d:
            sem = portalocker.NamedBoundedSemaphore(2, name="named", directory=d); return {"name": sem.name, "count": len(sem.get_filenames())}
    if name in {"open-atomic-binary", "open-atomic-text"}:
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "atomic"; binary = name.endswith("binary")
            with portalocker.open_atomic(p, binary=binary) as fh: fh.write(b"bytes" if binary else "text")
            return p.read_bytes() == b"bytes" if binary else p.read_text() == "text"
    if name == "open-atomic-existing":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "atomic"; p.write_text("old")
            try:
                with portalocker.open_atomic(p) as fh: fh.write(b"new")
            except FileExistsError: return p.read_text()
            return "wrong"
    if name == "open-atomic-cleanup":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "atomic"
            with portalocker.open_atomic(p) as fh: temp_name = fh.name
            return {"published": p.exists(), "temp_gone": not pathlib.Path(temp_name).exists()}
    if name == "flags-validation":
        with tempfile.TemporaryDirectory() as d:
            fh = (pathlib.Path(d) / "flags").open("a"); outcomes = []
            for flags in (constants.LockFlags(0), constants.LockFlags.SHARED | constants.LockFlags.EXCLUSIVE):
                try: portalocker.lock(fh, flags)
                except RuntimeError: outcomes.append(True)
            fh.close(); return outcomes
    if name == "shared-lock":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "shared"; a, b = p.open("a"), p.open("a"); portalocker.lock(a, portalocker.LOCK_SH | portalocker.LOCK_NB); portalocker.lock(b, portalocker.LOCK_SH | portalocker.LOCK_NB); portalocker.unlock(a); portalocker.unlock(b); a.close(); b.close(); return True
    if name == "low-level-lock":
        with tempfile.TemporaryDirectory() as d:
            fh = (pathlib.Path(d) / "low").open("a"); portalocker.lock(fh, portalocker.LOCK_EX | portalocker.LOCK_NB); portalocker.unlock(fh); fh.close(); return True
    if name == "lock-file-open-kwargs":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "kwargs"
            with portalocker.Lock(p, "w", encoding="utf-8") as fh: fh.write("ok")
            return p.read_text() == "ok"
    if name == "lock-timeout-defaults": return {"timeout": utils.DEFAULT_TIMEOUT, "interval": utils.DEFAULT_CHECK_INTERVAL, "fail": utils.DEFAULT_FAIL_WHEN_LOCKED}
    if name == "rlock-overrelease":
        with tempfile.TemporaryDirectory() as d:
            lock = portalocker.RLock(pathlib.Path(d) / "rlock", timeout=1); lock.acquire(); lock.release()
            try: lock.release()
            except exceptions.LockException as exc: return type(exc).__name__
            return "wrong"
    if name == "pidfile-cleanup":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "pid"; lock = portalocker.PidFileLock(p); lock.acquire(); lock.release(); return not p.exists()
    if name == "semaphore-invalid":
        try: portalocker.BoundedSemaphore(0)
        except (ValueError, AssertionError) as exc: return type(exc).__name__
        return "wrong"
    if name == "semaphore-filename":
        with tempfile.TemporaryDirectory() as d: return [p.name for p in portalocker.BoundedSemaphore(2, name="demo", directory=d).get_filenames()]
    if name == "deterministic-repeated":
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "repeat"; values = []
            for _ in range(2):
                with portalocker.Lock(p): values.append(p.exists())
            return values
    if name == "candidate-isolation": return {"uid": os.getuid(), "site": os.environ.get("PORTALOCKER_CANDIDATE_SITE")}
    if name == "network-false": return True
    raise ValueError(name)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--candidate-site", required=True); parser.add_argument("--scenario", required=True); args = parser.parse_args()
    import sys
    sys.path.insert(0, args.candidate_site)
    try: result = {"ok": True, "value": scenario(args.scenario)}
    except BaseException as exc: result = {"ok": False, "type": f"{type(exc).__module__}.{type(exc).__qualname__}", "message": str(exc)}
    print(PREFIX + json.dumps(result, sort_keys=True, default=str)); return 0


if __name__ == "__main__": raise SystemExit(main())
