"""Normalize JUnit Platform Open Test Reporting 0.1.0 events into canonical leaves."""

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
JAVA_NS = "https://schemas.opentest4j.org/reporting/java/0.1.0"
JUNIT_NS = "https://schemas.junit.org/open-test-reporting"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
MAX_REPORT_BYTES = 8 * 1024 * 1024
MAX_NODES = 100_000
MAX_DEPTH = 128
MAX_ATTRIBUTES = 32
MAX_ATTRIBUTE_CHARS = 4096
MAX_TEXT_CHARS = 4096
MAX_ID_CHARS = 512
MAX_DETAILS_CHARS = 4096


@dataclass(frozen=True, slots=True)
class _Started:
    event_id: str
    parent_id: str | None
    unique_id: str
    name: str
    item_type: str
    time: datetime


def _fail(reason: VerificationReason, message: str) -> ReportNormalizationError:
    return ReportNormalizationError(reason, message)


def _qname(tag: str) -> tuple[str, str]:
    if not tag.startswith("{") or "}" not in tag:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test XML tag has no namespace")
    namespace, local = tag[1:].split("}", 1)
    return namespace, local


def _timestamp(value: str, description: str) -> datetime:
    if not value or len(value) > MAX_ATTRIBUTE_CHARS:
        raise _fail(
            VerificationReason.REPORT_MALFORMED,
            f"{description} is missing or exceeds the size limit",
        )
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _fail(VerificationReason.REPORT_MALFORMED, f"{description} is not RFC3339") from exc


def _single_text(parent: Element, qname: tuple[str, str], description: str) -> str:
    matches = [child for child in list(parent) if _qname(child.tag) == qname]
    if len(matches) != 1 or matches[0].attrib or list(matches[0]):
        raise _fail(
            VerificationReason.REPORT_MALFORMED,
            f"Open Test metadata requires one scalar {description}",
        )
    value = (matches[0].text or "").strip()
    if not value or len(value) > MAX_TEXT_CHARS:
        raise _fail(
            VerificationReason.REPORT_MALFORMED,
            f"Open Test metadata {description} is empty or oversized",
        )
    return value


def _metadata(element: Element) -> tuple[str, str]:
    metadata_nodes = [
        child for child in list(element) if _qname(child.tag) == (CORE_NS, "metadata")
    ]
    if len(metadata_nodes) != 1 or metadata_nodes[0].attrib:
        raise _fail(
            VerificationReason.REPORT_MALFORMED,
            "Open Test started event requires one core metadata element",
        )
    metadata = metadata_nodes[0]
    allowed = {
        (CORE_NS, "tags"),
        (JUNIT_NS, "uniqueId"),
        (JUNIT_NS, "legacyReportingName"),
        (JUNIT_NS, "type"),
    }
    if any(_qname(child.tag) not in allowed for child in list(metadata)):
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test metadata is invalid")
    tags = [child for child in list(metadata) if _qname(child.tag) == (CORE_NS, "tags")]
    if len(tags) > 1:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test tags are duplicated")
    if tags:
        if tags[0].attrib or any(
            _qname(child.tag) != (CORE_NS, "tag") or child.attrib or list(child)
            for child in list(tags[0])
        ):
            raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test tags are invalid")
    unique_id = _single_text(metadata, (JUNIT_NS, "uniqueId"), "junit:uniqueId")
    _single_text(metadata, (JUNIT_NS, "legacyReportingName"), "junit:legacyReportingName")
    item_type = _single_text(metadata, (JUNIT_NS, "type"), "junit:type")
    if len(unique_id) > MAX_ID_CHARS or item_type not in {
        "TEST",
        "CONTAINER",
        "CONTAINER_AND_TEST",
    }:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test JUnit metadata is invalid")
    return unique_id, item_type


def _validate_file_position(element: Element) -> None:
    if _qname(element.tag) != (CORE_NS, "filePosition") or list(element):
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test file position is invalid")
    if not set(element.attrib).issubset({"line", "column"}) or "line" not in element.attrib:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test file position is invalid")
    try:
        line = int(element.attrib["line"])
        column = int(element.attrib["column"]) if "column" in element.attrib else None
    except ValueError as exc:
        raise _fail(
            VerificationReason.REPORT_MALFORMED, "Open Test file position is invalid"
        ) from exc
    if line < 0 or (column is not None and column < 0):
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test file position is negative")


