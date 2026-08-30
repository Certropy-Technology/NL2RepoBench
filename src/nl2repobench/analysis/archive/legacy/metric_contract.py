"""Explicit conversion of archived metric records into the active contract."""

from __future__ import annotations

from nl2repobench.domain.canonical_models import MetricContract

from .models import LegacyMetricContract


def convert_legacy_metric(value: LegacyMetricContract) -> MetricContract:
    """Convert only archive records that preserve the fixed denominator."""

    if value.contract_id not in {
        "fixed-test-pass-rate-v1",
        "node-test-leaf-pass-rate-v1",
    }:
        raise ValueError(f"unsupported archived metric contract: {value.contract_id}")
    if value.excluded_statuses:
        raise ValueError("archived excluded statuses cannot change the fixed denominator")
    return MetricContract(
        passed_statuses=value.passed_statuses,
        collection_mismatch=value.collection_mismatch,
    )


__all__ = ["convert_legacy_metric"]
