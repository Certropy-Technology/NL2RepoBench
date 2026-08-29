# Build `importlib-metadata`

Create a complete installable Python project for the distribution
`importlib_metadata` and import package `importlib_metadata` from an empty
workspace. The project reads installed-distribution metadata from directories,
legacy eggs, and zip archives. It must work without a preinstalled copy of
`importlib-metadata` and without runtime network access.

## Project Description

Implement the backport of Python's distribution-metadata API represented by
the frozen `importlib-metadata` revision. The library discovers `.dist-info`
and `.egg-info` metadata on caller-supplied search paths, parses package
metadata and entry points, exposes files and requirements, and maps top-level
import names back to distributions.

The distribution name is `importlib_metadata`, the import package is
`importlib_metadata`, and the frozen development version is
`8.9.1.dev28+g9757b400e`. Package metadata must declare the runtime requirement
`zipp>=3.20`.

## Supports

- Support CPython 3.12 on Linux. The preinstalled runtime dependency is
  `zipp==4.1.0`; do not fetch packages during evaluation.
- Provide an installable project rooted at the workspace. A `pyproject.toml`
  build may use the preinstalled setuptools, setuptools-scm, coherent license,
  packaging, and vcs-versioning build closure, or use another already available
  backend without adding network requirements.
- Export these names in `importlib_metadata.__all__`, in this order:
  `Distribution`, `DistributionFinder`, `PackageMetadata`,
  `PackageNotFoundError`, `PackagePath`, `MetadataNotFound`, `SimplePath`,
  `distribution`, `distributions`, `entry_points`, `files`, `metadata`,
  `packages_distributions`, `requires`, and `version`.
- Normal operations may read local files and zip archives. They must not make
  network requests or launch subprocesses. Discovery order must follow the
  supplied path and metadata entry order for fixed inputs.
- Accept `str` and `os.PathLike` paths. Decode metadata and text resources as
  UTF-8. Missing, unreadable, or malformed optional metadata files should
  follow the contracts below rather than escaping discovery with unrelated
  filesystem errors.

## API Usage Guide

### Top-level lookup functions

```python
distribution(distribution_name: str) -> Distribution
distributions(**kwargs) -> Iterable[Distribution]
metadata(distribution_name: str) -> PackageMetadata
version(distribution_name: str) -> str
entry_points(**params) -> EntryPoints
files(distribution_name: str) -> list[PackagePath] | None
requires(distribution_name: str) -> list[str] | None
packages_distributions() -> Mapping[str, list[str]]
```

`distribution`, `metadata`, `version`, `files`, and `requires` locate a name
using installed distribution finders. A missing distribution raises
`PackageNotFoundError(name)`, whose read-only `name` property is the requested
name and whose string form is
`No package metadata was found for <name>`. An empty distribution name raises
`ValueError`.

`distributions` delegates to `Distribution.discover`. `entry_points` combines
entry points from unique normalized distributions and applies optional
`group`, `name`, `value`, `module`, `attr`, or `extras` filters. The mapping
from `packages_distributions` uses `top_level.txt` when present and otherwise
infers importable top-level names from recorded distribution files. Preserve
distribution discovery order in each mapping value.

### `EntryPoint`

```python
EntryPoint(name: str, value: str, group: str)
EntryPoint.load() -> Any
EntryPoint.matches(**params) -> bool
```

An entry-point value has the form `module`, `module:attribute`, or either form
followed by an extras list such as `[fast, test_2]`. Expose read-only `module`,
`attr`, and `extras` properties. `attr` is absent when no attribute is given;
`extras` is a list of word-like extra names in source order. Accessing or
constructing an invalid object reference raises `ValueError` describing the
invalid value.

`load` imports the module and follows each dot-separated attribute component;
module-only values return the imported module. `matches` compares every given
field and returns true when called without filters. Matching on `dist` raises
`ValueError` because distribution objects do not have value equality.

Entry points are immutable after construction. Equality, hashing, sorting,
and `repr` use `(name, value, group)`. The representation is
`EntryPoint(name=<repr>, value=<repr>, group=<repr>)`. A distribution's parsed
entry points carry that `Distribution` in their `dist` attribute.

### `EntryPoints`

```python
EntryPoints(iterable=())
EntryPoints.select(**params) -> EntryPoints
```

`EntryPoints` is an immutable tuple subclass. Integer and slice access retain
tuple behavior; string access returns the first entry whose name matches and
raises `KeyError` when absent. `select` preserves order. `names` and `groups`
return sets, and `repr` uses the explicit `EntryPoints((...))` form.

