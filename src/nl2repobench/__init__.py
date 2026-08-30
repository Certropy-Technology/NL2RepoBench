"""Metadata and authoring core for NL2RepoBench."""

from .domain.canonical_contract import (
    DependencyBundle,
    EnvironmentLock,
    TaskManifest,
    TestManifest,
)
from .domain.canonical_models import (
    ArtifactRef,
    DatasetManifest,
    MetricContract,
    SourceLock,
    TaskLifecycleRecord,
)

__all__ = [
    "ArtifactRef",
    "DatasetManifest",
    "DependencyBundle",
    "EnvironmentLock",
    "MetricContract",
    "SourceLock",
    "TaskLifecycleRecord",
    "TaskManifest",
    "TestManifest",
]

__version__ = "0.1.0"