def _validate_sources(element: Element) -> None:
    source_nodes = [
        child for child in list(element) if _qname(child.tag) == (CORE_NS, "sources")
    ]
    if len(source_nodes) > 1:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test sources are duplicated")
    if not source_nodes:
        return
    sources = source_nodes[0]
    if sources.attrib:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test sources have attributes")
    allowed_attributes = {
        (CORE_NS, "directorySource"): {"path"},
        (CORE_NS, "fileSource"): {"path"},
        (CORE_NS, "uriSource"): {"uri"},
        (JAVA_NS, "classSource"): {"className"},
        (JAVA_NS, "methodSource"): {
            "className",
            "methodName",
            "methodParameterTypes",
        },
        (JAVA_NS, "classpathResourceSource"): {"resourceName"},
        (JAVA_NS, "packageSource"): {"name"},
    }
    required_attributes = {
        (CORE_NS, "directorySource"): {"path"},
        (CORE_NS, "fileSource"): {"path"},
        (CORE_NS, "uriSource"): {"uri"},
        (JAVA_NS, "classSource"): {"className"},
        (JAVA_NS, "methodSource"): {"className", "methodName"},
        (JAVA_NS, "classpathResourceSource"): {"resourceName"},
        (JAVA_NS, "packageSource"): {"name"},
    }
    position_sources = {
        (CORE_NS, "fileSource"),
        (JAVA_NS, "classSource"),
        (JAVA_NS, "classpathResourceSource"),
    }
    for source in list(sources):
        name = _qname(source.tag)
        if name not in allowed_attributes or not set(source.attrib).issubset(
            allowed_attributes[name]
        ) or not required_attributes[name].issubset(source.attrib):
            raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test source is invalid")
        required = required_attributes[name]
        if any(
            not value or len(value) > MAX_ATTRIBUTE_CHARS
            for key, value in source.attrib.items()
            if key in required
        ):
            raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test source is invalid")
        children = list(source)
        if name == (CORE_NS, "uriSource"):
            if list(source):
                raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test URI source is invalid")
        elif name in position_sources:
            if len(children) > 1:
                raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test source is invalid")
            if children:
                _validate_file_position(children[0])
        elif children:
            raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test source is invalid")


def _validate_attachments(element: Element) -> None:
    attachment_nodes = [
        child for child in list(element) if _qname(child.tag) == (CORE_NS, "attachments")
    ]
    if len(attachment_nodes) > 1:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test attachments are duplicated")
    if not attachment_nodes:
        return
    attachments = attachment_nodes[0]
    if attachments.attrib:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test attachments are invalid")
    for data in list(attachments):
        if _qname(data.tag) != (CORE_NS, "data") or set(data.attrib) != {"time"}:
            raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test attachment data is invalid")
        _timestamp(data.attrib["time"], "attachment time")
        for entry in list(data):
            if (
                _qname(entry.tag) != (CORE_NS, "entry")
                or set(entry.attrib) != {"key"}
                or not entry.attrib["key"]
                or len(entry.attrib["key"]) > MAX_ATTRIBUTE_CHARS
                or list(entry)
            ):
                raise _fail(
                    VerificationReason.REPORT_MALFORMED,
                    "Open Test attachment entry is invalid",
                )


def _validate_infrastructure(element: Element) -> None:
    if element.attrib:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test infrastructure is invalid")
    allowed = {
        (CORE_NS, "hostName"): set(),
        (CORE_NS, "userName"): set(),
        (CORE_NS, "operatingSystem"): set(),
        (CORE_NS, "cpuCores"): set(),
        (JAVA_NS, "javaVersion"): set(),
        (JAVA_NS, "fileEncoding"): set(),
        (JAVA_NS, "heapSize"): {"max"},
    }
    seen: set[tuple[str, str]] = set()
    for child in list(element):
        name = _qname(child.tag)
        if name not in allowed or name in seen or set(child.attrib) != allowed[name] or list(child):
            raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test infrastructure is invalid")
        seen.add(name)
        if child.text is not None and len(child.text) > MAX_TEXT_CHARS:
            raise _fail(
                VerificationReason.REPORT_MALFORMED,
                "Open Test infrastructure is oversized",
            )


