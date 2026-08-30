from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest
import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.domain.canonical_contract import PackageManager, RuntimeLanguage
from nl2repobench.domain.canonical_models import Visibility
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.harbor.go_compiler import (
    GoHarborCompileError,
    GoHarborCompiler,
    go_network_failure_reason,
)
from nl2repobench.harbor.private_artifacts import PrivateArtifactsManifest
from nl2repobench.package_managers.go_modules import GoModulesPackageManager
from nl2repobench.runtimes.go import GoRuntimeAdapter
from nl2repobench.storage.artifacts import (
    FileArtifactStore,
    LocalArtifactResolver,
    PrivateArtifactAuthorization,
)
from nl2repobench.verification.go_bridge import (
    GoBridgeOperation,
    GoBridgeSpec,
    generate_go_bridge,
)
from nl2repobench.verification.go_grader import grade_go_report
from nl2repobench.verification.go_supervisor import run_go_bridge
from nl2repobench.verification.taxonomy import VerificationReason


def _go_bundle(root) -> None:
    go_mod = root / "go.mod"
    go_sum = root / "go.sum"
    vendor = root / "vendor"
    vendor.mkdir()
    go_mod.write_text("module example.com/synthetic\n\ngo 1.26.5\n", encoding="utf-8")
    go_sum.write_text("", encoding="utf-8")
    (vendor / "modules.txt").write_text("# example.com/synthetic\n", encoding="utf-8")
    files = []
    for path in (go_mod, go_sum, vendor / "modules.txt"):
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    (root / "module.manifest.json").write_text(
        json.dumps({"schema_version": "1.0", "offline": True, "files": files}),
        encoding="utf-8",
    )


def _private_archive(store: FileArtifactStore, files: dict[str, bytes]):
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        for name, data in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o755 if name.endswith(".sh") else 0o644
            info.mtime = 0
            archive.addfile(info, io.BytesIO(data))
    return store.put_bytes(payload.getvalue(), visibility=Visibility.PRIVATE)


def _artifact_toml(reference) -> str:
    return (
        f'{{ digest = "{reference.digest}", size_bytes = {reference.size_bytes}, '
        f'uri = "{reference.uri}", visibility = "private" }}'
    )


def _canonical_go_source(
    root: Path,
    destination: Path,
    *,
    module=None,
    verifier=None,
    oracle=None,
    expected_total: int = 1,
) -> Path:
    shutil.copytree(root / "catalog/sources/go-synthetic", destination)
    production = module is not None and verifier is not None and oracle is not None
    dependencies: dict[str, object] = {
        "status": "known" if production else "unknown",
        "package_manager": "go-modules",
        "packages": [],
    }
    tests: dict[str, object] = {
        "framework": "go-bridge",
        "report_format": "go-test-json-v1",
        "expected_total": expected_total,
        "expected_total_source": "frozen-collection",
    }
    task: dict[str, object] = {
        "schema_version": "1.0",
        "task_id": "go-synthetic",
        "version": "0.1.0",
        "instruction": "instruction.md",
        "metadata": {
            "difficulty": "easy",
            "category": "go-foundation",
            "tags": ["go", "go-modules", "typed-bridge"],
            "language": "go",
        },
        "source": {"status": "unknown"},
        "environment": {
            "status": "unknown",
            "runtime": {
                "language": "go",
                "runtime": "go",
                "version": "1.26.5",
                "package_manager": "go-modules",
                "package_manager_version": "1.26.5",
            },
            "network_policy": {
                "mode": "no-network",
                "offline_dependencies": "missing",
                "reference_source_fetch": "forbidden",
                "reason": "Development fixture closure is intentionally absent.",
            },
        },
        "dependencies": dependencies,
        "tests": tests,
        "metric": {"contract_id": "fixed-test-pass-rate-v1", "collection_mismatch": "fail"},
        "lifecycle": {"status": "discovered"},
        "harbor": {
            "description": "Synthetic typed Go bridge fixture.",
            "keywords": ["go", "go-modules", "typed-bridge"],
            "agent_timeout_sec": 900.0,
            "verifier_timeout_sec": 600.0,
            "candidate_install_timeout_sec": 90.0,
            "candidate_total_timeout_sec": 300.0,
            "agent_network_mode": "no-network",
            "verifier_network_mode": "no-network",
            "cpus": 1,
            "memory_mb": 1024,
            "storage_mb": 4096,
            "workspace_artifact": "/workspace",
        },
    }
    if production:
        assert module is not None and verifier is not None and oracle is not None
        task["source"] = {
            "status": "known",
            "upstream_url": "https://example.invalid/go-source",
            "revision": "1" * 40,
            "license_spdx": "BSD-3-Clause",
            "source_digest": "sha256:" + "2" * 64,
        }
        environment = task["environment"]
        assert isinstance(environment, dict)
        environment.update(
            status="known",
            os_name="linux",
            base_image="golang",
            base_image_digest="sha256:" + "3" * 64,
        )
        network_policy = environment["network_policy"]
        assert isinstance(network_policy, dict)
        network_policy["offline_dependencies"] = "private-artifact"
        network_policy["reason"] = "Canonical private Go closure is staged before execution."
        reference = module.model_dump(mode="json")
        dependencies.update(
            lock=reference,
            offline_store=reference,
            inventory=reference,
        )
        tests["commands_artifact"] = verifier.model_dump(mode="json")
        task["verifier"] = {
            "protocol": "custom-json-v1",
            "bundle": verifier.model_dump(mode="json"),
            "entrypoint": "contract.sh",
        }
        task["oracle_bundle"] = oracle.model_dump(mode="json")
    (destination / "task.toml").write_text(tomli_w.dumps(task), encoding="utf-8")
    return destination


