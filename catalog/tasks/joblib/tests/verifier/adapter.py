from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import threading
import warnings
from typing import Any


def type_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def exercise(name: str) -> Any:
    import joblib

    if name == "exports":
        return all(hasattr(joblib, item) for item in ("Memory", "Parallel", "delayed", "dump", "load", "hash"))
    if name == "delayed-sequential":
        return joblib.Parallel(n_jobs=1)(joblib.delayed(lambda x: x * x)(x) for x in range(5))
    if name == "thread-backend":
        with joblib.parallel_backend("threading", n_jobs=2):
            return joblib.Parallel()(joblib.delayed(sum)([x, 1]) for x in range(4))
    if name == "sequential-config":
        with joblib.parallel_config(backend="sequential", n_jobs=1):
            return joblib.Parallel()(joblib.delayed(str)(x) for x in range(3))
    if name == "generator-order":
        generator = joblib.Parallel(n_jobs=1, return_as="generator")(
            joblib.delayed(lambda x: x + 10)(x) for x in range(3)
        )
        return list(generator)
    if name == "backend-invalid":
        try:
            joblib.Parallel(n_jobs=1, backend="missing-backend")([])
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "parallel-error":
        def fail() -> None:
            raise ValueError("expected")

        try:
            joblib.Parallel(n_jobs=1)(joblib.delayed(fail)() for _ in range(1))
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "dump-load":
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "value.pkl"
            joblib.dump({"b": [2, 3], "a": 1}, path)
            return joblib.load(path)
    if name == "dump-load-zlib":
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "value.pkl"
            joblib.dump(list(range(100)), path, compress=3)
            return joblib.load(path)
    if name == "dump-load-gzip":
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "value.gz"
            joblib.dump({"value": "gzip"}, path, compress="gzip")
            return joblib.load(path)
    if name == "dump-file-object":
        import io

        stream = io.BytesIO()
        result = joblib.dump((1, "two"), stream)
        stream.seek(0)
        return {"result": result, "value": list(joblib.load(stream))}
    if name == "numpy-roundtrip":
        import numpy as np

        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "array.joblib"
            value = np.arange(12, dtype=np.float64).reshape(3, 4)
            joblib.dump(value, path)
            loaded = joblib.load(path)
            return {"shape": list(loaded.shape), "dtype": str(loaded.dtype), "sum": float(loaded.sum())}
    if name == "numpy-mmap":
        import numpy as np

        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "array.joblib"
            joblib.dump(np.arange(6, dtype=np.int64), path)
            loaded = joblib.load(path, mmap_mode="r")
            return {"type": type(loaded).__name__, "values": loaded.tolist()}
    if name == "numpy-compressed-mmap":
        import numpy as np

        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "array.joblib"
            joblib.dump(np.arange(4), path, compress=3)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                loaded = joblib.load(path, mmap_mode="r")
            return {"type": type(loaded).__name__, "values": loaded.tolist(), "warning": len(caught) > 0}
    if name == "hash-dict-order":
        return joblib.hash({"alpha": 1, "beta": [2, 3]}) == joblib.hash({"beta": [2, 3], "alpha": 1})
    if name == "hash-set-order":
        return joblib.hash({"x", "y", "z"}) == joblib.hash({"z", "x", "y"})
    if name == "hash-numpy":
        import numpy as np

        return joblib.hash(np.arange(5)) == joblib.hash(np.arange(5))
    if name == "hash-invalid-method":
        try:
            joblib.hash("value", hash_name="not-a-hash")
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "memory-cache":
        calls = {"count": 0}

        def square(x: int) -> int:
            calls["count"] += 1
            return x * x

        with tempfile.TemporaryDirectory() as directory:
            cached = joblib.Memory(directory, verbose=0).cache(square)
            values = [cached(7), cached(7)]
            return {"values": values, "calls": calls["count"]}
    if name == "memory-cache-check":
        def plus(x: int) -> int:
            return x + 1

        with tempfile.TemporaryDirectory() as directory:
            cached = joblib.Memory(directory, verbose=0).cache(plus)
            before = cached.check_call_in_cache(3)
            cached(3)
            after = cached.check_call_in_cache(3)
            return [before, after]
    if name == "memory-clear":
        calls = {"count": 0}

        def identity(x: int) -> int:
            calls["count"] += 1
            return x

        with tempfile.TemporaryDirectory() as directory:
            cached = joblib.Memory(directory, verbose=0).cache(identity)
            cached(2)
            cached.clear(warn=False)
            cached(2)
            return calls["count"]
    if name == "memory-kwargs":
        calls = {"count": 0}

        def combine(left: int, right: int = 1) -> int:
            calls["count"] += 1
            return left + right

        with tempfile.TemporaryDirectory() as directory:
            cached = joblib.Memory(directory, verbose=0).cache(combine)
            values = [cached(2, right=3), cached(left=2, right=3)]
            return {"values": values, "calls": calls["count"]}
    if name == "memory-ignore":
        calls = {"count": 0}

        def combine(value: int, noisy: int) -> int:
            calls["count"] += 1
            return value + noisy

        with tempfile.TemporaryDirectory() as directory:
            cached = joblib.Memory(directory, verbose=0).cache(combine, ignore=["noisy"])
            values = [cached(2, 1), cached(2, 99)]
            return {"values": values, "calls": calls["count"]}
    if name == "memory-exception-recompute":
        calls = {"count": 0}

        def fail_once(value: int) -> int:
            calls["count"] += 1
            if calls["count"] == 1:
                raise RuntimeError("first")
            return value

        with tempfile.TemporaryDirectory() as directory:
            cached = joblib.Memory(directory, verbose=0).cache(fail_once)
            try:
                cached(4)
            except RuntimeError:
                pass
            return {"value": cached(4), "calls": calls["count"]}
    if name == "memstr":
        return [joblib.disk.memstr_to_bytes(value) for value in ("1K", "2M", "3G", "4K", "0.5K")]
    if name == "memstr-invalid":
        try:
            joblib.disk.memstr_to_bytes("not-a-size")
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "effective-n-jobs":
        return [joblib.effective_n_jobs(1), joblib.effective_n_jobs(-1) >= 1, joblib.cpu_count() >= 1]
    if name == "wrap-non-picklable":
        def make_multiplier(factor: int):
            return lambda value: value * factor

        wrapped = joblib.wrap_non_picklable_objects(make_multiplier(3))
        return wrapped(4)
    if name == "register-compressor-invalid":
        try:
            joblib.register_compressor("bad/name", object())
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "testing-success":
        from joblib.testing import check_subprocess_call

        check_subprocess_call([sys.executable, "-c", "print('ready')"], stdout_regex="ready")
        return True
    if name == "testing-failure":
        from joblib.testing import check_subprocess_call

        try:
            check_subprocess_call([sys.executable, "-c", "raise SystemExit(3)"])
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "parallel-config-invalid":
        try:
            with joblib.parallel_config(prefer="invalid"):
                joblib.Parallel(n_jobs=1)([])
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "memory-pathlib":
        with tempfile.TemporaryDirectory() as directory:
            memory = joblib.Memory(pathlib.Path(directory), verbose=0)
            return str(memory.location) == directory
    raise ValueError(f"unknown scenario: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--dependency-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    sys.path.insert(1, args.dependency_site)
    try:
        value = exercise(args.scenario)
        print(json.dumps({"ok": True, "value": value}, sort_keys=True))
    except BaseException as exc:
        print(json.dumps({"ok": False, "exception_type": type_name(exc), "exception_message": str(exc)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
