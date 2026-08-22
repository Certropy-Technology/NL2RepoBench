"""Focused contract tests for bounded observability records and process reports."""

from __future__ import annotations

import json
import os
import signal
import sys
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import ValidationError

from nl2repobench.domain.models import FailureClass
from nl2repobench.observability import (
    MAX_ARTIFACT_REFS,
    MAX_CONTEXT_ITEMS,
    MAX_CONTEXT_STRING_CHARS,
    Event,
    EventSink,
    FieldRedactor,
    JsonlStderrEventSink,
    ObservationArtifact,
    Outcome,
    ResultEnvelope,
    run_process,
)

FIXED_TIMESTAMP = datetime(2025, 1, 2, 3, 4, 5, 678901, tzinfo=UTC)


def _event(**overrides: object) -> Event:
    """Build a deterministic event while allowing one test to replace fields."""

    values: dict[str, object] = {
        "timestamp": FIXED_TIMESTAMP,
        "component": "compiler",
        "operation": "compile-task",
        "phase": "materialize",
        "outcome": Outcome.SUCCESS,
    }
    values.update(overrides)
    return Event.model_validate(values)


def test_event_and_result_envelope_have_deterministic_serialization_shape() -> None:
    """Injected timestamps make the complete JSON shape reproducible."""

    artifact = ObservationArtifact(
        name="compiler-log",
        uri="artifact://public/sha256:" + "a" * 64,
        digest="sha256:" + "a" * 64,
        media_type="application/jsonl",
    )
    event = _event(
        task_id="task-1",
        run_id="run-2",
        attempt_id="attempt-3",
        duration_ms=17,
        error_code="compiler.partial-result",
        failure_class=FailureClass.VERIFIER,
        retryable=False,
        context={"count": 2, "valid": True},
        artifact_refs=(artifact,),
    )

    assert event.model_dump(mode="json") == {
        "schema_version": "1.0",
        "timestamp": "2025-01-02T03:04:05.678901Z",
        "component": "compiler",
        "operation": "compile-task",
        "phase": "materialize",
        "outcome": "success",
        "task_id": "task-1",
        "run_id": "run-2",
        "attempt_id": "attempt-3",
        "duration_ms": 17,
        "error_code": "compiler.partial-result",
        "failure_class": "verifier",
        "retryable": False,
        "context": {"count": 2, "valid": True},
        "artifact_refs": [
            {
                "schema_version": "1.0",
                "name": "compiler-log",
                "uri": "artifact://public/sha256:" + "a" * 64,
                "digest": "sha256:" + "a" * 64,
                "media_type": "application/jsonl",
            }
        ],
        "kind": "event",
    }

    envelope = ResultEnvelope(
        timestamp=FIXED_TIMESTAMP,
        component="compiler",
        operation="compile-task",
        phase="complete",
        outcome=Outcome.SUCCESS,
        duration_ms=18,
        result={"manifest_count": 1},
    )
    assert envelope.model_dump(mode="json") == {
        "schema_version": "1.0",
        "timestamp": "2025-01-02T03:04:05.678901Z",
        "component": "compiler",
        "operation": "compile-task",
        "phase": "complete",
        "outcome": "success",
        "task_id": None,
        "run_id": None,
        "attempt_id": None,
        "duration_ms": 18,
        "error_code": None,
        "failure_class": None,
        "retryable": None,
        "context": {},
        "artifact_refs": [],
        "kind": "result-envelope",
        "result": {"manifest_count": 1},
    }


def test_timestamp_must_be_aware_and_is_normalized_to_utc() -> None:
    """Wall-clock timestamps are unambiguous even when callers inject an offset."""

    with pytest.raises(ValidationError, match="timezone-aware"):
        _event(timestamp=datetime(2025, 1, 2, 3, 4, 5))

    offset = timezone(timedelta(hours=2))
    event = _event(timestamp=datetime(2025, 1, 2, 5, 4, 5, tzinfo=offset))
    assert event.timestamp == datetime(2025, 1, 2, 3, 4, 5, tzinfo=UTC)