def test_go_modules_validates_offline_vendor_closure(tmp_path) -> None:
    _go_bundle(tmp_path)
    adapter = GoModulesPackageManager()
    summary = adapter.validate_lock(tmp_path, "1.26.5")
    assert summary.identity == adapter.identity
    assert adapter.build_commands({})[0].argv == (
        "/usr/local/go/bin/go",
        "test",
        "-mod=vendor",
        "./...",
    )


def test_go_modules_reject_replace_directive(tmp_path) -> None:
    (tmp_path / "go.mod").write_text(
        "module example.com/synthetic\n\ngo 1.26.5\nreplace example.com/x => ../x\n",
        encoding="utf-8",
    )
    (tmp_path / "go.sum").write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="replace directives"):
        GoModulesPackageManager().validate_lock(tmp_path, "1.26.5")


def test_go_runtime_identity_is_explicit() -> None:
    assert GoRuntimeAdapter.identity == RuntimeDiscriminator(
        language=RuntimeLanguage.GO,
        package_manager=PackageManager.GO_MODULES,
    )


@pytest.mark.parametrize("report_data", [None, b"not-json", {"tests": []}])
def test_go_grader_rejects_zero_denominator_with_structured_reason(report_data) -> None:
    result = grade_go_report(expected_total=0, report_data=report_data)

    assert result.valid is False
    assert result.failure_reason is VerificationReason.REPORT_MALFORMED
    assert result.failure_class.value == "verifier"
    assert result.reward == 0.0
    assert result.details == ("expected_total must be positive (got 0)",)


