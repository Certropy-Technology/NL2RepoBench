"""Canonical current metric contract, isolated from legacy schema snapshots."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from nl2repobench.domain.models import RecordModel

MetricStatus = Literal["passed", "failed", "error", "skipped", "todo", "xfail"]


class MetricContract(RecordModel):
    """Fixed-denominator score semantics consumed by the unified evaluator."""

    contract_id: Literal["fixed-test-pass-rate-v1"] = "fixed-test-pass-rate-v1"
    passed_statuses: tuple[MetricStatus, ...] = ("passed",)
    denominator_statuses: tuple[MetricStatus, ...] = (
        "passed",
        "failed",
        "error",
        "skipped",
        "todo",
        "xfail",
    )
    collection_mismatch: Literal["fail", "record-only"] = "fail"
    formula: Literal["clamp(passed / frozen_total, 0, 1)"] = (
        "clamp(passed / frozen_total, 0, 1)"
    )

    @model_validator(mode="after")
    def validate_status_sets(self) -> Self:
        if not self.passed_statuses:
            raise ValueError("metric contract must define passed statuses")
        if len(set(self.passed_statuses)) != len(self.passed_statuses):
            raise ValueError("metric contract passed statuses must be unique")
        if len(set(self.denominator_statuses)) != len(self.denominator_statuses):
            raise ValueError("metric contract denominator statuses must be unique")
        if not set(self.passed_statuses).issubset(self.denominator_statuses):
            raise ValueError("passed statuses must be in denominator statuses")
        return self


__all__ = ["MetricContract", "MetricStatus"]
