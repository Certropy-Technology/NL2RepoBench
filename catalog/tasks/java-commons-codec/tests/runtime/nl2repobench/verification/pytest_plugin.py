"""Tiny pytest plugin that writes collection facts as JSON.

This module intentionally depends only on the Python standard library so it can
be copied into a separate verifier image without installing nl2repobench.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

_NODEIDS: list[str] = []
_ERRORS: list[dict[str, str]] = []


def _output_path() -> Path | None:
    value = os.environ.get("NL2REPO_COLLECTION_REPORT")
    return Path(value) if value else None


def _write_report() -> None:
    path = _output_path()
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "collected": len(_NODEIDS),
        "nodeids": _NODEIDS,
        "collection_errors": _ERRORS,
    }
    descriptor, temporary = tempfile.mkstemp(prefix=".collection-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def pytest_sessionstart(session: Any) -> None:
    del session
    _NODEIDS.clear()
    _ERRORS.clear()


def pytest_collection_finish(session: Any) -> None:
    _NODEIDS.clear()
    _NODEIDS.extend(item.nodeid for item in session.items)
    _write_report()


def pytest_collectreport(report: Any) -> None:
    if report.failed:
        _ERRORS.append(
            {
                "nodeid": str(getattr(report, "nodeid", "collection")),
                "message": str(getattr(report, "longrepr", "collection failed")),
            }
        )
        _write_report()


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    del session, exitstatus
    _write_report()
