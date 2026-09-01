from __future__ import annotations

import base64
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tomllib
from pathlib import Path

import pytest
import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.domain.canonical import canonical_json
from nl2repobench.domain.canonical_contract import PackageManager, RuntimeLanguage
from nl2repobench.domain.canonical_models import Visibility
from nl2repobench.domain.command_plan import CommandPlan
from nl2repobench.domain.runtime import RuntimeDiscriminator
from nl2repobench.harbor.go_compiler import (
    GO_RUNTIME_LOCK_FILES,
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
from nl2repobench.verification.go_command_plan import (
    EXPECTED_GO_PLAN,
    load_go_command_plan,
    validate_go_command_plan,
)
from nl2repobench.verification.go_grader import grade_go_report
from nl2repobench.verification.go_supervisor import run_go_bridge
from nl2repobench.verification.taxonomy import VerificationReason


def _current_locked_go_toolchain(root: Path, destination: Path) -> Path:
    """Build a temporary locked fixture whose runtime digest matches this lane."""

    lock = tomllib.loads((root / "toolchain.go.lock.toml").read_text(encoding="utf-8"))
    for relative in (
        *GO_RUNTIME_LOCK_FILES,
        "verifier/requirements.lock.txt",
        "harbor-runner/uv.lock",
    ):
        source = root / relative
        target = destination.parent / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    digest = hashlib.sha256()
    for relative in GO_RUNTIME_LOCK_FILES:
        path = root / relative
        digest.update(relative.removeprefix("src/nl2repobench/").encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    lock["go_runtime_sha256"] = f"sha256:{digest.hexdigest()}"
    destination.write_text(tomli_w.dumps(lock), encoding="utf-8")
    return destination


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
    commands=None,
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
        assert (
            module is not None
            and verifier is not None
            and oracle is not None
            and commands is not None
        )
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
        tests["commands_artifact"] = commands.model_dump(mode="json")
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
        (str(Path(sys.executable).resolve()), "-c", "import sys; sys.stdout.write('x' * 1000000)"),
        b"",
        timeout_sec=5,
        max_output_bytes=1024,
    )
    assert result.output_limit_exceeded is True
    assert result.returncode == 125
    assert len(result.stdout) <= 1024


def _python_script(tmp_path: Path, body: str) -> str:
    script = tmp_path / "bridge.sh"
    encoded = base64.b64encode(body.encode()).decode("ascii")
    script.write_text(
        "#!/bin/sh\n"
        f"exec {Path(sys.executable).resolve()} -c "
        f"\"import base64; exec(base64.b64decode('{encoded}'))\"\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return str(script)


def test_go_supervisor_caps_stdout_and_stderr_together() -> None:
    result = run_go_bridge(
        (
            str(Path(sys.executable).resolve()),
            "-c",
            "import sys; sys.stdout.write('o' * 800); sys.stderr.write('e' * 800)",
        ),
        b"",
        timeout_sec=5,
        max_output_bytes=1024,
    )
    assert result.output_limit_exceeded is True
    assert len(result.stdout) + len(result.stderr) <= 1024


def test_go_supervisor_preserves_nonzero_stdout_and_stderr(tmp_path: Path) -> None:
    result = run_go_bridge(
        (
            _python_script(
                tmp_path,
                "import sys; sys.stdout.buffer.write(b'out'); "
                "sys.stderr.buffer.write(b'err'); sys.exit(3)",
            ),
        ),
        b"",
        timeout_sec=5,
    )
    assert result.returncode == 3
    assert result.stdout == b"out"
    assert result.stderr == b"err"
    assert result.verifier_invalid is False


def test_go_supervisor_maps_timeout_to_legacy_returncode(tmp_path: Path) -> None:
    result = run_go_bridge(
        (_python_script(tmp_path, "import time; time.sleep(30)"),),
        b"",
        timeout_sec=1,
    )
    assert result.returncode == 124
    assert result.timed_out is True
    assert result.output_limit_exceeded is False


def test_go_supervisor_rejects_malformed_generic_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def malformed(*args, **kwargs):
        del args, kwargs
        return subprocess.CompletedProcess([], 0, stdout=b"not-json\n", stderr=b"")

    monkeypatch.setattr("nl2repobench.verification.go_supervisor.subprocess.run", malformed)
    result = run_go_bridge(("/usr/bin/true",), b"")
    assert result.returncode == 70
    assert result.verifier_invalid is True
    assert b"invalid generic bridge result" in result.stderr


def test_go_supervisor_marks_cleanup_failure_as_verifier_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "schema_version": "1.0",
        "request_id": "0" * 32,
        "returncode": 0,
        "stdout_base64": base64.b64encode(b"out").decode(),
        "stderr_base64": "",
        "timed_out": False,
        "output_limit_exceeded": False,
        "cleanup_complete": False,
        "spawn_error": None,
        "cleanup_error": {
            "code": "cleanup-residue",
            "stage": "cleanup",
            "message": "residue",
            "pids": [123],
        },
    }

    def cleanup_failure(*args, **kwargs):
        del args, kwargs
        return subprocess.CompletedProcess(
            [], 75, stdout=(json.dumps(payload) + "\n").encode(), stderr=b""
        )

    monkeypatch.setattr("nl2repobench.verification.go_supervisor.subprocess.run", cleanup_failure)
    monkeypatch.setattr(
        "nl2repobench.verification.go_supervisor.secrets.token_hex",
        lambda size: "0" * (size * 2),
    )
    result = run_go_bridge(("/usr/bin/true",), b"")
    assert result.cleanup_complete is False
    assert result.verifier_invalid is True
    assert result.returncode == 0


def test_go_supervisor_cleans_escaped_session_child(tmp_path: Path) -> None:
    result = run_go_bridge(
        (
            _python_script(
                tmp_path,
                "import os,time; child=os.fork(); time.sleep(30) if child == 0 else None",
            ),
        ),
        b"",
        timeout_sec=1,
    )
    assert result.returncode == 124
    assert result.timed_out is True


def test_go_candidate_boundary_has_no_independent_spawn_or_address_limit() -> None:
    root = Path(__file__).parents[1] / "src/nl2repobench/verification"
    source = "\n".join((root / name).read_text(encoding="utf-8") for name in (
        "go_supervisor.py", "go_bridge_proxy.py", "go_contract_runner.py"
    ))
    assert "preexec_fn" not in source
    assert "RLIMIT_AS" not in source
    assert "subprocess.Popen" not in source
    assert "candidate_process_cli" in (root / "go_supervisor.py").read_text(encoding="utf-8")


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
    command_plan = output / "tests/command-plan.json"
    assert load_go_command_plan(command_plan.read_bytes()).identity == "go+go-modules"
    validate_go_command_plan(command_plan)
    assert "COPY command-plan.json /tests/command-plan.json" in (
        output / "tests/Dockerfile"
    ).read_text()
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
    assert "verification.go_command_plan" in test_script
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
    locked = GoHarborCompiler(
        _current_locked_go_toolchain(root, tmp_path / "toolchain.go.lock.toml")
    )
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
    commands = store.put_bytes(
        canonical_json(CommandPlan.model_validate(EXPECTED_GO_PLAN)) + b"\n",
        media_type="application/vnd.nl2repobench.command-plan+json",
        visibility=Visibility.PRIVATE,
    )
    _canonical_go_source(
        root,
        source,
        module=module_bundle,
        verifier=verifier_bundle,
        oracle=oracle_bundle,
        commands=commands,
    )
    manifest_digest = CatalogCompiler(
        FileArtifactStore(tmp_path / "manifest-artifacts")
    ).compile_task(source, tmp_path / "manifest-output").manifest.content_digest()

    authorization = PrivateArtifactAuthorization(
        task_id="go-synthetic",
        manifest_digest=manifest_digest,
        purpose="compile",
        allowed_digests=frozenset(
            {
                module_bundle.digest,
                verifier_bundle.digest,
                oracle_bundle.digest,
                commands.digest,
            }
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
        _current_locked_go_toolchain(root, tmp_path / "toolchain.go.lock.toml"),
        artifact_resolver=resolver,
    )
    assert production._resolve_go_command_plan(commands) == CommandPlan.model_validate(  # noqa: SLF001
        EXPECTED_GO_PLAN
    )
    with pytest.raises(GoHarborCompileError, match="private-staging-contract-missing"):
        production.compile_task(source, tmp_path / "production")

    multi_leaf = tmp_path / "multi-leaf"
    _canonical_go_source(root, multi_leaf, expected_total=2)
    with pytest.raises(GoHarborCompileError, match="exactly one verifier-owned leaf"):
        development.compile_task(multi_leaf, tmp_path / "multi-output", allow_incomplete=True)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("identity", "python+uv"),
        ("runner", "pytest-subprocess-boundary-v1"),
        ("candidate_install", "pip-target-no-deps-v1"),
        ("report_format", "pytest-junit-xml-v1"),
    ],
)
def test_go_command_plan_rejects_other_adapter_semantics(field: str, value: str) -> None:
    payload = {**EXPECTED_GO_PLAN, field: value}
    data = canonical_json(CommandPlan.model_validate(payload)) + b"\n"

    with pytest.raises(ValueError, match="allowlisted verifier protocol"):
        load_go_command_plan(data)


