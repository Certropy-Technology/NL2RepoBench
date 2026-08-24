# Build `tabulate`

Create a complete, installable Python package named `tabulate` from an empty
workspace. It is a local library for turning rectangular data into readable
plain-text, terminal, markup, and machine-oriented table representations. The
observable behavior must match the pinned `astanin/python-tabulate` revision
recorded in `task.toml`; do not copy the upstream source or tests.

This is a behavior contract, not a request to reproduce the upstream directory
layout. A clean workspace must be sufficient to build and install the package,
and the package must not rely on an already installed copy of `tabulate`.

## Project Description

The library accepts rows, records, mappings, iterators, and compatible table
objects, normalizes them into a rectangular table, and renders the result with
one of the named table formats or a caller-supplied `TableFormat`. It supports
headers, row indexes, numeric and text alignment, numeric formatting, missing
values, multiline cells, width limits, and HTML escaping. It also exposes a
small CLI through `python -m tabulate` for formatting text supplied on standard
input or through the source-defined command-line options.

The base task lane is deliberately pure Python. Runtime behavior must work
without `numpy`, `pandas`, or `wcwidth`. Optional integrations may be detected
when installed, but they must not be required, imported unconditionally, or
change the result of the base lane.

## Supports

- Provide an installable package whose import name is `tabulate`.
- Support the CPython version selected by the task environment and recorded by
  the audit; do not require a network connection, service, subprocess, or
  mutable source checkout for normal library calls.
- Keep the base runtime dependency-free beyond Python's standard library.
- Expose package metadata and the public names described below from the normal
  import paths.
- Preserve input order and deterministic output. Do not sort rows or mapping
  keys unless the caller has supplied an ordered input whose order is part of
  the input contract.
- Read and write text as Unicode. Do not use the host locale, terminal width,
  current time, random state, or filesystem paths to make formatting choices.

## API Usage Guide

### Main function

Implement the source-defined `tabulate` function with the following behavior
surface (the pinned revision is authoritative for any exact default or keyword
that differs):

```python
tabulate(
    tabular_data,
    headers=(),
    tablefmt="simple",
    floatfmt="g",
    intfmt="",
    numalign="default",
    stralign="default",
    missingval="",
    showindex="default",
    disable_numparse=False,
    colalign=None,
    maxcolwidths=None,
    rowalign=None,
    maxheadercolwidths=None,
    headersglobalalign=None,
    wrap_text=False,
    unsafehtml=False,
    preserve_whitespace=True,
)
```

`tabular_data` may be a sequence or iterator of row sequences, a sequence of
mappings, or a compatible table object accepted by the pinned revision.
Consume an iterator once and preserve its row and column order. Rows with
missing cells are padded with `missingval`; invalid cell structures follow the
source revision's exception behavior. An empty input produces the source
revision's empty result.

`headers` may be omitted, supplied as a sequence, or use a source-defined
header sentinel such as the first-row form. Header length and mapping-key
behavior must match the pinned revision. `showindex` supports the source forms
for hiding, always showing, or explicitly supplying an index column.

### Formatting and alignment

Support the built-in names exposed by `tabulate_formats` and the exact
`TableFormat` and `Line` structures exposed by the pinned package. A custom
`TableFormat` must be accepted anywhere the source accepts one. Horizontal
rules, separators, padding, header rules, and final newline behavior must be
deterministic for fixed input.

`floatfmt` and `intfmt` select per-column or shared numeric format strings
according to the source contract. `numalign` controls numeric alignment and
`stralign` controls text alignment; `colalign` overrides these choices per
column. Invalid format names, alignment values, or incompatible format
sequences must raise the same exception class as the pinned revision.

Numeric-looking strings are parsed and aligned according to the source rules
unless `disable_numparse` is true. Integers, real numbers, booleans, `None`,
empty strings, and explicitly supplied missing values must retain the source
distinction. Do not use locale-dependent decimal separators.

### Multiline, widths, and markup

Honor embedded line breaks in cell and header values. `maxcolwidths`,
`maxheadercolwidths`, `wrap_text`, and `rowalign` must follow the source
revision's handling of long and multiline content, including continuation
prefixes and vertical alignment.

Width calculations must remain stable for ASCII, combining characters, CJK
characters, and emoji when `wcwidth` is absent. The fallback is part of the
base contract; installing an optional width package is not.

For HTML-producing formats, escape cell and header text by default, including
HTML-sensitive characters wherever the source escapes them. `unsafehtml`
selects the source-defined opt-out behavior. Do not escape plain-text formats.
Preserve the exact tags, attributes, separators, and newline conventions of the
selected built-in format.

### Public names and CLI

The package root must expose the source-defined public API, including:

- `tabulate` and `tabulate_formats`;
- `simple_separated_format`;
- `TableFormat` and `Line`;
- source-defined version and configuration constants; and
- helpers intentionally re-exported by the pinned revision.

The module `tabulate.__main__` must provide the source-defined CLI entry point.
`python -m tabulate --help` and `python -m tabulate --version` must terminate
cleanly. CLI errors must use a non-zero exit status with diagnostics on stderr;
stdout is reserved for the rendered table.

## Implementation Notes

- Match the pinned revision's public signatures, import paths, exception types,
  and output strings. Internal helper names and implementation strategy are
  not part of the contract.
- Optional `numpy`, `pandas`, and `wcwidth` integrations are outside the base
  dependency lane. A missing optional module must not make `import tabulate`
  fail or alter ordinary list-of-lists formatting.
- Treat locale and Unicode as explicit inputs. For fixed UTF-8 input, output
  must be stable under the locale matrix specified by the audit, except for
  behavior explicitly defined by the pinned source.
- Keep the package usable from a fresh environment with an offline installer.
  Do not fetch packages during library calls or hide an undeclared dependency
  behind an import-time fallback.
- The verification boundary may execute the candidate in a separate child
  process. A child that receives JSON-encoded rows and emits rendered text must
  keep stdout reserved for the result, stderr reserved for diagnostics, use
  UTF-8, return a meaningful non-zero status on invalid input, and honor a
  bounded timeout. This boundary is an audit probe, not an additional public
  library API.
