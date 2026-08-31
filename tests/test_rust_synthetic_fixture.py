from __future__ import annotations

import tomllib
from pathlib import Path

from nl2repobench.package_managers import CargoPackageManager

ROOT = Path(__file__).parent / "fixtures/rust-cargo-r0/synthetic"


def test_development_rust_fixture_is_one_explicit_package() -> None:
    manifest = tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))

    assert "workspace" not in manifest
    assert manifest["package"] == {
        "name": "nl2repo-rust-synthetic",
        "version": "0.0.0",
        "edition": "2021",
        "build": False,
        "autolib": False,
        "autobins": False,
        "autoexamples": False,
        "autotests": False,
        "autobenches": False,
    }
    assert manifest["lib"] == {"path": "src/lib.rs"}
    assert manifest["bin"] == [
        {"name": "nl2repo-rust-synthetic", "path": "src/bin/main.rs"}
    ]
    assert manifest["dependencies"] == {}
    assert not (ROOT / "build.rs").exists()
    assert not (ROOT / ".cargo").exists()


def test_development_rust_fixture_lock_uses_cargo_v4_identity(tmp_path: Path) -> None:
    (tmp_path / "Cargo.lock").write_bytes((ROOT / "Cargo.lock").read_bytes())

    summary = CargoPackageManager().validate_lock(tmp_path, "1.100.0-nightly")

    assert [(item.name, item.version, item.kind) for item in summary.resolved] == [
        ("nl2repo-rust-synthetic", "0.0.0", "cargo-root")
    ]
