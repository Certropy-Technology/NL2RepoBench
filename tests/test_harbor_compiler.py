from __future__ import annotations

import hashlib
import io
import json
import shutil
import tarfile
import tomllib
from pathlib import Path

import pytest
import tomli_w

from nl2repobench.domain.models import Visibility
from nl2repobench.harbor.compiler import HarborCompileError, HarborCompiler
from nl2repobench.harbor.models import (
    AgentRuntimeImageLock,
    load_command_plan,
    load_toolchain_lock,
)
from nl2repobench.harbor.registry import HarborCompilerRegistry
from nl2repobench.package_managers.dependency_artifacts import (
    LOCK_MEDIA_TYPE,
    STORE_MEDIA_TYPE,
    put_dependency_archive,
    put_dependency_inventory,
)
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.storage.canonical_ustar import CanonicalEntry
from nl2repobench.verification.command_plan import validate_command_plan

ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "catalog/sources/ministats"
TOOLCHAIN = ROOT / "toolchain.lock.toml"


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _tar_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            info.mode = 0o755 if name.endswith(".sh") else 0o644
            archive.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


def _dependency_bundle(store: FileArtifactStore, lock_data: bytes) -> dict[str, object]:
    lock_entries = (
        CanonicalEntry("requirements.lock.txt", "file", 0o444, lock_data),
    )
    store_entries: tuple[CanonicalEntry, ...] = ()
    lock = put_dependency_archive(store, lock_entries, media_type=LOCK_MEDIA_TYPE)
    offline_store = put_dependency_archive(
        store, store_entries, media_type=STORE_MEDIA_TYPE
    )
    inventory = put_dependency_inventory(
        store,
        identity="python+uv",
        adapter_version="python-preinstalled-image-v1",
        toolchain_digest="sha256:" + hashlib.sha256(TOOLCHAIN.read_bytes()).hexdigest(),
        lock_ref=lock,
        lock_entries=lock_entries,
        store_ref=offline_store,
        store_entries=store_entries,
        smoke_command_id="python-preinstalled-image-v1",
    )
    return {
        "status": "known",
        "package_manager": "uv",
        "lock": lock.model_dump(mode="json"),
        "offline_store": offline_store.model_dump(mode="json"),
        "inventory": inventory.model_dump(mode="json"),
    }


def test_toolchain_images_are_digest_pinned() -> None:
    lock = load_toolchain_lock(TOOLCHAIN)

    assert lock.harbor.version == "0.21.0"
    assert lock.harbor.runner == "uv run --frozen --project harbor-runner harbor"
    assert lock.harbor.lock_sha256.startswith("sha256:")
    assert "@sha256:" in lock.images.agent_base
    assert "@sha256:" in lock.images.verifier_base
    assert lock.agent_runtime.image == (
        "nl2repobench/openhands-sdk-fork:930e9b1da"
    )
    assert lock.agent_runtime.image_id.startswith("sha256:")
    assert lock.agent_runtime.fork_commit == "930e9b1daee0f5d2c7f3b261f045527a0ddae87d"
    assert lock.verifier.requirements_sha256.startswith("sha256:")


def test_agent_runtime_digest_is_bound_to_locked_image_id() -> None:
    lock = load_toolchain_lock(TOOLCHAIN).agent_runtime
    digest_reference = lock.model_copy(
        update={"image": f"nl2repobench/openhands-sdk-fork@{lock.image_id}"}
    )
    assert digest_reference.image.rsplit("@", 1)[1] == digest_reference.image_id
    with pytest.raises(ValueError, match="image digest must match image_id"):
        AgentRuntimeImageLock.model_validate(
            digest_reference.model_dump(mode="python")
            | {"image_id": "sha256:" + "0" * 64}
        )


