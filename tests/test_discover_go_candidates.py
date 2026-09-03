from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script():
    path = Path(__file__).parents[1] / "scripts/discover_go_candidates.py"
    spec = importlib.util.spec_from_file_location("discover_go_candidates", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


discover = _load_script()


def test_repository_and_seed_normalization() -> None:
    assert discover._normalize_repository(
        "git+https://github.com/tidwall/gjson.git"
    ) == "tidwall/gjson"
    assert discover._parse_seed("go-json-query=tidwall/gjson") == (
        "go-json-query",
        "tidwall/gjson",
    )
    assert discover._parse_seed("google/uuid") == ("go-uuid", "google/uuid")


def test_inspect_checkout_accepts_pure_single_module(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text(
        "module example.com/demo\n\ngo 1.24.0\n", encoding="utf-8"
    )
    (tmp_path / "demo.go").write_text(
        "package demo\n\ntype Value struct{}\nfunc Parse() {}\n", encoding="utf-8"
    )
    (tmp_path / "demo_test.go").write_text(
        "package demo\n\nfunc TestParse(t *testing.T) {}\nfunc ExampleParse() {}\n",
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")

    result = discover._inspect_checkout(tmp_path)

    assert result["module_path"] == "example.com/demo"
    assert result["test_count"] == 2
    assert result["public_symbols"] == 2
    assert result["profile_eligible"] is True
    assert result["risk_flags"] == []
    assert result["license_file"] == "LICENSE"


def test_inspect_checkout_rejects_foundation_profile_risks(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text(
        "module example.com/demo\n\nreplace example.com/other => ../other\n",
        encoding="utf-8",
    )
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "go.mod").write_text("module example.com/nested\n", encoding="utf-8")
    (tmp_path / "demo.go").write_text(
        'package demo\n//go:generate stringer -type X\nimport "C"\n', encoding="utf-8"
    )

    result = discover._inspect_checkout(tmp_path)

    assert result["profile_eligible"] is False
    assert {"cgo", "go-generate", "local-replace", "multi-module", "no-go-tests"} <= set(
        result["risk_flags"]
    )


def test_license_spdx_uses_auditable_file_when_api_has_no_assertion(
    tmp_path: Path,
) -> None:
    license_path = tmp_path / "LICENSE"
    license_path.write_text(
        "Permission is hereby granted, free of charge, to any person obtaining a copy",
        encoding="utf-8",
    )

    assert discover._license_spdx(
        {"license": {"spdx_id": "NOASSERTION"}}, license_path
    ) == "MIT"


def test_main_treats_archived_repository_as_rejected_not_discovery_failure(
    tmp_path: Path, monkeypatch
) -> None:
    output = tmp_path / "report.json"
    monkeypatch.setattr(
        discover,
        "_load_seeds",
        lambda repositories, seed_files: [("go-old", "owner/old")],
    )
    monkeypatch.setattr(
        discover,
        "discover",
        lambda *args: (_ for _ in ()).throw(
            ValueError("repository is archived: owner/old")
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "discover_go_candidates.py",
            "--repository",
            "go-old=owner/old",
            "--output",
            str(output),
        ],
    )

    assert discover.main() == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["errors"] == []
    assert report["rejected"] == [
        {
            "package": "go-old",
            "repository": "owner/old",
            "reason": "ValueError: repository is archived: owner/old",
        }
    ]
