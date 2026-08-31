"""Human-facing declarative authoring sources and compilers."""

from nl2repobench.domain.canonical_contract import TaskSource

from .backup import (
    activate_database,
    backup_database,
    issue_quiescence_receipt,
    restore_database,
    verify_backup,
)
from .catalog import (
    CatalogCompiler,
    CatalogError,
    DeclarativeDatasetSource,
    validate_compiled_dataset,
)
from .migration import (
    MANIFEST_SCHEMA,
    MigrationError,
    barrier_check,
    classify_integration_failure,
    generate_manifest,
    import_manifest,
    validate_manifest,
)
from .scheduler import (
    BusyError,
    ConflictError,
    CorruptionError,
    Identity,
    LostLeaseError,
    Scheduler,
    SchedulerError,
    ValidationError,
    readonly_status,
)

__all__ = [
    "CatalogCompiler",
    "CatalogError",
    "DeclarativeDatasetSource",
    "TaskSource",
    "validate_compiled_dataset",
    "BusyError",
    "ConflictError",
    "CorruptionError",
    "Identity",
    "LostLeaseError",
    "Scheduler",
    "SchedulerError",
    "ValidationError",
    "readonly_status",
    "MANIFEST_SCHEMA",
    "MigrationError",
    "generate_manifest",
    "validate_manifest",
    "import_manifest",
    "barrier_check",
    "classify_integration_failure",
    "backup_database",
    "issue_quiescence_receipt",
    "verify_backup",
    "restore_database",
    "activate_database",
]
