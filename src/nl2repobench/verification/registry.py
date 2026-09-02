"""Explicit verifier-runtime registry with lazy runtime imports."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from .evaluator import EvaluationResult
from .metric_contract import MetricContract
from .taxonomy import VerificationReason


class UnknownVerifierRuntimeError(ValueError):
    """Raised when the requested verifier runtime is not registered."""


class VerifierAdapter(Protocol):
    """Runtime-specific input normalization into the canonical result."""

    limits: Mapping[str, int]

    def grade(
        self,
        *,
        expected_total: int,
        metric_contract: MetricContract | str,
        junit_data: bytes | None,
        collection_data: bytes | None,
        report_data: bytes | None,
        pytest_exit_code: int | None,
        runner_exit_code: int | None,
        explicit_reason: VerificationReason | None,
    ) -> EvaluationResult: ...

    def write(self, result: EvaluationResult, output_dir: Path) -> None: ...


@dataclass(frozen=True)
class _PythonVerifierAdapter:
    limits: Mapping[str, int]

    def grade(self, **kwargs: Any) -> Any:
        from .grader import grade_verification

        return grade_verification(
            expected_total=kwargs["expected_total"],
            metric_contract=kwargs["metric_contract"],
            junit_data=kwargs["junit_data"],
            collection_data=kwargs["collection_data"],
            pytest_exit_code=kwargs["pytest_exit_code"],
            explicit_reason=kwargs["explicit_reason"],
        )

    def write(self, result: Any, output_dir: Path) -> None:
        from .grader import write_grading_outputs

        write_grading_outputs(result, output_dir)


@dataclass(frozen=True)
class _NodeVerifierAdapter:
    limits: Mapping[str, int]

    def grade(self, **kwargs: Any) -> Any:
        from .node_grader import grade_node_test_report

        return grade_node_test_report(
            expected_total=kwargs["expected_total"],
            metric_contract=kwargs["metric_contract"],
            report_data=kwargs["report_data"],
            runner_exit_code=kwargs["runner_exit_code"],
            explicit_reason=kwargs["explicit_reason"],
        )

    def write(self, result: Any, output_dir: Path) -> None:
        from .node_grader import write_node_grading_outputs

        write_node_grading_outputs(result, output_dir)


@dataclass(frozen=True)
class _GoVerifierAdapter:
    limits: Mapping[str, int]

    def grade(self, **kwargs: Any) -> Any:
        from .go_grader import grade_go_report

        return grade_go_report(
            expected_total=kwargs["expected_total"],
            metric_contract=kwargs["metric_contract"],
            report_data=kwargs["report_data"],
            runner_exit_code=kwargs["runner_exit_code"],
            explicit_reason=kwargs["explicit_reason"],
        )

    def write(self, result: Any, output_dir: Path) -> None:
        from .go_grader import write_go_grading_outputs

        write_go_grading_outputs(result, output_dir)


@dataclass(frozen=True)
class _RustVerifierAdapter:
    limits: Mapping[str, int]

    def grade(self, **kwargs: Any) -> Any:
        from .rust_grader import grade_rust_report

        return grade_rust_report(
            expected_total=kwargs["expected_total"],
            metric_contract=kwargs["metric_contract"],
            report_data=kwargs["report_data"],
            runner_exit_code=kwargs["runner_exit_code"],
            explicit_reason=kwargs["explicit_reason"],
        )

    def write(self, result: Any, output_dir: Path) -> None:
        from .rust_grader import write_rust_grading_outputs

        write_rust_grading_outputs(result, output_dir)


@dataclass(frozen=True)
class VerifierRuntimeRegistry:
    """Resolve exactly one explicit runtime identity to a verifier adapter."""

    adapters: Mapping[str, Any]

    @classmethod
    def default(cls) -> VerifierRuntimeRegistry:
        return cls(
            adapters={
                "python": _PythonVerifierAdapter(
                    limits={"junit": 64 * 1024 * 1024, "collection": 4 * 1024 * 1024}
                ),
                "node": _NodeVerifierAdapter(limits={"report": 8 * 1024 * 1024}),
                "go": _GoVerifierAdapter(limits={"report": 8 * 1024 * 1024}),
                "rust": _RustVerifierAdapter(limits={"report": 8 * 1024 * 1024}),
            }
        )

    def resolve(self, runtime: str) -> VerifierAdapter:
        try:
            return cast(VerifierAdapter, self.adapters[runtime])
        except KeyError as exc:
            available = ", ".join(sorted(self.adapters))
            raise UnknownVerifierRuntimeError(
                f"unknown verifier runtime {runtime!r}; registered: {available}"
            ) from exc


__all__ = ["UnknownVerifierRuntimeError", "VerifierAdapter", "VerifierRuntimeRegistry"]