def test_runtime_metadata_records_both_locked_variants() -> None:
    for metadata_name, toolchain_name, variant in (
        ("runtime.json", "toolchain.lock.toml", "trixie"),
        ("runtime.bookworm.json", "toolchain.node.lock.toml", "bookworm"),
    ):
        metadata = json.loads(
            (ROOT / "runtime/openhands-agent" / metadata_name).read_text(encoding="utf-8")
        )
        toolchain = tomllib.loads((ROOT / toolchain_name).read_text(encoding="utf-8"))
        runtime = toolchain["agent_runtime"]
        assert metadata["variant"] == variant
        assert metadata["image"] == runtime["image"]
        assert metadata["image_id"] == runtime["image_id"]
        assert metadata["image_tag"] == metadata["image"]
        assert metadata["image_digest"] == runtime["image_id"]


def test_arbitrary_legacy_command_lists_are_not_execution_plans() -> None:
    with pytest.raises(ValueError, match="invalid verifier command plan"):
        load_command_plan(b'["pip install -e .", "pytest tests"]')


def test_compiler_requires_publishable_task_by_default(tmp_path) -> None:
    with pytest.raises(HarborCompileError, match="not publishable"):
        HarborCompiler(TOOLCHAIN).compile_task(SOURCE, tmp_path / "output")


def test_development_compiler_generates_separate_verifier_bundle(tmp_path) -> None:
    task_root = HarborCompiler(TOOLCHAIN).compile_task(
        SOURCE,
        tmp_path / "output",
        allow_incomplete=True,
    )

    task = tomllib.loads((task_root / "task.toml").read_text())
    assert task["schema_version"] == "1.4"
    assert task["verifier"]["environment_mode"] == "separate"
    assert task["verifier"]["network_mode"] == "no-network"
    assert task["verifier"]["environment"]["network_mode"] == "no-network"
    assert task["metadata"]["expected_test_count"] == 18
    agent_dockerfile = (task_root / "environment/Dockerfile").read_text()
    assert (
        "nl2repobench/openhands-sdk-fork:930e9b1da"
        in agent_dockerfile
    )
    assert "agent-runtime-image-id" in agent_dockerfile
    assert "pip-index-hash-locked-v1" in agent_dockerfile
    assert "/opt/openhands-sdk-venv/bin/python" in agent_dockerfile
    assert not (task_root / "environment/docker-compose.yaml").exists()
    assert "network_mode: none" in (task_root / "tests/docker-compose.yaml").read_text()
    verifier_dockerfile = (task_root / "tests/Dockerfile").read_text()
    assert "--require-hashes" in verifier_dockerfile
    assert "--index-url https://pypi.org/simple" in verifier_dockerfile
    assert "COPY candidate-requirements.lock.txt" in verifier_dockerfile
    assert "COPY dependencies" not in verifier_dockerfile
    assert "--no-index" not in verifier_dockerfile
    assert not (task_root / "tests/dependencies").exists()
    assert "useradd --uid 10001" in (task_root / "tests/Dockerfile").read_text()
    assert "chmod -R 0500 /tests/private" in (task_root / "tests/Dockerfile").read_text()
    assert (task_root / "tests/runtime/nl2repobench/verification/candidate_client.py").is_file()
    assert (task_root / "tests/runtime/nl2repobench/verification/candidate_install.py").is_file()
    assert (task_root / "tests/runtime/nl2repobench/verification/candidate_runner.py").is_file()
    assert (task_root / "tests/runtime/nl2repobench/verification/workspace_copy.py").is_file()
    assert (task_root / "tests/runtime/nl2repobench/domain/network_policy.py").is_file()
    assert (task_root / "tests/private/test_ministats.py").is_file()
    assert (task_root / "tests/runtime/nl2repobench/verification/grader.py").is_file()
    assert (task_root / "tests/runtime/nl2repobench/verification/network_check.py").is_file()
    assert (task_root / "tests/candidate-requirements.lock.txt").read_bytes() == b""
    test_script = (task_root / "tests/test.sh").read_text()
    assert "verifier-network-available" in test_script
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1" in test_script
    assert "verification.command_plan" in test_script
    assert "setsid runuser" not in test_script
    assert "env HOME=/root" in test_script
    assert "PYTHONDONTWRITEBYTECODE=1" in test_script
    assert "/tmp/trusted-results/collection.json" in test_script
    assert "/tmp/candidate-results" not in test_script
    assert "verification.workspace_copy" in test_script
    assert "verification.candidate_install" in test_script
    assert "NL2REPO_CANDIDATE_TOTAL_TIMEOUT_SEC=60.0" in test_script
    assert "cp -a" not in test_script
    assert "verification.integrity verify" in test_script
    assert "verification.process_cleanup --uid 10001" in test_script
    assert (task_root / "solution/solve.sh").stat().st_mode & 0o111
    assert (task_root / "controls/stub.sh").stat().st_mode & 0o111
    assert not list((task_root / "environment").rglob("test_ministats.py"))


