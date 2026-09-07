"""Deterministic verifier contracts and grading helpers."""

from .evaluator import (
    CURRENT_CONTRACT_ID,
    EvaluationResult,
    LeafCounts,
    evaluate_leaf_report,
    metric_contract_from_legacy,
)
from .go_grader import grade_go_report, write_go_grading_outputs
from .grader import grade_verification, write_grading_outputs
from .leaf_report import LeafCase, LeafCollectionError, LeafReport
from .metric_contract import MetricContract as CanonicalMetricContract
from .models import (
    CollectionReport,
    GradingResult,
    TestCounts,
    VerificationReason,
)
from .registry import UnknownVerifierRuntimeError, VerifierRuntimeRegistry

__all__ = [
    "CURRENT_CONTRACT_ID",
    "CollectionReport",
    "EvaluationResult",
    "GradingResult",
    "LeafCase",
    "LeafCollectionError",
    "LeafCounts",
    "LeafReport",
    "CanonicalMetricContract",
    "TestCounts",
    "UnknownVerifierRuntimeError",
    "VerificationReason",
    "VerifierRuntimeRegistry",
    "evaluate_leaf_report",
    "grade_verification",
    "grade_go_report",
    "metric_contract_from_legacy",
    "write_grading_outputs",
    "write_go_grading_outputs",
]
