# Project Description

Create an installable Python distribution named `trove-classifiers` with the import
package `trove_classifiers`. It exposes the frozen PyPI classifier catalog through
four mutable containers and provides a command-line program that prints the ordered
valid classifiers.

The benchmark is offline. The package is a static-data library: importing it must not
contact PyPI, GitHub, a database, or any other service. Implement the catalog and
packaging behavior described below from the public contract.

# Natural Language Instruction

Create the installable `trove-classifiers` package from an empty workspace.
Implement the frozen classifier containers, relationships, ordering,
deprecation map, package metadata, and local command-line output below. Keep
the catalog static and deterministic; no online synchronization is required.

# Supports

- Support Python 3.9 and newer. Verification uses CPython 3.12.14 on Debian 13
  `linux/amd64`.
- Provide distribution version `2026.6.1.19`.
- A `src/trove_classifiers/` or flat `trove_classifiers/` layout is acceptable.
- `python -m pip install . --no-deps --no-build-isolation` must succeed with the
  preinstalled `setuptools`, `calver`, and `wheel` build closure.
- Declare no third-party runtime dependencies.
- Include `trove_classifiers/py.typed` as package data.
- Install exactly one console entry point:
  `trove-classifiers = trove_classifiers.__main__:cli`.
- `python -m trove_classifiers` and the console entry point accept no required
  arguments and print the same output.
- Include an Apache-2.0 `LICENSE` file in the project root.
- Do not download or vendor dependencies, classifier data, or source code at runtime.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── LICENSE
└── src/
    └── trove_classifiers/
        ├── __init__.py
        ├── __main__.py
        └── py.typed