def test_go_compiler_requires_private_authorized_command_plan_media(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    store = FileArtifactStore(tmp_path / "artifacts")
    data = canonical_json(CommandPlan.model_validate(EXPECTED_GO_PLAN)) + b"\n"
    commands = store.put_bytes(
        data,
        media_type="application/vnd.nl2repobench.command-plan+json",
        visibility=Visibility.PRIVATE,
    )
    allowed = store.put_bytes(b"allowed", visibility=Visibility.PRIVATE)
    authorization = PrivateArtifactAuthorization(
        task_id="go-synthetic",
        manifest_digest="sha256:" + "a" * 64,
        purpose="compile",
        allowed_digests=frozenset({commands.digest}),
        staging_root=(tmp_path / "staging").resolve(),
    )
    resolver = LocalArtifactResolver.scoped_private(
        store,
        authorization,
        task_id=authorization.task_id,
        manifest_digest=authorization.manifest_digest,
        purpose=authorization.purpose,
        staging_root=authorization.staging_root,
    )
    compiler = GoHarborCompiler(
        _current_locked_go_toolchain(root, tmp_path / "toolchain.go.lock.toml"),
        artifact_resolver=resolver,
    )

    wrong_media = commands.model_copy(update={"media_type": "application/json"})
    with pytest.raises(GoHarborCompileError, match="command-plan media type"):
        compiler._resolve_go_command_plan(wrong_media)  # noqa: SLF001

    public = store.put_bytes(
        data,
        media_type="application/vnd.nl2repobench.command-plan+json",
        visibility=Visibility.PUBLIC,
    )
    with pytest.raises(GoHarborCompileError, match="must be private"):
        compiler._resolve_go_command_plan(public)  # noqa: SLF001

    unauthorized = allowed.model_copy(
        update={"media_type": "application/vnd.nl2repobench.command-plan+json"}
    )
    with pytest.raises(GoHarborCompileError, match="not authorized"):
        compiler._resolve_go_command_plan(unauthorized)  # noqa: SLF001


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