### Distribution providers

```python
Distribution.from_name(name: str) -> Distribution
Distribution.discover(*, context: DistributionFinder.Context | None = None,
                      **kwargs) -> Iterable[Distribution]
Distribution.at(path: str | os.PathLike[str]) -> Distribution
```

`Distribution` is abstract: subclasses implement `read_text(filename)` and
`locate_file(path)`. `Distribution.at` creates a filesystem-backed
`PathDistribution` for one metadata path. `discover` accepts either one
`DistributionFinder.Context` or keyword arguments used to construct one, but
not both. Its results prefer distributions with readable metadata while
preserving order within valid and invalid groups.

`DistributionFinder.Context(**kwargs)` stores arbitrary finder-specific
attributes. Its canonical `name` defaults to `None`; its `path` defaults to
the current `sys.path` and otherwise returns the supplied path sequence.

The standard `MetadataPathFinder.find_distributions(context)` discovers
case-insensitive `.dist-info`, `.egg-info`, and `.egg/EGG-INFO` metadata in
ordinary directories and zip archives. Distribution names use PEP 503-style
normalization with runs of periods, underscores, and dashes treated
equivalently. A query must not match a longer name merely by prefix.
`MetadataPathFinder.invalidate_caches()` makes subsequent discovery observe
filesystem changes.

### Distribution properties

```python
dist.metadata -> PackageMetadata
dist.name -> str
dist.version -> str
dist.entry_points -> EntryPoints
dist.files -> list[PackagePath] | None
dist.requires -> list[str] | None
dist.origin -> types.SimpleNamespace | None
dist.read_text(filename) -> str | None
dist.locate_file(path) -> SimplePath
```

Read `METADATA`, then `PKG-INFO`, then legacy metadata content. If none exists,
`metadata` raises `MetadataNotFound("No package metadata was found.")`.
Metadata behaves like an email message and provides a JSON-compatible `json`
mapping: field names are lowercase with dashes converted to underscores,
multi-use fields become lists, `Keywords` is split into a list, and the
message body is available as `description`.

`name` and `version` read their core metadata fields. `entry_points` parses
`entry_points.txt` as INI-like sections in file order, ignoring comments and
blank lines. `requires` returns `Requires-Dist` fields for modern metadata. For
legacy `requires.txt`, preserve requirement order and translate `[extra]`,
`[:marker]`, and `[extra:marker]` sections into PEP 508 marker strings. Return
`None` when no requirements are declared.

`origin` parses `direct_url.json` and recursively exposes JSON object members
as attributes; return `None` if the file is absent.

### Recorded files

`dist.files` reads `RECORD`, legacy `installed-files.txt`, or `SOURCES.txt` in
that order. Return `None` when no file listing exists. Each existing record is
a `PackagePath`, a `pathlib.PurePosixPath` subclass with attached `dist`,
optional `size`, and optional `FileHash`. Missing recorded paths are omitted.

```python
PackagePath.locate() -> SimplePath
PackagePath.read_text(encoding: str = "utf-8") -> str
PackagePath.read_binary() -> bytes
FileHash(spec: str)
```

`FileHash` splits `mode=value` at the first equals sign and exposes `mode` and
`value`. Its representation is
`<FileHash mode: <mode> value: <value>>`. Package-path reads resolve relative
to the distribution root and preserve file bytes.

### Metadata protocols

`PackageMetadata` is the public typing protocol for mapping-like core metadata
with `get`, `get_all`, and a JSON-compatible `json` property. `SimplePath` is
the public protocol required from custom providers: `joinpath`, `/`, `parent`,
`read_text`, `read_bytes`, and `exists`.

## Implementation Notes

- Keep candidate code and dependency code separate. Do not include a copy of
  `zipp`, private tests, verifier helpers, or reference-source material.
- Filesystem and zip discovery may cache directory lookup state, but cache
  invalidation must be observable and caches must not change deterministic
  results.
- Parse metadata using standards-compatible behavior. Preserve repeated
  headers and entry-point/requirement ordering; do not reduce metadata to a
  small hard-coded dictionary.
- The verifier constructs temporary metadata trees and zip archives in an
  unprivileged child process. Trusted collection, JUnit, network, and reward
  reports are verifier-owned; candidate code must not write `/tests`, `/logs`,
  or trusted report paths.
