from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/discover_java_candidates.py"
    spec = importlib.util.spec_from_file_location("discover_java_candidates", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


discover = _load_script()


def test_repository_and_seed_normalization() -> None:
    assert (
        discover._normalize_repository("git+https://github.com/vdurmont/semver4j.git")
        == "vdurmont/semver4j"
    )
    assert discover._parse_seed("java-semver=vdurmont/semver4j") == (
        "java-semver",
        "vdurmont/semver4j",
    )
    assert discover._parse_seed("java-diff-utils/java-diff-utils") == (
        "java-java-diff-utils",
        "java-diff-utils/java-diff-utils",
    )


def test_inspect_checkout_accepts_single_module_java_project(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").write_text(
        """<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId>
<artifactId>demo</artifactId><version>1.0.0</version><packaging>jar</packaging>
<properties><maven.compiler.release>17</maven.compiler.release></properties></project>""",
        encoding="utf-8",
    )
    source = tmp_path / "src/main/java/example"
    source.mkdir(parents=True)
    (source / "Demo.java").write_text("public final class Demo {}\n", encoding="utf-8")
    tests = tmp_path / "src/test/java/example"
    tests.mkdir(parents=True)
    (tests / "DemoTest.java").write_text("@Test void testDemo() {}\n", encoding="utf-8")

    result = discover._inspect_checkout(tmp_path)

    assert result["pom_release"] == 17
    assert result["test_count"] == 2
    assert result["public_symbols"] == 1
    assert result["profile_eligible"] is True


def test_inspect_checkout_rejects_multi_module_dynamic_build(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").write_text(
        """<project><modules><module>child</module></modules><profiles /></project>""",
        encoding="utf-8",
    )

    result = discover._inspect_checkout(tmp_path)

    assert result["profile_eligible"] is False
    assert {"multi-module", "profiles", "custom-build", "no-java-tests"} <= set(
        result["risk_flags"]
    )


def test_inspect_checkout_treats_profiles_as_remediation_risk(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").write_text(
        """<project><profiles><profile><id>release</id></profile></profiles></project>""",
        encoding="utf-8",
    )
    source = tmp_path / "src/main/java/example"
    source.mkdir(parents=True)
    (source / "Demo.java").write_text("public final class Demo {}\n", encoding="utf-8")
    tests = tmp_path / "src/test/java/example"
    tests.mkdir(parents=True)
    (tests / "DemoTest.java").write_text("@Test void testDemo() {}\n", encoding="utf-8")

    result = discover._inspect_checkout(tmp_path)

    assert result["profile_eligible"] is True
    assert {"profiles", "custom-build"} <= set(result["risk_flags"])