def test_typed_go_bridge_compiles_and_calls_public_string_api(tmp_path) -> None:
    go = shutil.which("go")
    if go is None:
        pytest.skip("go is not installed")
    (tmp_path / "go.mod").write_text("module example.com/bridge\n\ngo 1.26.5\n", encoding="utf-8")
    package = tmp_path / "stringsx"
    package.mkdir()
    (package / "stringsx.go").write_text(
        "package stringsx\n\n"
        'import "fmt"\n\n'
        "func Normalize(value string) (string, error) {\n"
        '    if value == "" { return "", fmt.Errorf("empty") }\n'
        '    return value + "!", nil\n'
        "}\n",
        encoding="utf-8",
    )
    spec = GoBridgeSpec(
        module_path="example.com/bridge",
        operations=(
            GoBridgeOperation(
                operation_id="normalize",
                import_path="example.com/bridge/stringsx",
                symbol="Normalize",
                argument_types=("string",),
                return_type="string",
                returns_error=True,
            ),
        ),
    )
    bridge = tmp_path / "cmd/bridge"
    bridge.mkdir(parents=True)
    (bridge / "main.go").write_text(generate_go_bridge(spec), encoding="utf-8")
    binary = tmp_path / "bridge-bin"
    built = subprocess.run(
        [go, "build", "-o", str(binary), "./cmd/bridge"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert built.returncode == 0, built.stdout + built.stderr
    for directory in (tmp_path, *tmp_path.parents):
        if directory == Path("/tmp"):
            break
        directory.chmod(0o755)
    result = run_go_bridge((str(binary),), b'{"operation":"normalize","args":["hi"]}\n')
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"value": "hi!"}


def test_go_supervisor_caps_output_flood() -> None:
    result = run_go_bridge(
        (sys.executable, "-c", "import sys; sys.stdout.write('x' * 1000000)"),
        b"",
        timeout_sec=5,
        max_output_bytes=1024,
    )
    assert result.output_limit_exceeded is True
    assert result.returncode == 125
    assert len(result.stdout) <= 1024


def test_go_supervisor_caps_stdout_and_stderr_together() -> None:
    result = run_go_bridge(
        (
            sys.executable,
            "-c",
            "import sys; sys.stdout.write('o' * 800); sys.stderr.write('e' * 800)",
        ),
        b"",
        timeout_sec=5,
        max_output_bytes=1024,
    )
    assert result.output_limit_exceeded is True
    assert len(result.stdout) + len(result.stderr) <= 1024


def test_go_compiler_writes_separate_bridge_task(tmp_path) -> None:
    root = Path(__file__).parents[1]
    source = _canonical_go_source(root, tmp_path / "source")
    output = GoHarborCompiler(root / "toolchain.go.dev.lock.toml").compile_task(
        source,
        tmp_path,
        allow_incomplete=True,
    )
    task = (output / "task.toml").read_text(encoding="utf-8")
    assert 'language = "go"' in task
    assert 'package_manager = "go-modules"' in task
    assert (output / "tests/private/bridge.go").is_file()
    assert (output / "tests/test.sh").stat().st_mode & 0o111
    assert not (output / "environment/docker-compose.yaml").exists()
    assert "network_mode: none" in (output / "tests/docker-compose.yaml").read_text()
    test_script = (output / "tests/test.sh").read_text()
    assert 'Path("/tmp/go-candidate"), expected_toolchain="1.26.5"' in test_script
    snippet = re.search(r"GO_VALIDATE=\$\(cat <<'PY'\n(.*?)\nPY\n\)", test_script, re.DOTALL)
    assert snippet is not None
    candidate = tmp_path / "go-candidate"
    candidate.mkdir()
    (candidate / "go.mod").write_text(
        "module example.com/synthetic\n\ngo 1.26.5\n", encoding="utf-8"
    )
    (candidate / "go.sum").write_text("", encoding="utf-8")
    validation = subprocess.run(
        [
            sys.executable,
            "-c",
            snippet.group(1).replace("/tmp/go-candidate", str(candidate)),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert validation.returncode == 0, validation.stdout + validation.stderr
    assert '"status":"failed"' in test_script
    assert "--runner-exit-code 1" in test_script
    assert "cp -a /opt/go-module-bundle/vendor" in test_script
    bundle = json.loads((output / "bundle.manifest.json").read_text(encoding="utf-8"))
    private = PrivateArtifactsManifest.model_validate(bundle["private_artifacts"])
    assert private.task_id == "go-synthetic"


def test_go_compiler_rejects_missing_control_script(tmp_path: Path) -> None:
    compiler = GoHarborCompiler(Path(__file__).parents[1] / "toolchain.go.dev.lock.toml")

    with pytest.raises(GoHarborCompileError, match="Go control script is missing"):
        compiler.prepare_control_bundle(tmp_path / "task", "stub", tmp_path / "controls")


def test_go_compiler_separates_development_and_locked_toolchains(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    development = GoHarborCompiler(root / "toolchain.go.dev.lock.toml")
    locked = GoHarborCompiler(root / "toolchain.go.lock.toml")
    development_source = _canonical_go_source(root, tmp_path / "development-source")

    with pytest.raises(GoHarborCompileError, match="toolchain.go.lock.toml"):
        development.compile_task(development_source, tmp_path / "development-output")
    with pytest.raises(GoHarborCompileError, match="incomplete"):
        locked.compile_task(development_source, tmp_path / "locked-output")

    source = tmp_path / "source"
    store = FileArtifactStore(tmp_path / "artifacts")
    module = tmp_path / "module"
    module.mkdir()
    _go_bundle(module)
    module_bundle = _private_archive(
        store,
        {
            path.relative_to(module).as_posix(): path.read_bytes()
            for path in module.rglob("*")
            if path.is_file()
        },
    )
    verifier_bundle = _private_archive(
        store,
        {"contract.sh": b"#!/bin/sh\nexit 0\n"},
    )
    oracle_bundle = _private_archive(
        store,
        {"solve.sh": b"#!/bin/sh\nexit 0\n"},
    )
    _canonical_go_source(
        root,
        source,
        module=module_bundle,
        verifier=verifier_bundle,
        oracle=oracle_bundle,
    )
    manifest_digest = CatalogCompiler(
        FileArtifactStore(tmp_path / "manifest-artifacts")
    ).compile_task(source, tmp_path / "manifest-output").manifest.content_digest()

    authorization = PrivateArtifactAuthorization(
        task_id="go-synthetic",
        manifest_digest=manifest_digest,
        purpose="compile",
        allowed_digests=frozenset(
            {module_bundle.digest, verifier_bundle.digest, oracle_bundle.digest}
        ),
        staging_root=(tmp_path / "compiled/go/private/aaaaaaaaaaaaaaaa").resolve(),
    )
    resolver = LocalArtifactResolver.scoped_private(
        store,
        authorization,
        task_id=authorization.task_id,
        manifest_digest=authorization.manifest_digest,
        purpose=authorization.purpose,
        staging_root=authorization.staging_root,
    )
    production = GoHarborCompiler(
        root / "toolchain.go.lock.toml",
        artifact_resolver=resolver,
    )
    with pytest.raises(GoHarborCompileError, match="private-staging-contract-missing"):
        production.compile_task(source, tmp_path / "production")

    multi_leaf = tmp_path / "multi-leaf"
    _canonical_go_source(root, multi_leaf, expected_total=2)
    with pytest.raises(GoHarborCompileError, match="exactly one verifier-owned leaf"):
        development.compile_task(multi_leaf, tmp_path / "multi-output", allow_incomplete=True)


def test_go_network_script_distinguishes_network_and_internal_exit_codes() -> None:
    compiler = GoHarborCompiler(Path(__file__).parents[1] / "toolchain.go.dev.lock.toml")
    script = compiler._test_script()  # noqa: SLF001
    network_branch = script.index('[[ "$network_exit" -eq 1 ]]')
    internal_branch = script.index('[[ "$network_exit" -ne 0 ]]')
    assert network_branch < internal_branch
    assert "grade --reason verifier-network-available" in script[network_branch:internal_branch]
    assert "grade --reason verifier-internal-error" in script[internal_branch:]


@pytest.mark.parametrize(
    ("exit_code", "reason"),
    [
        (0, None),
        (1, "verifier-network-available"),
        (70, "verifier-internal-error"),
        (2, "verifier-internal-error"),
    ],
)
def test_go_network_failure_reason_contract(exit_code: int, reason: str | None) -> None:
    assert go_network_failure_reason(exit_code) == reason
