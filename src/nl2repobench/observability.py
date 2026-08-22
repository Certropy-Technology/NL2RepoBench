"""Versioned, bounded observability records and process execution helpers.

This module owns diagnostic events only. It deliberately does not define or
modify benchmark manifests, task schemas, grading results, or compiler output.
Values remain in memory until a sink emits them; the stderr sink is the
security boundary that applies centralized redaction before serialization.

``run_process`` is an argv-only subprocess boundary. It uses a monotonic
clock for elapsed time, enforces a finite timeout, captures bounded output
without buffering an unbounded child stream in memory, and never invokes a
shell.
"""

from __future__ import annotations

import json
import math
import os
import re
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, BinaryIO, Literal, TypeAlias, cast
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StringConstraints,
    field_validator,
    model_validator,
)

from nl2repobench.domain.models import FailureClass

OBSERVABILITY_SCHEMA_VERSION: Literal["1.0"] = "1.0"
REDACTED = "[REDACTED]"
TRUNCATED = "...[truncated]"
MAX_IDENTIFIER_CHARS = 128
MAX_CONTEXT_BYTES = 16 * 1024
MAX_CONTEXT_DEPTH = 4
MAX_CONTEXT_ITEMS = 32
MAX_CONTEXT_KEY_CHARS = 128
MAX_CONTEXT_STRING_CHARS = 4096
MAX_ARTIFACT_REFS = 16
MAX_ARTIFACT_URI_CHARS = 2048
DEFAULT_PROCESS_TIMEOUT_SEC = 60.0
MAX_PROCESS_TIMEOUT_SEC = 3600.0
DEFAULT_PROCESS_OUTPUT_BYTES = 64 * 1024
MAX_PROCESS_OUTPUT_BYTES = 1024 * 1024

Identifier = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=MAX_IDENTIFIER_CHARS,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._/-]*$",
    ),
]
ErrorCode = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=MAX_IDENTIFIER_CHARS,
        pattern=r"^[a-z][a-z0-9._-]*$",
    ),
]
ArtifactUri = Annotated[str, StringConstraints(min_length=1, max_length=MAX_ARTIFACT_URI_CHARS)]
Digest = Annotated[str, StringConstraints(pattern=r"^sha256:[0-9a-f]{64}$")]
ProcessText = Annotated[str, StringConstraints(max_length=MAX_PROCESS_OUTPUT_BYTES)]
JsonOutput: TypeAlias = (
    None | bool | int | float | str | list["JsonOutput"] | dict[str, "JsonOutput"]
)

_SECRET_FIELD_PARTS = frozenset(
    {
        "authorization",
        "cookie",
        "credential",
        "credentials",
        "passwd",
        "password",
        "secret",
        "signature",
        "token",
    }
)
_SECRET_FIELD_NAMES = frozenset(
    {
        "access_key",
        "api_key",
        "authorization",
        "client_secret",
        "cookie",
        "credentials",
        "password",
        "private_key",
        "refresh_token",
        "secret",
        "session_id",
        "token",
    }
)
_URL_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9+.-]*://[^\s<>'\"]+")
_AUTH_PATTERN = re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]+")
_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|authorization|client[_-]?secret|password|passwd|secret|token)"
    r"(\s*[:=]\s*)([^\s,;&]+)"
)


def _utc_now() -> datetime:
    """Return an aware UTC timestamp for a newly created observation."""

    return datetime.now(UTC)


