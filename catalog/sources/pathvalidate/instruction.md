# pathvalidate

## Project Description

Build an installable `pathvalidate` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `pathvalidate`; public import package begins at `pathvalidate`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Platforms`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Validation errors`: preserve the documented object or module behavior, including state and side effects.
3. `Common text helpers`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Filename API`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `pathvalidate`; public import package begins at `pathvalidate`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `click==8.5.0`, `packaging==26.3`, `setuptools==84.0.0`, `setuptools-scm==10.2.1`, `vcs-versioning==2.3.1`, `wheel==0.48.0`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── package/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

## Platforms

```python
class Platform(enum.Enum):
    POSIX = "POSIX"
    UNIVERSAL = "universal"
    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "macOS"

normalize_platform(name: str | Platform | None) -> Platform
```

`None`, an empty string, unknown names, and `"universal"` normalize to
`UNIVERSAL`. Matching is case-insensitive after stripping. `"posix"`,
`"linux"`, names beginning with `"win"`, and `"mac"`/`"macos"`/`"darwin"`
map to their corresponding members. `"auto"` maps the host returned by
`platform.system()`. Passing a `Platform` returns it unchanged.

The default platform for public filename/filepath APIs is universal. Universal
rules combine portable POSIX and Windows restrictions.

## Validation errors

```python
class ErrorReason(enum.Enum): ...

class ValidationError(ValueError):
    @property
    def platform(self) -> Platform | None: ...
    @property
    def reason(self) -> ErrorReason: ...
    @property
    def description(self) -> str | None: ...
    @property
    def reserved_name(self) -> str: ...
    @property
    def reusable_name(self) -> bool | None: ...
    @property
    def fs_encoding(self) -> str | None: ...
    @property
    def byte_count(self) -> int | None: ...
    def as_slog(self) -> dict[str, str]: ...

class NullNameError(ValidationError): ...
class InvalidCharError(ValidationError): ...
class ReservedNameError(ValidationError): ...
class ValidReservedNameError(ReservedNameError): ...
class InvalidReservedNameError(ReservedNameError): ...
```

`ValidationError` requires a `reason` keyword. The public reason members are:

| Name | Code | Description |
| --- | --- | --- |
| `NULL_NAME` | `PV1001` | `the value must not be an empty string` |
| `RESERVED_NAME` | `PV1002` | `found a reserved name by a platform` |
| `INVALID_CHARACTER` | `PV1100` | `invalid characters found` |
| `INVALID_LENGTH` | `PV1101` | `found an invalid string length` |
| `FOUND_ABS_PATH` | `PV1200` | `found an absolute path where must be a relative path` |
| `MALFORMED_ABS_PATH` | `PV1201` | `found a malformed absolute path` |
| `INVALID_AFTER_SANITIZE` | `PV2000` | `found invalid value after sanitizing` |

Each reason exposes `.code`, `.name`, and `.description`. `str(reason)` is
`"[<code>] <description>"`. Error strings append available details such as
platform, description, reserved-name status, encoding, byte count, and value.
`as_slog()` returns the code and description plus only populated details; all
values except the code and description are strings.

## Common text helpers

```python
validate_pathtype(
    text: str | os.PathLike,
    allow_whitespaces: bool = False,
    error_msg: str | None = None,
) -> None

validate_unprintable_char(text: str) -> None
replace_unprintable_char(text: str, replacement_text: str = "") -> str
replace_ansi_escape(text: str, replacement_text: str = "") -> str
```

`validate_pathtype` accepts nonempty strings and `pathlib.PurePath` values.
`None`, an empty string, and whitespace-only strings raise `ValidationError`
with `NULL_NAME`, except whitespace is accepted when `allow_whitespaces=True`.
Other values raise `TypeError` containing `text must be a string`.

`unprintable_ascii_chars` is a tuple of ASCII characters absent from
`string.printable`. `ascii_symbols` is a tuple of printable ASCII symbols and
whitespace excluding letters and digits. The replacement helpers replace every
match and preserve all other text. Non-string replacement inputs raise
`TypeError("text must be a string")`. `validate_unprintable_char` raises
`InvalidCharError` when a listed character occurs.

`replace_ansi_escape` recognizes single-character escapes and CSI sequences.
For example:

```python
assert replace_ansi_escape("A\x1b[31mred\x1b[0mB") == "AredB"
```

## Filename API

```python
validate_filename(
    filename,
    platform=None,
    min_len=1,
    max_len=255,
    fs_encoding=None,
    check_reserved=True,
    additional_reserved_names=None,
) -> None

