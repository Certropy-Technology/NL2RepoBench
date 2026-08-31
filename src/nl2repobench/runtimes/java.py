"""Java runtime identity and Maven composition boundary."""

from __future__ import annotations

from dataclasses import dataclass

from nl2repobench.package_managers.maven import JAVA_MAVEN_IDENTITY, MavenPackageManager


@dataclass(frozen=True)
class JavaRuntimeAdapter:
    identity = JAVA_MAVEN_IDENTITY
    package_manager = MavenPackageManager()
    runtime = "jdk"


__all__ = ["JavaRuntimeAdapter"]