def _validate_json_structure(value: JsonValue, *, depth: int = 0) -> None:
    """Reject context values that exceed deterministic depth, width, or string bounds."""

    if depth > MAX_CONTEXT_DEPTH:
        raise ValueError(f"context exceeds maximum depth {MAX_CONTEXT_DEPTH}")
    if isinstance(value, dict):
        if len(value) > MAX_CONTEXT_ITEMS:
            raise ValueError(f"context mapping exceeds {MAX_CONTEXT_ITEMS} items")
        for key, item in value.items():
            if len(key) > MAX_CONTEXT_KEY_CHARS:
                raise ValueError(f"context key exceeds {MAX_CONTEXT_KEY_CHARS} characters")
            _validate_json_structure(item, depth=depth + 1)
        return
    if isinstance(value, list):
        if len(value) > MAX_CONTEXT_ITEMS:
            raise ValueError(f"context sequence exceeds {MAX_CONTEXT_ITEMS} items")
        for item in value:
            _validate_json_structure(item, depth=depth + 1)
        return
    if isinstance(value, str) and len(value) > MAX_CONTEXT_STRING_CHARS:
        raise ValueError(f"context string exceeds {MAX_CONTEXT_STRING_CHARS} characters")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("context numbers must be finite")


def _validate_json_document(value: JsonValue, *, label: str) -> None:
    """Reject a JSON value whose encoded diagnostic payload exceeds the byte budget."""

    _validate_json_structure(value)
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if len(encoded) > MAX_CONTEXT_BYTES:
        raise ValueError(f"{label} exceeds {MAX_CONTEXT_BYTES} encoded bytes")