def _check_structure(data: bytes) -> Element:
    if len(data) > MAX_REPORT_BYTES:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test report exceeds the size limit")
    if not data.strip():
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test report is empty")
    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise _fail(
            VerificationReason.REPORT_MALFORMED,
            "Open Test report DTD/entities are forbidden",
        )
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
                    raise _fail(
                        VerificationReason.REPORT_MALFORMED,
                        "Open Test report exceeds structural bounds",
                    )
                _qname(element.tag)
                if len(element.attrib) > MAX_ATTRIBUTES or any(
                    len(name) > MAX_ATTRIBUTE_CHARS or len(value) > MAX_ATTRIBUTE_CHARS
                    for name, value in element.attrib.items()
                ):
                    raise _fail(
                        VerificationReason.REPORT_MALFORMED,
                        "Open Test report attributes exceed bounds",
                    )
                if root is None:
                    root = element
            else:
                if element.text is not None and len(element.text) > MAX_TEXT_CHARS:
                    raise _fail(
                        VerificationReason.REPORT_MALFORMED,
                        "Open Test report text exceeds the size limit",
                    )
                depth -= 1
    except ReportNormalizationError:
        raise
    except Exception as exc:
        raise _fail(
            VerificationReason.REPORT_MALFORMED, f"cannot parse Open Test XML: {exc}"
        ) from exc
    if root is None or _qname(root.tag) != (EVENT_NS, "events"):
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test report root is invalid")
    schema_location = f"{{{XSI_NS}}}schemaLocation"
    if not set(root.attrib).issubset({schema_location}):
        raise _fail(
            VerificationReason.REPORT_MALFORMED,
            "Open Test report root attributes are invalid",
        )
    if schema_location in root.attrib and not root.attrib[schema_location].strip():
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test schemaLocation is empty")
    return root


def _result(event: Element) -> tuple[str, str | None]:
    results = [child for child in list(event) if _qname(child.tag) == (CORE_NS, "result")]
    if len(results) != 1:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test finish requires one result")
    result = results[0]
    if set(result.attrib) != {"status"}:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test result attributes are invalid")
    status = result.attrib["status"]
    if status not in {"SUCCESSFUL", "SKIPPED", "ABORTED", "FAILED"}:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test result status is invalid")
    details: list[str] = []
    seen_reason = False
    seen_throwable = False
    for child in list(result):
        name = _qname(child.tag)
        if name == (CORE_NS, "reason") and not seen_reason:
            if child.attrib or list(child):
                raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test reason is invalid")
            seen_reason = True
        elif name == (JAVA_NS, "throwable") and not seen_throwable:
            if set(child.attrib) != {"type", "assertionError"} or list(child):
                raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test throwable is invalid")
            if child.attrib["assertionError"] not in {"true", "false"} or not child.attrib["type"]:
                raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test throwable is invalid")
            seen_throwable = True
        else:
            raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test result content is invalid")
        value = (child.text or "").strip()
        if value:
            details.append(value)
    detail = "\n".join(details) or None
    if detail is not None and len(detail) > MAX_DETAILS_CHARS:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test details exceed the size limit")
    return status, detail


