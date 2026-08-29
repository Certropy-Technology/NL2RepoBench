# Build `hatchling`

## Project Description

Create a complete, installable Python distribution named `hatchling` from an
empty workspace. Hatchling is a standards-compliant Python build backend. It
reads `pyproject.toml` project metadata and produces deterministic wheels,
source distributions, and metadata through the PEP 517 and PEP 660 hooks.

The target version is `1.32.0`. Do not wrap or import an already-installed copy
of Hatchling. The evaluator installs your project normally and exercises its
public modules in isolated child processes.

## Supports

- Support Python 3.10 and newer; the evaluation runtime is CPython 3.12.
- Provide a normal `pyproject.toml` project whose distribution name and import
  package are both `hatchling`.
- Expose `hatchling.__about__.__version__ == "1.32.0"`.
- Declare these runtime dependencies with compatible lower bounds:
  `packaging>=24.2`, `pathspec>=0.10.1`, `pluggy>=1.0.0`,
  `tomlkit>=0.11.1`, `trove-classifiers`, and `tomli>=1.2.2` only on Python
  versions below 3.11.
- Provide the `hatchling` console script and the `hatchling.build` backend.
- Perform all metadata parsing and standard wheel/sdist builds locally. Normal
  operation must not require network access or an external service.
- Respect `SOURCE_DATE_EPOCH` so repeating a build from unchanged bytes is
  reproducible.

## API Usage Guide

### PEP 517 and PEP 660 backend

`hatchling.build` exports:

```python
get_requires_for_build_sdist(config_settings: dict | None = None) -> list[str]
build_sdist(sdist_directory: str, config_settings: dict | None = None) -> str
get_requires_for_build_wheel(config_settings: dict | None = None) -> list[str]
build_wheel(
    wheel_directory: str,
    config_settings: dict | None = None,
    metadata_directory: str | None = None,
) -> str
prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: dict | None = None,
) -> str
get_requires_for_build_editable(config_settings: dict | None = None) -> list[str]
build_editable(
    wheel_directory: str,
    config_settings: dict | None = None,
    metadata_directory: str | None = None,
) -> str
prepare_metadata_for_build_editable(
    metadata_directory: str,
    config_settings: dict | None = None,
) -> str
```

The hooks operate on the project in the current directory. Build hooks return
the basename of the created artifact or metadata directory. Requirement hooks
return target-specific additional requirements in deterministic order; a
standard pure-Python wheel or sdist commonly needs none, while a regular
editable build advertises `editables~=0.3` when required by its mode.

Wheel output follows PEP 427. It includes selected package files, a normalized
`{name}-{version}.dist-info` directory, `METADATA`, `WHEEL`, `RECORD`, declared
license files, and `entry_points.txt` when scripts or entry points exist.
`RECORD` uses URL-safe SHA-256 without padding and leaves its own hash and size
empty. Source distributions are gzip-compressed tar archives rooted at
`{normalized_name}-{version}` and include `PKG-INFO`.

File selection is configured under `tool.hatch.build` and
`tool.hatch.build.targets.<target>`. Support `include`, `exclude`, `packages`,
`only-include`, `sources`, `force-include`, artifacts, VCS ignores, and standard
`src/` package layouts. Invalid configuration types, missing required metadata,
unknown targets/versions, and ambiguous default package selection raise clear
`TypeError` or `ValueError` exceptions rather than silently producing an empty
artifact.

### Project metadata

Construct metadata with:

```python
ProjectMetadata(
    root: str,
    plugin_manager: PluginManager | None,
    config: dict | None = None,
)
```

`hatchling.metadata.core.ProjectMetadata` reads the closest
`pyproject.toml`. Its public `name`, `version`, `build`, `core`, `hatch`,
`dynamic`, `context`, and `has_project_file()` interfaces expose normalized
metadata. The nested core metadata supports the PEP 621 fields `description`,
`readme`, `requires-python`, `license`, `license-files`, authors, maintainers,
keywords, classifiers, URLs, scripts, GUI scripts, entry points,
dependencies, optional dependencies, import names/namespaces, and dynamic
fields. `validate_fields()` validates all declared fields.

The helper functions in `hatchling.metadata.utils` are public:

```python
is_valid_project_name(project_name: str) -> bool
normalize_project_name(project_name: str) -> str
split_import_name_annotation(import_name: str) -> tuple[str, bool]
is_valid_import_name(import_name: str) -> bool
normalize_requirement(requirement: packaging.requirements.Requirement) -> None
format_dependency(requirement: packaging.requirements.Requirement) -> str
get_normalized_dependency(requirement: packaging.requirements.Requirement) -> str
resolve_metadata_fields(metadata: ProjectMetadata) -> dict[str, object]
```