is_valid_filename(
    filename,
    platform=None,
    min_len=1,
    max_len=None,
    fs_encoding=None,
    check_reserved=True,
    additional_reserved_names=None,
) -> bool

sanitize_filename(
    filename,
    replacement_text="",
    platform=None,
    max_len=255,
    fs_encoding=None,
    check_reserved=None,
    null_value_handler=None,
    reserved_name_handler=None,
    additional_reserved_names=None,
    validate_after_sanitize=False,
): ...
```

Strings and `pathlib.PurePath` values are accepted. Sanitizers preserve the
input category: a path-like input returns a `pathlib.Path`; a string returns a
string. Length is measured in encoded bytes using `fs_encoding` or the runtime
filesystem encoding. Truncation never returns a partial multibyte character.
`max_len=None` selects the platform default rather than disabling limits.

Every filename platform rejects NUL and `/`. Universal and Windows filenames
also reject ASCII controls and `<>:"\\|?*`. Windows/universal names may not
start with a space or end with a space or period; sanitization strips those
boundary characters after invalid-character replacement. `.` and `..` remain
valid reusable directory entries.

An absolute POSIX or drive-qualified Windows path is not a filename and raises
`ValidationError` with `FOUND_ABS_PATH`. Invalid characters raise
`InvalidCharError`. Byte lengths outside `[min_len, max_len]` raise
`ValidationError` with `INVALID_LENGTH`, `byte_count`, and `fs_encoding`.

Windows/universal reserved base names are case-insensitive and include
`CON`, `PRN`, `AUX`, `CLOCK$`, `NUL`, `COM0` through `COM9`, `LPT0` through
`LPT9`, and their superscript 1/2/3 forms. The reservation applies before a
suffix, so `con.txt` is reserved as `con`. macOS reserves `:`. Values from
`additional_reserved_names` are also case-insensitive base names.

The default reserved-name sanitizer adds `_` after the reserved base while
preserving a suffix:

```python
assert sanitize_filename("con.txt", platform="windows") == "con_.txt"
assert sanitize_filename('fi:l*e/p"a?t>h|.t<xt') == "filepath.txt"
assert sanitize_filename("属/性.txt", "-") == "属-性.txt"
```

`check_reserved` on a sanitizer is deprecated. Supplying it emits one
`DeprecationWarning`; `False` selects `ReservedNameHandler.as_is`. Validator
`check_reserved=False` disables reserved-name rejection without warning.

## Filename classes

```python
class FileNameValidator(AbstractValidator):
    def __init__(
        self,
        min_len=1,
        max_len=255,
        fs_encoding=None,
        platform=None,
        check_reserved=True,
        additional_reserved_names=None,
    ) -> None: ...
    @property
    def reserved_keywords(self) -> tuple[str, ...]: ...
    def validate(self, value) -> None: ...
    def validate_abspath(self, value: str) -> None: ...
    def is_valid(self, value) -> bool: ...

class FileNameSanitizer(AbstractSanitizer):
    def __init__(
        self,
        max_len=255,
        fs_encoding=None,
        platform=None,
        null_value_handler=None,
        reserved_name_handler=None,
        additional_reserved_names=None,
        validate_after_sanitize=False,
        validator=None,
    ) -> None: ...
    def sanitize(self, value, replacement_text=""): ...
```

Validators expose `min_len`, `max_len`, `platform`, and sorted
`reserved_keywords`. Sanitizers expose `max_len` and `platform`. A supplied
validator replaces the automatically constructed validator.
`validate_after_sanitize=True` validates the final result; a failure is raised
as `ValidationError` with `INVALID_AFTER_SANITIZE`.

## Filepath API

```python
validate_filepath(
    file_path,
    platform=None,
    min_len=1,
    max_len=None,
    fs_encoding=None,
    check_reserved=True,
    additional_reserved_names=None,
) -> None

is_valid_filepath(
    file_path,
    platform=None,
    min_len=1,
    max_len=None,
    fs_encoding=None,
    check_reserved=True,
    additional_reserved_names=None,
) -> bool

sanitize_filepath(
    file_path,
    replacement_text="",
    platform=None,
    max_len=None,
    fs_encoding=None,
    check_reserved=None,
    null_value_handler=None,
    reserved_name_handler=None,
    additional_reserved_names=None,
    normalize=True,
    validate_after_sanitize=False,
): ...
```

Platform default maximum path lengths are Linux 4096 bytes, macOS/POSIX 1024,
and Windows/universal 260. Validation checks the total path and then validates
each nonempty component except `.` and `..` as a filename. POSIX absolute paths
are valid for POSIX/Linux; drive-qualified absolute paths are valid for
Windows. Passing the opposite format raises `MALFORMED_ABS_PATH`.

