from __future__ import annotations

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