Project normalization is PEP 503 compatible: runs of `-`, `_`, or `.` become
one lowercase hyphen. Requirements normalize project and extra names while
preserving markers and produce TOML-friendly single quotes around marker
strings. Import names are dotted Python identifiers and may end with
`; private`.

`hatchling.metadata.spec` constructs Core Metadata versions 1.2 and 2.1
through 2.5 and provides:

```python
project_metadata_from_core_metadata(core_metadata: str) -> dict[str, object]
get_core_metadata_constructors() -> dict[str, callable]
```

Metadata ordering is deterministic. Dependencies and optional dependency
groups preserve normalized requirement semantics; scripts and entry-point
groups preserve declaration order.

### Version files and schemes

`hatchling.version.core.VersionFile(root: str, relative_path: str)` supports:

```python
read(*, pattern: str | bool) -> str
set_version(version: str) -> None
write(version: str, template: str = DEFAULT_TEMPLATE) -> None
```

The default pattern recognizes a line assigning `__version__` or `VERSION`,
allows a leading `v`, and requires a named `version` group for custom patterns.
`read()` caches the matched span so `set_version()` changes only that span.
Missing files raise `OSError`; unmatched patterns and patterns without a named
group raise `ValueError`.

`hatchling.version.scheme.standard.StandardScheme(root, config)` implements:

```python
update(desired_version: str, original_version: str, version_data: dict) -> str
```

It supports explicit PEP 440 versions and the operations `release`, `major`,
`minor`, `micro`/`patch`/`fix`, `a`/`alpha`, `b`/`beta`, `rc`, `post`, and
`dev`, including comma-separated operations. By default, an explicit version
must be greater than the original version.

### Plugins and builders

`hatchling.plugin.manager.PluginManager()` lazily registers built-in classes.
Its `builder`, `build_hook`, `metadata_hook`, `version_source`, and
`version_scheme` registers expose `collect(include_third_party=True)` and
`get(name)`. Built-ins include wheel/sdist/binary/app builders, custom/version
build hooks, custom metadata, regex/code/env version sources, and the standard
version scheme. Third-party plugins use the `hatch` entry-point group.

`WheelBuilder(root: str, plugin_manager: PluginManager | None = None, ...)`
and `SdistBuilder(...)` expose the normal builder interface, target config,
artifact project ID, build versions, file traversal, cleaning, and artifact
generation. A standard pure-Python wheel selects a `py2.py3-none-any` or
compatible `py3-none-any` tag from `requires-python`.

Stable helpers in `hatchling.builders.utils` include:

```python
safe_walk(path: str)
get_known_python_major_versions()
get_relative_path(path: str, start: str) -> str
normalize_relative_path(path: str) -> str
normalize_relative_directory(path: str) -> str
normalize_inclusion_map(inclusion_map: dict[str, str], root: str) -> dict[str, str]
normalize_archive_path(path: str) -> str
format_file_hash(digest: bytes) -> str
get_reproducible_timestamp() -> int
normalize_file_permissions(st_mode: int) -> int
normalize_artifact_permissions(path: str) -> None
set_zip_info_mode(zip_info, mode: int = 0o644) -> None
```

Paths are normalized for the host OS and archive paths use forward slashes.
Inclusion maps become absolute-source to normalized-destination mappings sorted
by destination depth, destination, then source. Regular files normalize to
mode `0644`; files with the owner executable bit normalize to `0755`.

## Example

With a project containing `src/demo/__init__.py`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "demo_package"
version = "1.2.0"
requires-python = ">=3.10"

[tool.hatch.build.targets.wheel]
packages = ["src/demo"]
```

the following creates a standard wheel and returns its filename:

```python
from hatchling.build import build_wheel

filename = build_wheel("dist")
assert filename.startswith("demo_package-1.2.0-")
```

## Implementation Notes

- Preserve the public module layout under `hatchling.build`, `builders`,
  `metadata`, `plugin`, `version`, `utils`, and `cli`; plugin import paths are
  part of the contract.
- Use standard ZIP, gzip, tar, email metadata, TOML, path and hashing semantics.
- Do not shell out to a package index or fetch build inputs during normal
  metadata and standard wheel/sdist operations.
- Complex builder/plugin objects are evaluated through deterministic child-side
  adapters. No evaluator-specific public entry point is required.
- Binary application builds, third-party plugin implementations, live package
  indexes, platform-specific macOS compatibility rewriting, and arbitrary
  custom build scripts are outside the frozen evaluation slice.
