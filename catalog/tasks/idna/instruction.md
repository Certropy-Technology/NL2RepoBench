# Build `idna`

## Project Description

Create a complete installable Python package named `idna`, version `3.19`, from
an empty workspace. It implements Internationalized Domain Names in
Applications (IDNA 2008) and Unicode Technical Standard #46 mapping for
converting Unicode domain names to ASCII-compatible labels and back. The
package must be usable as a library, a registered `idna2008` Python codec, and
the `python -m idna` command-line tool.

The scored behavior is deterministic and local. Do not copy the reference
repository or its tests. Do not use network access, subprocesses, or external
services during normal library calls. Unicode tables required by IDNA 2008
and UTS #46 must be included in the package so the behavior does not depend on
the host's installed `idna` distribution.

## Supports

- CPython 3.14 on Linux amd64 with glibc.
- An installable `src`-optional or flat package layout whose import package is
  `idna`, with `idna/py.typed` present.
- A `pyproject.toml` using the `flit_core.buildapi` backend, distribution name
  `idna`, version `3.19`, and `requires-python = ">=3.9"`.
- No runtime third-party dependencies. The build backend is a build-time
  dependency only. The package must install with the verifier's offline
  candidate installation procedure without downloading anything.
- A console script named `idna` pointing to `idna.cli:main`.
- `python -m idna` must behave the same way as the console entry point.

## Natural Language Instruction

Create the `idna` distribution from an empty workspace. Implement IDNA 2008
encoding and decoding, UTS #46 remapping, validation helpers and error
metadata, compatibility functions, codec registration, and the CLI described
below. Preserve Unicode table behavior, exact bytes/text return shapes,
warning behavior, and deterministic boundary errors.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── idna/__init__.py
├── idna/core.py
├── idna/codec.py
├── idna/compat.py
├── idna/cli.py
├── idna/intranges.py
├── idna/idnadata.py
├── idna/uts46data.py
├── idna/__main__.py
└── idna/py.typed
```

The package root exports the documented conversion functions and exceptions;
the codec, compatibility module, and CLI use those same implementations.
Unicode data must be local package data and must not be downloaded at runtime.

## API Usage Guide

### Root exports

The module `idna` must expose `__version__ == "3.19"`,
`unicode_version == "17.0.0"`, and these names:

```text
IDNAError, IDNABidiError, InvalidCodepoint, InvalidCodepointContext,
alabel, check_bidi, check_hyphen_ok, check_initial_combiner, check_label,
check_nfc, decode, encode, intranges_contain, ulabel, uts46_remap,
valid_contextj, valid_contexto, valid_label_length, valid_string_length
```

`idna.compat` provides `ToASCII(label)`, `ToUnicode(label)`, and
`nameprep(value)`. The first two delegate to the IDNA 2008 whole-domain
operations and return `bytes` and `str`; `nameprep` always raises
`NotImplementedError` because Nameprep is not part of IDNA 2008.

### Domain conversion

```python
idna.encode(s: str | bytes, strict: bool = False, uts46: bool = False,
            std3_rules: bool = False, transitional: bool = False) -> bytes
idna.decode(s: str | bytes, strict: bool = False, uts46: bool = False,
            std3_rules: bool = False) -> str
idna.alabel(label: str) -> bytes
idna.ulabel(label: str | bytes) -> str
idna.uts46_remap(domain: str, std3_rules: bool = False,
                 transitional: bool = False) -> str
