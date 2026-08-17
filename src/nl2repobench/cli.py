"""Typer CLI for the metadata core.

Commands are intentionally thin orchestration adapters. Domain validation and
storage behavior live in importable modules so CI and future authoring stages
do not need to shell out to the CLI.
"""

from __future__ import annotations

import importlib.metadata
import json
import shutil
import sys
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel

from nl2repobench.authoring.catalog import (
    CatalogCompiler,
    CatalogError,
    DeclarativeDatasetSource,
    DeclarativeTaskSource,
    scaffold_task,
    validate_compiled_dataset,
)
from nl2repobench.domain.canonical import canonical_file_payload, canonical_json
from nl2repobench.domain.models import (
    DatasetManifest,
    MetadataGapReport,
    TaskManifest,
)
from nl2repobench.legacy.importer import LegacyImporter, LegacyImportError
from nl2repobench.storage.artifacts import FileArtifactStore
from nl2repobench.storage.state import StateStore

app = typer.Typer(
    name="nl2repo",
    help="Authoring metadata and reproducibility tools for NL2RepoBench.",
    no_args_is_help=True,
)
task_app = typer.Typer(help="Inspect and import task manifests.", no_args_is_help=True)
dataset_app = typer.Typer(help="Validate and inspect dataset manifests.", no_args_is_help=True)
schema_app = typer.Typer(help="Export versioned JSON Schemas.", no_args_is_help=True)
app.add_typer(task_app, name="task")
app.add_typer(dataset_app, name="dataset")
app.add_typer(schema_app, name="schema")


def _json_print(value: object) -> None:
    typer.echo(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))


@schema_app.command("export")
def export_schemas(
    output: Annotated[
        Path,
        typer.Option("--output", help="Directory for generated JSON Schemas."),
    ] = Path("schemas/v1"),
) -> None:
    """Export the machine-readable v1 schemas used by CI and other tools."""

    models: dict[str, type[BaseModel]] = {
        "task-manifest.schema.json": TaskManifest,
        "dataset-manifest.schema.json": DatasetManifest,
        "metadata-gap-report.schema.json": MetadataGapReport,
        "declarative-task-source.schema.json": DeclarativeTaskSource,
        "declarative-dataset-source.schema.json": DeclarativeDatasetSource,
    }
    output.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for filename, model in models.items():
        path = output / filename
        path.write_text(
            json.dumps(model.model_json_schema(), ensure_ascii=False, sort_keys=True, indent=2)
            + "\n",
            encoding="utf-8",
        )
        paths.append(str(path))
    _json_print({"schema_version": "1.0", "files": paths})


@app.command()
def doctor() -> None:
    """Check the Phase 1 runtime without contacting external services."""

    packages: dict[str, str] = {}
    for package in ("nl2repobench", "pydantic", "polars", "typer"):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = "missing"
    _json_print(
        {
            "python": sys.version.split()[0],
            "uv": shutil.which("uv") is not None,
            "packages": packages,
            "cwd": str(Path.cwd()),
        }
    )