```

# API Usage Guide

The package root exports exactly these names in this order:

```python
__all__ = [
    "all_classifiers",
    "classifiers",
    "deprecated_classifiers",
    "sorted_classifiers",
]
```

## Valid classifiers

```python
sorted_classifiers: list[str]
classifiers: set[str]
```

`sorted_classifiers` contains 895 unique valid classifier strings. `classifiers`
is exactly `set(sorted_classifiers)` and therefore also contains 895 values. Both
objects are ordinary mutable built-in containers, not tuples, frozensets, or custom
proxies.

Every valid classifier uses `" :: "` as its segment separator and has at least two
segments. Segments are nonempty, have no leading or trailing whitespace, contain no
stray `:`, and do not begin with `Private` in any letter case. For every classifier
with three or more segments, each intermediate parent beginning with the first two
segments is also a valid classifier.

The ordered list uses natural ordering: numeric runs compare by integer value. In
particular, the contiguous Python sequence from `3.8` through `3.16` is:

```text
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Programming Language :: Python :: 3.13
Programming Language :: Python :: 3.14
Programming Language :: Python :: 3.15
Programming Language :: Python :: 3.16
```

The first two values are `Development Status :: 1 - Planning` and
`Development Status :: 2 - Pre-Alpha`. The final two are
`Typing :: Stubs Only` and `Typing :: Typed`.

The ten top-level families and their exact valid-value counts are:

| Family | Count |
| --- | ---: |
| Development Status | 7 |
| Environment | 74 |
| Framework | 185 |
| Intended Audience | 14 |
| License | 84 |
| Natural Language | 64 |
| Operating System | 43 |
| Programming Language | 102 |
| Topic | 320 |
| Typing | 2 |

The complete Development Status family is:

```text
Development Status :: 1 - Planning
Development Status :: 2 - Pre-Alpha
Development Status :: 3 - Alpha
Development Status :: 4 - Beta
Development Status :: 5 - Production/Stable
Development Status :: 6 - Mature
Development Status :: 7 - Inactive
```

The complete Typing family is:

```text
Typing :: Stubs Only
Typing :: Typed
```

The frozen catalog must include the following representative entries. They are
part of the public data contract; preserve their exact spelling and case.

### Environment

```text
Environment :: Console
Environment :: GPU :: NVIDIA CUDA :: 4.1
Environment :: GPU :: NVIDIA CUDA :: 11.3
Environment :: MacOS X :: Carbon
Environment :: X11 Applications :: Qt
Environment :: Cygwin (MS Windows)
```

### Framework

```text
Framework :: AWS CDK
Framework :: Django :: 5
Framework :: MkDocs
Framework :: Pycsou
Framework :: tox
Framework :: Litestar
Framework :: Litestar :: 1
Framework :: Litestar :: 2
Framework :: Litestar :: 3
Framework :: Django :: 6.1
Framework :: Django CMS :: 5.1
Framework :: Plone :: 6.3
Framework :: Wagtail :: 8
```

### Intended Audience

```text
Intended Audience :: Customer Service
Intended Audience :: End Users/Desktop
Intended Audience :: Legal Industry
Intended Audience :: Religion
Intended Audience :: Telecommunications Industry
```

### License

```text
License :: Aladdin Free Public License (AFPL)
License :: OSI Approved
License :: OSI Approved :: Attribution Assurance License
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
License :: OSI Approved :: Open Group Test Suite License
License :: Repoze Public License
```

### Natural Language

```text
Natural Language :: Afrikaans
Natural Language :: English
Natural Language :: Japanese
Natural Language :: Romanian
Natural Language :: Ukrainian
Natural Language :: Yiddish
```

### Operating System

```text
Operating System :: Android
Operating System :: Microsoft :: Windows :: Windows 8
Operating System :: OS Independent
Operating System :: POSIX :: GNU Hurd
Operating System :: iOS
```

### Programming Language

```text
Programming Language :: APL
Programming Language :: Java
Programming Language :: Python
Programming Language :: Python :: 2.5
Programming Language :: Python :: 3
Programming Language :: Python :: 3.16
Programming Language :: Python :: Free Threading :: 3 - Stable
Programming Language :: Zope
```

### Topic

```text
Topic :: Adaptive Technologies
Topic :: File Formats :: JSON :: JSON Schema
Topic :: Office/Business :: Financial :: Spreadsheet
Topic :: Scientific/Engineering :: Instrument Drivers :: IVI Conformant
Topic :: Software Development
Topic :: Software Development :: Widget Sets
Topic :: Utilities
```

Membership uses ordinary exact string equality. For example:

```python
assert "License :: OSI Approved" in classifiers
assert "Programming Language :: Python :: 3" in classifiers
assert "Fuzzy :: Wuzzy :: Was :: A :: Bear" not in classifiers
assert "Programming Language :: Python :: 99" not in classifiers
```

## Deprecated classifiers

```python
deprecated_classifiers: dict[str, list[str]]
```

This mutable dictionary contains exactly eight entries. Keys are deprecated
classifier spellings; values are zero or more valid replacements:

```python
{
    "Framework :: Django CMS :: 4.2": ["Framework :: Django CMS :: 5.0"],
    "License :: OSI Approved :: Intel Open Source License": [],
    "License :: OSI Approved :: Jabber Open Source License": [],
    "License :: OSI Approved :: MITRE Collaborative Virtual Workspace License (CVW)": [],
    "License :: OSI Approved :: Sun Industry Standards Source License (SISSL)": [],
    "License :: OSI Approved :: X.Net License": [],
    "Natural Language :: Ukranian": ["Natural Language :: Ukrainian"],
    "Topic :: Communications :: Chat :: AOL Instant Messenger": [],
}
```

Deprecated keys do not occur in `classifiers`. Every nonempty replacement value
does occur in `classifiers`.

## All classifiers

```python
all_classifiers: list[str]
```

`all_classifiers` is a mutable built-in list containing all 895 valid strings and
the eight deprecated keys, for 903 unique strings total. It is exactly:

```python
sorted(sorted_classifiers + list(deprecated_classifiers.keys()))
```

This list uses Python's built-in lexicographic `sorted`, independently of the
natural ordering used by `sorted_classifiers`.

## Command-line interface

```python
trove_classifiers.__main__.cli() -> None
```

`cli` prints every item of `sorted_classifiers` to standard output, one item per
line, in list order, with a newline after the final item. It returns `None` and
writes nothing to standard error. Both invocations below therefore emit exactly
895 lines:

```bash
python -m trove_classifiers
trove-classifiers
```

# Implementation Notes

- Keep all catalog data local and deterministic. Importing the package must have no
  filesystem, subprocess, clock, locale, environment, or network side effect.
- Preserve the four container types and relationships. Callers may mutate these
  objects after import.
- Build version generation may use the provided `SOURCE_DATE_EPOCH=1780342838`, or
  the project may declare the required version directly. Do not derive a changing
  version from the current clock.
- The verifier installs the candidate into an isolated target, then executes every
  import and CLI operation in bounded unprivileged child processes. Evaluation
  code does not import candidate modules.
- Exact unlisted classifier bytes are not a hidden requirement. Scoring covers the
  documented counts, grammar, hierarchy, relationships, ordering boundaries,
  deprecation map, and representative frozen values above.

# Examples

```python
from trove_classifiers import classifiers, sorted_classifiers

assert "License :: OSI Approved" in classifiers
assert sorted_classifiers[0] == "Development Status :: 1 - Planning"
```

```bash
python -m trove_classifiers
```

# Error Handling and Boundary Conditions

The four exported containers are ordinary mutable built-ins with the exact
relationships specified above. Import and CLI execution must not contact a
registry or read caller-specific files. Deprecated keys stay out of
`classifiers`; unknown classifier strings are ordinary membership misses.
