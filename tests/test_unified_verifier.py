from __future__ import annotations

import json

import pytest

from nl2repobench.domain.models import MetricContract as LegacyMetricContract
from nl2repobench.verification.evaluator import evaluate_leaf_report
from nl2repobench.verification.leaf_report import (
    LeafCase,
    LeafReport,
    ReportNormalizationError,
)
from nl2repobench.verification.metric_contract import MetricContract
from nl2repobench.verification.normalize.node_test_json import normalize_node_test_json
from nl2repobench.verification.normalize.pytest_junit import normalize_pytest_junit
from nl2repobench.verification.registry import (
    UnknownVerifierRuntimeError,
    VerifierRuntimeRegistry,
)
from nl2repobench.verification.taxonomy import VerificationReason


def _report(*statuses: str, exit_code: int | None = None) -> LeafReport:
    return LeafReport(
        framework="synthetic",
        report_format="synthetic-v1",
        collected=len(statuses),
        leaves=tuple(
            LeafCase(leaf_id=f"leaf-{index}", status=status)  # type: ignore[arg-type]
            for index, status in enumerate(statuses)
        ),
        trusted_runner_exit_code=exit_code,
        frozen_total=len(statuses),
    )


def test_evaluator_keeps_skipped_in_the_fixed_denominator() -> None:
    result = evaluate_leaf_report(
        _report("passed", "skipped", "failed", exit_code=1),
        MetricContract(),
    )
    assert result.valid is True
    assert result.reward == pytest.approx(1 / 3)
    assert result.counts.skipped == 1


def test_metric_contract_fields_change_evaluation() -> None:
    report = _report("passed", "skipped", exit_code=0)
    default = evaluate_leaf_report(report, MetricContract())
    custom = evaluate_leaf_report(
        report,
        MetricContract(passed_statuses=("passed", "skipped")),
    )
    mismatch_report = LeafReport(
        framework="synthetic",
        report_format="synthetic-v1",
        collected=1,
        leaves=(LeafCase(leaf_id="only", status="passed"),),
        frozen_total=2,
        trusted_runner_exit_code=0,
    )
    record_only = evaluate_leaf_report(
        mismatch_report,
        MetricContract(collection_mismatch="record-only"),
    )
    assert default.reward == 0.5
    assert custom.reward == 1.0
    assert record_only.valid is True


def test_legacy_excluded_statuses_cannot_silently_change_current_scoring() -> None:
    from nl2repobench.verification.evaluator import metric_contract_from_legacy

    with pytest.raises(TypeError, match="metric contract"):
        metric_contract_from_legacy(LegacyMetricContract(excluded_statuses=("skipped",)))


def test_evaluator_rejects_runner_status_mismatch() -> None:
    result = evaluate_leaf_report(_report("passed", exit_code=1), MetricContract())
    assert result.valid is False
    assert result.failure_reason is VerificationReason.REPORT_EXIT_MISMATCH


def test_leaf_report_rejects_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="IDs must be unique"):
        LeafReport(
            framework="synthetic",
            report_format="synthetic-v1",
            collected=2,
            leaves=(
                LeafCase(leaf_id="same", status="passed"),
                LeafCase(leaf_id="same", status="passed"),
            ),
            frozen_total=2,
        )


def test_pytest_normalizer_maps_collection_ids_and_statuses() -> None:
    collection = json.dumps(
        {
            "schema_version": "1.0",
            "collected": 2,
            "nodeids": ["test.py::test_a", "test.py::test_b"],
            "collection_errors": [],
        }
    ).encode()
    report = normalize_pytest_junit(
        junit_data=(
            b'<testsuite><testcase name="a" />'
            b'<testcase name="b"><skipped type="pytest.xfail" /></testcase></testsuite>'
        ),
        collection_data=collection,
        frozen_total=2,
        trusted_runner_exit_code=0,
    )
    assert [leaf.leaf_id for leaf in report.leaves] == ["test.py::test_a", "test.py::test_b"]
    assert [leaf.status for leaf in report.leaves] == ["passed", "xfail"]


def test_node_normalizer_rejects_duplicate_ids() -> None:
    with pytest.raises(ReportNormalizationError) as error:
        normalize_node_test_json(
            report_data={
                "schema_version": "2.0",
                "framework": "node:test",
                "report_format": "node-test-json-v1",
                "collected": 2,
                "tests": [
                    {"test_id": "same", "status": "passed"},
                    {"test_id": "same", "status": "passed"},
                ],
                "collection_errors": [],
                "runner_exit_code": 0,
            },
            frozen_total=2,
            trusted_runner_exit_code=0,
        )
    assert error.value.reason is VerificationReason.DUPLICATE_LEAF_ID


def test_verifier_registry_fails_closed() -> None:
    registry = VerifierRuntimeRegistry.default()
    assert registry.resolve("python") is not None
    assert registry.resolve("node") is not None
    with pytest.raises(UnknownVerifierRuntimeError, match="registered: go, node, python"):
        registry.resolve("rust")
