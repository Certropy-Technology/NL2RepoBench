# Build `wcwidth`

```text
workspace/
├── pyproject.toml
└── wcwidth/__init__.py
```

Create an installable Python package named `wcwidth` from an empty workspace. Reproduce the pinned
upstream package's public Unicode display-width and terminal-text layout behavior on CPython 3.12.
Evaluation is local and deterministic. Do not fetch source code or dependencies during evaluation.

## Project Description

`wcwidth` measures how much terminal column space Unicode text occupies. It provides low-level
single-codepoint and string width functions, grapheme-cluster iteration, ANSI/OSC sequence parsing,
display-aware alignment, wrapping, clipping, SGR propagation, terminal correction tables, and the
small public record types used by OSC 8 hyperlinks and Kitty OSC 66 text sizing.

The implementation must be a normal importable package, not a script or a hard-coded answer table for
the examples. Unicode data tables are part of the package and must be available at runtime.

## Natural Language Instruction

Create the package from an empty `workspace/`. Implement the documented
Unicode display-width, grapheme, ANSI/OSC, clipping, wrapping, alignment,
SGR propagation, and text-sizing APIs. Keep tables and behavior deterministic
without probing a live terminal.

## Supports

- Support Python 3.12 and an installable distribution named `wcwidth`, version `0.8.3`.
- The package has no third-party runtime dependency and must not access the network, filesystem,
  subprocesses, terminal devices, current time, or external services during ordinary API calls.
- Export the documented names from `wcwidth`: `wcwidth`, `wcswidth`, `wcstwidth`, `width`,
  `iter_sequences`, `iter_graphemes`, `iter_graphemes_reverse`, `grapheme_boundary_before`,
  `ljust`, `rjust`, `center`, `wrap`, `clip`, `strip_sequences`, `list_versions`,
  `list_term_programs`, `propagate_sgr`, `Hyperlink`, `HyperlinkParams`, `TextSizing`, and
  `TextSizingParams`.
- Keep the legacy `wcwidth.wcwidth` module importable, as well as the top-level re-exports.
- Results must be deterministic for the same arguments. Do not depend on the host locale or terminal;
  explicit `term_program` arguments are used for correction behavior.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── wcwidth/
    ├── __init__.py
    ├── wcwidth.py
    ├── tables.py
    ├── grapheme.py
    ├── escape.py
    └── text.py
