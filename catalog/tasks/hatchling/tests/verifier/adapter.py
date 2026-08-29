#!/usr/bin/env python3
"""Candidate-side observations for the bounded Hatchling contract."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tarfile
from tempfile import TemporaryDirectory
import zipfile


def configure_candidate(candidate_site: str) -> None:
    dependency_site = os.environ.get(
        "NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"
    )
    sys.path.insert(0, dependency_site)
    sys.path.insert(0, candidate_site)


def write_project(root: Path, *, variant: str = "basic") -> None:
    package = root / "src" / "acme_demo"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(
        '__version__ = "2.4.1"\n\n'
        'def greet(name: str) -> str:\n    return f"Hello, {name}!"\n',
        encoding="utf-8",
    )
    (package / "data.txt").write_text("payload\n", encoding="utf-8")
    (root / "README.md").write_text("# Acme Demo\n\nA deterministic fixture.\n", encoding="utf-8")
    (root / "LICENSE.txt").write_text("Fixture license\n", encoding="utf-8")
    (root / ".gitignore").write_text("dist/\n", encoding="utf-8")
    pyproject = '''\
[build-system]
requires = []
build-backend = "hatchling.build"

[project]
name = "Acme_Demo"
version = "2.4.1"
description = "A deterministic fixture"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
license-files = ["LICENSE.txt"]
authors = [{name = "Ada Example", email = "ada@example.test"}]
maintainers = [{name = "Maintainer"}]
keywords = ["build", "fixture"]
classifiers = ["Programming Language :: Python :: 3"]
dependencies = ["packaging>=24", "pluggy; python_version >= '3.10'"]

[project.optional-dependencies]
test = ["pytest>=8"]

[project.urls]
Homepage = "https://example.test/acme"

[project.scripts]
acme-demo = "acme_demo:greet"

[project.gui-scripts]
acme-gui = "acme_demo:greet"

[project.entry-points."acme.plugins"]
demo = "acme_demo:greet"

[tool.hatch.build.targets.wheel]
packages = ["src/acme_demo"]
'''
    if variant == "selection":
        (root / "notes.txt").write_text("include me\n", encoding="utf-8")
        (root / "secret.txt").write_text("exclude me\n", encoding="utf-8")
        pyproject += '''\
include = ["src/acme_demo/**", "notes.txt"]
exclude = ["**/data.txt", "secret.txt"]
'''
    (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")


def in_project(variant: str = "basic"):
    temporary = TemporaryDirectory(prefix="hatchling-case-")
    root = Path(temporary.name)
    write_project(root, variant=variant)
    old = Path.cwd()
    os.chdir(root)
    return temporary, root, old


def restore_project(temporary: TemporaryDirectory, old: Path) -> None:
    os.chdir(old)
    temporary.cleanup()


def metadata_headers(data: str) -> dict[str, object]:
    from email.parser import Parser

    message = Parser().parsestr(data)
    return {
        "name": message["Name"],
        "version": message["Version"],
        "summary": message["Summary"],
        "requires_python": message["Requires-Python"],
        "requires_dist": message.get_all("Requires-Dist", []),
        "provides_extra": message.get_all("Provides-Extra", []),
        "project_urls": message.get_all("Project-URL", []),
        "license_expression": message["License-Expression"],
        "license_files": message.get_all("License-File", []),
    }


def api_surface():
    import hatchling.build as build
    from hatchling.__about__ import __version__

    return {
        "version": __version__,
        "all": list(build.__all__),
        "callable": {name: callable(getattr(build, name, None)) for name in build.__all__ if name != "__all__"},
    }


def metadata_utils():
    from hatchling.metadata.utils import (
        is_valid_import_name,
        is_valid_project_name,
        normalize_project_name,
        split_import_name_annotation,
    )

    names = ["Demo", "demo.pkg", "demo_pkg", "demo--pkg", "-bad", "bad-", "", "a"]
    imports = ["pkg", "pkg.sub", "pkg.sub ; private", "pkg; unknown", "bad-name", ".bad"]
    return {
        "normalized": [normalize_project_name(name) for name in names],
        "valid_names": [is_valid_project_name(name) for name in names],
        "imports": [[value, is_valid_import_name(value), list(split_import_name_annotation(value))] for value in imports],
    }


def requirement_normalization():
    from packaging.requirements import Requirement
    from hatchling.metadata.utils import get_normalized_dependency

    values = [
        'Demo_Pkg[Foo_Bar,baz]>=1.0,!=1.5; python_version >= "3.10"',
        "Other.Pkg~=2.0",
        "simple",
    ]
    return [get_normalized_dependency(Requirement(value)) for value in values]


def version_file():
    from hatchling.version.core import VersionFile

    with TemporaryDirectory(prefix="hatchling-version-") as td:
        root = Path(td)
        path = root / "pkg" / "version.py"
        version_file = VersionFile(str(root), "pkg/version.py")
        path.parent.mkdir()
        path.write_text("__version__ = '1.2.3'\n", encoding="utf-8")
        first = version_file.read(pattern=True)
        version_file.set_version("2.0rc1")
        second = VersionFile(str(root), "pkg/version.py").read(pattern=True)
        generated = root / "generated.py"
        generated_file = VersionFile(str(root), "generated.py")
        generated_file.write("3.4.5")
        custom = root / "custom.txt"
        custom.write_text("release = 7.8.9\n", encoding="utf-8")
        third = VersionFile(str(root), "custom.txt").read(pattern=r"release = (?P<version>.+)")
        return {"first": first, "second": second, "custom": third, "generated": generated.read_text(encoding="utf-8").splitlines()[-1]}


def version_file_errors():
    from hatchling.version.core import VersionFile

    results = []
    with TemporaryDirectory(prefix="hatchling-version-errors-") as td:
        root = Path(td)
        for relative, pattern in [("missing.py", True), ("bad.py", True), ("nogroup.py", r"value=(.+)")]:
            if relative != "missing.py":
                (root / relative).write_text("value=123\n", encoding="utf-8")
            try:
                VersionFile(str(root), relative).read(pattern=pattern)
            except Exception as error:
                results.append([type(error).__name__, str(error)])
    return results


def standard_version_scheme():
    from hatchling.version.scheme.standard import StandardScheme

    scheme = StandardScheme(root=".", config={})
    operations = ["major", "minor", "patch", "a", "b", "rc", "post", "dev", "release", "2.5.0"]
    output = {}
    for operation in operations:
        try:
            output[operation] = scheme.update(operation, "1.2.3", {})
        except Exception as error:
            output[operation] = [type(error).__name__, str(error)]
    return output


def plugin_builtins():
    from hatchling.plugin.manager import PluginManager

    manager = PluginManager()
    return {
        "builders": sorted(manager.builder.collect(include_third_party=False)),
        "build_hooks": sorted(manager.build_hook.collect(include_third_party=False)),
        "metadata_hooks": sorted(manager.metadata_hook.collect(include_third_party=False)),
        "version_schemes": sorted(manager.version_scheme.collect(include_third_party=False)),
        "version_sources": sorted(manager.version_source.collect(include_third_party=False)),
    }


def project_metadata_basic():
    from hatchling.metadata.core import ProjectMetadata
    from hatchling.metadata.utils import resolve_metadata_fields
    from hatchling.plugin.manager import PluginManager

    temporary, root, old = in_project()
    try:
        metadata = ProjectMetadata(str(root), PluginManager())
        fields = resolve_metadata_fields(metadata)
        return {
            "has_file": metadata.has_project_file(),
            "name": metadata.name,
            "version": metadata.version,
            "build": {"backend": metadata.build.build_backend, "requires": metadata.build.requires},
            "fields": fields,
        }
    finally:
        restore_project(temporary, old)


def project_metadata_errors():
    from hatchling.metadata.core import ProjectMetadata
    from hatchling.plugin.manager import PluginManager

    configs = [
        {},
        {"project": {}},
        {"project": {"name": "-bad", "version": "1.0"}},
        {"project": {"name": "ok", "version": "not a version"}},
        {"project": {"name": "ok", "version": "1.0", "dependencies": "bad"}},
    ]
    output = []
    with TemporaryDirectory(prefix="hatchling-metadata-errors-") as td:
        for config in configs:
            metadata = ProjectMetadata(td, PluginManager(), config=config)
            try:
                metadata.core.validate_fields()
                output.append("ok")
            except Exception as error:
                output.append([type(error).__name__, str(error)])
    return output


def build_requires():
    import hatchling.build as build

    temporary, _root, old = in_project()
    try:
        return {
            "sdist": build.get_requires_for_build_sdist(),
            "wheel": build.get_requires_for_build_wheel(),
            "editable": build.get_requires_for_build_editable(),
        }
    finally:
        restore_project(temporary, old)


def prepare_metadata():
    import hatchling.build as build

    temporary, root, old = in_project()
    try:
        output = root / "metadata"
        output.mkdir()
        directory = build.prepare_metadata_for_build_wheel(str(output))
        metadata = (output / directory / "METADATA").read_text(encoding="utf-8")
        return {"directory": directory, "headers": metadata_headers(metadata), "body_tail": metadata.split("\n\n", 1)[1].strip()}
    finally:
        restore_project(temporary, old)


def build_wheel_basic():
    import hatchling.build as build

    temporary, root, old = in_project()
    try:
        output = root / "dist"
        output.mkdir()
        filename = build.build_wheel(str(output))
        with zipfile.ZipFile(output / filename) as archive:
            members = archive.namelist()
            metadata_name = next(name for name in members if name.endswith(".dist-info/METADATA"))
            wheel_name = next(name for name in members if name.endswith(".dist-info/WHEEL"))
            return {
                "filename": filename,
                "members": members,
                "metadata": metadata_headers(archive.read(metadata_name).decode()),
                "wheel": archive.read(wheel_name).decode().splitlines(),
            }
    finally:
        restore_project(temporary, old)


def build_wheel_entry_points():
    import hatchling.build as build

    temporary, root, old = in_project()
    try:
        output = root / "dist"
        output.mkdir()
        filename = build.build_wheel(str(output))
        with zipfile.ZipFile(output / filename) as archive:
            name = next(item for item in archive.namelist() if item.endswith("entry_points.txt"))
            return archive.read(name).decode().splitlines()
    finally:
        restore_project(temporary, old)


def build_wheel_record():
    import hatchling.build as build

    temporary, root, old = in_project()
    try:
        output = root / "dist"
        output.mkdir()
        filename = build.build_wheel(str(output))
        with zipfile.ZipFile(output / filename) as archive:
            record_name = next(item for item in archive.namelist() if item.endswith(".dist-info/RECORD"))
            rows = [line.split(",") for line in archive.read(record_name).decode().splitlines()]
            return {
                "count": len(rows),
                "self": rows[-1],
                "hashed": all(row[1].startswith("sha256=") and row[2].isdigit() for row in rows[:-1]),
                "sorted": [row[0] for row in rows],
            }
    finally:
        restore_project(temporary, old)


def build_wheel_selection():
    import hatchling.build as build

    temporary, root, old = in_project("selection")
    try:
        output = root / "dist"
        output.mkdir()
        filename = build.build_wheel(str(output))
        with zipfile.ZipFile(output / filename) as archive:
            return archive.namelist()
    finally:
        restore_project(temporary, old)


def build_wheel_reproducible():
    import hatchling.build as build

    temporary, root, old = in_project()
    old_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = "1700000000"
    try:
        digests = []
        timestamps = []
        for index in range(2):
            output = root / f"dist{index}"
            output.mkdir()
            filename = build.build_wheel(str(output))
            data = (output / filename).read_bytes()
            digests.append(hashlib.sha256(data).hexdigest())
            with zipfile.ZipFile(output / filename) as archive:
                timestamps.append(sorted({item.date_time for item in archive.infolist()}))
        return {"same": digests[0] == digests[1], "timestamps": timestamps, "size": len(data)}
    finally:
        if old_epoch is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)
        else:
            os.environ["SOURCE_DATE_EPOCH"] = old_epoch
        restore_project(temporary, old)


def build_sdist_basic():
    import hatchling.build as build

    temporary, root, old = in_project()
    try:
        output = root / "dist"
        output.mkdir()
        filename = build.build_sdist(str(output))
        with tarfile.open(output / filename, "r:gz") as archive:
            members = archive.getnames()
            pkg_info = next(name for name in members if name.endswith("/PKG-INFO"))
            data = archive.extractfile(pkg_info).read().decode()
            return {"filename": filename, "members": members, "metadata": metadata_headers(data)}
    finally:
        restore_project(temporary, old)


def build_sdist_reproducible():
    import hatchling.build as build

    temporary, root, old = in_project()
    old_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = "1700000000"
    try:
        output = root / "dist"
        output.mkdir()
        filename = build.build_sdist(str(output))
        with tarfile.open(output / filename, "r:gz") as archive:
            members = archive.getmembers()
            return {
                "members": [member.name for member in members],
                "modes": sorted({oct(member.mode) for member in members}),
                "mtimes": sorted({member.mtime for member in members}),
                "gzip": (output / filename).read_bytes()[:2].hex(),
            }
    finally:
        if old_epoch is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)
        else:
            os.environ["SOURCE_DATE_EPOCH"] = old_epoch
        restore_project(temporary, old)


def builder_utils():
    from hatchling.builders.utils import (
        format_file_hash,
        get_known_python_major_versions,
        get_relative_path,
        get_reproducible_timestamp,
        normalize_file_permissions,
        normalize_inclusion_map,
        normalize_relative_directory,
        normalize_relative_path,
    )

    with TemporaryDirectory(prefix="hatchling-utils-") as td:
        root = Path(td)
        old_epoch = os.environ.get("SOURCE_DATE_EPOCH")
        os.environ["SOURCE_DATE_EPOCH"] = "1234567890"
        try:
            inclusion = normalize_inclusion_map({"src/pkg": "pkg", "README.md": "docs/README.md"}, str(root))
            return {
                "hash": format_file_hash(hashlib.sha256(b"demo").digest()),
                "majors": list(get_known_python_major_versions()),
                "relative": [get_relative_path(str(root), str(root)), get_relative_path(str(root / "a"), str(root))],
                "paths": [normalize_relative_path("./a/b/"), normalize_relative_directory("./a/b/")],
                "permissions": [oct(normalize_file_permissions(mode)) for mode in (stat.S_IFREG | 0o600, stat.S_IFREG | 0o700)],
                "timestamp": get_reproducible_timestamp(),
                "inclusion": [[Path(source).relative_to(root).as_posix(), target] for source, target in inclusion.items()],
            }
        finally:
            if old_epoch is None:
                os.environ.pop("SOURCE_DATE_EPOCH", None)
            else:
                os.environ["SOURCE_DATE_EPOCH"] = old_epoch


def core_metadata_roundtrip():
    from hatchling.metadata.core import ProjectMetadata
    from hatchling.metadata.spec import construct_metadata_file_2_4, project_metadata_from_core_metadata
    from hatchling.plugin.manager import PluginManager

    temporary, root, old = in_project()
    try:
        metadata = ProjectMetadata(str(root), PluginManager())
        text = construct_metadata_file_2_4(metadata)
        parsed = project_metadata_from_core_metadata(text)
        return {
            "headers": metadata_headers(text),
            "parsed": {key: parsed.get(key) for key in ("name", "version", "description", "requires-python", "dependencies", "optional-dependencies")},
        }
    finally:
        restore_project(temporary, old)


def wheel_default_tag():
    from hatchling.builders.wheel import WheelBuilder

    temporary, root, old = in_project()
    try:
        builder = WheelBuilder(str(root))
        return {"tag": builder.get_default_tag(), "artifact_project_id": builder.artifact_project_id, "versions": builder.get_default_versions()}
    finally:
        restore_project(temporary, old)


SCENARIOS = {
    "api-surface": api_surface,
    "metadata-utils": metadata_utils,
    "requirement-normalization": requirement_normalization,
    "version-file": version_file,
    "version-file-errors": version_file_errors,
    "standard-version-scheme": standard_version_scheme,
    "plugin-builtins": plugin_builtins,
    "project-metadata-basic": project_metadata_basic,
    "project-metadata-errors": project_metadata_errors,
    "build-requires": build_requires,
    "prepare-metadata": prepare_metadata,
    "build-wheel-basic": build_wheel_basic,
    "build-wheel-entry-points": build_wheel_entry_points,
    "build-wheel-record": build_wheel_record,
    "build-wheel-selection": build_wheel_selection,
    "build-wheel-reproducible": build_wheel_reproducible,
    "build-sdist-basic": build_sdist_basic,
    "build-sdist-reproducible": build_sdist_reproducible,
    "builder-utils": builder_utils,
    "core-metadata-roundtrip": core_metadata_roundtrip,
    "wheel-default-tag": wheel_default_tag,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=SCENARIOS, required=True)
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    configure_candidate(args.candidate_site)
    try:
        value = SCENARIOS[args.scenario]()
        payload = {"schema_version": "1.0", "scenario": args.scenario, "ok": True, "value": value}
    except BaseException as error:
        payload = {
            "schema_version": "1.0",
            "scenario": args.scenario,
            "ok": False,
            "exception_type": f"{type(error).__module__}.{type(error).__qualname__}",
            "exception_message": str(error),
        }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
