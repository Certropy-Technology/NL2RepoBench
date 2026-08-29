#!/usr/bin/env python3
"""Private sniffio contract verifier.

The trusted process only sends source snippets to the canonical candidate
runner. Candidate imports therefore happen in the UID-isolated child, never in
this verifier process.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any, Callable


RUNNER = [
    sys.executable,
    "-I",
    "-B",
    "-m",
    "nl2repobench.verification.candidate_runner",
    "--candidate-site",
    "/tmp/candidate-site",
    "script",
]
PREFIX = "NL2REPO_CANDIDATE_RESULT="


def run_child(source: str) -> tuple[bool, Any]:
    try:
        completed = subprocess.run(
            RUNNER,
            input=json.dumps({"source": source}),
            capture_output=True,
            text=True,
            cwd="/workspace",
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"child execution failed: {exc}"
    lines = [line for line in completed.stdout.splitlines() if line.startswith(PREFIX)]
    if not lines:
        return False, f"child returned {completed.returncode}: {completed.stderr[-500:]}"
    try:
        payload = json.loads(lines[-1][len(PREFIX) :])
    except json.JSONDecodeError as exc:
        return False, f"invalid child payload: {exc}"
    if not payload.get("ok"):
        return False, payload.get("exception_message", "candidate scenario failed")
    return True, payload.get("value")


def expect(source: str, predicate: Callable[[Any], bool]) -> tuple[bool, str]:
    ok, value = run_child(source)
    if not ok:
        return False, str(value)
    try:
        passed = predicate(value)
    except Exception as exc:  # verifier assertion diagnostics
        return False, f"predicate failed: {exc}"
    return passed, "unexpected result: " + repr(value)


def is_true(value: Any) -> bool:
    return value is True


CASES: list[tuple[str, str, Callable[[Any], bool]]] = [
    (
        "exports",
        "import sniffio\nresult = sniffio.__all__",
        lambda value: value == [
            "current_async_library",
            "AsyncLibraryNotFoundError",
            "current_async_library_cvar",
            "thread_local",
        ],
    ),
    (
        "version",
        "import importlib.metadata\nimport sniffio\nresult = (sniffio.__version__, importlib.metadata.version('sniffio'))",
        lambda value: value == ["1.3.1+dev", "1.3.1+dev"],
    ),
    (
        "marker-and-submodules",
        "import importlib.resources\nimport sniffio._impl\nimport sniffio._version\nresult = importlib.resources.files('sniffio').joinpath('py.typed').is_file()",
        is_true,
    ),
    (
        "error-type",
        "from sniffio import AsyncLibraryNotFoundError\nresult = issubclass(AsyncLibraryNotFoundError, RuntimeError)",
        is_true,
    ),
    (
        "outside-context",
        "import sniffio\ntry:\n    sniffio.current_async_library()\nexcept sniffio.AsyncLibraryNotFoundError as exc:\n    result = (type(exc).__name__, 'unknown async library' in str(exc))\nelse:\n    result = False",
        lambda value: value == ["AsyncLibraryNotFoundError", True],
    ),
    (
        "cvar-default",
        "import sniffio\nresult = sniffio.current_async_library_cvar.get() is None",
        is_true,
    ),
    (
        "cvar-override",
        "import sniffio\ntoken = sniffio.current_async_library_cvar.set('generic-lib')\ntry:\n    result = sniffio.current_async_library()\nfinally:\n    sniffio.current_async_library_cvar.reset(token)",
        lambda value: value == "generic-lib",
    ),
    (
        "cvar-reset",
        "import sniffio\ntoken = sniffio.current_async_library_cvar.set('temporary')\nsniffio.current_async_library_cvar.reset(token)\ntry:\n    sniffio.current_async_library()\nexcept sniffio.AsyncLibraryNotFoundError:\n    result = True\nelse:\n    result = False",
        is_true,
    ),
    (
        "thread-default",
        "import sniffio\nresult = sniffio.thread_local.name is None",
        is_true,
    ),
    (
        "thread-override",
        "import sniffio\nsniffio.thread_local.name = 'thread-lib'\ntry:\n    result = sniffio.current_async_library()\nfinally:\n    sniffio.thread_local.name = None",
        lambda value: value == "thread-lib",
    ),
    (
        "thread-priority",
        "import sniffio\ncvar_token = sniffio.current_async_library_cvar.set('context-lib')\nsniffio.thread_local.name = 'thread-lib'\ntry:\n    result = sniffio.current_async_library()\nfinally:\n    sniffio.thread_local.name = None\n    sniffio.current_async_library_cvar.reset(cvar_token)",
        lambda value: value == "thread-lib",
    ),
    (
        "cvar-priority-over-asyncio",
        "import asyncio\nimport sniffio\nasync def main():\n    token = sniffio.current_async_library_cvar.set('context-lib')\n    try:\n        return sniffio.current_async_library()\n    finally:\n        sniffio.current_async_library_cvar.reset(token)\nresult = asyncio.run(main())",
        lambda value: value == "context-lib",
    ),
    (
        "asyncio-detection",
        "import asyncio\nimport sniffio\nasync def main():\n    return sniffio.current_async_library()\nresult = asyncio.run(main())",
        lambda value: value == "asyncio",
    ),
    (
        "asyncio-repeat",
        "import asyncio\nimport sniffio\nasync def main():\n    return (sniffio.current_async_library(), sniffio.current_async_library())\nresult = asyncio.run(main())",
        lambda value: value == ["asyncio", "asyncio"],
    ),
    (
        "after-asyncio",
        "import asyncio\nimport sniffio\nasync def main():\n    return sniffio.current_async_library()\nasyncio.run(main())\ntry:\n    sniffio.current_async_library()\nexcept sniffio.AsyncLibraryNotFoundError:\n    result = True\nelse:\n    result = False",
        is_true,
    ),
    (
        "imported-asyncio-outside-task",
        "import asyncio\nimport sniffio\ntry:\n    sniffio.current_async_library()\nexcept sniffio.AsyncLibraryNotFoundError:\n    result = True\nelse:\n    result = False",
        is_true,
    ),
    (
        "thread-isolation",
        "import threading\nimport sniffio\nsniffio.thread_local.name = 'main-lib'\nseen = []\ndef worker():\n    try:\n        seen.append((sniffio.thread_local.name, sniffio.current_async_library()))\n    except sniffio.AsyncLibraryNotFoundError:\n        seen.append((sniffio.thread_local.name, 'error'))\nt = threading.Thread(target=worker)\nt.start()\nt.join()\nsniffio.thread_local.name = None\nresult = seen",
        lambda value: value == [[None, "error"]],
    ),
    (
        "cvar-context-isolation",
        "import contextvars\nimport sniffio\ntoken = sniffio.current_async_library_cvar.set('outer')\ntry:\n    copied = contextvars.copy_context()\n    result = (copied.run(sniffio.current_async_library), sniffio.current_async_library_cvar.get())\nfinally:\n    sniffio.current_async_library_cvar.reset(token)",
        lambda value: value == ["outer", "outer"],
    ),
    (
        "asyncio-nested-task",
        "import asyncio\nimport sniffio\nasync def child():\n    return sniffio.current_async_library()\nasync def main():\n    task = asyncio.create_task(child())\n    return await task\nresult = asyncio.run(main())",
        lambda value: value == "asyncio",
    ),
    (
        "no-runtime-import-side-effect",
        "import sys\nimport sniffio\nresult = 'curio' not in sys.modules",
        is_true,
    ),
    (
        "public-symbols-importable",
        "from sniffio import current_async_library, AsyncLibraryNotFoundError, current_async_library_cvar, thread_local\nresult = all(value is not None for value in (current_async_library, AsyncLibraryNotFoundError, current_async_library_cvar, thread_local))",
        is_true,
    ),
]


def main() -> None:
    leaves: list[dict[str, str]] = []
    for leaf_id, source, predicate in CASES:
        passed, message = expect(source, predicate)
        leaf: dict[str, str] = {"id": leaf_id, "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = message
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