@task_app.command("scaffold")
def scaffold_catalog_task(
    task_id: Annotated[str, typer.Argument(help="Stable task identifier.")],
    root: Annotated[
        Path,
        typer.Option("--root", help="Human-facing task catalog root."),
    ] = Path("catalog/tasks"),
) -> None:
    """Create a minimal declarative TOML/Markdown task source."""

    try:
        target = scaffold_task(root, task_id)
    except (CatalogError, OSError) as exc:
        typer.echo(f"scaffold failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print({"task_id": task_id, "source": str(target)})


@task_app.command("validate-source")
def validate_task_source(
    source: Annotated[
        Path,
        typer.Argument(help="Task source directory containing task.toml."),
    ],
) -> None:
    """Validate the Human-facing TOML source without compiling artifacts."""

    try:
        parsed = CatalogCompiler.load_task(source)
    except CatalogError as exc:
        typer.echo(f"invalid task source: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(
        {
            "task_id": parsed.task_id,
            "version": parsed.version,
            "instruction": str(source / parsed.instruction),
            "status": parsed.lifecycle.status.value,
            "source_digest": parsed.content_digest(),
        }
    )


@task_app.command("compile")
def compile_catalog_task(
    source: Annotated[
        Path,
        typer.Argument(help="Task source directory containing task.toml."),
    ],
    output_root: Annotated[
        Path,
        typer.Option("--output", help="Canonical manifest output root."),
    ] = Path("build/catalog"),
    artifact_root: Annotated[
        Path,
        typer.Option("--artifact-root", help="Content-addressed artifact directory."),
    ] = Path(".nl2repo/artifacts"),
    state_db: Annotated[
        Path,
        typer.Option("--state-db", help="SQLite state index path."),
    ] = Path(".nl2repo/state.db"),
) -> None:
    """Compile a declarative task source into canonical JSON."""

    try:
        with StateStore(state_db) as state:
            compiled = CatalogCompiler(
                FileArtifactStore(artifact_root), state_store=state
            ).compile_task(source, output_root)
    except (CatalogError, OSError, ValueError) as exc:
        typer.echo(f"compile failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(
        {
            "task_id": compiled.manifest.task_id,
            "manifest": str(compiled.path),
            "digest": compiled.reference.manifest_digest,
        }
    )


@task_app.command("import-legacy")
def import_legacy(
    legacy_root: Annotated[
        Path,
        typer.Option("--legacy-root", help="Historical test_files directory."),
    ] = Path("test_files"),
    output_root: Annotated[
        Path,
        typer.Option("--output", help="Directory for canonical task manifests."),
    ] = Path("authoring"),
    artifact_root: Annotated[
        Path,
        typer.Option("--artifact-root", help="Content-addressed artifact directory."),
    ] = Path(".nl2repo/artifacts"),
    state_db: Annotated[
        Path,
        typer.Option("--state-db", help="SQLite state index path."),
    ] = Path(".nl2repo/state.db"),
    difficulty_file: Annotated[
        Path | None,
        typer.Option("--difficulty-file", help="Optional task difficulty CSV."),
    ] = Path("test_files/task_difficulty.csv"),
    report: Annotated[
        Path | None,
        typer.Option("--report", help="Optional metadata gap report path."),
    ] = None,
) -> None:
    """Import legacy task directories without embedding private test bytes."""

    if difficulty_file is not None and not difficulty_file.is_file():
        difficulty_file = None
    try:
        with StateStore(state_db) as state:
            summary = LegacyImporter(
                legacy_root=legacy_root,
                output_root=output_root,
                artifact_store=FileArtifactStore(artifact_root),
                difficulty_file=difficulty_file,
                state_store=state,
            ).run(gap_report_path=report)
    except (LegacyImportError, OSError, ValueError) as exc:
        typer.echo(f"import failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(summary.as_dict())


@task_app.command("validate")
def validate_task(
    manifest: Annotated[Path, typer.Argument(help="Path to a canonical manifest.json.")],
) -> None:
    """Validate a task manifest and its canonical byte representation."""

    try:
        raw = canonical_file_payload(manifest.read_bytes())
        parsed = TaskManifest.model_validate_json(raw)
        canonical = canonical_json(parsed)
        canonical_match = raw == canonical
    except (OSError, ValueError) as exc:
        typer.echo(f"invalid manifest: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(
        {
            "path": str(manifest),
            "task_id": parsed.task_id,
            "version": parsed.version,
            "status": parsed.lifecycle.status.value,
            "content_digest": parsed.content_digest(),
            "canonical_bytes": canonical_match,
        }
    )
    if not canonical_match:
        raise typer.Exit(code=1)


@dataset_app.command("validate")
def validate_dataset(
    root: Annotated[
        Path, typer.Argument(help="Directory containing task manifest subdirectories.")
    ],
) -> None:
    """Validate every task manifest in a canonical authoring directory."""

    errors = validate_compiled_dataset(root)
    _json_print(
        {
            "root": str(root),
            "manifest_count": len(list(root.glob("*/manifest.json"))),
            "errors": errors,
        }
    )
    if errors:
        raise typer.Exit(code=1)


@dataset_app.command("compile")
def compile_catalog_dataset(
    source: Annotated[
        Path,
        typer.Argument(help="Dataset source TOML containing relative task paths."),
    ],
    output_root: Annotated[
        Path,
        typer.Option("--output", help="Canonical dataset output root."),
    ] = Path("build/catalog"),
    artifact_root: Annotated[
        Path,
        typer.Option("--artifact-root", help="Content-addressed artifact directory."),
    ] = Path(".nl2repo/artifacts"),
    state_db: Annotated[
        Path,
        typer.Option("--state-db", help="SQLite state index path."),
    ] = Path(".nl2repo/state.db"),
) -> None:
    """Compile a declarative dataset and every referenced task source."""

    try:
        with StateStore(state_db) as state:
            dataset = CatalogCompiler(
                FileArtifactStore(artifact_root), state_store=state
            ).compile_dataset(source, output_root)
    except (CatalogError, OSError, ValueError) as exc:
        typer.echo(f"dataset compile failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(
        {
            "dataset_id": dataset.dataset_id,
            "version": dataset.version,
            "task_count": len(dataset.tasks),
            "manifest": str(output_root / "dataset.manifest.json"),
            "digest": dataset.content_digest(),
        }
    )


@task_app.command("show")
def show_task(
    manifest: Annotated[Path, typer.Argument(help="Path to a canonical manifest.json.")],
) -> None:
    """Print a canonical task manifest for human or machine inspection."""

    try:
        parsed = TaskManifest.model_validate_json(manifest.read_bytes())
    except (OSError, ValueError) as exc:
        typer.echo(f"invalid manifest: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(parsed.model_dump(mode="json", exclude_none=True))
