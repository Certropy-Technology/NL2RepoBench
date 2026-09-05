# Project Description

```text
workspace/
├── pyproject.toml
└── charset_normalizer/
    ├── __init__.py
    ├── models.py
    ├── utils.py
    └── __main__.py
```

Build an installable Python package named `charset-normalizer` from an empty workspace. It detects the most plausible Python codec for raw text, exposes decoded candidates and metadata, and provides a compatibility-oriented legacy detector and command-line interface. Implement the behavior contract below for CPython 3.12 on Linux without runtime network access.

## Natural Language Instruction

Create `charset-normalizer` from an empty workspace. Implement deterministic
codec detection, match models, Unicode helpers, legacy detection, and the CLI
described below. Keep all runtime inputs and file operations local.

## Supports or Environment Configuration

- Provide distribution `charset-normalizer` version `3.5.1`, import package `charset_normalizer`, and a `normalizer` console command.
- Provide a PEP 517 `pyproject.toml` and an installable package. Runtime dependencies are not required; standard-library codecs, Unicode metadata, logging, filesystem access, and subprocess invocation for the CLI are sufficient.
- Expose the names listed in `charset_normalizer.__all__`. Keep detection deterministic for identical input and options.
- Evaluation runs from an empty workspace with a separate verifier. Do not fetch source, packages, or services at runtime.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── charset_normalizer/
    ├── __init__.py
    ├── models.py
    ├── utils.py
    └── __main__.py
```

# API Usage Guide

## Detection functions

`charset_normalizer.from_bytes(sequences: bytes | bytearray, steps: int = 5, chunk_size: int = 512, threshold: float = 0.2, cp_isolation: list[str] | None = None, cp_exclusion: list[str] | None = None, preemptive_behaviour: bool = True, explain: bool = False, language_threshold: float = 0.1, enable_fallback: bool = True) -> CharsetMatches` analyzes raw bytes and returns candidates ordered from most plausible to least plausible. Bytes and bytearray are accepted; other values raise `TypeError`. Empty bytes yield one UTF-8 match with empty decoded text. Recognize UTF-8, UTF-16, and UTF-32 byte-order marks, preserve original `raw` bytes, and remove the mark from decoded text where appropriate. ASCII text is identified as `ascii`; ordinary UTF-8 text is identified as `utf_8`.

`cp_isolation` restricts testing to named codecs after normalizing aliases; `cp_exclusion` removes named codecs. The result ordering is deterministic. `threshold`, sampling, fallback, and language options must preserve the stated signature and produce stable results.

`charset_normalizer.from_fp(fp: BinaryIO, ...) -> CharsetMatches` reads a binary file-like object from its current contents and applies the same detection semantics. `charset_normalizer.from_path(path: str | bytes | os.PathLike, ...) -> CharsetMatches` reads a local path and applies the same semantics.

`charset_normalizer.is_binary(fp_or_path_or_payload: os.PathLike | str | BinaryIO | bytes, steps: int = 5, chunk_size: int = 512, threshold: float = 0.2, cp_isolation: list[str] | None = None, cp_exclusion: list[str] | None = None, preemptive_behaviour: bool = True, explain: bool = False, language_threshold: float = 0.1, enable_fallback: bool = False) -> bool` reports whether the input is likely binary. Plain text is false and a broad all-byte payload is true. It accepts bytes, file-like objects, and paths.

## Match models

`charset_normalizer.models.CharsetMatch(payload: bytes | bytearray, guessed_encoding: str, mean_mess_ratio: float, has_sig_or_bom: bool, languages: list[tuple[str, float]], decoded_payload: str | None = None, preemptive_declaration: str | None = None)` stores one candidate. Its `encoding`, `raw`, `bom`, `byte_order_mark`, `chaos`, `coherence`, `percent_chaos`, `percent_coherence`, `language`, `languages`, `alphabets`, `could_be_from_charset`, `has_submatch`, and `submatch` properties are deterministic. `str(match)` lazily decodes the payload; `output(encoding="utf_8")` re-encodes the decoded text. Empty payloads have `multi_byte_usage == 0.0`.

`charset_normalizer.models.CharsetMatches(results: list[CharsetMatch] | None = None)` is a list-like ordered container. `best()` and `first()` return the first candidate or `None`; iteration and integer indexing use sorted order; string indexing accepts codec aliases; `bool` and `len` reflect whether matches exist. `append` accepts only `CharsetMatch` instances and raises `ValueError` otherwise.

## Compatibility and helpers

`charset_normalizer.detect(byte_str: bytes, should_rename_legacy: bool = False, **kwargs) -> dict[str, str | float | None]` returns `encoding`, `language`, and `confidence` keys using legacy codec spellings where applicable. It accepts bytes and bytearray and rejects text strings with `TypeError`.

`charset_normalizer.utils.iana_name(cp_name: str, strict: bool = True) -> str` normalizes common codec aliases such as `utf-8`, `latin1`, and `windows-1252`; strict unknown names raise `ValueError`, while non-strict lookup returns the normalized unknown spelling. `any_specified_encoding(sequence: bytes | bytearray, search_zone: int = 8192)` recognizes ASCII encoding declarations such as HTML `charset` and Python `coding` markers. `identify_sig_or_bom(sequence)` returns the recognized normalized codec and mark bytes, or `(None, b"")`.

Unicode helpers in `charset_normalizer.utils` include `unicode_range(character)`, `is_accentuated`, `is_latin`, `is_cjk`, `is_hiragana`, `is_katakana`, `is_hangul`, `is_thai`, `is_arabic`, `is_emoticon`, `is_punctuation`, `is_separator`, `is_symbol`, `is_unprintable`, and `remove_accent`. Each accepts one character and returns the documented boolean, range name, or normalized character based on standard Unicode properties.

## CLI

`python -m charset_normalizer --version` and `normalizer --version` print the package version and interpreter/Unicode information and exit successfully. The `-m`/`normalizer` command accepts one or more paths; `-m` selects minimal encoding output. Invalid paths exit with status 2. Normal detection must not rewrite files unless normalization options explicitly request it.

# Implementation Notes

Keep candidate code independent of evaluation assets. Use a separate
child-process boundary for isolated calls, preserve deterministic exception
types and output shapes, and keep all runtime operations local. The
implementation may use pure Python; the optional Cython accelerator is not
required. Do not contact package hosts, DNS, or external services during any
execution.

## Examples

```python
from charset_normalizer import from_bytes
match = from_bytes('hello'.encode()).best()
assert match is not None
assert match.encoding in {'ascii', 'utf_8'}
```

```python
from charset_normalizer import detect
assert detect(b'hello')['encoding'] in {'ascii', 'utf-8'}
```

## Error Handling and Boundary Conditions

Text strings passed where bytes are required raise `TypeError`. Empty input
returns the documented empty UTF-8 match; missing paths and invalid CLI paths
fail locally with the documented non-zero status.
