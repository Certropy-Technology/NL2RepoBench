from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.harbor.ruby_compiler import RubyHarborCompileError, RubyHarborCompiler
from nl2repobench.package_managers.bundler import BundlerPackageManager
from nl2repobench.runtimes.ruby import RubyRuntimeAdapter
from nl2repobench.verification.normalize.ruby_json import normalize_ruby_json
from nl2repobench.verification.ruby_contract_report import build_report
from nl2repobench.verification.ruby_grader import grade_ruby_report
from nl2repobench.verification.ruby_supervisor import run_ruby_bridge

ROOT = Path(__file__).parents[1]
# The Ruby lane fixture is a development-only synthetic task, so it lives under
# tests/fixtures rather than the public catalog/sources authoring surface.
RUBY_SOURCE = ROOT / "tests/fixtures/ruby-v1/ruby-synthetic"
RUBY_TOOLCHAIN = ROOT / "toolchain.ruby.dev.lock.toml"


def test_bundler_validates_offline_cache_manifest(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    shutil.copytree(RUBY_SOURCE / "harbor/dependencies", bundle)
    BundlerPackageManager().validate_offline_store(
        bundle,
        lockfile=bundle / "Gemfile.lock",
        manifest=bundle / "gem.manifest.json",
        expected_version="2.6.9",
    )


def test_ruby_runtime_identity_is_explicit() -> None:
    assert RubyRuntimeAdapter.identity == RuntimeDiscriminator(
        language=RuntimeLanguage.RUBY,
        package_manager=PackageManager.BUNDLER,
    )
    assert BundlerPackageManager().install_command(store_dir="/tmp/gems") == (
        "/usr/bin/env",
        "BUNDLE_PATH=/tmp/gems",
        "/usr/local/bin/bundle",
        "install",
        "--local",
        "--jobs",
        "1",
        "--retry",
        "0",
    )


def test_bundler_rejects_git_source(tmp_path: Path) -> None:
    gemfile = tmp_path / "Gemfile"
    gemfile.write_text('source "https://rubygems.org"\n', encoding="utf-8")
    lockfile = tmp_path / "Gemfile.lock"
    lockfile.write_text(
        "GIT\n  remote: https://example.invalid/repo.git\n\n"
        "PLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="GIT"):
        BundlerPackageManager().validate_lock(lockfile, expected_version="2.6.9")


def test_ruby_report_normalizes_to_canonical_leaves() -> None:
    report = normalize_ruby_json(
        report_data={
            "framework": "ruby",
            "report_format": "ruby-contract-json-v1",
            "collected": 1,
            "tests": [{"test_id": "contract::public-api", "status": "passed"}],
            "collection_errors": [],
            "runner_exit_code": 0,
        },
        frozen_total=1,
        trusted_runner_exit_code=0,
    )
    assert report.framework == "ruby"
    assert report.leaves[0].status == "passed"


def test_ruby_report_uses_fixed_denominator_grader() -> None:
    result = grade_ruby_report(
        expected_total=1,
        report_data={
            "framework": "ruby",
            "report_format": "ruby-contract-json-v1",
            "collected": 1,
            "tests": [{"test_id": "contract::public-api", "status": "failed"}],
            "collection_errors": [],
            "runner_exit_code": 1,
        },
        runner_exit_code=1,
    )
    assert result.valid is True
    assert result.reward == 0.0
    assert result.frozen_total == 1


def test_ruby_contract_report_collects_multiple_leaves(tmp_path: Path) -> None:
    output = tmp_path / "contract.jsonl"
    output.write_text(
        '{"test_id":"one","status":"passed"}\n'
        '{"test_id":"two","status":"failed","details":"mismatch"}\n',
        encoding="utf-8",
    )
    report = build_report(output, expected=2, runner_exit_code=1)
    assert report["collected"] == 2
    assert report["collection_errors"] == []
    assert [case["status"] for case in report["tests"]] == ["passed", "failed"]


def test_ruby_compiler_writes_development_bundle(tmp_path: Path) -> None:
    output = RubyHarborCompiler(RUBY_TOOLCHAIN).compile_task(
        RUBY_SOURCE, tmp_path, allow_incomplete=True
    )
    task = (output / "task.toml").read_text(encoding="utf-8")
    assert 'language = "ruby"' in task
    assert 'package_manager = "bundler"' in task
    assert (output / "tests/private/bridge.rb").is_file()
    assert "network_mode: none" in (output / "tests/docker-compose.yaml").read_text()
    assert (output / "environment/gem-bundle/Gemfile.lock").is_file()
    assert (output / "tests/test.sh").stat().st_mode & 0o111
    test_script = (output / "tests/test.sh").read_text(encoding="utf-8")
    assert "max_output_bytes=256*1024," in test_script
    assert "max_file_bytes=512*1024*1024);" in test_script


def test_ruby_compiler_rejects_production_with_development_toolchain(tmp_path: Path) -> None:
    with pytest.raises(RubyHarborCompileError, match="locked toolchain"):
        RubyHarborCompiler(RUBY_TOOLCHAIN).compile_task(RUBY_SOURCE, tmp_path)


def test_ruby_bridge_caps_output_flood() -> None:
    result = run_ruby_bridge(
        (sys.executable, "-c", "print('x' * 1000000)"),
        b"",
        timeout_sec=5,
        max_output_bytes=1024,
    )
    assert result.output_limit_exceeded is True
    assert result.returncode == 125
    assert len(result.stdout) <= 1024


def test_ruby_bridge_file_limit_is_separate_from_output_limit() -> None:
    descriptor, output_name = tempfile.mkstemp(prefix="ruby-supervisor-")
    os.close(descriptor)
    output_path = Path(output_name)
    try:
        output_path.chmod(0o666)
        result = run_ruby_bridge(
            (
                sys.executable,
                "-c",
                f"open({str(output_path)!r}, 'wb').write(b'x' * 2048)",
            ),
            b"",
            timeout_sec=5,
            max_output_bytes=1024,
            max_file_bytes=4096,
        )
        assert result.returncode == 0
        assert output_path.stat().st_size == 2048
    finally:
        output_path.unlink(missing_ok=True)