Linux/POSIX paths reject NUL but permit characters such as `:`, `*`, and `?`
inside components. Universal/Windows paths reject Windows-invalid characters
within components while retaining path separators and a Windows drive.
Windows sanitizer output uses `\\`; other platforms use `/`.

With `normalize=True`, sanitization first applies `os.path.normpath`, collapsing
redundant separators and `.`/`..` segments according to the host semantics.
With `normalize=False`, those segments are preserved. Every component is then
sanitized as a filename. Root NTFS metadata entries such as `$Mft`, `$LogFile`,
and `$Extend` receive a trailing underscore. Ordinary reserved components and
additional reserved names use the configured reserved-name handler.

Examples:

```python
assert sanitize_filepath('fi:l*e/p"a?t>h|.t<xt') == "file/path.txt"
assert sanitize_filepath("a/./b/../c", platform="linux") == "a/c"
assert sanitize_filepath("CON/file", platform="windows") == "CON_\\file"
```

## Filepath classes

```python
class FilePathValidator(AbstractValidator):
    def __init__(
        self,
        min_len=1,
        max_len=-1,
        fs_encoding=None,
        platform=None,
        check_reserved=True,
        additional_reserved_names=None,
    ) -> None: ...
    @property
    def reserved_keywords(self) -> tuple[str, ...]: ...
    def validate(self, value) -> None: ...
    def validate_abspath(self, value) -> None: ...
    def is_valid(self, value) -> bool: ...

class FilePathSanitizer(AbstractSanitizer):
    def __init__(
        self,
        max_len=-1,
        fs_encoding=None,
        platform=None,
        null_value_handler=None,
        reserved_name_handler=None,
        additional_reserved_names=None,
        normalize=True,
        validate_after_sanitize=False,
        validator=None,
    ) -> None: ...
    def sanitize(self, value, replacement_text=""): ...
```

The classes expose the same common properties and `is_valid` semantics as the
filename classes.

## Null and reserved-name handlers

Import these from `pathvalidate.handler`:

```python
raise_error(error: ValidationError) -> str

class NullValueHandler:
    @classmethod
    def return_null_string(cls, error: ValidationError) -> str: ...
    @classmethod
    def return_timestamp(cls, error: ValidationError) -> str: ...

class ReservedNameHandler:
    @classmethod
    def add_leading_underscore(cls, error: ValidationError) -> str: ...
    @classmethod
    def add_trailing_underscore(cls, error: ValidationError) -> str: ...
    @classmethod
    def as_is(cls, error: ValidationError) -> str: ...
```

The default null handler returns `""`; the timestamp handler returns
`str(datetime.now().timestamp())`; and `raise_error` re-raises its argument.
Reserved handlers preserve `.`/`..` and any error marked reusable. Otherwise
they add the indicated underscore or return the reserved base unchanged.

## LTSV labels and symbols

```python
sanitize_ltsv_label(label: str, replacement_text: str = "") -> str
validate_ltsv_label(label: str) -> None

replace_symbol(
    text: str,
    replacement_text: str = "",
    exclude_symbols=(),
    is_replace_consecutive_chars: bool = False,
    is_strip: bool = False,
) -> str
validate_symbol(text: str) -> None
```

LTSV labels permit only ASCII letters, digits, `_`, `.`, and `-`. Sanitization
replaces every other character; validation raises `InvalidCharError`.

Symbols are the characters in `ascii_symbols` plus unprintable ASCII.
`exclude_symbols` preserves listed symbols. When
`is_replace_consecutive_chars=True`, repeated replacement text collapses to one
occurrence. `is_strip=True` strips replacement characters from both ends after
replacement. Non-ASCII letters remain unchanged.

## argparse and Click adapters

`pathvalidate.argparse` exports:

```python
validate_filename_arg(value: str) -> str
validate_filepath_arg(value: str) -> str
sanitize_filename_arg(value: str) -> str
sanitize_filepath_arg(value: str) -> str
```

Empty input returns `""`. Validators return the original value on success and
convert `ValidationError` to `argparse.ArgumentTypeError`. The filepath
argparse functions use `platform="auto"`.

`pathvalidate.click` exports callback-compatible forms:

```python
validate_filename_arg(ctx, param, value: str) -> str
validate_filepath_arg(ctx, param, value: str) -> str
sanitize_filename_arg(ctx, param, value: str) -> str
sanitize_filepath_arg(ctx, param, value: str) -> str
```

