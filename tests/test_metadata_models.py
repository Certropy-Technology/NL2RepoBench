from __future__ import annotations

import pytest
from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validate as validate_json_schema
from pydantic import ValidationError

from nl2repobench.domain.models import (
    ArtifactRef,
    DependencyBundle,
    EnvironmentLock,
    HarborExecutionProfile,
    ProvenanceStatus,
    SourceLock,
    TaskLifecycleRecord,
    TaskManifest,
    TaskStatus,
    Visibility,
)
from nl2repobench.domain.models import (
    TestManifest as ManifestTests,
)


def test_canonical_digest_does_not_depend_on_field_order() -> None:
    uri = "artifact://public/sha256:" + "a" * 64
    left = ArtifactRef(digest="sha256:" + "a" * 64, size_bytes=3, uri=uri)
    right = ArtifactRef.model_validate(
        {"uri": uri, "size_bytes": 3, "digest": "sha256:" + "a" * 64}
    )

    assert left.content_digest() == right.content_digest()


def test_known_source_requires_provenance() -> None:
    with pytest.raises(ValidationError, match="known source provenance"):
        SourceLock(status=ProvenanceStatus.KNOWN)


def test_artifact_uri_cannot_downgrade_visibility() -> None:
    with pytest.raises(ValidationError, match="must match visibility"):
        ArtifactRef(
            digest="sha256:" + "d" * 64,
            size_bytes=1,
            uri="artifact://private/sha256:" + "d" * 64,
            visibility=Visibility.PUBLIC,
        )


def test_known_environment_requires_image_digest() -> None:
    with pytest.raises(ValidationError, match="known environment"):
        EnvironmentLock(
            status=ProvenanceStatus.KNOWN,
            python_version="3.12",
            os_name="linux",
            base_image="python:3.12-slim",
        )


def test_known_dependencies_require_lock_store_and_inventory() -> None:
    artifact = ArtifactRef(
        digest="sha256:" + "e" * 64,
        size_bytes=1,
        uri="artifact://private/sha256:" + "e" * 64,
        visibility=Visibility.PRIVATE,
    )

    with pytest.raises(ValidationError, match="lock, offline_store, and inventory"):
        DependencyBundle(
            status=ProvenanceStatus.KNOWN,
            package_manager="pip",
            lock=artifact,
        )

    bundle = DependencyBundle(
        status=ProvenanceStatus.KNOWN,
        package_manager="pip",
        lock=artifact,
        offline_store=artifact,
        inventory=artifact,
    )
    assert bundle.lock == artifact


def test_dependency_artifacts_must_be_private() -> None:
    private = ArtifactRef(
        digest="sha256:" + "f" * 64,
        size_bytes=1,
        uri="artifact://private/sha256:" + "f" * 64,
        visibility=Visibility.PRIVATE,
    )
    public = private.model_copy(
        update={
            "uri": "artifact://public/sha256:" + "f" * 64,
            "visibility": Visibility.PUBLIC,
        }
    )

    bundle = DependencyBundle(
        status=ProvenanceStatus.KNOWN,
        package_manager="go-modules",
        lock=private,
        offline_store=private,
        inventory=private,
    )
    assert bundle.offline_store == private
    with pytest.raises(ValidationError, match="offline_store must be private"):
        DependencyBundle(
            status=ProvenanceStatus.KNOWN,
            package_manager="go-modules",
            lock=private,
            offline_store=public,
            inventory=private,
        )


def test_known_go_environment_accepts_runtime_version() -> None:
    environment = EnvironmentLock(
        status=ProvenanceStatus.KNOWN,
        runtime_version="1.26.5",
        os_name="debian-bookworm",
        base_image="docker.io/library/golang@sha256:" + "a" * 64,
        base_image_digest="sha256:" + "a" * 64,
    )

    assert environment.python_version is None
    assert environment.runtime_version == "1.26.5"


def test_blocked_task_requires_reason() -> None:
    with pytest.raises(ValidationError, match="require a reason"):
        TaskLifecycleRecord(status=TaskStatus.BLOCKED)


def test_blocked_task_can_record_unfrozen_collection() -> None:
    tests = ManifestTests(expected_total=0, expected_total_source="unknown")

    assert tests.commands == ()
    assert tests.expected_total == 0

    instruction = ArtifactRef(
        digest="sha256:" + "b" * 64,
        size_bytes=1,
        uri="artifact://public/sha256:" + "b" * 64,
        visibility=Visibility.PUBLIC,
    )
    manifest = TaskManifest(
        task_id="blocked-unfrozen",
        instruction=instruction,
        tests=tests,
        lifecycle=TaskLifecycleRecord(status=TaskStatus.BLOCKED, reason="source freeze failed"),
    )
    assert "tests.expected_total>0" in manifest.publication_gaps()


def test_published_lifecycle_requires_auditable_evidence() -> None:
    with pytest.raises(ValidationError, match="published lifecycle is missing"):
        TaskLifecycleRecord(status=TaskStatus.PUBLISHED)


def test_manifest_explains_publication_gaps() -> None:
    instruction = ArtifactRef(
        digest="sha256:" + "c" * 64,
        size_bytes=1,
        uri="artifact://public/sha256:" + "c" * 64,
        visibility=Visibility.PUBLIC,
    )
    manifest = TaskManifest.model_validate(
        {
            "task_id": "incomplete",
            "instruction": instruction.model_dump(mode="json"),
            "tests": {"expected_total": 1, "commands": ["pytest"]},
        }
    )

    assert "source_lock.status=known" in manifest.publication_gaps()
    assert "tests.test_bundle" in manifest.publication_gaps()


def test_source_json_schema_enforces_known_provenance_fields() -> None:
    schema = SourceLock.model_json_schema()

    with pytest.raises(JsonSchemaValidationError):
        validate_json_schema(
            {"schema_version": "1.0", "status": "known"},
            schema,
        )
    assert schema["x-nl2repobench-runtime-validation"] is True
    assert schema["x-nl2repobench-model"] == "SourceLock"


def test_conditional_schemas_accept_runtime_defaults() -> None:
    for model in (SourceLock, EnvironmentLock, DependencyBundle, TaskLifecycleRecord):
        validate_json_schema({}, model.model_json_schema())
        model.model_validate({})


def test_harbor_profile_reserves_time_for_verifier_cleanup() -> None:
    with pytest.raises(ValidationError, match="60s reserve"):
        HarborExecutionProfile(
            description="budget boundary",
            keywords=("python", "pytest", "harbor"),
            verifier_timeout_sec=100.0,
            candidate_install_timeout_sec=20.0,
            candidate_total_timeout_sec=20.0,
        )
