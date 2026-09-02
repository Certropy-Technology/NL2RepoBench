from __future__ import annotations

import json
from pathlib import Path

import pytest

from nl2repobench.analysis.archive.legacy.metric_contract import convert_legacy_metric
from nl2repobench.analysis.archive.legacy.models import LegacyMetricContract
from nl2repobench.verification.evaluator import evaluate_leaf_report
from nl2repobench.verification.leaf_report import (
    LeafCase,
    LeafReport,
    ReportNormalizationError,
)
from nl2repobench.verification.metric_contract import MetricContract
from nl2repobench.verification.node_grader import grade_node_test_report
from nl2repobench.verification.normalize.node_test_json import normalize_node_test_json
from nl2repobench.verification.normalize.pytest_junit import normalize_pytest_junit
from nl2repobench.verification.provenance import slice_provenance
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


def test_slice_provenance_binds_required_inputs(tmp_path: Path) -> None:
    for relative, content in (
        ("catalog/sources/node-pnpm-synthetic/source.txt", "source"),
        ("src/nl2repobench/runtime.py", "implementation"),
        ("toolchain.node.dev.lock.toml", "toolchain"),
        ("scripts/run_pnpm_harbor_controls.sh", "controls"),
        ("scripts/verify_p2_vertical_slices.py", "slice-verifier"),
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    bundle = tmp_path / "bundle.manifest.json"
    bundle.write_text(
        json.dumps({"canonical_manifest_digest": "sha256:test"}), encoding="utf-8"
    )
    result = slice_provenance(
        tmp_path,
        runtime="node",
        package_manager="pnpm",
        bundle_manifest=bundle,
    )
    assert result["schema_version"] == "p2-slice-provenance-v1"
    assert result["runtime"] == "node"
    assert result["canonical_manifest_digest"] == "sha256:test"
    assert all(isinstance(result[key], str) for key in result if key.endswith("sha256"))


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
    with pytest.raises(ValueError, match="excluded"):
        convert_legacy_metric(LegacyMetricContract(excluded_statuses=("skipped",)))


def test_active_node_grader_rejects_archived_metric_id() -> None:
    with pytest.raises(ValueError, match="unsupported metric contract"):
        grade_node_test_report(
            expected_total=1,
            report_data=None,
            metric_contract="node-test-leaf-pass-rate-v1",
        )


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
    assert report.report_format == "pytest-junit-xml-v1"


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
    assert registry.resolve("rust") is not None
    with pytest.raises(UnknownVerifierRuntimeError, match="registered: go, node, python, rust"):
        registry.resolve("ruby")