class Outcome(StrEnum):
    """Stable outcomes shared by event, result, and process observations."""

    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class _ObservabilityModel(BaseModel):
    """Strict immutable policy for records owned by this observability module."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ArtifactRefV1(_ObservabilityModel):
    """A bounded diagnostic artifact reference with no inline URL credentials.

    Artifact references may point to local paths or stable URIs. URL userinfo,
    query strings, and fragments are rejected because they commonly carry
    credentials or mutable access signatures. Put descriptive, non-secret URL
    details in event context and let a sink redact them instead.
    """

    schema_version: Literal["1.0"] = OBSERVABILITY_SCHEMA_VERSION
    name: Identifier
    uri: ArtifactUri
    digest: Digest | None = None
    media_type: Annotated[str, StringConstraints(min_length=1, max_length=128)] | None = None

    @field_validator("uri")
    @classmethod
    def validate_safe_uri(cls, value: str) -> str:
        """Reject control characters and credential-bearing or mutable URL components."""

        if any(ord(character) < 32 or ord(character) == 127 for character in value):
            raise ValueError("artifact URI must not contain control characters")
        parsed = urlsplit(value)
        try:
            _ = parsed.port
        except ValueError as exc:
            raise ValueError("artifact URI has an invalid port") from exc
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("artifact URI must not contain credentials")
        if parsed.query:
            raise ValueError("artifact URI must not contain a query string")
        if parsed.fragment:
            raise ValueError("artifact URI must not contain a fragment")
        return value


class _ObservationV1(_ObservabilityModel):
    """Common typed metadata for one operation observation.

    ``duration_ms`` is an elapsed duration, never a wall-clock subtraction.
    Callers constructing records directly own that monotonic-clock invariant;
    ``run_process`` enforces it with ``time.monotonic_ns``.
    """

    schema_version: Literal["1.0"] = OBSERVABILITY_SCHEMA_VERSION
    timestamp: datetime = Field(default_factory=_utc_now)
    component: Identifier
    operation: Identifier
    phase: Identifier
    outcome: Outcome
    task_id: Identifier | None = None
    run_id: Identifier | None = None
    attempt_id: Identifier | None = None
    duration_ms: Annotated[int, Field(ge=0)] | None = None
    error_code: ErrorCode | None = None
    failure_class: FailureClass | None = None
    retryable: bool | None = None
    context: dict[str, JsonValue] = Field(default_factory=dict)
    artifact_refs: Annotated[tuple[ArtifactRefV1, ...], Field(max_length=MAX_ARTIFACT_REFS)] = ()

    @field_validator("timestamp")
    @classmethod
    def normalize_utc_timestamp(cls, value: datetime) -> datetime:
        """Require an aware timestamp and normalize offsets to UTC."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("context")
    @classmethod
    def validate_bounded_context(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        """Enforce the context depth, item, string, and encoded-byte budgets."""

        _validate_json_document(cast(JsonValue, value), label="context")
        return value


class EventV1(_ObservationV1):
    """A versioned diagnostic event emitted at an operation phase boundary."""

    kind: Literal["event"] = "event"


class ResultEnvelopeV1(_ObservationV1):
    """A bounded terminal operation result for diagnostic transport.

    This envelope is observability data, not a benchmark score or verifier
    result. Its result mapping is bounded under the same limits as context so
    it cannot become an unbounded logging channel.
    """

    kind: Literal["result-envelope"] = "result-envelope"
    result: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("result")
    @classmethod
    def validate_bounded_result(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        """Enforce deterministic size and nesting limits on the result mapping."""

        _validate_json_document(cast(JsonValue, value), label="result")
        return value


class ProcessReportV1(_ObservationV1):
    """A bounded subprocess outcome returned by ``run_process``.

    Normal exit status and terminating signal are separate fields. A timeout
    is explicit and normally reports the signal used to kill the isolated
    process group. Captured text is bounded in bytes by ``run_process`` and in
    characters by this model.
    """

    model_config = ConfigDict(str_strip_whitespace=False)
    kind: Literal["process-report"] = "process-report"
    return_code: Annotated[int, Field(ge=0)] | None = None
    signal: Annotated[int, Field(gt=0)] | None = None
    timed_out: bool = False
    stdout: ProcessText = ""
    stderr: ProcessText = ""
    stdout_bytes: Annotated[int, Field(ge=0)] = 0
    stderr_bytes: Annotated[int, Field(ge=0)] = 0
    stdout_truncated: bool = False
    stderr_truncated: bool = False

    @model_validator(mode="after")
    def validate_process_outcome(self) -> ProcessReportV1:
        """Keep timeout, signal, and normal return-code states unambiguous."""

        if self.return_code is not None and self.signal is not None:
            raise ValueError("process report cannot contain both return_code and signal")
        if self.outcome is Outcome.SUCCESS:
            if self.return_code != 0 or self.signal is not None or self.timed_out:
                raise ValueError("successful process report requires return_code=0")
        if self.outcome is Outcome.TIMEOUT:
            if not self.timed_out or self.return_code is not None:
                raise ValueError("timeout process report requires timed_out=true")
        elif self.timed_out:
            raise ValueError("timed_out=true requires outcome=timeout")
        return self


def _is_secret_field(field_name: str) -> bool:
    """Return whether a field name conventionally carries credential material."""

    normalized = re.sub(r"[^a-z0-9]+", "_", field_name.casefold()).strip("_")
    if normalized in _SECRET_FIELD_NAMES:
        return True
    parts = frozenset(part for part in normalized.split("_") if part)
    if {"session", "id"}.issubset(parts):
        return True
    if "private" in parts and "key" in parts:
        return True
    if "api" in parts and "key" in parts:
        return True
    if "access" in parts and ("key" in parts or "token" in parts):
        return True
    return bool(parts & _SECRET_FIELD_PARTS)


def _redact_url(value: str) -> str:
    """Remove URL userinfo and redact values of credential-like query parameters."""

    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError:
        return REDACTED
    if not parsed.scheme or not parsed.netloc:
        return value

    changed = False
    netloc = parsed.netloc
    if parsed.username is not None or parsed.password is not None:
        netloc = netloc.rsplit("@", maxsplit=1)[-1]
        changed = True

    query = parsed.query
    if query:
        pairs = parse_qsl(query, keep_blank_values=True)
        redacted_pairs: list[tuple[str, str]] = []
        for key, item in pairs:
            if _is_secret_field(key) or key.casefold() in {"auth", "sig", "x-amz-signature"}:
                redacted_pairs.append((key, REDACTED))
                changed = True
            else:
                redacted_pairs.append((key, item))
        if changed:
            query = urlencode(redacted_pairs)

    if not changed:
        return value
    return urlunsplit((parsed.scheme, netloc, parsed.path, query, parsed.fragment))


class FieldRedactor:
    """Central field-aware redactor for JSON-compatible diagnostic values.

    Field names identify common credential containers, explicit secret values
    are replaced wherever they occur, and URL userinfo or credential query
    parameters are scrubbed. Recursive values and strings are truncated so a
    sink cannot serialize unbounded context. Redaction is a logging boundary,
    not a general-purpose secret store or taint tracker.
    """

    def __init__(
        self,
        *,
        secret_values: Iterable[str] = (),
        max_string_chars: int = MAX_CONTEXT_STRING_CHARS,
        max_depth: int = MAX_CONTEXT_DEPTH,
        max_items: int = MAX_CONTEXT_ITEMS,
    ) -> None:
        """Configure explicit secrets and deterministic recursive output limits."""

        if max_string_chars < len(TRUNCATED):
            raise ValueError(f"max_string_chars must be at least {len(TRUNCATED)}")
        if max_depth < 1:
            raise ValueError("max_depth must be positive")
        if max_items < 1:
            raise ValueError("max_items must be positive")
        self._secret_values = tuple(
            sorted({value for value in secret_values if value}, key=len, reverse=True)
        )
        self._max_string_chars = max_string_chars
        self._max_depth = max_depth
        self._max_items = max_items

    def _redact_text(self, value: str) -> str:
        """Redact credentials in one string, then enforce the configured length bound."""

        redacted = value
        for secret_value in self._secret_values:
            redacted = redacted.replace(secret_value, REDACTED)
        redacted = _URL_PATTERN.sub(lambda match: _redact_url(match.group(0)), redacted)
        redacted = _AUTH_PATTERN.sub(lambda match: f"{match.group(1)} {REDACTED}", redacted)
        redacted = _ASSIGNMENT_PATTERN.sub(
            lambda match: f"{match.group(1)}{match.group(2)}{REDACTED}", redacted
        )
        if len(redacted) > self._max_string_chars:
            return redacted[: self._max_string_chars - len(TRUNCATED)] + TRUNCATED
        return redacted

    def _redact(self, value: object, *, field_name: str | None, depth: int) -> JsonOutput:
        """Recursively redact one value while preserving a JSON-compatible shape."""

        if field_name is not None and _is_secret_field(field_name) and value is not None:
            return REDACTED
        if value is None or isinstance(value, (bool, int)):
            return value
        if isinstance(value, float):
            return value if math.isfinite(value) else "[NON_FINITE]"
        if isinstance(value, str):
            return self._redact_text(value)
        if depth >= self._max_depth:
            return "[MAX_DEPTH]"
        if isinstance(value, Mapping):
            mapping = cast(Mapping[object, object], value)
            items = sorted(mapping.items(), key=lambda item: str(item[0]))
            result: dict[str, JsonOutput] = {}
            for raw_key, item in items[: self._max_items]:
                key = self._redact_text(str(raw_key))
                result[key] = self._redact(item, field_name=key, depth=depth + 1)
            if len(items) > self._max_items:
                marker = "__truncated_items__"
                while marker in result:
                    marker = f"_{marker}"
                result[marker] = len(items) - self._max_items
            return result
        if isinstance(value, Sequence):
            sequence = cast(Sequence[object], value)
            result_list = [
                self._redact(item, field_name=None, depth=depth + 1)
                for item in sequence[: self._max_items]
            ]
            if len(sequence) > self._max_items:
                result_list.append(f"[{len(sequence) - self._max_items} items truncated]")
            return result_list
        return self._redact_text(str(value))

    def redact(self, value: object) -> JsonOutput:
        """Return a bounded, JSON-compatible, redacted copy of ``value``."""

        return self._redact(value, field_name=None, depth=0)


class EventSink:
    """No-op event sink used when callers do not configure diagnostics.

    The default deliberately performs no I/O and is safe to leave in production
    call paths. Subclasses own serialization and redaction boundaries.
    """

    def emit(self, event: EventV1) -> None:
        """Discard ``event`` without writing to stdout, stderr, or storage."""


class JsonlStderrEventSink(EventSink):
    """Emit one redacted JSON event per line to the current process stderr.

    The stream is intentionally not injectable: every emission resolves
    ``sys.stderr`` at call time and can never be redirected to stdout by sink
    configuration. A lock keeps each JSONL record intact across threads.
    """

    def __init__(self, *, secret_values: Iterable[str] = ()) -> None:
        """Create a stderr sink with optional exact secret values to scrub."""

        self._redactor = FieldRedactor(secret_values=secret_values)
        self._lock = threading.Lock()

    def emit(self, event: EventV1) -> None:
        """Redact and serialize ``event`` as a compact deterministic JSONL record."""

        payload = self._redactor.redact(event.model_dump(mode="json"))
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        with self._lock:
            sys.stderr.write(encoded + "\n")
            sys.stderr.flush()


@dataclass
class _BoundedCapture:
    """Drain one child stream while retaining only its configured byte prefix."""

    limit: int
    data: bytearray = field(default_factory=bytearray)
    total_bytes: int = 0

    def consume(self, chunk: bytes) -> None:
        """Count every byte and retain at most ``limit`` bytes."""

        self.total_bytes += len(chunk)
        remaining = self.limit - len(self.data)
        if remaining > 0:
            self.data.extend(chunk[:remaining])

    @property
    def truncated(self) -> bool:
        """Return whether bytes were discarded after the retained prefix."""

        return self.total_bytes > self.limit

    def text(self) -> str:
        """Decode retained bytes as UTF-8 with deterministic replacement."""

        return bytes(self.data).decode("utf-8", errors="replace")


def _drain_stream(stream: BinaryIO, capture: _BoundedCapture) -> None:
    """Drain a pipe to EOF so verbose children cannot block on a full pipe."""

    try:
        while chunk := stream.read(8192):
            capture.consume(chunk)
    finally:
        stream.close()


def _kill_process_group(process: subprocess.Popen[bytes]) -> None:
    """Kill the isolated process group, falling back to the direct child."""

    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        return


def _elapsed_ms(start_ns: int) -> int:
    """Return non-negative elapsed whole milliseconds from a monotonic start."""

    return max(0, (time.monotonic_ns() - start_ns) // 1_000_000)


def _exit_status(returncode: int) -> tuple[int | None, int | None]:
    """Split ``Popen.returncode`` into a normal code or POSIX signal number."""

    if returncode < 0:
        return None, -returncode
    return returncode, None


def run_process(
    command: Sequence[str],
    *,
    timeout_sec: float = DEFAULT_PROCESS_TIMEOUT_SEC,
    max_output_bytes: int = DEFAULT_PROCESS_OUTPUT_BYTES,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
    component: Identifier = "process",
    operation: Identifier = "execute",
    phase: Identifier = "run",
    task_id: Identifier | None = None,
    run_id: Identifier | None = None,
    attempt_id: Identifier | None = None,
    context: Mapping[str, JsonValue] | None = None,
    artifact_refs: Sequence[ArtifactRefV1] = (),
    failure_class: FailureClass | None = None,
    retryable: bool | None = None,
) -> ProcessReportV1:
    """Run an argv command with bounded output and a hard elapsed timeout.

    ``command`` must be a non-empty sequence of argument strings. It is passed
    directly to ``subprocess.Popen`` with ``shell=False``; shell strings and
    interpolation are intentionally unsupported. stdout and stderr are
    drained concurrently, only their leading ``max_output_bytes`` are retained,
    and the whole process group is killed after ``timeout_sec``. The returned
    duration is measured exclusively with ``time.monotonic_ns``.

    This helper supervises process lifetime but does not sandbox filesystem,
    network, user, or environment access. Callers retain ownership of those
    security boundaries and of domain-specific failure classification.
    """

    if isinstance(command, (str, bytes)) or not command:
        raise ValueError("command must be a non-empty argv sequence")
    argv = tuple(command)
    if any(
        not isinstance(argument, str) or not argument or "\x00" in argument for argument in argv
    ):
        raise ValueError("command arguments must be non-empty strings without NUL bytes")
    if not math.isfinite(timeout_sec) or not 0 < timeout_sec <= MAX_PROCESS_TIMEOUT_SEC:
        raise ValueError(f"timeout_sec must be within (0, {MAX_PROCESS_TIMEOUT_SEC}]")
    if not 0 < max_output_bytes <= MAX_PROCESS_OUTPUT_BYTES:
        raise ValueError(f"max_output_bytes must be within [1, {MAX_PROCESS_OUTPUT_BYTES}]")

    started_at = _utc_now()
    start_ns = time.monotonic_ns()
    report_context = dict(context or {})
    report_artifacts = tuple(artifact_refs)
    try:
        process = subprocess.Popen(
            argv,
            cwd=cwd,
            env=dict(env) if env is not None else None,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=os.name == "posix",
            shell=False,
        )
    except OSError as exc:
        message = str(exc).encode("utf-8", errors="replace")
        captured = message[:max_output_bytes]
        return ProcessReportV1(
            timestamp=started_at,
            component=component,
            operation=operation,
            phase=phase,
            outcome=Outcome.FAILURE,
            task_id=task_id,
            run_id=run_id,
            attempt_id=attempt_id,
            duration_ms=_elapsed_ms(start_ns),
            error_code="process.spawn-failed",
            failure_class=failure_class,
            retryable=retryable,
            context=report_context,
            artifact_refs=report_artifacts,
            stderr=captured.decode("utf-8", errors="replace"),
            stderr_bytes=len(message),
            stderr_truncated=len(message) > max_output_bytes,
        )

    if process.stdout is None or process.stderr is None:
        _kill_process_group(process)
        process.wait()
        raise RuntimeError("subprocess capture pipes were not created")

    stdout_capture = _BoundedCapture(max_output_bytes)
    stderr_capture = _BoundedCapture(max_output_bytes)
    stdout_thread = threading.Thread(
        target=_drain_stream,
        args=(process.stdout, stdout_capture),
        name="nl2repo-stdout-capture",
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_drain_stream,
        args=(process.stderr, stderr_capture),
        name="nl2repo-stderr-capture",
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()

    timed_out = False
    try:
        process.wait(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_process_group(process)
        process.wait()
    except BaseException:
        _kill_process_group(process)
        process.wait()
        raise
    finally:
        stdout_thread.join()
        stderr_thread.join()

    if process.returncode is None:
        raise RuntimeError("subprocess did not report a return code")
    return_code, signal_number = _exit_status(process.returncode)
    if timed_out:
        outcome = Outcome.TIMEOUT
        error_code: ErrorCode | None = "process.timeout"
        return_code = None
    elif signal_number is not None:
        outcome = Outcome.FAILURE
        error_code = "process.signal"
    elif return_code == 0:
        outcome = Outcome.SUCCESS
        error_code = None
    else:
        outcome = Outcome.FAILURE
        error_code = "process.nonzero-exit"

    return ProcessReportV1(
        timestamp=started_at,
        component=component,
        operation=operation,
        phase=phase,
        outcome=outcome,
        task_id=task_id,
        run_id=run_id,
        attempt_id=attempt_id,
        duration_ms=_elapsed_ms(start_ns),
        error_code=error_code,
        failure_class=failure_class,
        retryable=retryable,
        context=report_context,
        artifact_refs=report_artifacts,
        return_code=return_code,
        signal=signal_number,
        timed_out=timed_out,
        stdout=stdout_capture.text(),
        stderr=stderr_capture.text(),
        stdout_bytes=stdout_capture.total_bytes,
        stderr_bytes=stderr_capture.total_bytes,
        stdout_truncated=stdout_capture.truncated,
        stderr_truncated=stderr_capture.truncated,
    )


__all__ = [
    "ArtifactRefV1",
    "EventSink",
    "EventV1",
    "FieldRedactor",
    "JsonlStderrEventSink",
    "OBSERVABILITY_SCHEMA_VERSION",
    "Outcome",
    "ProcessReportV1",
    "ResultEnvelopeV1",
    "run_process",
]
