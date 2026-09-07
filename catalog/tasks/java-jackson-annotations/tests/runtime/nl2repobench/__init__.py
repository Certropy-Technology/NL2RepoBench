"""Metadata and authoring core for NL2RepoBench."""

from .domain.models import (
    ArtifactRef,
    DatasetManifest,
    DependencyBundle,
    EnvironmentLock,
    MetricContract,
    SourceLock,
    TaskLifecycleRecord,
    TaskManifest,
    TestManifest,
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
