from __future__ import annotations

import json
from pathlib import Path

import pytest

from nl2repobench.domain.models import ArtifactRef, TaskVerifierSpec, Visibility
from nl2repobench.verification.custom_verifier import run


def _private_bundle() -> ArtifactRef:
    return ArtifactRef(
        digest="sha256:" + "a" * 64,
        size_bytes=1,
        uri="artifact://private/sha256:" + "a" * 64,
        visibility=Visibility.PRIVATE,
    )


def test_custom_verifier_requires_private_bundle_and_safe_entrypoint() -> None:
    spec = TaskVerifierSpec(bundle=_private_bundle(), entrypoint="run.py")
    assert spec.protocol == "custom-json-v1"
    with pytest.raises(ValueError, match="artifact URI"):
        TaskVerifierSpec(
            bundle=_private_bundle().model_copy(update={"visibility": Visibility.PUBLIC}),
        )
    with pytest.raises(ValueError, match="safe relative"):
        TaskVerifierSpec(bundle=_private_bundle(), entrypoint="../run.py")


def test_custom_verifier_writes_fixed_collection_and_junit(tmp_path: Path) -> None:
    entrypoint = tmp_path / "run.py"
    entrypoint.write_text(
        "import json\n"
        "print(json.dumps({'schema_version': '1.0', 'leaves': ["
        "{'id': 'a', 'status': 'passed'}, {'id': 'b', 'status': 'failed', 'message': 'no'}]}))\n",
        encoding="utf-8",
    )
    junit = tmp_path / "junit.xml"
    collection = tmp_path / "collection.json"

    assert run(entrypoint, 2, junit, collection, 10.0) == 1
    assert json.loads(collection.read_text(encoding="utf-8"))["collected"] == 2
    assert junit.is_file()


def test_custom_verifier_rejects_duplicate_leaf_ids(tmp_path: Path) -> None:
    entrypoint = tmp_path / "run.py"
    entrypoint.write_text(
        "print('{\"schema_version\":\"1.0\",\"leaves\":['"
        "'{\"id\":\"a\",\"status\":\"passed\"},'"
        "'{\"id\":\"a\",\"status\":\"passed\"}]}')\n",
        encoding="utf-8",
    )

    assert run(entrypoint, 2, tmp_path / "junit.xml", tmp_path / "collection.json", 10.0) == 70
