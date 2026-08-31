from __future__ import annotations

from pathlib import Path

import pytest

from nl2repobench.authoring.runtime_asset_registry import (
    JavaSourceAssetValidator,
    RuntimeSourceAssetError,
    RuntimeSourceAssetRegistry,
)
from nl2repobench.domain.canonical_contract import (
    DependencyBundle,
    EnvironmentLock,
    RuntimeProfile,
    TaskMetadata,
    TaskSource,
)
from nl2repobench.domain.canonical_contract import TestManifest as CanonicalTestManifest
from nl2repobench.domain.runtime import RuntimeDiscriminator


def _source() -> TaskSource:
    return TaskSource(
        task_id="java-profile",
        metadata=TaskMetadata(language="java"),
        environment=EnvironmentLock(
            status="unknown",
            runtime=RuntimeProfile(
                language="java",
                runtime="jdk",
                version="temurin-21.0.5+11",
                package_manager="maven",
                package_manager_version="3.9.9",
            ),
        ),
        dependencies=DependencyBundle(status="unknown", package_manager="maven"),
        tests=CanonicalTestManifest(
            framework="junit-platform",
            report_format="junit-open-test-report-xml-v1",
        ),
    )


def test_java_source_validator_is_registered_by_exact_identity() -> None:
    identity = RuntimeDiscriminator(language="java", package_manager="maven")
    validator = RuntimeSourceAssetRegistry.default().resolve(identity)
    assert isinstance(validator, JavaSourceAssetValidator)


def test_java_source_validator_accepts_only_source_roots(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    (source_dir / "src/main/java/example").mkdir(parents=True)
    (source_dir / "src/main/resources/config").mkdir(parents=True)
    (source_dir / "src/main/java/example/App.java").write_text(
        "package example;\n", encoding="utf-8"
    )
    (source_dir / "src/main/resources/config/app.properties").write_text(
        "mode=test\n", encoding="utf-8"
    )
    (source_dir / "instruction.md").write_text("# Java\n", encoding="utf-8")
    (source_dir / "task.toml").write_text("", encoding="utf-8")

    JavaSourceAssetValidator().validate_source_assets(source_dir, _source())


@pytest.mark.parametrize(
    "relative",
    [
        "target/classes/App.class",
        ".mvn/extensions.xml",
        "mvnw",
        "scripts/build.sh",
        "src/main/native/lib.so",
        "src/main/java/example/App.txt",
        "src/test/java/example/Unexpected.java",
        "README.md",
    ],
)
def test_java_source_validator_rejects_forbidden_or_outside_assets(
    tmp_path: Path, relative: str
) -> None:
    source_dir = tmp_path / "source"
    (source_dir / "src/main/java/example").mkdir(parents=True)
    (source_dir / "src/main/java/example/App.java").write_text(
        "package example;\n", encoding="utf-8"
    )
    path = source_dir / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("unsafe\n", encoding="utf-8")

    with pytest.raises(RuntimeSourceAssetError):
        JavaSourceAssetValidator().validate_source_assets(source_dir, _source())


def test_java_source_validator_rejects_symlink(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    (source_dir / "src/main/java/example").mkdir(parents=True)
    (source_dir / "src/main/java/example/App.java").write_text(
        "package example;\n", encoding="utf-8"
    )
    target = tmp_path / "outside.java"
    target.write_text("outside\n", encoding="utf-8")
    (source_dir / "src/main/java/example/Link.java").symlink_to(target)

    with pytest.raises(RuntimeSourceAssetError, match="symlinks"):
        JavaSourceAssetValidator().validate_source_assets(source_dir, _source())


def test_java_source_validator_preserves_exact_runtime_identity(tmp_path: Path) -> None:
    source = _source()
    bad = source.model_copy(
        update={
            "environment": source.environment.model_copy(
                update={
                    "runtime": source.environment.runtime.model_copy(
                        update={"version": "latest"}
                    )
                }
            )
        }
    )
    source_dir = tmp_path / "source"
    (source_dir / "src/main/java/example").mkdir(parents=True)
    (source_dir / "src/main/java/example/App.java").write_text(
        "package example;\n", encoding="utf-8"
    )

    with pytest.raises(RuntimeSourceAssetError, match="exact JDK 21"):
        JavaSourceAssetValidator().validate_source_assets(source_dir, bad)

