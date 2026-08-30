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
import tomllib
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel

from nl2repobench.authoring.catalog import (
    CatalogCompiler,
    CatalogError,
    DeclarativeDatasetSource,
    scaffold_task,
    validate_compiled_dataset,
)
from nl2repobench.authoring.inventory import InventoryError, scan_python_source, write_inventory
from nl2repobench.authoring.network_lint import lint_catalog_roots
from nl2repobench.domain.canonical import canonical_file_payload, canonical_json
from nl2repobench.domain.canonical_contract import (
    TaskManifest as CanonicalTaskManifest,
)
from nl2repobench.domain.canonical_contract import (
    TaskSource as CanonicalTaskSource,
)
from nl2repobench.domain.canonical_models import (
    DatasetManifest,
    MetadataGapReport,
)
from nl2repobench.harbor.compiler import HarborCompileError
from nl2repobench.harbor.models import HarborToolchainLock
from nl2repobench.harbor.private_artifacts import compile_authorization
from nl2repobench.harbor.registry import (
    HarborCompilerRegistry,
    UnknownRuntimeAdapterError,
)
from nl2repobench.storage.artifacts import (
    FileArtifactStore,
    LocalArtifactResolver,
)
from nl2repobench.storage.state import StateStore
from nl2repobench.verification.models import CollectionReport, GradingResult

app = typer.Typer(
    name="nl2repo",
    help="Authoring metadata and reproducibility tools for NL2RepoBench.",
    no_args_is_help=True,
)
task_app = typer.Typer(help="Inspect and import task manifests.", no_args_is_help=True)
dataset_app = typer.Typer(help="Validate and inspect dataset manifests.", no_args_is_help=True)
schema_app = typer.Typer(help="Export versioned JSON Schemas.", no_args_is_help=True)
harbor_app = typer.Typer(help="Compile canonical tasks into Harbor bundles.", no_args_is_help=True)
author_app = typer.Typer(help="Run deterministic authoring inventory stages.", no_args_is_help=True)
app.add_typer(task_app, name="task")
app.add_typer(dataset_app, name="dataset")
app.add_typer(schema_app, name="schema")
app.add_typer(harbor_app, name="harbor")
app.add_typer(author_app, name="author")


def _json_print(value: object) -> None:
    typer.echo(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))


@author_app.command("scan-source")
def scan_authoring_source(
    source: Annotated[
        Path,
        typer.Argument(help="Candidate source root; candidate code is parsed, never imported."),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", help="Inventory JSON output path."),
    ] = Path("authoring/api-inventory.json"),
    language: Annotated[
        str,
        typer.Option("--language", help="Scanner language currently implemented: python."),
    ] = "python",
) -> None:
    """Create a deterministic static API/test inventory for one source root."""

    if language != "python":
        typer.echo(
            "no local scanner is registered for this language; use the language adapter tool",
            err=True,
        )
        raise typer.Exit(code=2)
    try:
        inventory = scan_python_source(source)
        write_inventory(inventory, output)
    except (InventoryError, OSError) as exc:
        typer.echo(f"source scan failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(
        {
            "stage": "scan-source",
            "language": inventory.language,
            "output": str(output),
            "source_digest": inventory.source_digest,
            "metrics": inventory.to_dict()["metrics"],
            "risk_flags": list(inventory.risk_flags),
        }
    )


@author_app.command("scan-tests")
def scan_authoring_tests(
    source: Annotated[
        Path,
        typer.Argument(help="Candidate source root containing source and test files."),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", help="Inventory JSON output path."),
    ] = Path("authoring/test-inventory.json"),
) -> None:
    """Write the static test portion of the source inventory."""

    try:
        inventory = scan_python_source(source)
        write_inventory(inventory, output)
    except (InventoryError, OSError) as exc:
        typer.echo(f"test scan failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(
        {
            "stage": "scan-tests",
            "language": inventory.language,
            "output": str(output),
            "source_digest": inventory.source_digest,
            "test_count": inventory.metrics.test_count,
            "test_files": inventory.metrics.test_files,
        }
    )