They also return `""` for empty values. Validation failures become
`click.BadParameter`. The Click filepath callbacks use the default universal
platform.


- Keep validation and sanitization deterministic for explicit platform values.
- Use encoded byte counts, not Python character counts, for length limits.
- Reserved-name comparisons are case-insensitive and preserve the original
  spelling when adding underscores.
- `is_valid_*` returns `False` for `ValidationError` and `True` after successful
  validation; it must not return sanitized text.
- Avoid touching the filesystem to decide whether a path is valid. The contract
  is lexical.
- Do not expose or depend on test files, reports, source-control metadata, or a
  network connection at runtime.

The fixed denominator contains 54 independent subprocess leaves:

```text
api-surface
module-metadata
core-signatures
platform-enum
normalize-platform
ascii-constants
ansi-escape-replacement
unprintable-character-helpers
path-type-validation
sanitize-filename-universal
sanitize-filename-replacement
sanitize-filename-pathlike
sanitize-filename-multibyte
sanitize-filename-byte-truncation
sanitize-filename-windows-boundaries
sanitize-filename-reserved-default
sanitize-filename-reserved-handlers
sanitize-filename-additional-reserved
sanitize-filename-null-handlers
validate-filename-valid
validate-filename-invalid-character
validate-filename-absolute-path
validate-filename-reserved-error
validate-filename-length
is-valid-filename
filename-validator-properties
filename-sanitizer-properties
sanitize-filepath-universal
sanitize-filepath-windows
sanitize-filepath-posix
sanitize-filepath-normalize
sanitize-filepath-pathlike
sanitize-filepath-reserved
sanitize-filepath-null
validate-filepath-valid
validate-filepath-invalid-character
validate-filepath-platform-absolute
validate-filepath-length
is-valid-filepath
filepath-validator-properties
filepath-sanitizer-properties
ltsv-labels
replace-symbol-basic
replace-symbol-options
validate-symbol
error-reason-metadata
validation-error-structure
exception-hierarchy
reserved-name-handlers
argparse-adapters-success
argparse-adapters-errors
click-adapters-success
click-adapters-errors
deprecated-check-reserved-flag
```

Each leaf constructs its values inside a fresh unprivileged candidate process.
The separate evaluator never imports candidate code. Performance, thread safety,
filesystem existence/permissions, exact timestamp values, deprecated handler
function warning text, and undocumented private classes are outside the scored
contract.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
(
    "__author__", "__copyright__", "__email__", "__license__", "__version__",
    "AbstractSanitizer", "AbstractValidator", "Platform", "ascii_symbols",
    "normalize_platform", "replace_ansi_escape", "replace_unprintable_char",
    "unprintable_ascii_chars", "validate_pathtype", "validate_unprintable_char",
    "FileNameSanitizer", "FileNameValidator", "is_valid_filename",
    "sanitize_filename", "validate_filename", "FilePathSanitizer",
    "FilePathValidator", "is_valid_filepath", "sanitize_filepath",
    "validate_filepath", "sanitize_ltsv_label", "validate_ltsv_label",
    "replace_symbol", "validate_symbol", "ErrorReason", "InvalidCharError",
    "InvalidReservedNameError", "NullNameError", "ReservedNameError",
    "ValidationError", "ValidReservedNameError",
)
```

### Example 2: ordinary usage
```text
__author__ = "Tsuyoshi Hombashi"
__email__ = "tsuyoshi.hombashi@gmail.com"
__license__ = "MIT License"
__version__ = "3.3.1"
```

### Example 3: boundary or error behavior
```text
class Platform(enum.Enum):
    POSIX = "POSIX"
    UNIVERSAL = "universal"
    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "macOS"

normalize_platform(name: str | Platform | None) -> Platform
```

### Example 4: boundary or error behavior
```text
class ErrorReason(enum.Enum): ...

class ValidationError(ValueError):
    @property
    def platform(self) -> Platform | None: ...
    @property
    def reason(self) -> ErrorReason: ...
    @property
    def description(self) -> str | None: ...
    @property
    def reserved_name(self) -> str: ...
    @property
    def reusable_name(self) -> bool | None: ...
    @property
    def fs_encoding(self) -> str | None: ...
    @property
    def byte_count(self) -> int | None: ...
    def as_slog(self) -> dict[str, str]: ...

class NullNameError(ValidationError): ...
class InvalidCharError(ValidationError): ...
class ReservedNameError(ValidationError): ...
class ValidReservedNameError(ReservedNameError): ...
class InvalidReservedNameError(ReservedNameError): ...
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
