from __future__ import annotations

import pytest

from nl2repobench.domain.runtime import (
    PackageManager,
    RuntimeContractError,
    RuntimeDiscriminator,
    RuntimeLanguage,
)


def test_runtime_discriminator_accepts_python_and_node_package_managers() -> None:
    assert (
        RuntimeDiscriminator(
            language=RuntimeLanguage.PYTHON,
            package_manager=PackageManager.UV,
        ).package_manager
        is PackageManager.UV
    )
    assert (
        RuntimeDiscriminator(
            language=RuntimeLanguage.NODE,
            package_manager=PackageManager.PNPM,
        ).language
        is RuntimeLanguage.NODE
    )


def test_runtime_discriminator_accepts_java_maven() -> None:
    assert (
        RuntimeDiscriminator(
            language=RuntimeLanguage.JAVA,
            package_manager=PackageManager.MAVEN,
        ).package_manager
        is PackageManager.MAVEN
    )


def test_runtime_discriminator_reads_explicit_java_source() -> None:
    result = RuntimeDiscriminator.from_catalog_source(
        {
            "metadata": {"language": "java"},
            "dependencies": {"package_manager": "maven"},
        }
    )
    assert result == RuntimeDiscriminator(
        language=RuntimeLanguage.JAVA,
        package_manager=PackageManager.MAVEN,
    )


def test_runtime_discriminator_rejects_cross_ecosystem_manager() -> None:
    with pytest.raises(ValueError, match="python runtime cannot use npm"):
        RuntimeDiscriminator(
            language=RuntimeLanguage.PYTHON,
            package_manager=PackageManager.NPM,
        )


def test_runtime_discriminator_reads_explicit_python_source() -> None:
    result = RuntimeDiscriminator.from_catalog_source(
        {
            "metadata": {"language": "python"},
            "dependencies": {"package_manager": "pip"},
        }
    )
    assert result == RuntimeDiscriminator(
        language=RuntimeLanguage.PYTHON,
        package_manager=PackageManager.PIP,
    )


def test_runtime_discriminator_reads_explicit_node_source() -> None:
    result = RuntimeDiscriminator.from_catalog_source(
        {
            "metadata": {"language": "node"},
            "environment": {
                "runtime": {
                    "language": "node",
                    "package_manager": "pnpm",
                }
            },
        }
    )
    assert result == RuntimeDiscriminator(
        language=RuntimeLanguage.NODE,
        package_manager=PackageManager.PNPM,
    )


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            {"metadata": {"language": "python"}, "dependencies": {}},
            "dependencies.package_manager",
        ),
        (
            {
                "metadata": {"language": "node"},
                "environment": {"runtime": {"language": "python", "package_manager": "npm"}},
            },
            "must explicitly match",
        ),
        ({"metadata": {"language": "ruby"}}, "metadata.language"),
    ],
)
def test_runtime_discriminator_fails_closed(source: dict[str, object], message: str) -> None:
    with pytest.raises(RuntimeContractError, match=message):
        RuntimeDiscriminator.from_catalog_source(source)