```

The root and legacy `wcwidth.wcwidth` module expose the documented public
functions, classes, constants, and version helpers.

## API Usage Guide

### Width measurement

`wcwidth.wcwidth(wc: str, unicode_version: str = "auto", ambiguous_width: int = 1) -> int`
measures one Unicode codepoint. Return `-1` for C0/C1 control characters, `0` for null and
combining/default-ignorable characters, `1` for ordinary narrow characters, and `2` for wide
characters. `ambiguous_width` may be `1` or `2` for East Asian Ambiguous characters.

`wcwidth.wcswidth(pwcs: str, n: int | None = None, unicode_version: str = "auto",
ambiguous_width: int = 1) -> int` measures a string and returns `-1` if a control character is
present. `n` limits the number of input codepoints and values larger than the string length are
accepted. Grapheme clusters, regional-indicator pairs, variation selectors, emoji modifiers, Mc
marks, and virama/invisible-stacker sequences follow the pinned Unicode tables.

`wcwidth.wcstwidth(pwcs: str, n: int | None = None, unicode_version: str = "auto",
ambiguous_width: int = 1, term_program: bool | str = True) -> int` applies the same measurement with
the terminal correction profile. A string terminal name selects that profile; `False` disables
corrections and `True` uses the process environment only for terminal-name detection.

`wcwidth.width(text: str, *, control_codes: Literal["parse", "strict", "ignore"] = "parse",
tabsize: int = 8, ambiguous_width: int = 1, term_program: bool | str = False) -> int` measures
terminal text. SGR, OSC 8 hyperlinks, Kitty OSC 66 text sizing, tabs, backspace, carriage return,
cursor-horizontal movement, and recognized zero-width sequences are handled in parse mode. Ignore
mode treats control characters as zero width. Strict mode raises `ValueError` for indeterminate or
invalid movement instead of guessing.

### Segmentation and layout

`iter_sequences(text: str) -> Iterator[tuple[str, bool]]` yields alternating text and terminal
sequence segments; the boolean is true for an escape sequence. `strip_sequences(text: str) -> str`
removes recognized terminal sequences.

`iter_graphemes(text: str) -> Iterator[str]` yields extended grapheme clusters as strings.
`iter_graphemes_reverse(text: str) -> Iterator[str]` yields the same clusters from right to left.
`grapheme_boundary_before(text: str, pos: int) -> int` returns the start of the cluster at or before
the given position, clamping at the valid string boundaries.

`ljust(text, dest_width, fillchar=" ", *, control_codes="parse", ambiguous_width=1,
term_program=False)`, `rjust(...)`, and `center(...)` pad by displayed width, preserve terminal
sequences, and return the original text when it already meets the requested width. `fillchar` must
provide a single display cell.

`wrap(text, width=70, *, initial_indent="", subsequent_indent="", expand_tabs=True,
replace_whitespace=True, fix_sentence_endings=False, break_long_words=True,
drop_whitespace=True, break_on_hyphens=True, tabsize=8, max_lines=None, placeholder=" [...]",
ambiguous_width=1, term_program=False, **kwargs)` is a display-width-aware counterpart of
`textwrap.wrap`. It preserves grapheme clusters and terminal sequences, propagates active SGR styles
by default, and returns a list of strings.

`clip(text, start, end, *, fillchar=" ", tabsize=8, ambiguous_width=1, propagate_sgr=True,
control_codes="parse", overtyping=None, term_program=False) -> str` extracts the half-open displayed
column interval `[start, end)`. It preserves relevant terminal sequences, fills partial wide cells
with `fillchar`, and can parse cursor overtyping. `overtyping=False` selects the simple path; `None`
allows automatic detection; `control_codes="strict"` raises on indeterminate sequences.

### Records and state helpers

`HyperlinkParams(url: str, params: str = "", terminator: str = "\x07")` is a NamedTuple with
`parse`, `make_open`, and `make_close`. `Hyperlink(params, text)` parses a complete OSC 8 unit,
finds its close sequence, reports `display_width`, and rebuilds it with `make_sequence`.

`TextSizingParams(scale=1, width=0, numerator=0, denominator=0, vertical_align=0,
horizontal_align=0)` parses bounded Kitty OSC 66 fields, clamps values in parse mode, and rebuilds
the parameter string. `TextSizing(params, text, terminator)` reports allocated display width and
rebuilds the complete sequence.

`propagate_sgr(lines: Sequence[str]) -> list[str]` carries active SGR attributes from one line to
the next, adding resets and restored styles where required. `list_versions() -> tuple[str, ...]`
returns the supported Unicode versions. `list_term_programs() -> tuple[str, ...]` returns the stable
sorted terminal profile names.

## Examples

```python
from wcwidth import wcswidth, wrap, truncate
wcswidth('表')
wrap('alpha beta', 5)
truncate('long text', 6)
```

ANSI sequences and combining marks do not consume terminal columns. Layout
helpers return the documented list or string shapes.

## Error Handling and Boundary Conditions

Empty strings, controls, combining marks, emoji sequences, malformed escape
sequences, and width-zero limits follow the public contract. Unsupported
Unicode versions or terminal profiles are handled as documented without TTY
probing.

## Implementation Notes

Use a modular package with immutable generated Unicode tables and a clear separation between low-level
codepoint width, grapheme scanning, escape parsing, and display layout. Preserve ordinary Python
types and exact return shapes. The optional native accelerator is not required, but any fallback must
provide the same public behavior. Terminal correction profiles must be selected only from explicit
arguments or environment names and must never probe a live terminal. Keep compatibility imports and
public `__all__` behavior consistent with the documented package surface.