def test_field_redactor_removes_named_and_explicit_secrets() -> None:
    """Credential fields and known secret bytes are redacted recursively."""

    payload = FieldRedactor(secret_values=("literal-secret",)).redact(
        {
            "api_key": "field-secret",
            "message": "Bearer abc.def and literal-secret",
            "nested": {"password": "another-secret", "safe": 3},
        }
    )

    assert payload == {
        "api_key": "[REDACTED]",
        "message": "Bearer [REDACTED] and [REDACTED]",
        "nested": {"password": "[REDACTED]", "safe": 3},
    }


def test_artifact_urls_reject_credentials_queries_and_fragments() -> None:
    """Persistent artifact references cannot contain mutable access material."""

    unsafe = (
        "https://user:password@example.test/report.json",
        "https://example.test/report.json?token=secret",
        "https://example.test/report.json#signed-fragment",
    )
    for uri in unsafe:
        with pytest.raises(ValidationError, match="artifact URI must not contain"):
            ObservationArtifact(name="report", uri=uri)


def test_redactor_sanitizes_url_userinfo_and_secret_query_values() -> None:
    """Transient context URLs retain useful routing fields without credentials."""

    payload = FieldRedactor().redact(
        {"endpoint": ("https://alice:password@example.test/report?token=secret&mode=read")}
    )
    assert isinstance(payload, dict)
    endpoint = payload["endpoint"]
    assert isinstance(endpoint, str)
    parsed = urlsplit(endpoint)
    assert parsed.username is None
    assert parsed.password is None
    assert parsed.hostname == "example.test"
    assert parse_qs(parsed.query) == {"token": ["[REDACTED]"], "mode": ["read"]}
    assert "password" not in endpoint
    assert "secret" not in endpoint


def test_context_artifact_and_redacted_string_bounds() -> None:
    """Model and sink-facing bounds reject or truncate oversized diagnostics."""

    with pytest.raises(ValidationError, match="context string exceeds"):
        _event(context={"message": "x" * (MAX_CONTEXT_STRING_CHARS + 1)})
    with pytest.raises(ValidationError, match="context mapping exceeds"):
        _event(context={f"key-{index}": index for index in range(MAX_CONTEXT_ITEMS + 1)})

    artifact = ObservationArtifact(name="log", uri="/logs/run.jsonl")
    with pytest.raises(ValidationError, match="at most"):
        _event(artifact_refs=(artifact,) * (MAX_ARTIFACT_REFS + 1))

    redacted = FieldRedactor(max_string_chars=24).redact("x" * 100)
    assert isinstance(redacted, str)
    assert len(redacted) == 24
    assert redacted.endswith("...[truncated]")


