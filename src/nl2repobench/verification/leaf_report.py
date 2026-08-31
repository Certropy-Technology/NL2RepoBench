"""Canonical verifier leaf records shared by every runtime adapter."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from nl2repobench.domain.canonical_models import CanonicalRecord as RecordModel

from .taxonomy import VerificationReason

LeafStatus = Literal["passed", "failed", "error", "skipped", "todo", "xfail"]


class CollectionError(RecordModel):
    nodeid: str
    message: str


class CollectionReport(RecordModel):
    collected: int = Field(ge=0)
    nodeids: tuple[str, ...] = ()
    collection_errors: tuple[CollectionError, ...] = ()

    @model_validator(mode="after")
    def validate_nodeids(self) -> CollectionReport:
        if self.nodeids and len(self.nodeids) != self.collected:
            raise ValueError("collection nodeid count does not match collected")
        if len(set(self.nodeids)) != len(self.nodeids):
            raise ValueError("collection nodeids must be unique")
        return self


class LeafCase(RecordModel):
    """One verifier-owned test leaf after framework normalization."""

    leaf_id: Annotated[str, Field(min_length=1, max_length=512)]
    display_name: Annotated[str | None, Field(min_length=1, max_length=512)] = None
    status: LeafStatus
    duration_ms: Annotated[float, Field(ge=0)] = 0.0
    details: Annotated[str | None, Field(max_length=4096)] = None


class LeafCollectionError(RecordModel):
    """A trusted runner error that prevents a valid score."""

    message: Annotated[str, Field(min_length=1, max_length=4096)]
    leaf_id: Annotated[str | None, Field(min_length=1, max_length=512)] = None


class LeafReport(RecordModel):
    """Runtime-neutral report consumed by the sole fixed-denominator evaluator."""

    framework: Annotated[str, Field(min_length=1, max_length=128)]
    report_format: Annotated[str, Field(min_length=1, max_length=128)]
    collected: Annotated[int, Field(ge=0)]
    leaves: tuple[LeafCase, ...] = ()
    collection_errors: tuple[LeafCollectionError, ...] = ()
    trusted_runner_exit_code: int | None = None
    frozen_total: Annotated[int, Field(gt=0)]

    @model_validator(mode="after")
    def validate_leaf_collection(self) -> LeafReport:
        if len(self.leaves) != self.collected:
            raise ValueError("leaf report count does not match collected")
        leaf_ids = [leaf.leaf_id for leaf in self.leaves]
        if len(set(leaf_ids)) != len(leaf_ids):
            raise ValueError("leaf report IDs must be unique")
        return self


class ReportNormalizationError(ValueError):
    """A bounded framework report could not become a canonical leaf report."""

    def __init__(
        self,
        reason: VerificationReason,
        message: str,
        *,
        details: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.details = details or (message,)


__all__ = [
    "CollectionError",
    "CollectionReport",
    "LeafCase",
    "LeafCollectionError",
    "LeafReport",
    "ReportNormalizationError",
]