def test_system_packages_are_installed_in_agent_and_verifier_images(tmp_path) -> None:
    source = tmp_path / "source"
    shutil.copytree(SOURCE, source)
    task_toml = source / "task.toml"
    task_text = task_toml.read_text(encoding="utf-8").replace(
        '[environment]\nstatus = "unknown"',
        '[environment]\nstatus = "unknown"\nsystem_packages = ["build-essential", "odd package"]',
    )
    task_toml.write_text(task_text, encoding="utf-8")

    task_root = HarborCompiler(TOOLCHAIN).compile_task(
        source,
        tmp_path / "output",
        allow_incomplete=True,
    )

    apt_install = (
        "RUN apt-get update && apt-get install -y --no-install-recommends "
        "build-essential 'odd package' && rm -rf /var/lib/apt/lists/*"
    )
    assert apt_install in (task_root / "environment/Dockerfile").read_text(encoding="utf-8")
    assert apt_install in (task_root / "tests/Dockerfile").read_text(encoding="utf-8")


def test_empty_system_packages_emit_no_apt_stanza(tmp_path) -> None:
    task_root = HarborCompiler(TOOLCHAIN).compile_task(
        SOURCE,
        tmp_path / "output",
        allow_incomplete=True,
    )

    assert "apt-get" not in (task_root / "environment/Dockerfile").read_text(encoding="utf-8")
    assert "apt-get" not in (task_root / "tests/Dockerfile").read_text(encoding="utf-8")


def test_catalog_network_policy_controls_generated_agent_runtime(tmp_path) -> None:
    source = tmp_path / "source"
    shutil.copytree(SOURCE, source)
    task_toml = source / "task.toml"
    task_text = task_toml.read_text()
    if "[environment.network_policy]" not in task_text:
        task_text = task_text.replace(
            "[dependencies]\n",
            """[environment.network_policy]
mode = "no-network"
offline_dependencies = "missing"
reference_source_fetch = "forbidden"
reason = "Synthetic compiler policy projection fixture."

[dependencies]
""",
        )
    task_toml.write_text(task_text)
    task_root = HarborCompiler(TOOLCHAIN).compile_task(
        source,
        tmp_path / "output",
        allow_incomplete=True,
    )
    task = tomllib.loads((task_root / "task.toml").read_text())
    assert task["environment"]["network_mode"] == "no-network"
    assert not (task_root / "environment/docker-compose.yaml").exists()


def test_compiler_output_is_byte_identical_across_roots(tmp_path) -> None:
    first = HarborCompiler(TOOLCHAIN).compile_task(
        SOURCE, tmp_path / "first", allow_incomplete=True
    )
    second = HarborCompiler(TOOLCHAIN).compile_task(
        SOURCE, tmp_path / "second", allow_incomplete=True
    )

    assert _files(first) == _files(second)