```

`encode` converts a Unicode domain to ASCII labels separated by `.` and
`decode` converts ASCII-compatible labels to Unicode. Both accept `str` or
UTF-8 `bytes`, preserve a single trailing dot, and return exactly `bytes` or
`str`. `strict=True` disables the default compatibility behavior; `uts46=True`
applies UTS #46 remapping before conversion; `std3_rules=True` applies the
stricter ASCII character restrictions; `transitional=True` selects the UTS #46
transitional mapping and emits a `DeprecationWarning`. These flags are
independent and must be honored for both ordinary and edge-case inputs.

`alabel` validates one Unicode label and returns its ASCII form. ASCII labels
are lower-case and non-ASCII labels use the `xn--` ACE prefix and Punycode.
`ulabel` accepts an A-label or ordinary ASCII label and returns its Unicode
label, rejecting invalid or non-canonical A-labels.

The conversion functions enforce a maximum of 63 octets per encoded label and
253 octets for a domain without a trailing dot, or 254 with one. Empty labels,
non-NFC labels, bad hyphen placement, leading combining marks, disallowed or
unassigned codepoints, invalid CONTEXTJ/CONTEXTO use, and Bidi rule violations
raise the appropriate `IDNAError` subclass.

### Validation helpers and errors

`valid_label_length(value)` and `valid_string_length(value, trailing_dot)`
return booleans using the DNS octet limits described above. The helpers
`check_nfc`, `check_hyphen_ok`, `check_initial_combiner`, `check_bidi`,
`valid_contextj`, `valid_contexto`, and `check_label` return `True` (or `None`
for `check_nfc`) on success and raise on invalid input. `check_bidi` accepts
`check_ltr=False`; `valid_contexto` accepts an unused `exception=False` flag.

`IDNAError` is a `UnicodeError` with attributes `code`, `text`, `codepoint`,
and `position`, each set to a meaningful value or `None`. The subclasses
`IDNABidiError`, `InvalidCodepoint`, and `InvalidCodepointContext` retain that
metadata. Error code strings are stable identifiers such as
`empty_label`, `hyphen_start_end`, `not_nfc`, `invalid_utf8`,
`disallowed_codepoint`, `contextj`, `contexto`, `bidi_rule_2`,
`invalid_alabel`, `non_canonical_alabel`, and `domain_too_long`.

### Codec and command line

Importing `idna.codec` registers the `idna2008` codec with `codecs`. Strict
codec encode/decode return `(converted_value, input_length)`. The incremental
encoder and decoder buffer a partial label, use `.` as output separator, and
support `reset`, `getstate`, and `setstate`; only the `strict` error handler is
accepted.

`python -m idna` and the `idna` console script accept `-e/--encode`,
`-d/--decode`, `--strict`, `--version`, and zero or more domain arguments. With
no explicit mode, an input containing an `xn--` label selects decode and all
remaining inputs use that same mode; otherwise encode is selected. If no
positional domains are given and stdin is piped, process one non-empty,
stripped domain per line. Print successful results one per line, continue
after per-domain errors, write failures to stderr, and return exit code 1 if
any conversion failed.

## Implementation Notes

Keep the public import paths and exception inheritance stable. Preserve Unicode
table data and deterministic ordering. The package must not import or invoke a
different installed copy of `idna`. Include compatibility shims and codec
classes even though the primary API is the root module. The verifier checks
observable behavior through an unprivileged subprocess; it does not import
candidate modules into the trusted verifier process.

## Examples

```python
import idna

idna.encode("例え.テスト")
idna.decode(b"xn--r8jz45g.xn--zckzah")
```

```python
idna.uts46_remap("EXAMPLE.COM", std3_rules=True)
```

```bash
python -m idna --encode "例え.テスト"
python -m idna --decode "xn--r8jz45g.xn--zckzah"
```

## Error Handling and Boundary Conditions

- Preserve a single trailing dot, reject empty interior labels, and enforce
  63-octet label and 253/254-octet domain limits.
- Non-NFC input, bad hyphens, leading combining marks, disallowed codepoints,
  invalid context rules, Bidi violations, invalid UTF-8, and non-canonical
  A-labels raise the documented `IDNAError` subclass with stable metadata.
- `strict`, `uts46`, `std3_rules`, and `transitional` are independent options;
  transitional mode emits its documented deprecation warning.
- CLI conversion errors go to stderr while later domains continue. A failed
  conversion makes the process exit with status 1, but successful lines remain
  one result per line on stdout. All runtime operations are offline.