def normalize_junit_open_test_report(
    *,
    report_data: bytes | None,
    frozen_total: int,
    trusted_runner_exit_code: int | None,
) -> LeafReport:
    """Map trusted JUnit events to leaves without computing a reward."""

    if frozen_total <= 0:
        raise ValueError("frozen_total must be positive")
    if report_data is None:
        raise _fail(VerificationReason.REPORT_MISSING, "Open Test report is missing")
    root = _check_structure(report_data)
    children = list(root)
    infrastructure = [
        child for child in children if _qname(child.tag) == (CORE_NS, "infrastructure")
    ]
    if len(infrastructure) > 1 or (infrastructure and children[0] is not infrastructure[0]):
        raise _fail(
            VerificationReason.REPORT_MALFORMED,
            "Open Test infrastructure position is invalid",
        )
    if infrastructure:
        _validate_infrastructure(infrastructure[0])
    started: dict[str, _Started] = {}
    finished: set[str] = set()
    unique_ids: set[str] = set()
    leaves: list[LeafCase] = []
    errors: list[LeafCollectionError] = []
    for event in children[len(infrastructure) :]:
        namespace, local = _qname(event.tag)
        if namespace != EVENT_NS or local not in {"started", "reported", "finished"}:
            raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test root child is invalid")
        if local == "started":
            if set(event.attrib) not in (
                {"id", "name", "time"},
                {"id", "name", "time", "parentId"},
            ):
                raise _fail(
                    VerificationReason.REPORT_MALFORMED,
                    "Open Test started attributes are invalid",
                )
            event_id = event.attrib["id"]
            name = event.attrib["name"]
            parent_id = event.attrib.get("parentId")
            unique_id, item_type = _metadata(event)
            _validate_sources(event)
            if any(
                _qname(child.tag) not in {(CORE_NS, "metadata"), (CORE_NS, "sources")}
                for child in list(event)
            ):
                raise _fail(
                    VerificationReason.REPORT_MALFORMED,
                    "Open Test started content is invalid",
                )
            if (
                not event_id
                or len(event_id) > MAX_ID_CHARS
                or event_id in started
                or not name
                or len(name) > MAX_ID_CHARS
                or unique_id in unique_ids
            ):
                raise _fail(
                    VerificationReason.REPORT_MALFORMED,
                    "Open Test started event is invalid",
                )
            if parent_id is not None and (
                parent_id == event_id or parent_id not in started or parent_id in finished
            ):
                raise _fail(
                    VerificationReason.REPORT_MALFORMED,
                    "Open Test parent hierarchy is invalid",
                )
            started[event_id] = _Started(
                event_id=event_id,
                parent_id=parent_id,
                unique_id=unique_id,
                name=name,
                item_type=item_type,
                time=_timestamp(event.attrib["time"], "started time"),
            )
            unique_ids.add(unique_id)
            continue
        if set(event.attrib) != {"id", "time"}:
            raise _fail(
                VerificationReason.REPORT_MALFORMED,
                f"Open Test {local} attributes are invalid",
            )
        event_id = event.attrib["id"]
        if event_id not in started or event_id in finished:
            raise _fail(VerificationReason.REPORT_MALFORMED, f"Open Test {local} ID is invalid")
        _timestamp(event.attrib["time"], f"{local} time")
        if local == "reported":
            _validate_attachments(event)
            if any(_qname(child.tag) != (CORE_NS, "attachments") for child in list(event)):
                raise _fail(
                    VerificationReason.REPORT_MALFORMED,
                    "Open Test reported content is invalid",
                )
            continue
        if any(
            record.parent_id == event_id
            for record in started.values()
            if record.event_id not in finished
        ):
            raise _fail(
                VerificationReason.REPORT_MALFORMED,
                "Open Test parent finished before a child",
            )
        status, details = _result(event)
        if len(list(event)) != 1:
            raise _fail(
                VerificationReason.REPORT_MALFORMED,
                "Open Test finished content is invalid",
            )
        record = started[event_id]
        ended = _timestamp(event.attrib["time"], "finished time")
        try:
            duration_ms = (ended - record.time).total_seconds() * 1000.0
        except TypeError as exc:
            raise _fail(
                VerificationReason.REPORT_MALFORMED, "Open Test timestamps disagree"
            ) from exc
        if duration_ms < 0:
            raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test duration is negative")
        status_map = {
            "SUCCESSFUL": "passed",
            "SKIPPED": "skipped",
            "ABORTED": "skipped",
            "FAILED": "failed",
        }
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
                    display_name=record.name,
                    status=status_map[status],  # type: ignore[arg-type]
                    duration_ms=duration_ms,
                    details=details,
                )
            )
        finished.add(event_id)
    if set(started) != finished:
        raise _fail(VerificationReason.REPORT_MALFORMED, "Open Test report has unfinished events")
    if len(leaves) != frozen_total:
        raise _fail(
            VerificationReason.COLLECTION_MISMATCH,
            f"collected {len(leaves)}, expected {frozen_total}",
        )
    expected_exit = 1 if any(leaf.status == "failed" for leaf in leaves) or errors else 0
    if trusted_runner_exit_code is not None and trusted_runner_exit_code != expected_exit:
        raise _fail(
            VerificationReason.REPORT_EXIT_MISMATCH,
            f"runner exited {trusted_runner_exit_code}, but Open Test leaves require "
            f"{expected_exit}",
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
        raise _fail(reason, str(exc)) from exc


__all__ = [
    "CORE_NS",
    "EVENT_NS",
    "JAVA_NS",
    "JUNIT_NS",
    "MAX_REPORT_BYTES",
    "normalize_junit_open_test_report",
]
