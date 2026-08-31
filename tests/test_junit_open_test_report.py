from __future__ import annotations

from pathlib import Path

import pytest

from nl2repobench.verification.java_grader import grade_java_report
from nl2repobench.verification.leaf_report import ReportNormalizationError
from nl2repobench.verification.normalize.junit_open_test_report import (
    normalize_junit_open_test_report,
)
from nl2repobench.verification.taxonomy import VerificationReason

EVENT = "https://schemas.opentest4j.org/reporting/events/0.1.0"
CORE = "https://schemas.opentest4j.org/reporting/core/0.1.0"
JAVA = "https://schemas.opentest4j.org/reporting/java/0.1.0"
JUNIT = "https://schemas.junit.org/open-test-reporting"


def _report(statuses: tuple[str, ...], *, container_status: str = "SUCCESSFUL") -> bytes:
    events = [
        '<infrastructure><hostName>synthetic</hostName><java:javaVersion>21</java:javaVersion>'
        '</infrastructure>',
        '<e:started id="c" name="Jupiter" time="2026-01-01T00:00:00Z">'
        '<metadata><junit:uniqueId>[engine:junit]</junit:uniqueId>'
        '<junit:legacyReportingName>Jupiter</junit:legacyReportingName>'
        '<junit:type>CONTAINER</junit:type></metadata>'
        '<sources><java:classSource className="example.Synthetic"/></sources></e:started>'
    ]
    for index, status in enumerate(statuses):
        events.append(
            f'<e:started id="t{index}" parentId="c" name="case {index}" '
            f'time="2026-01-01T00:00:00Z"><metadata>'
            f'<junit:uniqueId>[engine:junit]/[test:{index}]</junit:uniqueId>'
            f'<junit:legacyReportingName>case {index}</junit:legacyReportingName>'
            f'<junit:type>TEST</junit:type></metadata></e:started>'
        )
        if index == 0:
            events.append(
                '<e:reported id="t0" time="2026-01-01T00:00:00.005Z">'
                '<attachments><data time="2026-01-01T00:00:00.005Z">'
                '<entry key="stdout">synthetic</entry></data></attachments></e:reported>'
            )
        events.append(
            f'<e:finished id="t{index}" time="2026-01-01T00:00:00.010Z">'
            f'<result status="{status}" /></e:finished>'
        )
    events.append(
        f'<e:finished id="c" time="2026-01-01T00:00:00.020Z">'
        f'<result status="{container_status}" /></e:finished>'
    )
    return (
        f'<e:events xmlns="{CORE}" xmlns:e="{EVENT}" xmlns:java="{JAVA}" '
        f'xmlns:junit="{JUNIT}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'xsi:schemaLocation="{JUNIT} https://junit.org/junit5/schemas/open-test-reporting/junit-1.9.xsd">'
        + "".join(events)
        + "</e:events>"
    ).encode()


def test_junit_open_test_report_maps_statuses_names_and_hierarchy() -> None:
    report = normalize_junit_open_test_report(
        report_data=_report(("SUCCESSFUL", "SKIPPED", "ABORTED", "FAILED")),
        frozen_total=4,
        trusted_runner_exit_code=1,
    )
    assert report.framework == "junit-platform"
    assert report.report_format == "junit-open-test-report-xml-v1"
    assert [leaf.status for leaf in report.leaves] == [
        "passed",
        "skipped",
        "skipped",
        "failed",
    ]
    assert report.leaves[0].display_name == "case 0"
    result = grade_java_report(
        expected_total=4,
        report_data=_report(("SUCCESSFUL", "SKIPPED", "ABORTED", "FAILED")),
        runner_exit_code=1,
    )
    assert result.valid is True
    assert result.reward == pytest.approx(0.25)


def test_published_junit_shape_with_core_metadata_and_java_throwable() -> None:
    data = (
        Path(__file__).parent / "fixtures/java/public/open-test-report-real-shape.xml"
    ).read_bytes()
    report = normalize_junit_open_test_report(
        report_data=data,
        frozen_total=1,
        trusted_runner_exit_code=1,
    )
    assert report.leaves[0].leaf_id == "[engine:junit-jupiter]/[test:display]"
    assert report.leaves[0].display_name == "display<-->Name"
    assert report.leaves[0].details == "synthetic failure"


def test_junit_container_failure_is_a_collection_error() -> None:
    report = normalize_junit_open_test_report(
        report_data=_report(("SUCCESSFUL",), container_status="FAILED"),
        frozen_total=1,
        trusted_runner_exit_code=1,
    )
    assert report.collection_errors
    result = grade_java_report(
        expected_total=1,
        report_data=_report(("SUCCESSFUL",), container_status="FAILED"),
        runner_exit_code=1,
    )
    assert result.valid is False
    assert result.failure_reason is VerificationReason.COLLECTION_ERROR


@pytest.mark.parametrize(
    ("data", "reason"),
    [
        (None, VerificationReason.REPORT_MISSING),
        (b"<events />", VerificationReason.REPORT_MALFORMED),
        (
            b'<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><x>&e;</x>',
            VerificationReason.REPORT_MALFORMED,
        ),
    ],
)
def test_junit_report_rejects_missing_namespace_and_entities(
    data: bytes | None, reason: VerificationReason
) -> None:
    with pytest.raises(ReportNormalizationError) as raised:
        normalize_junit_open_test_report(
            report_data=data,
            frozen_total=1,
            trusted_runner_exit_code=0,
        )
    assert raised.value.reason is reason


def test_junit_report_requires_frozen_count_and_trusted_exit() -> None:
    with pytest.raises(ReportNormalizationError) as count:
        normalize_junit_open_test_report(
            report_data=_report(("SUCCESSFUL",)),
            frozen_total=2,
            trusted_runner_exit_code=0,
        )
    assert count.value.reason is VerificationReason.COLLECTION_MISMATCH
    with pytest.raises(ReportNormalizationError) as exit_error:
        normalize_junit_open_test_report(
            report_data=_report(("FAILED",)),
            frozen_total=1,
            trusted_runner_exit_code=0,
        )
    assert exit_error.value.reason is VerificationReason.REPORT_EXIT_MISMATCH
