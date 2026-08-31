from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from nl2repobench.authoring.catalog import CatalogCompiler, CatalogError
from nl2repobench.verification.rust_bridge import canonical_json_bytes
from nl2repobench.verification.rust_profile import (
    canonical_rust_profile_bytes,
    load_rust_profile,
    rust_profile_projection_digest,
)

PROFILE = '''schema_version = "1.0"

[package]
name = "demo"
version = "1.2.3"
edition = "2021"
rust_version = "1.85"
library_path = "src/lib.rs"
binaries = ["demo"]

[target]
triple = "x86_64-unknown-linux-gnu"

[features]
default_features = false
enabled = ["serde", "std"]

[features.declarations]
serde = ["dep:serde"]
std = []

[[candidate_dependencies]]
name = "itoa"
version = "1.0.15"
default_features = false
features = []

[bridge]
api_plan_digest = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
max_operations_per_request = 64
max_state_handles = 32
max_state_bytes = 8388608
unsafe_api_ids = []

[[cli]]
profile_id = "demo-cli"
binary_name = "demo"
argv_max_items = 64
stdin_max_bytes = 1048576
max_output_bytes = 8388608
tempdir_policy = "none"
tempdir_max_entries = 0
tempdir_max_bytes = 0
tempdir_max_file_bytes = 0
cli_timeout_sec = 120.0
expected_exit_codes = [0]

[limits]
build_timeout_sec = 600
leaf_timeout_sec = 120
cpu_sec = 120
max_stdin_bytes = 1048576
max_output_bytes = 8388608
max_file_bytes = 536870912
max_open_files = 256
max_processes = 64
'''


def test_rust_profile_loads_the_strict_typed_source(tmp_path: Path) -> None:
    path = tmp_path / "rust-profile.toml"
    path.write_text(PROFILE, encoding="utf-8")

    profile = load_rust_profile(path)

    assert profile.package.library_path == "src/lib.rs"
    assert profile.features.enabled == ("serde", "std")
    assert profile.candidate_dependencies[0].target_selector is None
    assert profile.cli[0].expected_exit_codes == (0,)


