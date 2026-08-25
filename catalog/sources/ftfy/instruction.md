# Project Description

Build `ftfy` 6.3.1, a Python library that repairs mojibake and other common
Unicode defects while conservatively leaving already-correct text alone. The
repository must be installable from its root, provide the `ftfy` package and
the `ftfy` console entry point, and work without network access at run time.

# Supports

- Python 3.12 on Linux.
- A standard `pyproject.toml` installation. The distribution name is `ftfy`,
  the version is `6.3.1`, and the runtime dependency is `wcwidth`.
- Package data includes `ftfy/py.typed`.
- Public modules `ftfy`, `ftfy.fixes`, `ftfy.chardata`, `ftfy.badness`,
  `ftfy.formatting`, `ftfy.cli`, and `ftfy.bad_codecs`, including
  `ftfy.bad_codecs.utf8_variants`.
- Deterministic Unicode processing. Functions return new strings or structured
  explanations and do not mutate their input.

# API Usage Guide

## Text repair

`ftfy.fix_text(text: str, config: TextFixerConfig | None = None, **kwargs) -> str`
repairs a complete text. It may divide long text at line boundaries before
calling `fix_text_segment`. It fixes repeated UTF-8 mojibake such as
`"sÃ³" -> "só"` and `"l'humanitÃ©" -> "l'humanité"`, removes a BOM and
terminal escapes, applies the configured Unicode normalization, and preserves
ordinary Unicode. Keyword options override the default configuration. An
unsupported normalization form raises `ValueError`.

`ftfy.fix_text_segment(text: str, config: TextFixerConfig | None = None,
**kwargs) -> str` applies the same configurable operations to one segment.
Its automatic HTML policy decodes entities when the segment does not look like
HTML. `unescape_html=True` always decodes recognized entities;
`unescape_html=False` preserves them. Repeated entities are decoded repeatedly.

`ftfy.fix_encoding(text: str) -> str` performs only the encoding-repair part.
It may repair multiple layers of UTF-8 decoded through single-byte encodings,
but leaves text alone when no candidate improves the badness score.

`ftfy.fix_and_explain(text: str, config: TextFixerConfig | None = None,
**kwargs) -> ExplainedText` and
`ftfy.fix_encoding_and_explain(text: str) -> ExplainedText` return a two-field
tuple-like value whose `.text` is the repaired string and whose `.explanation`
is either a list of `ExplanationStep(action, parameter)` values or `None`.
Actions are `encode`, `decode`, `transcode`, and `apply`.

`ftfy.apply_plan(text: str, plan: list[ExplanationStep | tuple[str, str]]) -> str`
replays an explanation in order. Unknown actions raise `ValueError`; unknown
codec or fixer names raise the corresponding lookup error.

`TextFixerConfig` is a named-tuple-like immutable configuration with defaults
for HTML unescaping, encoding repair, curly-quote uncurling, line-break repair,
surrogate repair, terminal-escape removal, control-character removal, and NFC
normalization. Deprecated keyword aliases remain accepted with a
`DeprecationWarning`.

## Byte and codec handling

`ftfy.guess_bytes(data: bytes) -> tuple[str, str]` decodes UTF-16 when a BOM is
present, valid UTF-8 as `utf-8`, UTF-8 variants such as CESU-8 and overlong NUL
as `utf-8-variants`, MacRoman when CR line endings identify it, and otherwise
uses `sloppy-windows-1252`. The returned encoding name identifies the chosen
codec.

Importing `ftfy.bad_codecs` registers sloppy single-byte codecs and
`utf-8-variants`. `ftfy.bad_codecs.search_function(name)` accepts normalized
aliases including `cesu8` and `cesu-8` and returns a `codecs.CodecInfo` or
`None`. `ftfy.bad_codecs.utf8_variants.IncrementalDecoder(errors="strict")`
implements the incremental decoder protocol and buffers incomplete sequences
when `final=False`.

## Character-level helpers

`ftfy.fixes.unescape_html(text: str) -> str` decodes named and numeric HTML
entities case-insensitively, including Windows-1252 interpretations of numeric
values 0x80 through 0x9f. Invalid Unicode noncharacters decode to an empty
string and out-of-range numeric entities become U+FFFD. Non-entities remain
unchanged.

`ftfy.fixes.fix_surrogates(text: str) -> str` combines valid UTF-16 surrogate
pairs and replaces unpaired surrogates with U+FFFD.

`ftfy.fixes.remove_control_chars(text: str) -> str` removes C0/C1 controls and
obsolete formatting controls while retaining tabs, CR/LF, and Unicode tag
characters used in emoji flag sequences.

`ftfy.fixes.remove_terminal_escapes(text: str) -> str` removes ANSI/terminal
escape sequences. `remove_bom`, `uncurl_quotes`, `fix_line_breaks`,
`fix_character_width`, and `decode_escapes` expose their corresponding single
repair operations.

`ftfy.chardata.possible_encoding(text: str, encoding: str) -> bool` reports
whether every character can be encoded by the named supported single-byte
encoding. Unknown encoding keys raise `KeyError`.

`ftfy.badness.badness(text: str) -> int` returns a non-negative mojibake score,
and `ftfy.badness.is_bad(text: str) -> bool` is equivalent to checking whether
that score is greater than zero. `sequence_weirdness` remains an old alias
that emits `UserWarning`.

## Files, formatting, and CLI

`ftfy.fix_file(input_file, encoding: str | None = None,
config: TextFixerConfig | None = None, **kwargs) -> Iterator[str]` accepts a
binary file or iterable of bytes, guesses the encoding when omitted, decodes
incrementally, and yields repaired text while preserving line boundaries.

`ftfy.formatting.monospaced_width(text: str) -> int` uses terminal cell width;
`display_ljust`, `display_rjust`, and `display_center` pad to a requested cell
width without truncating text.

`python -m ftfy.cli [options] [filename]` and the `ftfy` script read bytes from
a file or standard input and write repaired UTF-8 to standard output unless
`-o/--output` names another file. `-g/--guess` enables byte guessing,
`-e/--encoding` selects an input codec, `-n/--normalization` selects the Unicode
normalization form, and `--preserve-entities` disables entity decoding. Reading
and writing the same path fails with a non-zero exit and a message beginning
`ftfy error:`. Decode failures use the same prefix and explain the selected
encoding.

# Implementation Notes

- Repair decisions must use the package's badness heuristic; do not replace
  them with unconditional encode/decode conversions.
- Preserve the order of explanation steps because `apply_plan` must replay
  them exactly.
- Keep the codec registry integration compatible with Python's normalization
  of codec names.
- Width helpers must account for full-width characters rather than using
  `len(text)`.
- The console implementation must stream input and must not fetch resources.
