# `tabulate` Evidence-First Audit

Status: **blocked / audit candidate**

This directory is intentionally limited to human-facing catalog source and
audit notes. It contains no upstream source, private tests, Oracle, Harbor
task, generated manifest, wheelhouse, or shared index update.

## Candidate Identity

| Field | Recorded value | Evidence state |
| --- | --- | --- |
| Project | `astanin/python-tabulate` | supplied candidate identity |
| Upstream URL | `https://github.com/astanin/python-tabulate` | recorded |
| Exact commit | `268615a5c27dc40e5c22454c07b44d5c50410da0` | recorded; fetched object still required |
| Source archive URL | `https://github.com/astanin/python-tabulate/archive/268615a5c27dc40e5c22454c07b44d5c50410da0.tar.gz` | deterministic URL recorded |
| License | expected upstream license is MIT, but no license bytes are present here | **not verified** |
| Archive SHA-256 | not claimed | **not verified** |
| Source-only LOC | not claimed | **not run** |

The commit string is full length and immutable. A branch, tag, package-index
version, or `latest` archive must not be substituted for it. The source status
in `task.toml` remains `unknown` until archive, license bytes, and source hash
are captured together.

## Required Bounded Provenance Probe

Run from a temporary directory with no repository-wide cache. The command must
download only the exact archive, list the relevant files, and calculate its
digest. Save the resulting digest and the license's SPDX conclusion in a
future audit revision; do not put archive bytes in this catalog directory.

```sh
set -eu
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
archive="$tmp/tabulate.tar.gz"
curl --fail --location --max-time 30 --output "$archive" \
  'https://github.com/astanin/python-tabulate/archive/268615a5c27dc40e5c22454c07b44d5c50410da0.tar.gz'
sha256sum "$archive"
tar -tzf "$archive" | awk -F/ '$2 == "" || $2 == "LICENSE" || $2 == "LICENSE.txt" || $2 == "pyproject.toml" || $2 == "setup.py" {print}'
tar -xzf "$archive" -C "$tmp"
find "$tmp" -maxdepth 3 -type f \( -iname 'license*' -o -iname 'copying*' \) -print
```

Acceptance requires the digest to be recorded from this exact URL, the
license text to be read from the extracted archive, and the archive source
tree to be compared with the detached commit. No such probe was run in this
isolated handoff, so the gate is open and publication is forbidden.

## Source-Only LOC Probe

Count only tracked Python implementation files in the extracted source tree.
Exclude `tests/`, documentation, examples, generated files, build metadata,
coverage output, caches, and any optional vendored copy. Count physical
non-blank lines and comment lines using one documented method, and record the
file list and total. Do not count the archive wrapper directory.

```sh
set -eu
root="$1"
find "$root" -type f -name '*.py' \
  -not -path '*/tests/*' -not -path '*/docs/*' -not -path '*/examples/*' \
  -not -path '*/.venv/*' -not -path '*/__pycache__/*' -print | sort
find "$root" -type f -name '*.py' \
  -not -path '*/tests/*' -not -path '*/docs/*' -not -path '*/examples/*' \
  -not -path '*/.venv/*' -not -path '*/__pycache__/*' -print0 \
  | xargs -0 awk 'NF { total += 1 } END { print total }'
```

The resulting LOC and file count must be entered in a later source lock or
audit record. `metadata.difficulty` is intentionally `unknown` until this
probe is complete.

## Official Pytest and Doctest Collection

The final collection must use the source repository's own pytest configuration
and test command. Record Python and pytest versions, exact commands, collection
errors, item node IDs, and whether the doctest pass is additive or duplicates
ordinary pytest items. The required bounded probes are:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  python -m pytest --collect-only -q
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  python -m pytest --collect-only -q --doctest-modules tabulate
```

The final `tests.expected_total` must come from the approved frozen collection,
not a hand-written count. This candidate has only the schema-required
provisional value `1` and `expected_total_source = "unknown"`; it is not a
score denominator.

## Base Pure-Python Lane and Offline Closure

The base lane excludes `numpy`, `pandas`, and `wcwidth`. It must prove in a
fresh environment that `import tabulate` succeeds without optional packages,
ordinary list/mapping/multiline/numeric/HTML cases work offline, and absence of
an optional module cannot break import-time behavior.

The offline installation probe must use a separately recorded, hash-locked
dependency bundle and fail closed on a missing artifact. No dependency bundle,
immutable environment lock, or large cache is available in this checkout, so
this gate is **not verified** and no package installation is authorized as part
of this task-local change.

## Locale and Unicode Determinism

Use one child process per environment and compare exact UTF-8 stdout bytes for
the same JSON input. Cover ASCII, a combining sequence written as
`Cafe\\u0301`, CJK text written as `\\u6771\\u4eac`, an emoji, embedded newlines,
and HTML-sensitive characters. Run with `PYTHONHASHSEED=0` under both a C
locale and an available UTF-8 locale. Record width fallback behavior with
`wcwidth` absent; a missing locale is not a passing result.

Expected result: fixed input and formatting options produce identical output
across selected locales and process runs, with widths and escaping determined
by the documented base-lane rules. This probe was **not run** in the isolated
handoff.

## JSON/Text Subprocess Boundary

The audit adapter must launch a fresh candidate process with an argument list,
not import candidate code into the trusted runner. Send one UTF-8 JSON value
containing rows and formatting options on stdin, read rendered text from
stdout, read diagnostics separately from stderr, and enforce a bounded timeout.
Invalid JSON and invalid formatting options must produce a non-zero exit status
without being converted into a false pass. The adapter must not accept a score,
JUnit file, or result JSON written by the candidate as grading authority.

The boundary is documented in `instruction.md`, but no adapter or execution
asset is included here and no subprocess probe was run. Status: **not
verified**.

## Gate Decision

The candidate remains `blocked` because exact archive SHA-256 and extracted
license evidence, source-only LOC, official pytest/doctest collection with
stable node IDs and a frozen denominator, an immutable no-network environment
and hash-locked offline closure, locale/Unicode results with optional extras
absent, and a separate JSON/text subprocess probe are missing.

No hidden tests, Harbor assets, Oracle run, or shared catalog edits may be
added to clear these gaps. A later authoring stage may append evidence in a
controlled revision and decide whether a private test bundle can be authored.
