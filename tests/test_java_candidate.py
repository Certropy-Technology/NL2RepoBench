from __future__ import annotations

import sys
from pathlib import Path

import pytest

from nl2repobench.verification import java_candidate
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


def test_java_workspace_accepts_bounded_resource(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    resource = root / "src/main/resources/example/config.json"
    resource.parent.mkdir(parents=True)
    resource.write_text("{}\n", encoding="utf-8")

    result = validate_java_workspace(root)

    assert result["java_files"] == 1
    assert result["total_bytes"] > 0


def test_java_workspace_rejects_symlink_executable_and_empty_source(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    source = root / "src/main/java/example/Api.java"
    source.unlink()
    source.symlink_to(root / "pom.xml")
    with pytest.raises(JavaWorkspaceRejected, match="symlink"):
        validate_java_workspace(root)

    source.unlink()
    source.write_text("class Api {}\n", encoding="utf-8")
    source.chmod(0o755)
    with pytest.raises(JavaWorkspaceRejected, match="executable"):
        validate_java_workspace(root)

    source.unlink()
    with pytest.raises(JavaWorkspaceRejected, match="contains no"):
        validate_java_workspace(root)


def test_java_workspace_rejects_count_and_size_limits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _workspace(tmp_path)
    monkeypatch.setattr(java_candidate, "MAX_JAVA_FILES", 0)
    with pytest.raises(JavaWorkspaceRejected, match="too many"):
        validate_java_workspace(root)

    monkeypatch.setattr(java_candidate, "MAX_JAVA_FILES", 10)
    monkeypatch.setattr(java_candidate, "MAX_JAVA_SOURCE_BYTES", 1)
    with pytest.raises(JavaWorkspaceRejected, match="too large"):
        validate_java_workspace(root)


def test_java_candidate_cli_returns_bounded_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "missing"
    monkeypatch.setattr(sys, "argv", ["java-candidate", "--root", str(missing)])

    with pytest.raises(SystemExit) as raised:
        java_candidate.main()

    assert raised.value.code == 20
    assert "root is not a directory" in capsys.readouterr().out
