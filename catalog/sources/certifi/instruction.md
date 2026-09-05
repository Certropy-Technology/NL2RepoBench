# Build `certifi`

Create a complete, installable Python distribution named `certifi` from an
empty workspace. It provides a bundled Mozilla CA certificate collection for
applications that need a stable PEM trust-store path or its text contents.
The package must work without network access at runtime and must not rely on a
preinstalled copy of `certifi`.

## Project Description

Implement a small pure-Python package with an import package named `certifi`.
The distribution includes one package data file, `cacert.pem`, containing the
frozen PEM certificate bundle, and a `py.typed` marker. The package metadata
version is `2026.07.22`. The certificate data is immutable application data:
do not generate it from the host trust store, download it, or substitute a
different certificate source.

The project must be installable by pip from the repository root using a normal
PEP 517 build. It may use `setuptools` and `wheel` as build tools, but it has
no third-party runtime dependencies. Support CPython 3.7 and newer Python 3
versions, including the Python 3.12 environment used for evaluation.

## Natural Language Instruction

Create the `certifi` distribution from an empty workspace. Include the frozen
PEM resource, package metadata, root exports, and module CLI. Resource lookup
must remain local to the installed package and must not use a system trust store.

## Supports or Environment Configuration

- Import `certifi` after installation from either a regular checkout or an
  installed wheel.
- Include `certifi/cacert.pem` as package data and include `certifi/py.typed`.
- Keep all normal operations local and deterministic. Runtime code must not
  use the network, subprocesses, environment-specific trust stores, or a
  system package manager.
- Preserve the exact root exports `contents` and `where` and the version value
  `2026.07.22`.
- Provide the module entry point `python -m certifi`.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── certifi/
    ├── __init__.py
    ├── __main__.py
    ├── cacert.pem
    └── py.typed
```

## API Usage Guide

### `certifi.where`

Import path: `certifi.where()`

Signature: `where() -> str`.

Return the filesystem path of the bundled `cacert.pem` resource. The result
must be a string naming a readable regular file whose basename is
`cacert.pem`. The file must be the package's own bundled resource, not a path
chosen from an operating-system CA store. Repeated calls in one process return
the same usable path. The function may lazily materialize a resource when the
package is imported from an archive, but callers do not need to manage a
context manager.

### `certifi.contents`

Import path: `certifi.contents()`

Signature: `contents() -> str`.

Return the complete contents of the bundled `cacert.pem` as an ASCII string.
The text is deterministic and includes matching PEM certificate blocks with
`-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----` delimiters. It
must be the exact text represented by the file returned from `where()`, and
repeated calls return the same text. The returned string ends with a newline.

### Module CLI

Run `python -m certifi` with no arguments to print the same path returned by
`where()`, followed by one newline. Run `python -m certifi -c` or
`python -m certifi --contents` to print the complete text returned by
`contents()`. The two contents flags are aliases. Unknown options must be
rejected with a non-zero exit status and a normal argparse usage message.

### Package metadata

`certifi.__all__` is exactly `['contents', 'where']` in that order, and the
root attributes `contents` and `where` are callable. `certifi.__version__`
must equal `2026.07.22`. `certifi/py.typed` is an empty or marker text file
installed alongside the Python package.

## Implementation Notes

Use package-resource APIs that work for an installed distribution, including a
wheel. Keep resource lookup relative to the `certifi` package and preserve
ASCII decoding. A regular source checkout may use a conventional setuptools
layout; package-data configuration must still include both `cacert.pem` and
`py.typed` in built distributions.

The frozen resource contains 121 matching certificate blocks and is larger
than 100 KiB. Implementations may organize helper code as they choose, but
the public behavior, output ordering, bytes, and CLI exit behavior above are
the contract. Do not include tests, verifier code, or reference source in the
generated distribution.

## Examples

```python
import certifi
path = certifi.where()
assert path.endswith('cacert.pem')
assert certifi.contents().endswith('\n')
```

```text
python -m certifi
python -m certifi --contents
```

## Error Handling and Boundary Conditions

Unknown module CLI options must exit non-zero with usage text. `where()` must
return the bundled regular file, and `contents()` must match that file after
ASCII decoding; neither may fall back to an operating-system trust store.

## Examples

```python
import certifi
path = certifi.where()
assert path.endswith('cacert.pem')
assert certifi.contents().endswith('\n')
```

```text
python -m certifi
python -m certifi --contents
```

## Error Handling and Boundary Conditions

Unknown module CLI options must exit non-zero with usage text. `where()` must
return the bundled regular file, and `contents()` must match that file after
ASCII decoding; neither may fall back to an operating-system trust store.