@schema_app.command("export")
def export_schemas(
    output: Annotated[
        Path,
        typer.Option("--output", help="Directory for generated JSON Schemas."),
    ] = Path("schemas/v1"),
    version: Annotated[
        str, typer.Option("--version", help="Current schema version (1.0).")
    ] = "1.0",
) -> None:
    """Export one immutable schema family without rewriting the other family."""

    if version == "1.0":
        models: dict[str, type[BaseModel]] = {
            "task-manifest.schema.json": CanonicalTaskManifest,
            "dataset-manifest.schema.json": DatasetManifest,
            "metadata-gap-report.schema.json": MetadataGapReport,
            "declarative-task-source.schema.json": CanonicalTaskSource,
            "declarative-dataset-source.schema.json": DeclarativeDatasetSource,
            "collection-report.schema.json": CollectionReport,
            "grading-result.schema.json": GradingResult,
            "harbor-toolchain-lock.schema.json": HarborToolchainLock,
        }
    else:
        raise typer.BadParameter("version must be 1.0")
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
    _json_print({"schema_version": version, "files": paths})


@schema_app.command("check")
def check_schemas(
    root: Annotated[
        Path,
        typer.Option("--root", help="Tracked canonical schema directory."),
    ] = Path("schemas/v1"),
) -> None:
    """Fail when checked-in canonical schemas are not generated from models."""

    import tempfile

    with tempfile.TemporaryDirectory(prefix="nl2repo-schema-"):
        # F0 has one current contract.  ``export`` remains the writer while
        # this command provides a reproducible CI gate for the tracked bytes.
        models: dict[str, type[BaseModel]] = {
            "task-manifest.schema.json": CanonicalTaskManifest,
            "dataset-manifest.schema.json": DatasetManifest,
            "metadata-gap-report.schema.json": MetadataGapReport,
            "declarative-task-source.schema.json": CanonicalTaskSource,
            "declarative-dataset-source.schema.json": DeclarativeDatasetSource,
            "collection-report.schema.json": CollectionReport,
            "grading-result.schema.json": GradingResult,
            "harbor-toolchain-lock.schema.json": HarborToolchainLock,
        }
        mismatches: list[str] = []
        for filename, model in models.items():
            expected = (
                json.dumps(model.model_json_schema(), ensure_ascii=False, sort_keys=True, indent=2)
                + "\n"
            )
            path = root / filename
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                mismatches.append(str(path))
    _json_print({"schema_version": "1.0", "root": str(root), "mismatches": mismatches})
    if mismatches:
        raise typer.Exit(code=1)


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


@harbor_app.command("compile")
def compile_harbor_task(
    source: Annotated[
        Path,
        typer.Argument(help="Declarative task source directory."),
    ],
    output_root: Annotated[
        Path,
        typer.Option("--output", help="Generated Harbor task root."),
    ] = Path("build/harbor"),
    toolchain: Annotated[
        Path,
        typer.Option("--toolchain", help="Pinned Harbor/toolchain lock."),
    ] = Path("toolchain.lock.toml"),
    artifact_root: Annotated[
        Path,
        typer.Option("--artifact-root", help="Content-addressed private artifact root."),
    ] = Path(".nl2repo/artifacts"),
    authorize_task_private_artifacts: Annotated[
        bool,
        typer.Option(
            "--authorize-task-private-artifacts",
            help="Authorize only private artifacts declared by this task.",
        ),
    ] = False,
    allow_incomplete: Annotated[
        bool,
        typer.Option(
            "--allow-incomplete",
            help="Compile a synthetic development fixture with public local assets.",
        ),
    ] = False,
) -> None:
    """Compile one declarative task into a deterministic Harbor bundle."""

    artifact_store = FileArtifactStore(artifact_root)
    authorization = None
    if authorize_task_private_artifacts:
        try:
            source_record = CanonicalTaskSource.model_validate(
                tomllib.loads((source / "task.toml").read_text(encoding="utf-8"))
            )
            instruction = artifact_store.put_file(
                source / source_record.instruction,
                media_type="text/markdown; charset=utf-8",
            )
            manifest = source_record.to_manifest(instruction)
            authorization = compile_authorization(
                manifest,
                compiled_root=Path(".nl2repo/compiled").resolve(),
            )
        except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
            typer.echo(f"private artifact authorization failed: {exc}", err=True)
            raise typer.Exit(code=1) from exc
    resolver = (
        LocalArtifactResolver.scoped_private(
            artifact_store,
            authorization,
            task_id=authorization.task_id,
            manifest_digest=authorization.manifest_digest,
            purpose="compile",
            staging_root=authorization.staging_root,
        )
        if authorization is not None
        else LocalArtifactResolver(artifact_store)
    )
    try:
        task_root = HarborCompilerRegistry.default().compile_task(
            source,
            output_root,
            toolchain,
            artifact_resolver=resolver,
            allow_incomplete=allow_incomplete,
        )
    except (
        HarborCompileError,
        UnknownRuntimeAdapterError,
        CatalogError,
        OSError,
        ValueError,
    ) as exc:
        typer.echo(f"Harbor compile failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(
        {
            "task": task_root.name,
            "output": str(task_root),
            "bundle_manifest": str(task_root / "bundle.manifest.json"),
        }
    )


