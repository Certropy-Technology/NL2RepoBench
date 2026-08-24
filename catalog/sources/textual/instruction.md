# Build `textual`

## Project Description

Create an installable Python package named `textual`, a modern text user interface
framework. Start from an empty workspace and implement the documented, deterministic
utility and value-object behavior below. The package must be usable with Python 3.12
and must not require a network connection at runtime.

## Supports

- A Poetry-backed `pyproject.toml` with package source under `src/textual/`.
- Runtime dependencies declared by the package metadata: `markdown-it-py` with its
  `linkify` extra, `mdit-py-plugins`, `rich`, `typing-extensions`, and `platformdirs`.
- `import textual` and the public version attribute `textual.__version__`.
- Text, slug, wrapping, geometry, color, markup escaping, and validation behavior
  described in the API guide. Results crossing the task boundary are JSON-compatible
  scalars, arrays, and strings.

## API Usage Guide

Implement these import paths and signatures:

1. `textual._slug.slug(text: str) -> str` trims and lowercases text, removes
   punctuation and emoji-like non-lingual symbols, converts whitespace to `-`, and
   percent-encodes the resulting UTF-8 text.
2. `textual._slug.slug_for_tcss_id(text: str) -> str` produces a lower-case TCSS id.
   Spaces become dashes; characters outside `a-z`, `0-9`, and `-` become their lower
   case hexadecimal code point; an empty result is `_`, and a leading digit is prefixed
   with `_`.
3. `textual.case.camel_to_snake(name: str) -> str` inserts an underscore at lower-to-
   upper transitions and lowercases the result.
4. `textual._cells.cell_len(text: str) -> int` returns terminal cell width, including
   combining-character behavior. `cell_width_to_column_index(line, cell_width,
   tab_width) -> int` maps a cell offset to a code-point column using tab stops.
5. `textual._wrap.chunks(text: str)` yields `(start, end, chunk)` tuples for each
   non-whitespace word together with following whitespace. `compute_wrap_offsets(text,
   width, tab_size, fold=True) -> list[int]` returns code-point break offsets.
6. `textual.geometry.clamp(value, minimum, maximum)` clamps comparable values while
   preserving the input type. `Offset(x, y)`, `Size(width, height)`, and `Region(x, y,
   width, height)` are tuple-like value objects. `Region.from_corners(x1, y1, x2, y2)`
   constructs a region from two corners.
7. `textual.color.Color.parse(value: str) -> Color`, `Color.from_hsl(h, s, l)`, and
   `Color.from_hsv(h, s, v)` return a six-field tuple-like color
   `(r, g, b, a, ansi, auto)`. Parse common named colors and hex colors, and raise
   `textual.color.ColorParseError` for malformed colors.
8. `textual.markup.escape(markup: str) -> str` escapes markup opening brackets while
   preserving ordinary text and backslash rules.
9. `textual.validation.ValidationResult.success()`, `ValidationResult.failure(message)`,
   and the `is_valid` attribute provide the success/failure value used by validators.

The exact edge cases exercised by the verifier are part of the contract. Preserve
deterministic ordering, tuple/list shapes when serialized, exception type names, and
the package's normal import layout. Do not add a benchmark-specific facade or test
server.

## Implementation Notes

Keep implementation modular and compatible with normal `textual` imports. The task
verifier invokes candidate functions in isolated subprocesses and sends only JSON-safe
arguments, so public functions should not depend on mutable global state for these
behaviors. Snapshot tests, terminal rendering, live application event loops, and
optional syntax-highlighting integrations are outside this deterministic contract; do
not claim them as implemented solely because the package imports.
