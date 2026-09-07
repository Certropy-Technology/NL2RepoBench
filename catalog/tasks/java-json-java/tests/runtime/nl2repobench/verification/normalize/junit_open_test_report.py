"""Normalize bounded JUnit Open Test Reporting XML into leaf reports."""

# ruff: noqa: E501

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import BinaryIO
from xml.etree.ElementTree import Element

from defusedxml import ElementTree

from nl2repobench.verification.leaf_report import (
    LeafCase,
    LeafCollectionError,
    LeafReport,
    ReportNormalizationError,
)
from nl2repobench.verification.taxonomy import VerificationReason

EVENT_NS = "https://schemas.opentest4j.org/reporting/events/0.1.0"
CORE_NS = "https://schemas.opentest4j.org/reporting/core/0.1.0"
JUNIT_NS = "https://schemas.junit.org/open-test-reporting"
MAX_REPORT_BYTES = 8 * 1024 * 1024
MAX_NODES = 100_000
MAX_DEPTH = 128
MAX_ATTRIBUTES = 32
MAX_ATTRIBUTE_CHARS = 4096
MAX_TEXT_CHARS = 4096
MAX_ID_CHARS = 512
MAX_DETAILS_CHARS = 4096


@dataclass(frozen=True)
class _Started:
    event_id: str
    parent_id: str | None
    unique_id: str
    name: str
    item_type: str
    started_at: datetime


def _error(message: str) -> ReportNormalizationError:
    return ReportNormalizationError(VerificationReason.REPORT_MALFORMED, message)


def _qname(tag: str) -> tuple[str, str]:
    if not tag.startswith("{") or "}" not in tag:
        raise _error("Open Test XML tag has no namespace")
    namespace, local = tag[1:].split("}", 1)
    return namespace, local


def _timestamp(value: str, description: str) -> datetime:
    if len(value) > MAX_ATTRIBUTE_CHARS:
        raise _error(f"{description} exceeds the size limit")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _error(f"{description} is not RFC3339") from exc


def _metadata(element: Element) -> dict[str, str]:
    result: dict[str, str] = {}
    for child in element.iter():
        namespace, local = _qname(child.tag)
        if namespace != CORE_NS or local != "entry":
            continue
        key = child.attrib.get("key")
        if not key or len(key) > MAX_ATTRIBUTE_CHARS or key in result:
            raise _error("Open Test metadata key is missing, duplicated, or oversized")
        values = [
            (nested.text or "").strip()
            for nested in list(child)
            if _qname(nested.tag) == (CORE_NS, "string")
        ]
        if not values:
            direct = (child.text or "").strip()
            values = [direct] if direct else []
        if len(values) != 1 or len(values[0]) > MAX_TEXT_CHARS:
            raise _error("Open Test metadata value is missing or oversized")
        result[key] = values[0]
    return result


def _check_structure(data: bytes) -> Element:
    if len(data) > MAX_REPORT_BYTES:
        raise _error("Open Test report exceeds the size limit")
    if not data.strip():
        raise ReportNormalizationError(
            VerificationReason.REPORT_MISSING, "Open Test report is empty"
        )
    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise _error("Open Test report DTD/entities are forbidden")
    allowed = {
        EVENT_NS: {"events", "started", "finished"},
        JUNIT_NS: {"metadata", "result", "throwable"},
        CORE_NS: {"entry", "string"},
    }
    attributes = {
        (EVENT_NS, "events"): set(),
        (EVENT_NS, "started"): {"id", "name", "time", "parentId", "uniqueId", "type"},
        (EVENT_NS, "finished"): {"id", "time"},
        (JUNIT_NS, "metadata"): set(),
        (JUNIT_NS, "result"): {"status"},
        (JUNIT_NS, "throwable"): set(),
        (CORE_NS, "entry"): {"key"},
        (CORE_NS, "string"): set(),
    }
    depth = 0
    nodes = 0
    root: Element | None = None
    try:
        stream: BinaryIO = BytesIO(data)
        for event, element in ElementTree.iterparse(stream, events=("start", "end")):
            if event == "start":
                depth += 1
                nodes += 1
                if depth > MAX_DEPTH or nodes > MAX_NODES:
                    raise _error("Open Test report exceeds structural bounds")
                namespace, local = _qname(element.tag)
                if local not in allowed.get(namespace, set()):
                    raise _error(f"unsupported Open Test element: {namespace}#{local}")
                if len(element.attrib) > MAX_ATTRIBUTES or any(
                    len(name) > MAX_ATTRIBUTE_CHARS or len(value) > MAX_ATTRIBUTE_CHARS
                    for name, value in element.attrib.items()
                ):
                    raise _error("Open Test report attributes exceed bounds")
                if any(name.startswith("{") for name in element.attrib):
                    raise _error("namespaced Open Test attributes are unsupported")
                if not set(element.attrib).issubset(attributes[(namespace, local)]):
                    raise _error(f"unsupported attributes on Open Test element {local}")
                if root is None:
                    root = element
            else:
                if element.text is not None and len(element.text) > MAX_TEXT_CHARS:
                    raise _error("Open Test report text exceeds the size limit")
                depth -= 1
    except ReportNormalizationError:
        raise
    except Exception as exc:
        raise _error(f"cannot parse Open Test XML: {exc}") from exc
    if root is None or _qname(root.tag) != (EVENT_NS, "events"):
        raise _error("Open Test report root is invalid")
    if root.attrib:
        raise _error("Open Test report root has attributes")
    return root