def test_sinks_do_not_pollute_stdout_and_jsonl_is_redacted(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Both sinks preserve stdout while the JSONL sink writes one safe stderr line."""

    event = _event(
        context={
            "token": "field-secret",
            "message": "configured-secret",
            "url": "https://user:pw@example.test/path?sig=query-secret",
        }
    )
    EventSink().emit(event)
    assert capsys.readouterr() == ("", "")

    JsonlStderrEventSink(secret_values=("configured-secret",)).emit(event)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.count("\n") == 1
    payload = json.loads(captured.err)
    assert payload["context"]["token"] == "[REDACTED]"
    assert payload["context"]["message"] == "[REDACTED]"
    assert "user:pw" not in payload["context"]["url"]
    assert "query-secret" not in payload["context"]["url"]


def test_run_process_reports_success_without_output_pollution(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A successful child is captured and represented with a normal return code."""

    report = run_process(
        [
            sys.executable,
            "-c",
            "import sys; print('child-out'); print('child-err', file=sys.stderr)",
        ],
        timeout_sec=2,
        component="tests",
        operation="success",
        task_id="task-1",
        run_id="run-1",
        attempt_id="attempt-1",
    )

    assert report.outcome is Outcome.SUCCESS
    assert report.return_code == 0
    assert report.signal is None
    assert report.timed_out is False
    assert report.stdout == "child-out\n"
    assert report.stderr == "child-err\n"
    assert report.duration_ms is not None and report.duration_ms >= 0
    assert report.timestamp.utcoffset() == timedelta(0)
    assert capsys.readouterr() == ("", "")


def test_run_process_reports_nonzero_failure() -> None:
    """A normal nonzero exit remains distinct from a signal or timeout."""

    report = run_process(
        [sys.executable, "-c", "import sys; print('failed', file=sys.stderr); sys.exit(7)"],
        timeout_sec=2,
        operation="failure",
    )

    assert report.outcome is Outcome.FAILURE
    assert report.return_code == 7
    assert report.signal is None
    assert report.error_code == "process.nonzero-exit"
    assert report.stderr == "failed\n"


def test_run_process_reports_signal() -> None:
    """Signal termination is represented separately from a normal return code."""

    report = run_process(
        [
            sys.executable,
            "-c",
            "import os, signal; os.kill(os.getpid(), signal.SIGTERM)",
        ],
        timeout_sec=2,
        operation="signal",
    )

    assert report.outcome is Outcome.FAILURE
    assert report.return_code is None
    assert report.signal == signal.SIGTERM
    assert report.error_code == "process.signal"


def test_run_process_kills_group_on_timeout() -> None:
    """Elapsed timeout returns promptly with an explicit timeout state."""

    report = run_process(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        timeout_sec=0.05,
        operation="timeout",
    )

    assert report.outcome is Outcome.TIMEOUT
    assert report.return_code is None
    assert report.signal == signal.SIGKILL
    assert report.timed_out is True
    assert report.error_code == "process.timeout"
    assert report.duration_ms is not None and 1 <= report.duration_ms < 2000


def test_run_process_truncates_both_streams_by_bytes() -> None:
    """Verbose children are drained fully while only bounded prefixes are retained."""

    report = run_process(
        [
            sys.executable,
            "-c",
            "import os; os.write(1, b'o' * 80); os.write(2, b'e' * 70)",
        ],
        timeout_sec=2,
        max_output_bytes=32,
        operation="bounded-output",
    )

    assert report.stdout == "o" * 32
    assert report.stderr == "e" * 32
    assert report.stdout_bytes == 80
    assert report.stderr_bytes == 70
    assert report.stdout_truncated is True
    assert report.stderr_truncated is True


def test_run_process_reports_spawn_failure_and_rejects_shell_strings(
    tmp_path: Path,
) -> None:
    """Spawn errors are structured and a command string cannot opt into shell parsing."""

    report = run_process(
        [os.fspath(tmp_path) + "/missing-executable"],
        timeout_sec=2,
        max_output_bytes=16,
        operation="spawn",
        failure_class=FailureClass.INFRASTRUCTURE,
        retryable=False,
    )
    assert report.outcome is Outcome.FAILURE
    assert report.return_code is None
    assert report.signal is None
    assert report.error_code == "process.spawn-failed"
    assert report.failure_class is FailureClass.INFRASTRUCTURE
    assert report.stderr_bytes > 0
    assert len(report.stderr.encode()) <= 16

    with pytest.raises(ValueError, match="argv sequence"):
        run_process("printf unsafe | sh", timeout_sec=2)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("timeout_sec", "max_output_bytes"),
    [(0.0, 1), (float("inf"), 1), (1.0, 0)],
)
def test_run_process_rejects_unbounded_configuration(
    timeout_sec: float, max_output_bytes: int
) -> None:
    """Timeout and retained-output limits must be finite positive bounds."""

    with pytest.raises(ValueError):
        run_process(
            [sys.executable, "-c", "pass"],
            timeout_sec=timeout_sec,
            max_output_bytes=max_output_bytes,
        )