def test_compiler_rejects_existing_output(tmp_path) -> None:
    output = tmp_path / "output"
    (output / "ministats").mkdir(parents=True)

    with pytest.raises(HarborCompileError, match="already exists"):
        HarborCompiler(TOOLCHAIN).compile_task(SOURCE, output, allow_incomplete=True)


def test_private_tar_rejects_path_traversal(tmp_path) -> None:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        content = b"escape"
        info = tarfile.TarInfo("../escape.txt")
        info.size = len(content)
        archive.addfile(info, io.BytesIO(content))
    store = FileArtifactStore(tmp_path / "artifacts")
    reference = store.put_bytes(buffer.getvalue(), visibility=Visibility.PRIVATE)
    compiler = HarborCompiler(
        TOOLCHAIN,
        artifact_resolver=LocalArtifactResolver(store, allow_private=True),
    )

    with pytest.raises(HarborCompileError, match="escapes bundle"):
        compiler._extract_private_bundle(  # noqa: SLF001 - adversarial archive test
            reference, tmp_path / "extracted"
        )


def test_private_tar_rejects_duplicate_paths(tmp_path) -> None:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        for content in (b"first", b"second"):
            info = tarfile.TarInfo("duplicate.txt")
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
    store = FileArtifactStore(tmp_path / "artifacts")
    reference = store.put_bytes(buffer.getvalue(), visibility=Visibility.PRIVATE)
    compiler = HarborCompiler(
        TOOLCHAIN,
        artifact_resolver=LocalArtifactResolver(store, allow_private=True),
    )

    with pytest.raises(HarborCompileError, match="duplicate archive path"):
        compiler._extract_private_bundle(  # noqa: SLF001 - adversarial archive test
            reference, tmp_path / "extracted"
        )


