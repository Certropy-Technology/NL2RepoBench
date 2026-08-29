#!/usr/bin/env python3
"""Child-side deterministic adapter for the distro public contract."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

CANDIDATE_SITE = ""


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect(exc_type: type[BaseException], function, message: str) -> None:
    try:
        function()
    except exc_type:
        return
    except BaseException as exc:
        raise AssertionError(f"{message}: expected {exc_type.__name__}, got {type(exc).__name__}") from exc
    raise AssertionError(f"{message}: expected {exc_type.__name__}")


def write_os_release(root: Path, *, name: str = "Foo Linux", distro_id: str = "ol") -> None:
    etc = root / "etc"
    etc.mkdir(parents=True, exist_ok=True)
    (etc / "os-release").write_text(
        f'NAME="{name}"\n'
        f"ID={distro_id}\n"
        'ID_LIKE="rhel fedora"\n'
        f'PRETTY_NAME="{name} 9.4"\n'
        'VERSION_ID="9.4.2"\n'
        'VERSION="9.4.2 (Saffron)"\n'
        'VERSION_CODENAME=saffron\n'
        "# ignored comment\n",
        encoding="utf-8",
    )


def make_distribution(root: Path):
    from distro import LinuxDistribution

    return LinuxDistribution(root_dir=str(root), include_lsb=False, include_uname=False, include_oslevel=False)


def api_surface() -> None:
    import distro

    required = {
        "LinuxDistribution", "linux_distribution", "id", "name", "version", "version_parts",
        "major_version", "minor_version", "build_number", "like", "codename", "info",
        "os_release_info", "lsb_release_info", "distro_release_info", "uname_info",
        "os_release_attr", "lsb_release_attr", "distro_release_attr", "uname_attr",
        "NORMALIZED_OS_ID", "NORMALIZED_LSB_ID", "NORMALIZED_DISTRO_ID", "__version__",
    }
    check((required - {"__version__"}).issubset(set(distro.__all__)), "root __all__ is incomplete")
    check(distro.__version__ == "1.9.0", "release metadata mismatch")
    check(distro.NORMALIZED_OS_ID["ol"] == "oracle", "OS ID normalization missing")
    check(distro.NORMALIZED_OS_ID["opensuse-leap"] == "opensuse", "openSUSE normalization missing")


def os_release_instance() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        distribution = make_distribution(root)
        check(distribution.os_release_info()["name"] == "Foo Linux", "NAME parse failed")
        check(distribution.os_release_info()["version_id"] == "9.4.2", "VERSION_ID parse failed")
        check(distribution.os_release_info()["codename"] == "saffron", "codename parse failed")
        check(distribution.id() == "oracle", "ID normalization failed")
        check(distribution.name() == "Foo Linux", "machine name failed")
        check(distribution.name(pretty=True) == "Foo Linux 9.4", "pretty name failed")
        check(distribution.version() == "9.4.2", "version failed")
        check(distribution.version(pretty=True) == "9.4.2 (saffron)", "pretty version failed")
        check(distribution.like() == "rhel fedora", "ID_LIKE failed")
        check(distribution.codename() == "saffron", "codename accessor failed")


def normalization_and_versions() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        distribution = make_distribution(root)
        check(distribution.version_parts() == ("9", "4", "2"), "version parts failed")
        check(distribution.major_version() == "9", "major version failed")
        check(distribution.minor_version() == "4", "minor version failed")
        check(distribution.build_number() == "2", "build number failed")
        check(distribution.info() == {
            "id": "oracle", "version": "9.4.2",
            "version_parts": {"major": "9", "minor": "4", "build_number": "2"},
            "like": "rhel fedora", "codename": "saffron",
        }, "info projection failed")
        check(distribution.linux_distribution(False) == ("oracle", "9.4.2", "Saffron"), "legacy tuple failed")
        check(distribution.linux_distribution(True) == ("Foo Linux", "9.4.2", "Saffron"), "pretty legacy tuple failed")


def release_file_fallback() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        etc = root / "etc"
        etc.mkdir()
        (etc / "foo-release").write_text("Foo Linux release 3.4 (Bar)\n", encoding="utf-8")
        distribution = make_distribution(root)
        check(distribution.distro_release_info() == {"name": "Foo Linux", "version_id": "3.4", "codename": "Bar", "id": "foo"}, "release fallback parse failed")
        check(distribution.info() == {"id": "foo", "version": "3.4", "version_parts": {"major": "3", "minor": "4", "build_number": ""}, "like": "", "codename": "Bar"}, "release fallback projection failed")


def root_isolation() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root, name="Private Linux", distro_id="debian")
        distribution = make_distribution(root)
        check(distribution.root_dir == str(root), "root directory was not retained")
        check(distribution.id() == "debian", "explicit root was not used")
        expect(ValueError, lambda: __import__("distro").LinuxDistribution(root_dir=str(root), include_lsb=True), "root/subprocess guard")


def global_accessors() -> None:
    import distro
    from distro import distro as implementation

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        old = implementation._distro
        implementation._distro = make_distribution(root)
        try:
            check(distro.id() == "oracle" and distro.name(pretty=True) == "Foo Linux 9.4", "global accessors failed")
            check(distro.version_parts() == ("9", "4", "2"), "global version parts failed")
            check(distro.os_release_attr("version_id") == "9.4.2", "global source accessor failed")
            check(distro.info()["codename"] == "saffron", "global info failed")
        finally:
            implementation._distro = old


def deprecated_compatibility() -> None:
    import distro
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        distribution = make_distribution(root)
        result = distribution.linux_distribution()
        check(result == ("Foo Linux", "9.4.2", "Saffron"), "instance compatibility tuple failed")
        implementation = __import__("distro.distro", fromlist=["distro"])
        old = implementation._distro
        implementation._distro = distribution
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                check(distro.linux_distribution(False) == ("oracle", "9.4.2", "Saffron"), "module compatibility tuple failed")
            check(any(item.category is DeprecationWarning for item in caught), "module deprecation warning missing")
        finally:
            implementation._distro = old


def cli_text() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        result = subprocess.run([sys.executable, "-m", "distro", "--root-dir", str(root)], capture_output=True, text=True, check=True, env={**os.environ, "PYTHONPATH": CANDIDATE_SITE})
        check(result.stdout == "Name: Foo Linux 9.4\nVersion: 9.4.2 (saffron)\nCodename: saffron\n", "CLI text output mismatch")
        check(result.stderr == "", "CLI wrote diagnostics to stderr")


def cli_json() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        result = subprocess.run([sys.executable, "-m", "distro", "--json", "--root-dir", str(root)], capture_output=True, text=True, check=True, env={**os.environ, "PYTHONPATH": CANDIDATE_SITE})
        payload = json.loads(result.stdout)
        check(payload == {"codename": "saffron", "id": "oracle", "like": "rhel fedora", "version": "9.4.2", "version_parts": {"build_number": "2", "major": "9", "minor": "4"}}, "CLI JSON output mismatch")


def source_accessors() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        distribution = make_distribution(root)
        check(distribution.os_release_attr("name") == "Foo Linux", "os-release attribute failed")
        check(distribution.os_release_attr("missing") == "", "missing attribute contract failed")
        check(distribution.distro_release_attr("name") == "", "empty fallback source contract failed")
        check(distribution.lsb_release_info() == {}, "root LSB source should be empty")
        check(distribution.uname_info() == {}, "root uname source should be empty")


def constructor_contract() -> None:
    from distro import LinuxDistribution
    expect(ValueError, lambda: LinuxDistribution(root_dir="/tmp", include_uname=True), "root/uname guard")
    expect(ValueError, lambda: LinuxDistribution(root_dir="/tmp", include_oslevel=True), "root/oslevel guard")
    expect(TypeError, lambda: LinuxDistribution(root_dir="/tmp", unknown_option=True), "unknown constructor option")


def metadata_and_determinism() -> None:
    import distro
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        first = make_distribution(root)
        second = make_distribution(root)
        check(repr(first) == repr(second), "repr is not deterministic")
        check(first.info() == second.info(), "info is not deterministic")
        check(isinstance(distro.__version__, str), "version type missing")


def missing_data() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        distribution = make_distribution(Path(temporary))
        check(distribution.info() == {"id": "", "version": "", "version_parts": {"major": "", "minor": "", "build_number": ""}, "like": "", "codename": ""}, "missing data projection failed")
        check(distribution.os_release_info() == {}, "missing os-release should be empty")
        check(distribution.distro_release_info() == {}, "missing release files should be empty")


def version_best() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        distribution = make_distribution(root)
        check(distribution.version(best=True) == "9.4.2", "best version failed")
        check(distribution.version_parts(best=True) == ("9", "4", "2"), "best version parts failed")


def local_only_behavior() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_os_release(root)
        distribution = make_distribution(root)
        check(distribution.os_release_info()["id"] == "ol", "fixture access failed")
        check(distribution.info()["id"] == "oracle", "local projection failed")


SCENARIOS = {
    "api-surface": api_surface,
    "os-release-instance": os_release_instance,
    "normalization-and-versions": normalization_and_versions,
    "release-file-fallback": release_file_fallback,
    "root-isolation": root_isolation,
    "global-accessors": global_accessors,
    "deprecated-compatibility": deprecated_compatibility,
    "cli-text": cli_text,
    "cli-json": cli_json,
    "source-accessors": source_accessors,
    "constructor-contract": constructor_contract,
    "metadata-and-determinism": metadata_and_determinism,
    "missing-data": missing_data,
    "version-best": version_best,
    "local-only-behavior": local_only_behavior,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    global CANDIDATE_SITE
    CANDIDATE_SITE = args.candidate_site
    sys.path.insert(0, args.candidate_site)
    try:
        SCENARIOS[args.scenario]()
    except BaseException as exc:
        verdict = {"id": args.scenario, "status": "failed", "message": f"{type(exc).__name__}: {exc}"}
    else:
        verdict = {"id": args.scenario, "status": "passed"}
    args.output.write_text(json.dumps(verdict, sort_keys=True), encoding="utf-8")
    return 0 if verdict["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
