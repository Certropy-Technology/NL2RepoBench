# Build `distro`

Create a complete, installable Python distribution named `distro` from an
empty workspace. The import package must be `distro` and the command
`python -m distro` must be available after installation. Implement the
observable behavior of the pinned source revision described below without
copying the upstream source or tests.

## Project Description

`distro` reports Linux distribution identity and version information from
standard local data sources. It parses `os-release` files first, can fall back
to distribution release files, and exposes a small object-oriented API as well
as module-level convenience functions and a CLI. This task uses only local,
deterministic inputs; it does not require a particular host distribution.

## Supports

- CPython `>=3.7` on Linux and BSD-like POSIX systems, with the task runtime
  using CPython 3.12.
- An installable package with `src/distro/__init__.py`,
  `src/distro/distro.py`, `src/distro/__main__.py`, and `py.typed`.
- No third-party runtime dependencies. The build backend may use setuptools,
  but the installed library must not import a third-party package.
- Local parsing of files and, when no explicit root directory is supplied,
  the platform's ordinary `lsb_release`, `uname`, and `os-release` sources.
  Do not contact a network or require a service.
- A deterministic module-global distribution object and a separately
  constructible `LinuxDistribution` object.

## API Usage Guide

### Package exports and metadata

`import distro` must expose `__version__` (the pinned release is `1.9.0`),
`LinuxDistribution`, the normalization mappings `NORMALIZED_OS_ID`,
`NORMALIZED_LSB_ID`, and `NORMALIZED_DISTRO_ID`, plus these functions:

```text
linux_distribution(full_distribution_name=True) -> tuple[str, str, str]
id() -> str
name(pretty=False) -> str
version(pretty=False, best=False) -> str
version_parts(best=False) -> tuple[str, str, str]
major_version(best=False) -> str
minor_version(best=False) -> str
build_number(best=False) -> str
like() -> str
codename() -> str
info(pretty=False, best=False) -> dict[str, object]
os_release_info() -> dict[str, str]
lsb_release_info() -> dict[str, str]
distro_release_info() -> dict[str, str]
uname_info() -> dict[str, str]
os_release_attr(attribute) -> str
lsb_release_attr(attribute) -> str
distro_release_attr(attribute) -> str
uname_attr(attribute) -> str
```

The convenience functions delegate to the module-global distribution object.
Missing values are empty strings and missing source dictionaries are empty
dictionaries. Deprecated compatibility functions may issue
`DeprecationWarning`, but must retain their documented return shapes.

### `LinuxDistribution`

Construct with:

```python
LinuxDistribution(
    include_lsb=True,
    os_release_file="",
    distro_release_file="",
    include_uname=True,
    root_dir="",
    include_oslevel=False,
)
```

The constructor accepts an explicit `root_dir` for deterministic fixture
trees. When a root directory is supplied, subprocess-backed sources must be
disabled (`include_lsb=False`, `include_uname=False`, and
`include_oslevel=False`); rejecting an unsafe combination with `ValueError`
is required. Explicit `os_release_file` and `distro_release_file` paths are
supported. The object exposes the same consolidated and source-specific
methods as the module-level API, plus `oslevel_info()`.

`os-release` lines use shell-like quoted values. Recognize `NAME`, `ID`,
`ID_LIKE`, `PRETTY_NAME`, `VERSION_ID`, `VERSION`, `VERSION_CODENAME`, and
`VARIANT` without treating comments or malformed lines as data. Normalize
known IDs (`ol` to `oracle`, `opensuse-leap` to `opensuse`, and the documented
LSB/release aliases). `info()` returns exactly the keys `id`, `version`,
`version_parts`, `like`, and `codename`; `version_parts` contains `major`,
`minor`, and `build_number` strings. `pretty=True` uses the human-readable
name/version forms, while `best=True` prefers the best available version
source.

If `os-release` is unavailable, parse a matching file such as
`foo-release` or `slackware-version`. A release line may contain a name,
version, and parenthesized codename. Preserve the parsed name and version and
return empty strings for fields that are absent. Child order and output
formatting must be deterministic.

### CLI

`python -m distro [--root-dir PATH] [-j|--json]` prints either three labeled
lines (`Name`, `Version`, `Codename`) or a JSON object equivalent to
`info()`. The root directory is interpreted as a filesystem root, and the
JSON output must be valid JSON with no diagnostic text on stdout.

## Implementation Notes

Keep the implementation local and side-effect bounded. Do not use Graphviz,
network clients, package-manager commands, or an external service. Use the
standard library for parsing, subprocess calls, and warnings. The evaluator
supplies temporary fixture roots, so do not read the evaluator's private
files or rely on the host's `/etc` contents. Build metadata must be stable
when the project is unpacked without `.git`; do not derive the runtime version
from a mutable branch or a network lookup.
