from __future__ import annotations

from pathlib import Path

import pytest

from nl2repobench.verification.java_candidate import (
    JavaWorkspaceRejected,
    validate_java_workspace,
)


def _workspace(tmp_path: Path) -> Path:
    root = tmp_path / "candidate"
    source = root / "src/main/java/example"
    source.mkdir(parents=True)
    (source / "Api.java").write_text("package example; public class Api {}\n", encoding="utf-8")
    (root / "pom.xml").write_text(
        "<project><artifactId>candidate</artifactId><version>1.0.0</version></project>",
        encoding="utf-8",
    )
    return root


def test_java_workspace_accepts_main_sources_and_static_pom(tmp_path: Path) -> None:
    result = validate_java_workspace(_workspace(tmp_path))

    assert result["java_files"] == 1
    assert result["pom_present"] is True


@pytest.mark.parametrize(
    "relative", ["target/Api.class", ".mvn/extensions.xml", "mvnw", "src/test/java/ApiTest.java"]
)
def test_java_workspace_rejects_build_and_test_assets(tmp_path: Path, relative: str) -> None:
    root = _workspace(tmp_path)
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("unsafe", encoding="utf-8")

    with pytest.raises(JavaWorkspaceRejected):
        validate_java_workspace(root)


@pytest.mark.parametrize("relative", ["src/main/resources/native.so", "src/main/resources/tool.sh"])
def test_java_workspace_rejects_native_and_script_resources(tmp_path: Path, relative: str) -> None:
    root = _workspace(tmp_path)
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("unsafe", encoding="utf-8")

    with pytest.raises(JavaWorkspaceRejected, match="resource type"):
        validate_java_workspace(root)