def test_private_tar_enforces_member_limit_while_streaming(tmp_path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    reference = store.put_bytes(
        _tar_bytes({"first.txt": b"", "second.txt": b""}),
        visibility=Visibility.PRIVATE,
    )
    compiler = HarborCompiler(
        TOOLCHAIN,
        artifact_resolver=LocalArtifactResolver(store, allow_private=True),
    )
    compiler.MAX_BUNDLE_MEMBERS = 1

    with pytest.raises(HarborCompileError, match="too many members"):
        compiler._extract_private_bundle(  # noqa: SLF001 - adversarial archive test
            reference, tmp_path / "extracted"
        )


def test_production_compiler_resolves_private_test_and_oracle_bundles(tmp_path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    tests = store.put_bytes(
        _tar_bytes({"test_private.py": b"def test_private(): assert True\n"}),
        visibility=Visibility.PRIVATE,
    )
    oracle = store.put_bytes(
        _tar_bytes({"solve.sh": b"#!/usr/bin/env bash\nset -euo pipefail\n"}),
        visibility=Visibility.PRIVATE,
    )
    dependency_bundle = _dependency_bundle(
        store,
        b"demo-pkg==1.0 \\\n" + b"    --hash=sha256:" + b"0" * 64 + b"\n",
    )
    commands = store.put_bytes(
        b'{"schema_version":"1.0","runner":"pytest-subprocess-boundary-v1",'
        b'"candidate_install":"pip-target-no-deps-v1"}',
        visibility=Visibility.PRIVATE,
    )
    source_dir = tmp_path / "catalog/sources/production"
    source_dir.mkdir(parents=True)
    (source_dir / "instruction.md").write_text("# Production task\n", encoding="utf-8")
    task = {
        "schema_version": "1.0",
        "task_id": "production",
        "version": "1.0.0",
        "instruction": "instruction.md",
        "metadata": {
            "difficulty": "easy",
            "category": "test",
            "tags": ["python"],
            "language": "python",
        },
        "source": {
            "status": "known",
            "upstream_url": "https://example.invalid/repo",
            "revision": "1" * 40,
            "license_spdx": "MIT",
            "source_digest": "sha256:" + "2" * 64,
        },
        "environment": {
            "status": "known",
            "python_version": "3.12",
            "os_name": "linux",
            "base_image": "python:3.12-slim",
            "base_image_digest": "sha256:" + "3" * 64,
            "network_mode": "no-network",
        },
        "dependencies": dependency_bundle,
        "tests": {
            "expected_total": 1,
            "expected_total_source": "frozen-collection",
            "commands_artifact": commands.model_dump(mode="json"),
            "test_bundle": tests.model_dump(mode="json"),
        },
        "harbor": {
            "description": "Production compiler fixture",
            "keywords": ["python", "pytest", "nl2repobench"],
        },
        "oracle_bundle": oracle.model_dump(mode="json"),
    }
    (source_dir / "task.toml").write_text(tomli_w.dumps(task), encoding="utf-8")
    compiler = HarborCompiler(
        TOOLCHAIN,
        artifact_resolver=LocalArtifactResolver(store, allow_private=True),
    )

    output = compiler.compile_task(source_dir, tmp_path / "output")

    assert (output / "tests/private/test_private.py").is_file()
    assert (output / "solution/solve.sh").is_file()
    assert (output / "tests/candidate-requirements.lock.txt").is_file()
    verifier_dockerfile = (output / "tests/Dockerfile").read_text()
    assert "python:3.12-slim@sha256:" in verifier_dockerfile
    assert "COPY dependencies" not in verifier_dockerfile
    assert "--no-index" not in verifier_dockerfile
    assert json.loads((output / "bundle.manifest.json").read_text())["mode"] == "production"


def test_runtime_command_plan_rejects_modified_protocol(tmp_path) -> None:
    plan = tmp_path / "command-plan.json"
    plan.write_text(
        '{"schema_version":"1.0","runner":"pytest-private-tree-v1",'
        '"candidate_install":"pip-target-no-deps-v1","test_root":"/tests/private"}',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="allowlisted verifier protocol"):
        validate_command_plan(plan)


def test_dependency_lock_requires_hashes() -> None:
    compiler = HarborCompiler(TOOLCHAIN)

    with pytest.raises(HarborCompileError, match="lack sha256 hashes"):
        compiler._validate_dependency_lock(b"demo-pkg==1.0\n")  # noqa: SLF001

    compiler._validate_dependency_lock(
        b"demo-pkg==1.0 \\\n" + b"    --hash=sha256:" + b"0" * 64 + b"\n"
    )


def test_vendor_dependency_bundle_is_forbidden(tmp_path) -> None:
    compiler = HarborCompiler(TOOLCHAIN)
    with pytest.raises(HarborCompileError, match="vendor dependency bundles are forbidden"):
        compiler._validate_dependency_bundle(tmp_path / "dependencies")  # noqa: SLF001


def test_production_compiler_emits_custom_verifier_bundle(tmp_path) -> None:
    store = FileArtifactStore(tmp_path / "artifacts")
    dependency_bundle = _dependency_bundle(store, b"")
    verifier_bundle = store.put_bytes(
        _tar_bytes(
            {
                "run.py": (
                    b"import json\n"
                    b"print(json.dumps({'schema_version':'1.0','leaves':"
                    b"[{'id':'one','status':'passed'}]}))\n"
                )
            }
        ),
        visibility=Visibility.PRIVATE,
    )
    oracle_bundle = store.put_bytes(
        _tar_bytes({"solve.sh": b"#!/usr/bin/env bash\nset -eu\n"}),
        visibility=Visibility.PRIVATE,
    )
    source_dir = tmp_path / "catalog/sources/custom"
    source_dir.mkdir(parents=True)
    (source_dir / "instruction.md").write_text("# Custom\n", encoding="utf-8")
    (source_dir / "task.toml").write_text(
        tomli_w.dumps(
            {
                "schema_version": "1.0",
                "task_id": "custom",
                "instruction": "instruction.md",
                "metadata": {
                    "difficulty": "easy",
                    "category": "test",
                    "tags": ["python"],
                    "language": "python",
                },
                "source": {
                    "status": "known",
                    "upstream_url": "https://example.invalid/repo",
                    "revision": "1" * 40,
                    "license_spdx": "MIT",
                    "source_digest": "sha256:" + "2" * 64,
                },
                "environment": {
                    "status": "known",
                    "python_version": "3.12",
                    "os_name": "linux",
                    "base_image": "python:3.12-slim",
                    "base_image_digest": "sha256:" + "3" * 64,
                    "network_mode": "no-network",
                },
                    "dependencies": dependency_bundle,
                "tests": {
                    "expected_total": 1,
                    "expected_total_source": "frozen-collection",
                    "commands": ["custom-json-v1"],
                },
                "verifier": {
                    "protocol": "custom-json-v1",
                    "bundle": verifier_bundle.model_dump(mode="json"),
                    "entrypoint": "run.py",
                },
                "harbor": {
                    "description": "Custom verifier fixture",
                    "keywords": ["python", "json", "custom"],
                },
                "oracle_bundle": oracle_bundle.model_dump(mode="json"),
            }
        ),
        encoding="utf-8",
    )

    output = HarborCompiler(
        TOOLCHAIN,
        artifact_resolver=LocalArtifactResolver(store, allow_private=True),
    ).compile_task(source_dir, tmp_path / "output")

    assert (output / "tests/verifier/run.py").is_file()
    assert "custom_verifier" in (output / "tests/test.sh").read_text(encoding="utf-8")
    assert "COPY --chmod=0500 verifier /tests/verifier" in (output / "tests/Dockerfile").read_text(
        encoding="utf-8"
    )
    assert "COPY dependencies" not in (output / "tests/Dockerfile").read_text(encoding="utf-8")


def test_dependency_lock_rejects_requirement_directives() -> None:
    with pytest.raises(HarborCompileError, match="forbidden directive"):
        HarborCompiler(TOOLCHAIN)._validate_dependency_lock(  # noqa: SLF001
            b"--index-url https://example.invalid/simple\n"
        )


def test_prepare_stub_control_replaces_only_control_solution(tmp_path) -> None:
    compiler = HarborCompiler(TOOLCHAIN)
    task_root = compiler.compile_task(SOURCE, tmp_path / "tasks", allow_incomplete=True)
    original_solution = (task_root / "solution/solve.sh").read_bytes()

    control = compiler.prepare_control_bundle(task_root, "stub", tmp_path / "controls")

    assert (task_root / "solution/solve.sh").read_bytes() == original_solution
    assert (control / "solution/solve.sh").read_bytes() == (
        task_root / "controls/stub.sh"
    ).read_bytes()
    assert json.loads((control / "bundle.manifest.json").read_text())["mode"] == "control-stub"


def test_prepare_control_rejects_unknown_kind(tmp_path) -> None:
    compiler = HarborCompiler(TOOLCHAIN)
    task_root = compiler.compile_task(SOURCE, tmp_path / "tasks", allow_incomplete=True)

    with pytest.raises(HarborCompileError, match="unsupported control kind"):
        compiler.prepare_control_bundle(task_root, "unknown", tmp_path / "controls")


def test_prepare_control_via_registry_preserves_python_dispatch(tmp_path) -> None:
    output = HarborCompilerRegistry.default().prepare_control_bundle(
        HarborCompiler(TOOLCHAIN).compile_task(SOURCE, tmp_path / "tasks", allow_incomplete=True),
        "stub",
        tmp_path / "controls",
        TOOLCHAIN,
    )

    assert output.name == "ministats-stub"
    assert (output / "solution/solve.sh").read_bytes() == (
        output.parent.parent / "tasks/ministats/controls/stub.sh"
    ).read_bytes()
