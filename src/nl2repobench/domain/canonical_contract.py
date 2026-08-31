"""Strict F0 canonical records.

This module is the migration target.  It intentionally has no decoder for the
historical v1/v2 records; decoding belongs exclusively to the migration tool.
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Annotated, Literal, cast

from pydantic import ConfigDict, Field, model_validator
from pydantic.json_schema import JsonSchemaValue

from .canonical_models import (
    ArtifactRef,
    CanonicalRecord,
    HarborExecutionProfile,
    MetricContract,
    NetworkPolicy,
    SourceLock,
    TaskLifecycleRecord,
    TaskStatus,
    TaskVerifierSpec,
    Visibility,
)

SHA256 = r"^sha256:[0-9a-f]{64}$"
TaskId = Annotated[
    str,
    Field(
        pattern=r"^(?:[A-Za-z0-9][A-Za-z0-9._-]*|@[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*)$"
    ),
]


class RuntimeLanguage(StrEnum):
    PYTHON = "python"
    NODE = "node"
    GO = "go"
    JAVA = "java"
    RUST = "rust"


class PackageManager(StrEnum):
    UV = "uv"
    PIP = "pip"
    NPM = "npm"
    PNPM = "pnpm"
    GO_MODULES = "go-modules"
    MAVEN = "maven"
    CARGO = "cargo"
    NONE = "none"


class RuntimeProfile(CanonicalRecord):
    model_config = ConfigDict(
        json_schema_extra=cast(
            JsonSchemaValue,
            {
                "allOf": [
                    {
                        "if": {"properties": {"language": {"const": language}}},
                        "then": {
                            "properties": {
                                "runtime": {"const": runtime},
                                "package_manager": {"enum": managers},
                            }
                        },
                    }
                    for language, runtime, managers in (
                        ("python", "cpython", ["uv", "pip", "none"]),
                        ("node", "node", ["npm", "pnpm", "none"]),
                        ("go", "go", ["go-modules"]),
                        ("java", "jdk", ["maven"]),
                        ("rust", "rust", ["cargo"]),
                    )
                ]
                + [
                    {
                        "if": {"properties": {"language": {"const": "rust"}}},
                        "then": {
                            "properties": {
                                "version": {"const": "1.100.0-nightly"},
                                "package_manager_version": {
                                    "const": "1.100.0-nightly"
                                },
                            }
                        },
                    },
                    {
                        "if": {"properties": {"package_manager": {"const": "none"}}},
                        "then": {"properties": {"package_manager_version": {"type": "null"}}},
                        "else": {
                            "required": ["package_manager_version"],
                            "properties": {
                                "package_manager_version": {"type": "string", "minLength": 1}
                            },
                        },
                    }
                ]
            },
        )
    )
    language: RuntimeLanguage
    runtime: Literal["cpython", "node", "go", "jdk", "rust"]
    version: str = Field(min_length=1)
    package_manager: PackageManager
    package_manager_version: str | None = None

    @model_validator(mode="after")
    def validate_identity(self) -> RuntimeProfile:
        expected = {
            "python": "cpython",
            "node": "node",
            "go": "go",
            "java": "jdk",
            "rust": "rust",
        }[
            self.language.value
        ]
        if self.runtime != expected:
            raise ValueError("runtime does not match language")
        if self.package_manager is PackageManager.NONE and self.package_manager_version is not None:
            raise ValueError("none package manager must not have a version")
        if self.package_manager is not PackageManager.NONE and not self.package_manager_version:
            raise ValueError("package manager version is required")
        allowed = {
            "python": {PackageManager.UV, PackageManager.PIP, PackageManager.NONE},
            "node": {PackageManager.NPM, PackageManager.PNPM, PackageManager.NONE},
            "go": {PackageManager.GO_MODULES},
            "java": {PackageManager.MAVEN},
            "rust": {PackageManager.CARGO},
        }
        if self.package_manager not in allowed[self.language.value]:
            raise ValueError("package manager is not valid for runtime")
        if self.language is RuntimeLanguage.NODE and not re.fullmatch(
            r"(?:22|24)\.[0-9]+\.[0-9]+", self.version
        ):
            raise ValueError("Node runtime version must be an exact supported 22.x.y or 24.x.y")
        if self.package_manager in {PackageManager.NPM, PackageManager.PNPM} and not re.fullmatch(
            r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?",
            self.package_manager_version or "",
        ):
            raise ValueError("Node package managers require an exact semantic version")
        if self.language is RuntimeLanguage.JAVA and not re.fullmatch(
            r"[A-Za-z][A-Za-z0-9._-]*-21\.0\.[0-9]+\+[0-9]+(?:\.[0-9]+)?",
            self.version,
        ):
            raise ValueError(
                "Java runtime version must include a distribution and exact JDK 21 build"
            )
        if self.package_manager is PackageManager.MAVEN and not re.fullmatch(
            r"3\.9\.[0-9]+", self.package_manager_version or ""
        ):
            raise ValueError("Maven version must be an exact supported 3.9.x version")
        if self.language is RuntimeLanguage.RUST and (
            self.version != "1.100.0-nightly"
            or self.package_manager_version != "1.100.0-nightly"
        ):
            raise ValueError("Rust and Cargo versions must be exactly 1.100.0-nightly")
        return self


class EnvironmentLock(CanonicalRecord):
    model_config = ConfigDict(
        json_schema_extra=cast(
            JsonSchemaValue,
            {
                "allOf": [
                    {
                        "if": {
                            "required": ["status"],
                            "properties": {"status": {"const": "known"}},
                        },
                        "then": {
                            "required": [
                                "runtime",
                                "os_name",
                                "base_image",
                                "base_image_digest",
                                "network_policy",
                            ],
                            "properties": {
                                "runtime": {"not": {"type": "null"}},
                                "os_name": {"type": "string", "minLength": 1},
                                "base_image": {"type": "string", "minLength": 1},
                                "base_image_digest": {"type": "string", "pattern": SHA256},
                                "network_policy": {"not": {"type": "null"}},
                            },
                        },
                    }
                ]
            },
        )
    )
    status: Literal["known", "unknown"] = "unknown"
    runtime: RuntimeProfile | None = None
    os_name: str | None = None
    base_image: str | None = None
    base_image_digest: Annotated[str | None, Field(pattern=SHA256)] = None
    system_packages: tuple[str, ...] = ()
    build_command: str | None = None
    network_policy: NetworkPolicy | None = None

    @model_validator(mode="after")
    def validate_known(self) -> EnvironmentLock:
        if self.status == "known":
            if (
                not self.runtime
                or not self.os_name
                or not self.base_image
                or not self.base_image_digest
            ):
                raise ValueError("known environment requires runtime, OS, image, and digest")
            if self.network_policy is None:
                raise ValueError("known environment requires network policy")
        return self


class DependencyBundle(CanonicalRecord):
    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {
                        "required": ["status"],
                        "properties": {
                            "status": {"const": "known"},
                        },
                    },
                    "then": {
                        "required": ["lock", "offline_store", "inventory"],
                        "properties": {
                            name: {
                                "allOf": [
                                    {"not": {"type": "null"}},
                                    {"properties": {"visibility": {"const": "private"}}},
                                ]
                            }
                            for name in ("lock", "offline_store", "inventory")
                        },
                    },
                    "else": {
                        "properties": {
                            name: {"type": "null"}
                            for name in ("lock", "offline_store", "inventory")
                        }
                    },
                },
                {
                    "if": {
                        "required": ["status", "package_manager"],
                        "properties": {
                            "status": {"const": "known"},
                            "package_manager": {"const": "none"},
                        },
                    },
                    "then": {"properties": {"packages": {"maxItems": 0}}},
                },
            ]
        }
    )
    status: Literal["known", "unknown"] = "unknown"
    package_manager: PackageManager
    lock: ArtifactRef | None = None
    offline_store: ArtifactRef | None = None
    inventory: ArtifactRef | None = None
    packages: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_refs(self) -> DependencyBundle:
        refs = (self.lock, self.offline_store, self.inventory)
        requires_closure = self.status == "known"
        if requires_closure and any(ref is None for ref in refs):
            raise ValueError("known dependency bundle requires lock, offline_store, and inventory")
        if not requires_closure and any(ref is not None for ref in refs):
            raise ValueError(
                "dependency bundle without a closure must not claim artifact references"
            )
        for name, ref in zip(("lock", "offline_store", "inventory"), refs, strict=True):
            if ref is not None and ref.visibility.value != "private":
                raise ValueError(f"dependencies.{name} must be private")
        if self.package_manager is PackageManager.NONE and self.status == "known" and self.packages:
            raise ValueError("known none dependency bundle cannot declare packages")
        return self


class TestManifest(CanonicalRecord):
    model_config = ConfigDict(
        json_schema_extra=cast(
            JsonSchemaValue,
            {
                "allOf": [
                    {
                        "if": {"properties": {"framework": {"const": framework}}},
                        "then": {"properties": {"report_format": {"const": report}}},
                    }
                    for framework, report in (
                        ("pytest", "pytest-junit-xml-v1"),
                        ("node:test", "node-test-json-v1"),
                        ("go-bridge", "go-test-json-v1"),
                        ("rust-harness", "rust-bridge-json-v1"),
                        ("custom", "custom-json-v1"),
                        ("junit-platform", "junit-open-test-report-xml-v1"),
                    )
                ]
                + [
                    {
                        "if": {
                            "required": ["expected_total_source"],
                            "properties": {"expected_total_source": {"const": "frozen-collection"}},
                        },
                        "then": {"properties": {"expected_total": {"minimum": 1}}},
                    },
                    *(
                        {
                            "properties": {
                                name: {
                                    "anyOf": [
                                        {"type": "null"},
                                        {
                                            "type": "object",
                                            "properties": {"visibility": {"const": "private"}},
                                        },
                                    ]
                                }
                            }
                        }
                        for name in (
                            "commands_artifact",
                            "protected_paths_artifact",
                            "test_bundle",
                        )
                    ),
                ]
            },
        )
    )
    framework: Literal[
        "pytest", "node:test", "go-bridge", "rust-harness", "custom", "junit-platform"
    ]
    report_format: Literal[
        "pytest-junit-xml-v1",
        "node-test-json-v1",
        "go-test-json-v1",
        "custom-json-v1",
        "junit-open-test-report-xml-v1",
        "rust-bridge-json-v1",
    ]
    expected_total: Annotated[int, Field(ge=0)] = 0
    expected_total_source: Literal["frozen-collection", "unknown"] = "unknown"
    commands_artifact: ArtifactRef | None = None
    protected_paths_artifact: ArtifactRef | None = None
    test_bundle: ArtifactRef | None = None

    @model_validator(mode="after")
    def validate_contract(self) -> TestManifest:
        if self.framework == "pytest" and self.report_format != "pytest-junit-xml-v1":
            raise ValueError("pytest requires pytest-junit-xml-v1")
        if self.framework == "node:test" and self.report_format != "node-test-json-v1":
            raise ValueError("node:test requires node-test-json-v1")
        if self.framework == "go-bridge" and self.report_format != "go-test-json-v1":
            raise ValueError("go-bridge requires go-test-json-v1")
        if self.framework == "rust-harness" and self.report_format != "rust-bridge-json-v1":
            raise ValueError("rust-harness requires rust-bridge-json-v1")
        if self.framework == "custom" and self.report_format != "custom-json-v1":
            raise ValueError("custom requires custom-json-v1")
        if (
            self.framework == "junit-platform"
            and self.report_format != "junit-open-test-report-xml-v1"
        ):
            raise ValueError("junit-platform requires junit-open-test-report-xml-v1")
        for name, ref in (
            ("commands_artifact", self.commands_artifact),
            ("protected_paths_artifact", self.protected_paths_artifact),
            ("test_bundle", self.test_bundle),
        ):
            if ref is not None and ref.visibility is not Visibility.PRIVATE:
                raise ValueError(f"tests.{name} must be private")
        if self.expected_total_source == "frozen-collection" and self.expected_total <= 0:
            raise ValueError("frozen test collection must have a positive expected_total")
        return self


class TaskMetadata(CanonicalRecord):
    difficulty: Literal["easy", "medium", "hard", "unknown"] = "unknown"
    category: str = "unknown"
    tags: tuple[str, ...] = ()
    language: RuntimeLanguage


def _task_contract_schema(environment_field: str, dependency_field: str) -> JsonSchemaValue:
    production = [
        "packaged",
        "oracle-passed",
        "controls-passed",
        "reviewed",
        "piloted",
        "published",
    ]
    rules: list[dict[str, object]] = []
    for language, frameworks in (
        ("python", ["pytest", "custom"]),
        ("node", ["node:test"]),
        ("go", ["go-bridge"]),
        ("java", ["junit-platform"]),
        ("rust", ["rust-harness"]),
    ):
        rules.append(
            {
                "if": {
                    "properties": {
                        environment_field: {
                            "properties": {
                                "runtime": {
                                    "type": "object",
                                    "properties": {"language": {"const": language}},
                                    "required": ["language"],
                                }
                            },
                            "required": ["runtime"],
                        }
                    },
                },
                "then": {
                    "properties": {
                        "metadata": {"properties": {"language": {"const": language}}},
                        "tests": {"properties": {"framework": {"enum": frameworks}}},
                    }
                },
            }
        )
    for manager in PackageManager:
        rules.append(
            {
                "if": {
                    "properties": {
                        environment_field: {
                            "properties": {
                                "runtime": {
                                    "type": "object",
                                    "properties": {"package_manager": {"const": manager.value}},
                                    "required": ["package_manager"],
                                }
                            },
                            "required": ["runtime"],
                        }
                    }
                },
                "then": {
                    "properties": {
                        dependency_field: {
                            "properties": {"package_manager": {"const": manager.value}}
                        }
                    }
                },
            }
        )
    rules.extend(
        [
            {
                "if": {
                    "properties": {
                        "tests": {
                            "properties": {"framework": {"const": "custom"}}
                        }
                    }
                },
                "then": {
                    "required": ["verifier"],
                    "properties": {"verifier": {"not": {"type": "null"}}},
                },
            },
            {
                "if": {
                    "properties": {
                        "tests": {
                            "properties": {
                                "framework": {
                                    "enum": ["pytest", "node:test", "junit-platform"]
                                }
                            }
                        }
                    }
                },
                "then": {"properties": {"verifier": {"type": "null"}}},
            },
            {
                "if": {
                    "properties": {
                        environment_field: {
                            "properties": {
                                "runtime": {
                                    "type": "object",
                                    "properties": {
                                        "language": {"const": "node"},
                                        "package_manager": {"const": "none"},
                                    },
                                    "required": ["language", "package_manager"],
                                }
                            },
                            "required": ["runtime"],
                        }
                    }
                },
                "then": {
                    "properties": {
                        dependency_field: {"properties": {"status": {"const": "unknown"}}}
                    }
                },
            },
            {
                "if": {
                    "required": ["lifecycle"],
                    "properties": {"lifecycle": {"properties": {"status": {"enum": production}}}},
                },
                "then": {
                    "properties": {
                        environment_field: {"properties": {"status": {"const": "known"}}},
                        "source" if environment_field == "environment" else "source_lock": {
                            "required": [
                                "upstream_url",
                                "revision",
                                "license_spdx",
                                "source_digest",
                            ],
                            "properties": {"status": {"const": "known"}},
                        },
                        dependency_field: {"properties": {"status": {"const": "known"}}},
                        "tests": {
                            "required": ["commands_artifact"],
                            "properties": {
                                "expected_total_source": {"const": "frozen-collection"},
                                "expected_total": {"minimum": 1},
                                "commands_artifact": {"not": {"type": "null"}},
                            },
                        },
                    },
                    "anyOf": [
                        {
                            "required": ["verifier"],
                            "properties": {"verifier": {"not": {"type": "null"}}},
                        },
                        {
                            "properties": {
                                "tests": {
                                    "required": ["test_bundle"],
                                    "properties": {"test_bundle": {"not": {"type": "null"}}},
                                }
                            }
                        },
                    ],
                },
            },
            {
                "properties": {
                    "oracle_bundle": {
                        "anyOf": [
                            {"type": "null"},
                            {
                                "type": "object",
                                "properties": {"visibility": {"const": "private"}},
                            },
                        ]
                    }
                }
            },
        ]
    )
    return cast(JsonSchemaValue, {"allOf": rules})


def _manifest_contract_schema() -> JsonSchemaValue:
    schema = _task_contract_schema("environment_lock", "dependency_bundle")
    rules = cast(list[dict[str, object]], schema["allOf"])
    rules.append(
        {
            "properties": {
                "instruction": {
                    "type": "object",
                    "properties": {"visibility": {"const": "public"}},
                }
            }
        }
    )
    return schema


def _source_contract_schema() -> JsonSchemaValue:
    schema = _task_contract_schema("environment", "dependencies")
    rules = cast(list[dict[str, object]], schema["allOf"])
    rules.append(
        {
            "properties": {
                "instruction": {
                    "type": "string",
                    "minLength": 1,
                    "pattern": r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$)).+$",
                }
            }
        }
    )
    return schema


class TaskSource(CanonicalRecord):
    model_config = ConfigDict(json_schema_extra=_source_contract_schema())
    task_id: TaskId
    version: str = "1.0.0"
    instruction: str = "instruction.md"
    metadata: TaskMetadata
    source: SourceLock = Field(default_factory=SourceLock)
    environment: EnvironmentLock
    dependencies: DependencyBundle
    tests: TestManifest
    metric: MetricContract = Field(default_factory=MetricContract)
    lifecycle: TaskLifecycleRecord = Field(default_factory=TaskLifecycleRecord)
    harbor: HarborExecutionProfile | None = None
    oracle_bundle: ArtifactRef | None = None
    verifier: TaskVerifierSpec | None = None

    @model_validator(mode="after")
    def validate_instruction(self) -> TaskSource:
        if (
            not self.instruction
            or self.instruction.startswith("/")
            or ".." in self.instruction.split("/")
        ):
            raise ValueError("instruction must be a safe relative path")
        if self.environment.runtime is not None:
            if self.environment.runtime.language != self.metadata.language:
                raise ValueError("metadata language must match environment runtime")
            if self.environment.runtime.package_manager != self.dependencies.package_manager:
                raise ValueError("dependency package manager must match environment runtime")
        if self.tests.framework == "custom" and self.verifier is None:
            raise ValueError("custom tests require a typed verifier specification")
        if (
            self.tests.framework not in {"custom", "go-bridge", "rust-harness"}
            and self.verifier is not None
        ):
            raise ValueError(
                "typed verifier is only valid for custom, go-bridge, and rust-harness tests"
            )
        if self.environment.runtime is not None:
            expected_tests = {
                RuntimeLanguage.PYTHON: ("pytest", "custom"),
                RuntimeLanguage.NODE: ("node:test",),
                RuntimeLanguage.GO: ("go-bridge",),
                RuntimeLanguage.RUST: ("rust-harness",),
                RuntimeLanguage.JAVA: ("junit-platform",),
            }[self.environment.runtime.language]
            if self.tests.framework not in expected_tests:
                raise ValueError("test framework does not match runtime language")
            if (
                self.environment.runtime.language is RuntimeLanguage.NODE
                and self.environment.runtime.package_manager is PackageManager.NONE
                and self.dependencies.status == "known"
            ):
                raise ValueError("node+none cannot have a known dependency closure")
        production = self.lifecycle.status in {
            TaskStatus.PACKAGED,
            TaskStatus.ORACLE_PASSED,
            TaskStatus.CONTROLS_PASSED,
            TaskStatus.REVIEWED,
            TaskStatus.PILOTED,
            TaskStatus.PUBLISHED,
        }
        if production:
            if self.environment.status != "known" or self.dependencies.status != "known":
                raise ValueError("production lifecycle requires known environment and dependencies")
            if self.source.status.value != "known":
                raise ValueError("production lifecycle requires known source provenance")
            if (
                self.tests.expected_total_source != "frozen-collection"
                or self.tests.expected_total <= 0
                or self.tests.commands_artifact is None
            ):
                raise ValueError("production lifecycle requires a frozen test command plan")
            if self.verifier is None and self.tests.test_bundle is None:
                raise ValueError("production lifecycle requires a private test or verifier bundle")
        if (
            self.oracle_bundle is not None
            and self.oracle_bundle.visibility is not Visibility.PRIVATE
        ):
            raise ValueError("oracle_bundle must be private")
        return self

    def to_manifest(self, instruction: ArtifactRef) -> TaskManifest:
        """Project a validated source into the single canonical manifest shape."""

        if instruction.visibility is not Visibility.PUBLIC:
            raise ValueError("compiled instruction artifact must be public")
        harbor = self.harbor
        if harbor is not None:
            harbor = harbor.apply_network_policy(self.environment.network_policy)
        return TaskManifest(
            task_id=self.task_id,
            version=self.version,
            metadata=self.metadata,
            instruction=instruction,
            source_lock=self.source,
            environment_lock=self.environment,
            dependency_bundle=self.dependencies,
            tests=self.tests,
            metric=self.metric,
            lifecycle=self.lifecycle,
            harbor=harbor,
            oracle_bundle=self.oracle_bundle,
            verifier=self.verifier,
        )


class TaskManifest(CanonicalRecord):
    """Canonical compiled manifest with public instruction artifact."""

    model_config = ConfigDict(json_schema_extra=_manifest_contract_schema())

    task_id: TaskId
    version: str = "1.0.0"
    metadata: TaskMetadata
    instruction: ArtifactRef
    source_lock: SourceLock = Field(default_factory=SourceLock)
    environment_lock: EnvironmentLock
    dependency_bundle: DependencyBundle
    tests: TestManifest
    metric: MetricContract = Field(default_factory=MetricContract)
    lifecycle: TaskLifecycleRecord = Field(default_factory=TaskLifecycleRecord)
    harbor: HarborExecutionProfile | None = None
    oracle_bundle: ArtifactRef | None = None
    verifier: TaskVerifierSpec | None = None

    def publication_gaps(self) -> tuple[str, ...]:
        """Return stable canonical field paths that block production output."""

        gaps: list[str] = []
        if self.metadata.difficulty == "unknown":
            gaps.append("metadata.difficulty")
        if self.metadata.category == "unknown":
            gaps.append("metadata.category")
        if self.instruction.visibility is not Visibility.PUBLIC:
            gaps.append("instruction.visibility=public")
        if self.source_lock.status.value != "known":
            gaps.append("source_lock.status=known")
        for name, value in {
            "source_lock.upstream_url": self.source_lock.upstream_url,
            "source_lock.revision": self.source_lock.revision,
            "source_lock.license_spdx": self.source_lock.license_spdx,
            "source_lock.source_digest": self.source_lock.source_digest,
        }.items():
            if not value:
                gaps.append(name)
        if self.environment_lock.status != "known":
            gaps.append("environment_lock.status=known")
        if self.environment_lock.runtime is None:
            gaps.append("environment_lock.runtime")
        if self.dependency_bundle.status != "known":
            gaps.append("dependency_bundle.status=known")
        for field_name, reference in (
            ("dependency_bundle.lock", self.dependency_bundle.lock),
            ("dependency_bundle.offline_store", self.dependency_bundle.offline_store),
            ("dependency_bundle.inventory", self.dependency_bundle.inventory),
        ):
            if reference is None:
                gaps.append(field_name)
            elif reference.visibility is not Visibility.PRIVATE:
                gaps.append(f"{field_name}.visibility=private")
        if self.tests.expected_total_source != "frozen-collection":
            gaps.append("tests.expected_total_source=frozen-collection")
        if self.tests.expected_total <= 0:
            gaps.append("tests.expected_total>0")
        if self.tests.commands_artifact is None:
            gaps.append("tests.commands_artifact")
        if self.verifier is None and self.tests.test_bundle is None:
            gaps.append("tests.test_bundle")
        if self.metric.contract_id != "fixed-test-pass-rate-v1":
            gaps.append("metric.contract_id=fixed-test-pass-rate-v1")
        if self.harbor is None:
            gaps.append("harbor")
        if self.oracle_bundle is None:
            gaps.append("oracle_bundle")
        elif self.oracle_bundle.visibility is not Visibility.PRIVATE:
            gaps.append("oracle_bundle.visibility=private")
        return tuple(gaps)

    @model_validator(mode="after")
    def validate_runtime_contract(self) -> TaskManifest:
        if self.instruction.visibility is not Visibility.PUBLIC:
            raise ValueError("compiled instruction artifact must be public")
        runtime = self.environment_lock.runtime
        if self.tests.framework == "custom" and self.verifier is None:
            raise ValueError("custom tests require a typed verifier specification")
        if (
            self.tests.framework not in {"custom", "go-bridge", "rust-harness"}
            and self.verifier is not None
        ):
            raise ValueError(
                "typed verifier is only valid for custom, go-bridge, and rust-harness tests"
            )
        if runtime is not None:
            if runtime.language.value != self.metadata.language.value:
                raise ValueError("metadata language must match environment runtime")
            if runtime.package_manager != self.dependency_bundle.package_manager:
                raise ValueError("dependency package manager must match environment runtime")
            expected_tests = {
                RuntimeLanguage.PYTHON: ("pytest", "custom"),
                RuntimeLanguage.NODE: ("node:test",),
                RuntimeLanguage.GO: ("go-bridge",),
                RuntimeLanguage.RUST: ("rust-harness",),
                RuntimeLanguage.JAVA: ("junit-platform",),
            }[runtime.language]
            if self.tests.framework not in expected_tests:
                raise ValueError("test framework does not match runtime language")
            if (
                runtime.language is RuntimeLanguage.NODE
                and runtime.package_manager is PackageManager.NONE
                and self.dependency_bundle.status == "known"
            ):
                raise ValueError("node+none cannot have a known dependency closure")
        production = self.lifecycle.status in {
            TaskStatus.PACKAGED,
            TaskStatus.ORACLE_PASSED,
            TaskStatus.CONTROLS_PASSED,
            TaskStatus.REVIEWED,
            TaskStatus.PILOTED,
            TaskStatus.PUBLISHED,
        }
        if production:
            if self.environment_lock.status != "known" or self.dependency_bundle.status != "known":
                raise ValueError("production lifecycle requires known environment and dependencies")
            if self.source_lock.status.value != "known":
                raise ValueError("production lifecycle requires known source provenance")
            if (
                self.tests.expected_total_source != "frozen-collection"
                or self.tests.expected_total <= 0
                or self.tests.commands_artifact is None
            ):
                raise ValueError("production lifecycle requires a frozen test command plan")
            if self.verifier is None and self.tests.test_bundle is None:
                raise ValueError("production lifecycle requires a private test or verifier bundle")
        if (
            self.oracle_bundle is not None
            and self.oracle_bundle.visibility is not Visibility.PRIVATE
        ):
            raise ValueError("oracle_bundle must be private")
        return self


__all__ = [
    "DependencyBundle",
    "EnvironmentLock",
    "PackageManager",
    "RuntimeLanguage",
    "RuntimeProfile",
    "TaskManifest",
    "TaskMetadata",
    "TaskSource",
    "TestManifest",
]
