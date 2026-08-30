"""Deterministic verifier contracts and grading helpers."""

from .evaluator import (
    CURRENT_CONTRACT_ID,
    EvaluationResult,
    LeafCounts,
    canonical_metric_contract,
    evaluate_leaf_report,
)
from .go_grader import grade_go_report, write_go_grading_outputs
from .grader import grade_verification, write_grading_outputs
from .leaf_report import (
    CollectionError,
    CollectionReport,
    LeafCase,
    LeafCollectionError,
    LeafReport,
)
from .metric_contract import MetricContract as CanonicalMetricContract
from .registry import UnknownVerifierRuntimeError, VerifierRuntimeRegistry
from .taxonomy import VerificationReason

__all__ = [
    "CURRENT_CONTRACT_ID",
    "EvaluationResult",
    "CollectionError",
    "CollectionReport",
    "LeafCase",
    "LeafCollectionError",
    "LeafCounts",
    "LeafReport",
    "CanonicalMetricContract",
    "UnknownVerifierRuntimeError",
    "VerificationReason",
    "VerifierRuntimeRegistry",
    "evaluate_leaf_report",
    "grade_verification",
    "grade_go_report",
    "canonical_metric_contract",
    "write_grading_outputs",
    "write_go_grading_outputs",
]