@harbor_app.command("prepare-control")
def prepare_harbor_control(
    task_root: Annotated[Path, typer.Argument(help="Compiled Harbor task directory.")],
    kind: Annotated[str, typer.Argument(help="Control kind: stub or forgery.")],
    output_root: Annotated[
        Path,
        typer.Option("--output", help="Directory for generated control bundles."),
    ] = Path("build/controls"),
    toolchain: Annotated[
        Path,
        typer.Option("--toolchain", help="Pinned Harbor/toolchain lock."),
    ] = Path("toolchain.lock.toml"),
) -> None:
    """Prepare a control bundle that Harbor executes with the Oracle agent."""

    try:
        output = HarborCompilerRegistry.default().prepare_control_bundle(
            task_root,
            kind,
            output_root,
            toolchain,
        )
    except (HarborCompileError, OSError, ValueError) as exc:
        typer.echo(f"control preparation failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print({"kind": kind, "output": str(output)})


@task_app.command("scaffold")
def scaffold_catalog_task(
    task_id: Annotated[str, typer.Argument(help="Stable task identifier.")],
    root: Annotated[
        Path,
        typer.Option("--root", help="Human-facing task catalog root."),
    ] = Path("catalog/sources"),
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

    from nl2repobench.legacy.importer import LegacyImporter, LegacyImportError

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
        parsed = CanonicalTaskManifest.model_validate_json(raw)
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


@task_app.command("lint-network")
def lint_network(
    tasks_root: Annotated[
        Path,
        typer.Option("--tasks-root", help="Catalog task directory to scan."),
    ] = Path("catalog/sources"),
    include_generated: Annotated[
        bool,
        typer.Option(
            "--include-generated",
            help="Also scan catalog/tasks as the generated Harbor runtime view.",
        ),
    ] = False,
    strict: Annotated[
        bool,
        typer.Option("--strict", help="Treat warnings as failures."),
    ] = False,
) -> None:
    """Lint run-time network egress policy across catalog tasks.

    Fails when a task can still reach the frozen upstream source it must
    reproduce: a missing or contradictory policy, a forbidden host, or
    reference-source acquisition such as ``git clone``.
    """

    roots = [tasks_root]
    generated = Path("catalog/tasks")
    if include_generated and generated != tasks_root and generated.is_dir():
        roots.append(generated)
    report = lint_catalog_roots(*roots)
    _json_print(report.as_dict())
    if report.errors or (strict and report.warnings):
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
        parsed = CanonicalTaskManifest.model_validate_json(manifest.read_bytes())
    except (OSError, ValueError) as exc:
        typer.echo(f"invalid manifest: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _json_print(parsed.model_dump(mode="json", exclude_none=True))