def normalize_junit_open_test_report(
    *,
    report_data: bytes | None,
    frozen_total: int,
    trusted_runner_exit_code: int | None,
) -> LeafReport:
    """Convert trusted JUnit events to common leaves without scoring them."""

    if frozen_total <= 0:
        raise ValueError("frozen_total must be positive")
    if report_data is None:
        raise ReportNormalizationError(
            VerificationReason.REPORT_MISSING, "Open Test report is missing"
        )
    root = _check_structure(report_data)
    started: dict[str, _Started] = {}
    finished: set[str] = set()
    leaves: list[LeafCase] = []
    errors: list[LeafCollectionError] = []
    status_map = {
        "SUCCESSFUL": "passed",
        "SKIPPED": "skipped",
        "ABORTED": "skipped",
        "FAILED": "failed",
    }
    for event in list(root):
        namespace, local = _qname(event.tag)
        if namespace != EVENT_NS:
            raise _error("Open Test root child is not an event")
        if local == "started":
            event_id = event.attrib.get("id", "")
            name = event.attrib.get("name", "")
            metadata = _metadata(event)
            parent_id = event.attrib.get("parentId") or metadata.get("parentId")
            unique_id = event.attrib.get("uniqueId") or metadata.get("uniqueId") or ""
            item_type = event.attrib.get("type") or metadata.get("type") or ""
            if (
                not event_id
                or len(event_id) > MAX_ID_CHARS
                or event_id in started
                or not name
                or len(name) > MAX_ID_CHARS
                or not unique_id
                or len(unique_id) > MAX_ID_CHARS
                or item_type not in {"TEST", "CONTAINER", "CONTAINER_AND_TEST"}
            ):
                raise _error("Open Test started event is invalid")
            if parent_id is not None and (parent_id == event_id or parent_id not in started):
                raise _error("Open Test parent hierarchy is invalid")
            if parent_id is not None and parent_id in finished:
                raise _error("Open Test child starts after its parent finished")
            if any(_qname(child.tag) != (JUNIT_NS, "metadata") for child in list(event)):
                raise _error("Open Test started event content is invalid")
            started[event_id] = _Started(
                event_id=event_id,
                parent_id=parent_id,
                unique_id=unique_id,
                name=name,
                item_type=item_type,
                started_at=_timestamp(event.attrib.get("time", ""), "started time"),
            )
            continue
        event_id = event.attrib.get("id", "")
        if event_id not in started or event_id in finished:
            raise _error("Open Test finish ID is missing or duplicated")
        if len(list(event)) != 1:
            raise _error("Open Test finished event content is invalid")
        result_nodes = [child for child in list(event) if _qname(child.tag) == (JUNIT_NS, "result")]
        if len(result_nodes) != 1 or set(result_nodes[0].attrib) != {"status"}:
            raise _error("Open Test finish requires one result")
        status = result_nodes[0].attrib["status"]
        if status not in status_map:
            raise _error("Open Test result status is invalid")
        record = started[event_id]
        ended = _timestamp(event.attrib.get("time", ""), "finished time")
        duration_ms = (ended - record.started_at).total_seconds() * 1000.0
        if duration_ms < 0:
            raise _error("Open Test duration is negative")
        details_parts = [
            (node.text or "").strip()
            for node in result_nodes[0].iter()
            if _qname(node.tag) == (JUNIT_NS, "throwable") and (node.text or "").strip()
        ]
        details = "\n".join(details_parts) or None
        if details is not None and len(details) > MAX_DETAILS_CHARS:
            raise _error("Open Test details exceed the size limit")
        if record.item_type == "CONTAINER":
            if status in {"FAILED", "ABORTED"}:
                errors.append(
                    LeafCollectionError(
                        leaf_id=record.unique_id,
                        message=details or f"container {record.name} ended with {status}",
                    )
                )
        else:
            leaves.append(
                LeafCase(
                    leaf_id=record.unique_id,
                    status=status_map[status],  # type: ignore[arg-type]
                    display_name=record.name,
                    duration_ms=duration_ms,
                    details=details,
                )
            )
        finished.add(event_id)
    if set(started) != finished:
        raise _error("Open Test report has unfinished events")
    if len(leaves) != frozen_total:
        raise ReportNormalizationError(
            VerificationReason.COLLECTION_MISMATCH,
            f"collected {len(leaves)}, expected {frozen_total}",
        )
    expected_exit = 1 if any(leaf.status == "failed" for leaf in leaves) or errors else 0
    if trusted_runner_exit_code is not None and trusted_runner_exit_code != expected_exit:
        raise ReportNormalizationError(
            VerificationReason.REPORT_EXIT_MISMATCH,
            "runner exited "
            f"{trusted_runner_exit_code}, but Open Test leaves require {expected_exit}",
        )
    try:
        return LeafReport(
            framework="junit-platform",
            report_format="junit-open-test-report-xml-v1",
            collected=len(leaves),
            leaves=tuple(leaves),
            collection_errors=tuple(errors),
            trusted_runner_exit_code=trusted_runner_exit_code,
            frozen_total=frozen_total,
        )
    except ValueError as exc:
        reason = (
            VerificationReason.DUPLICATE_LEAF_ID
            if "IDs must be unique" in str(exc)
            else VerificationReason.REPORT_MALFORMED
        )
        raise ReportNormalizationError(reason, str(exc)) from exc


__all__ = [
    "CORE_NS",
    "EVENT_NS",
    "JUNIT_NS",
    "MAX_REPORT_BYTES",
    "normalize_junit_open_test_report",
]
