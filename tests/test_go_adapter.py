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

from nl2repobench.domain.models import Visibility
from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.harbor.go_compiler import GoHarborCompileError, GoHarborCompiler
from nl2repobench.package_managers.go_modules import GoModulesPackageManager
from nl2repobench.runtimes.go import GoRuntimeAdapter
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.verification.go_bridge import (
    GoBridgeOperation,
    GoBridgeSpec,
    generate_go_bridge,
)
from nl2repobench.verification.go_supervisor import run_go_bridge


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
    summary = GoModulesPackageManager().validate_lock(go_mod, expected_version="1.26.5")
    (root / "module.manifest.json").write_text(
        json.dumps({"schema_version": "1.0", **summary, "offline": True, "files": files}),
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


def test_go_modules_validates_offline_vendor_closure(tmp_path) -> None:
    _go_bundle(tmp_path)
    adapter = GoModulesPackageManager()
    adapter.validate_offline_store(
        tmp_path,
        lockfile=tmp_path / "go.mod",
        manifest=tmp_path / "module.manifest.json",
        expected_version="1.26.5",
    )
    assert adapter.install_command(store_dir="/vendor") == (
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
        GoModulesPackageManager().validate_lock(tmp_path / "go.mod", expected_version="1.26.5")


def test_go_runtime_identity_is_explicit() -> None:
    assert GoRuntimeAdapter.identity == RuntimeDiscriminator(
        language=RuntimeLanguage.GO,
        package_manager=PackageManager.GO_MODULES,
    )


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
    output = GoHarborCompiler(root / "toolchain.go.dev.lock.toml").compile_task(
        root / "catalog/sources/go-synthetic",
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
    assert 'expected_version="1.26.5"' in (output / "tests/test.sh").read_text()
    test_script = (output / "tests/test.sh").read_text()
    assert "rm -rf /tmp/go-candidate/vendor" in test_script
    assert "cp -a /opt/go-module-bundle/vendor /tmp/go-candidate/vendor" in test_script


def test_go_compiler_rejects_missing_control_script(tmp_path: Path) -> None:
    compiler = GoHarborCompiler(Path(__file__).parents[1] / "toolchain.go.dev.lock.toml")

    with pytest.raises(GoHarborCompileError, match="Go control script is missing"):
        compiler.prepare_control_bundle(tmp_path / "task", "stub", tmp_path / "controls")


def test_go_compiler_separates_development_and_locked_toolchains(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    development = GoHarborCompiler(root / "toolchain.go.dev.lock.toml")
    locked = GoHarborCompiler(root / "toolchain.go.lock.toml")

    with pytest.raises(GoHarborCompileError, match="toolchain.go.lock.toml"):
        development.compile_task(root / "catalog/sources/go-google-uuid", tmp_path)
    with pytest.raises(GoHarborCompileError, match="private artifact resolver is required"):
        locked.compile_task(root / "catalog/sources/go-google-uuid", tmp_path)

    source = tmp_path / "source"
    shutil.copytree(root / "catalog/sources/go-google-uuid", source)
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
    descriptor = source / "task.toml"
    data = descriptor.read_text(encoding="utf-8")
    data = re.sub(
        r"module_bundle = \{[^\n]+\}",
        "module_bundle = " + _artifact_toml(module_bundle),
        data,
    )
    data = re.sub(
        r"^bundle = \{[^\n]+\}",
        "bundle = " + _artifact_toml(verifier_bundle),
        data,
        count=1,
        flags=re.MULTILINE,
    )
    data = re.sub(
        r"oracle_bundle = \{[^\n]+\}",
        "oracle_bundle = " + _artifact_toml(oracle_bundle),
        data,
        count=1,
    )
    descriptor.write_text(data, encoding="utf-8")

    production = GoHarborCompiler(
        root / "toolchain.go.lock.toml",
        artifact_resolver=LocalArtifactResolver(
            store,
            allow_private=True,
        ),
    )
    output = production.compile_task(
        source, tmp_path / "production"
    )
    manifest = json.loads((output / "bundle.manifest.json").read_text())
    assert manifest["mode"] == "production"
    assert (output / "tests/private/contract.sh").is_file()
    assert (output / "tests/private/bridge.go").is_file()
    assert (output / "solution/solve.sh").is_file()

    multi_leaf = tmp_path / "multi-leaf"
    shutil.copytree(root / "catalog/sources/go-google-uuid", multi_leaf)
    descriptor = multi_leaf / "task.toml"
    descriptor.write_text(
        descriptor.read_text().replace("expected_total = 1", "expected_total = 2"),
        encoding="utf-8",
    )
    with pytest.raises(GoHarborCompileError, match="exactly one verifier-owned leaf"):
        development.compile_task(multi_leaf, tmp_path / "multi-output", allow_incomplete=True)
