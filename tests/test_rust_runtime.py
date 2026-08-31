from __future__ import annotations

import pytest
from pydantic import ValidationError

from nl2repobench.authoring.runtime_asset_registry import (
    RuntimeSourceAssetRegistry,
    RustSourceAssetValidator,
)
from nl2repobench.domain.canonical_contract import (
    PackageManager,
    RuntimeLanguage,
    RuntimeProfile,
)
from nl2repobench.domain.canonical_contract import (
    TestManifest as CanonicalTestManifest,
)
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.runtimes import RustRuntimeAdapter


def test_rust_cargo_is_the_only_supported_rust_runtime_pair() -> None:
    profile = RuntimeProfile(
        language="rust",
        runtime="rust",
        version="1.100.0-nightly",
        package_manager="cargo",
        package_manager_version="1.100.0-nightly",
    )

    assert profile.language is RuntimeLanguage.RUST
    assert profile.package_manager is PackageManager.CARGO
    assert RustRuntimeAdapter.identity == RuntimeDiscriminator(
        language=RuntimeLanguage.RUST,
        package_manager=PackageManager.CARGO,
    )
    assert RuntimeDiscriminator(
        language=RuntimeLanguage.RUST,
        package_manager=PackageManager.CARGO,
    ).package_manager is PackageManager.CARGO

    with pytest.raises(ValidationError, match="rust runtime cannot use none"):
        RuntimeDiscriminator(
            language=RuntimeLanguage.RUST,
            package_manager=PackageManager.NONE,
        )


def test_rust_runtime_and_test_protocol_are_exact() -> None:
    with pytest.raises(ValidationError, match="runtime does not match language"):
        RuntimeProfile(
            language="rust",
            runtime="node",
            version="1.100.0-nightly",
            package_manager="cargo",
            package_manager_version="1.100.0-nightly",
        )

    assert CanonicalTestManifest(
        framework="rust-harness",
        report_format="rust-bridge-json-v1",
    ).report_format == "rust-bridge-json-v1"
    with pytest.raises(ValidationError, match="rust-harness requires rust-bridge-json-v1"):
        CanonicalTestManifest(
            framework="rust-harness",
            report_format="custom-json-v1",
        )

    with pytest.raises(ValidationError, match="Rust and Cargo versions must be exactly"):
        RuntimeProfile(
            language="rust",
            runtime="rust",
            version="1.99.0",
            package_manager="cargo",
            package_manager_version="1.99.0",
        )


def test_rust_source_asset_validator_is_registered_by_exact_identity() -> None:
    validator = RuntimeSourceAssetRegistry.default().resolve(
        RuntimeDiscriminator(
            language=RuntimeLanguage.RUST,
            package_manager=PackageManager.CARGO,
        )
    )
    assert isinstance(validator, RustSourceAssetValidator)


def test_runtime_profile_schema_exports_rust_cargo_literals() -> None:
    schema = RuntimeProfile.model_json_schema()
    encoded = str(schema)
    assert "rust" in encoded
    assert "cargo" in encoded
    assert "1.100.0-nightly" in encoded
