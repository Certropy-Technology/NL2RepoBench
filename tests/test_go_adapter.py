from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.harbor.go_compiler import GoHarborCompileError, GoHarborCompiler
from nl2repobench.package_managers.go_modules import GoModulesPackageManager
from nl2repobench.runtimes.go import GoRuntimeAdapter
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
        "import \"fmt\"\n\n"
        "func Normalize(value string) (string, error) {\n"
        "    if value == \"\" { return \"\", fmt.Errorf(\"empty\") }\n"
        "    return value + \"!\", nil\n"
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


def test_go_compiler_rejects_unimplemented_control_bundles(tmp_path: Path) -> None:
    compiler = GoHarborCompiler(Path(__file__).parents[1] / "toolchain.go.dev.lock.toml")

    with pytest.raises(GoHarborCompileError, match="unsupported Go control kind: stub"):
        compiler.prepare_control_bundle(tmp_path / "task", "stub", tmp_path / "controls")
