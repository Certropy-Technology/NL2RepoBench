from __future__ import annotations

import pytest

from nl2repobench.domain.canonical_contract import TaskSource
from nl2repobench.domain.runtime import (
    PackageManager,
    RuntimeContractError,
    RuntimeDiscriminator,
    RuntimeLanguage,
)


def test_runtime_discriminator_accepts_python_and_node_package_managers() -> None:
    assert RuntimeDiscriminator(
        language=RuntimeLanguage.PYTHON,
        package_manager=PackageManager.UV,
    ).package_manager is PackageManager.UV
    assert RuntimeDiscriminator(
        language=RuntimeLanguage.NODE,
        package_manager=PackageManager.PNPM,
    ).language is RuntimeLanguage.NODE


def test_runtime_discriminator_rejects_cross_ecosystem_manager() -> None:
    with pytest.raises(ValueError, match="python runtime cannot use npm"):
        RuntimeDiscriminator(
            language=RuntimeLanguage.PYTHON,
            package_manager=PackageManager.NPM,
        )


def test_runtime_discriminator_reads_explicit_python_source() -> None:
    source = TaskSource.model_validate(
        {
            "task_id": "python-runtime",
            "metadata": {"language": "python"},
            "environment": {
                "runtime": {
                    "language": "python",
                    "runtime": "cpython",
                    "version": "3.12",
                    "package_manager": "pip",
                    "package_manager_version": "24.0",
                }
            },
            "dependencies": {"status": "unknown", "package_manager": "pip"},
            "tests": {"framework": "pytest", "report_format": "pytest-junit-xml-v1"},
        }
    )
    result = RuntimeDiscriminator.from_task_source(source)
    assert result == RuntimeDiscriminator(
        language=RuntimeLanguage.PYTHON,
        package_manager=PackageManager.PIP,
    )


def test_runtime_discriminator_reads_explicit_node_source() -> None:
    source = TaskSource.model_validate(
        {
            "task_id": "node-runtime",
            "metadata": {"language": "node"},
            "environment": {
                "runtime": {
                    "language": "node",
                    "runtime": "node",
                    "version": "22.23.1",
                    "package_manager": "pnpm",
                    "package_manager_version": "9.15.0",
                }
            },
            "dependencies": {"status": "unknown", "package_manager": "pnpm"},
            "tests": {"framework": "node:test", "report_format": "node-test-json-v1"},
        }
    )
    result = RuntimeDiscriminator.from_task_source(source)
    assert result == RuntimeDiscriminator(
        language=RuntimeLanguage.NODE,
        package_manager=PackageManager.PNPM,
    )


def test_runtime_discriminator_fails_closed_without_canonical_runtime() -> None:
    source = TaskSource.model_validate(
        {
            "task_id": "missing-runtime",
            "metadata": {"language": "python"},
            "environment": {"status": "unknown"},
            "dependencies": {"status": "unknown", "package_manager": "uv"},
            "tests": {"framework": "pytest", "report_format": "pytest-junit-xml-v1"},
        }
    )
    with pytest.raises(RuntimeContractError, match="environment.runtime"):
        RuntimeDiscriminator.from_task_source(source)