@pytest.mark.parametrize(
    ("before", "after", "message"),
    [
        ('enabled = ["serde", "std"]', 'enabled = ["std", "serde"]', "sorted"),
        ('binaries = ["demo"]', 'binaries = ["demo", "demo"]', "unique"),
        ('expected_exit_codes = [0]', 'expected_exit_codes = [1, 0]', "sorted"),
        ('max_processes = 64', 'max_processes = 65', "less than or equal to 64"),
        ('[target]\n', '[target]\nunknown = true\n', "Extra inputs"),
    ],
)
def test_rust_profile_rejects_noncanonical_or_unknown_values(
    tmp_path: Path,
    before: str,
    after: str,
    message: str,
) -> None:
    path = tmp_path / "rust-profile.toml"
    path.write_text(PROFILE.replace(before, after), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_rust_profile(path)


def test_rust_profile_rejects_json_and_symlink_sources(tmp_path: Path) -> None:
    profile = tmp_path / "rust-profile.toml"
    profile.write_text(PROFILE, encoding="utf-8")
    alias = tmp_path / "profile-link.toml"
    alias.symlink_to(profile)

    with pytest.raises(ValueError, match="regular file"):
        load_rust_profile(alias)


def _private_ref(digit: str, media_type: str) -> str:
    return f'''digest = "sha256:{digit * 64}"
size_bytes = 1
media_type = "{media_type}"
uri = "artifact://private/sha256:{digit * 64}"
visibility = "private"
'''


def _api_plan() -> bytes:
    payload = {
        "schema_version": "1.0",
        "package_name": "demo",
        "types": [],
        "functions": [
            {
                "api_id": "echo",
                "rust_path": "crate::echo",
                "kind": "sync",
                "receiver": None,
                "state_type": None,
                "args": [{"name": "value", "type": "string"}],
                "returns": "string",
                "error": None,
                "unsafe": False,
                "leaf_ids": ["echo.basic"],
            }
        ],
        "state_types": [],
        "cli_profiles": [{"profile_id": "demo-cli", "binary_name": "demo"}],
        "unsafe_leaf_ids": [],
    }
    digest = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    payload["api_plan_digest"] = f"sha256:{digest}"
    return canonical_json_bytes(payload)


def test_catalog_source_hook_validates_rust_profile_and_api_plan_digest(
    tmp_path: Path,
) -> None:
    api_plan = _api_plan()
    digest = hashlib.sha256(api_plan).hexdigest()
    (tmp_path / "instruction.md").write_text("# Rust task\n", encoding="utf-8")
    (tmp_path / "rust-api-plan.json").write_bytes(api_plan)
    (tmp_path / "rust-profile.toml").write_text(
        PROFILE.replace("a" * 64, digest), encoding="utf-8"
    )
    (tmp_path / "task.toml").write_text(
        f'''schema_version = "1.0"
task_id = "rust-source"

[metadata]
language = "rust"

[environment]
status = "unknown"

[environment.runtime]
language = "rust"
runtime = "rust"
version = "1.100.0-nightly"
package_manager = "cargo"
package_manager_version = "1.100.0-nightly"

[dependencies]
status = "known"
package_manager = "cargo"

[dependencies.lock]
{_private_ref("1", "application/vnd.nl2repobench.package-lock.tar")}
[dependencies.offline_store]
{_private_ref("2", "application/vnd.nl2repobench.offline-store.tar")}
[dependencies.inventory]
{_private_ref("3", "application/vnd.nl2repobench.inventory+json")}

[tests]
framework = "rust-harness"
report_format = "rust-bridge-json-v1"

[tests.commands_artifact]
{_private_ref("4", "application/vnd.nl2repobench.command-plan+json")}
[tests.protected_paths_artifact]
{_private_ref("8", "application/vnd.nl2repobench.protected-paths+json")}
[tests.test_bundle]
{_private_ref("5", "application/vnd.nl2repobench.test-bundle.tar")}

[verifier]
entrypoint = "run.py"

[verifier.bundle]
{_private_ref("6", "application/vnd.nl2repobench.verifier-bundle.tar")}
[oracle_bundle]
{_private_ref("7", "application/vnd.nl2repobench.oracle-bundle.tar")}
''',
        encoding="utf-8",
    )

    source = CatalogCompiler.load_task(tmp_path)
    assert source.metadata.language.value == "rust"

    task_path = tmp_path / "task.toml"
    task_text = task_path.read_text(encoding="utf-8")
    task_path.write_text(
        task_text.replace(
            "application/vnd.nl2repobench.package-lock.tar",
            "application/octet-stream",
        ),
        encoding="utf-8",
    )
    with pytest.raises(CatalogError, match="media type"):
        CatalogCompiler.load_task(tmp_path)
    task_path.write_text(task_text, encoding="utf-8")

    task_path.write_text(
        task_text.replace(
            "application/vnd.nl2repobench.protected-paths+json",
            "application/octet-stream",
        ),
        encoding="utf-8",
    )
    with pytest.raises(CatalogError, match="media type"):
        CatalogCompiler.load_task(tmp_path)
    task_path.write_text(task_text, encoding="utf-8")

    (tmp_path / "rust-profile.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(CatalogError, match="rust-profile.json"):
        CatalogCompiler.load_task(tmp_path)
    (tmp_path / "rust-profile.json").unlink()

    changed_plan = json.loads(api_plan)
    changed_plan["functions"][0]["leaf_ids"] = ["echo.changed"]
    del changed_plan["api_plan_digest"]
    changed_plan["api_plan_digest"] = "sha256:" + hashlib.sha256(
        canonical_json_bytes(changed_plan)
    ).hexdigest()
    (tmp_path / "rust-api-plan.json").write_bytes(canonical_json_bytes(changed_plan))
    with pytest.raises(CatalogError, match="exact-file digest"):
        CatalogCompiler.load_task(tmp_path)


def test_rust_profile_projection_is_canonical_and_digest_bound(tmp_path: Path) -> None:
    path = tmp_path / "rust-profile.toml"
    path.write_text(PROFILE, encoding="utf-8")
    profile = load_rust_profile(path)

    projection = canonical_rust_profile_bytes(profile)

    assert projection.endswith(b"\n") and not projection.endswith(b"\n\n")
    assert projection == (
        json.dumps(
            profile.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
        + b"\n"
    )
    assert rust_profile_projection_digest(profile) == (
        f"sha256:{hashlib.sha256(projection).hexdigest()}"
    )


def test_discovered_rust_source_can_defer_runtime_and_private_assets(
    tmp_path: Path,
) -> None:
    (tmp_path / "instruction.md").write_text("# Rust discovery\n", encoding="utf-8")
    (tmp_path / "task.toml").write_text(
        '''task_id = "rust-discovered"

[metadata]
language = "rust"

[environment]
status = "unknown"

[dependencies]
status = "unknown"
package_manager = "cargo"

[tests]
framework = "rust-harness"
report_format = "rust-bridge-json-v1"
''',
        encoding="utf-8",
    )

    assert CatalogCompiler.load_task(tmp_path).task_id == "rust-discovered"


def test_source_asset_hook_preserves_runtime_optional_non_rust_sources(
    tmp_path: Path,
) -> None:
    (tmp_path / "instruction.md").write_text("# Python task\n", encoding="utf-8")
    (tmp_path / "task.toml").write_text(
        '''task_id = "python-discovered"

[metadata]
language = "python"

[environment]
status = "unknown"

[dependencies]
status = "unknown"
package_manager = "uv"

[tests]
framework = "pytest"
report_format = "pytest-junit-xml-v1"
''',
        encoding="utf-8",
    )

    assert CatalogCompiler.load_task(tmp_path).task_id == "python-discovered"
