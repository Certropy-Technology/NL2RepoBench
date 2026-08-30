from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from nl2repobench.cli import app


def test_doctor_command() -> None:
    result = CliRunner().invoke(app, ["doctor"])

    assert result.exit_code == 0, result.stdout
    assert '"packages"' in result.stdout
    assert '"python"' in result.stdout


def test_schema_export_command(tmp_path) -> None:
    output = tmp_path / "schemas"
    result = CliRunner().invoke(app, ["schema", "export", "--output", str(output)])

    assert result.exit_code == 0, result.stdout
    assert (output / "task-manifest.schema.json").is_file()
    assert (output / "declarative-task-source.schema.json").is_file()
    tracked = Path(__file__).parents[1] / "schemas/v1"
    for generated in sorted(output.glob("*.json")):
        assert generated.read_bytes() == (tracked / generated.name).read_bytes()


def test_author_scan_commands_write_deterministic_inventory(tmp_path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "inventory-python"
    source_output = tmp_path / "source.json"
    result = CliRunner().invoke(
        app,
        ["author", "scan-source", str(fixture), "--output", str(source_output)],
    )
    assert result.exit_code == 0, result.stdout
    summary = json.loads(result.stdout)
    assert summary["stage"] == "scan-source"
    assert summary["metrics"]["test_count"] == 2
    assert json.loads(source_output.read_text(encoding="utf-8"))["language"] == "python"

    test_output = tmp_path / "tests.json"
    result = CliRunner().invoke(
        app,
        ["author", "scan-tests", str(fixture), "--output", str(test_output)],
    )
    assert result.exit_code == 0, result.stdout
    assert json.loads(result.stdout)["stage"] == "scan-tests"


def test_author_scan_rejects_unregistered_language(tmp_path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "inventory-python"
    result = CliRunner().invoke(
        app,
        ["author", "scan-source", str(fixture), "--language", "ruby"],
    )
    assert result.exit_code == 2
    assert "no local scanner" in result.stderr


def test_public_cli_does_not_expose_legacy_import() -> None:
    result = CliRunner().invoke(app, ["task", "import-legacy"])

    assert result.exit_code != 0
    assert "No such command" in result.output
