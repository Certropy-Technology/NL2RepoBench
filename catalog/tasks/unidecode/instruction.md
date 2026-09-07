# Project Description

Build **Unidecode 1.4.0**, an installable Python package that performs lossy,
context-free transliteration from Unicode text to 7-bit ASCII. The package is
intended for legacy interfaces, identifiers, and other places where readable
ASCII approximations are more useful than dropping every non-ASCII character.

This is not language detection or language-specific romanization. Each Unicode
code point is mapped independently. Except when the `preserve` error policy is
selected, the result must be encodable with the ASCII codec.

# Natural Language Instruction

Create the installable `Unidecode` distribution and `unidecode` package from
an empty workspace. Implement lazy block-table transliteration, error policy,
cache behavior, command-line decoding, and exact public exports below as a
local deterministic library.

# Supports

- Python 3.7 or later; grading uses CPython 3.12 on Linux.
- Distribution name `Unidecode`, version `1.4.0`, with no runtime dependencies.
- `pip install .` from the repository root.
- Package `unidecode` containing `__init__.py`, `util.py`, `__main__.py`, the
  marker file `py.typed`, and lazily imported block tables named `xNNN.py`.
- Console entry point `unidecode = unidecode.util:main`.
- The project is self-contained. Do not depend on another transliteration
  package or access the network at runtime.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── unidecode/
    ├── __init__.py
    ├── util.py
    ├── __main__.py
    ├── py.typed
    └── x001.py
```

# API Usage Guide

## Public imports

The following imports must work:

```python
from unidecode import (
    Cache,
    UnidecodeError,
    unidecode,
    unidecode_expect_ascii,
    unidecode_expect_nonascii,
)
```

`Cache` is a mutable dictionary used by the lazy table loader.
`UnidecodeError` is a subclass of `ValueError` and has an `index` attribute.
When constructed as `UnidecodeError("message")`, its `index` is `None`.

## `unidecode_expect_ascii`

```python
def unidecode_expect_ascii(
    string: str,
    errors: str = "ignore",
    replace_str: str = "?",
) -> str:
```

Return the transliteration of `string`. This entry point first attempts an
ASCII fast path: an ASCII-only string is returned unchanged. If that attempt
fails, it uses the same block-table conversion as
`unidecode_expect_nonascii`.

## `unidecode_expect_nonascii`

```python
def unidecode_expect_nonascii(
    string: str,
    errors: str = "ignore",
    replace_str: str = "?",
) -> str:
```

Return the transliteration using the table conversion path directly. Its
observable output and error behavior are identical to
`unidecode_expect_ascii` for every input.

## `unidecode`

`unidecode` is the same function object as `unidecode_expect_ascii`, not a
wrapper around it.

## Exact transliteration examples

All three entry points must produce these results:

```python
unidecode("") == ""
unidecode("Hello, World!\r\n") == "Hello, World!\r\n"
unidecode("kožušček") == "kozuscek"
unidecode("ČŽŠčžš") == "CZSczs"
unidecode("příliš žluťoučký kůň pěl ďábelské ódy") == (
    "prilis zlutoucky kun pel dabelske ody"
)
unidecode("Κνωσός") == "Knosos"
unidecode("Привет мир!") == "Privet mir!"
unidecode("ア") == "a"
unidecode("こんにちは世界") == "konnichihaShi Jie "
unidecode("北京") == "Bei Jing "
unidecode("Hello, 世界!") == "Hello, Shi Jie !"
unidecode("Efﬁcient") == "Efficient"
unidecode("30 km/h ± 5%") == "30 km/h +- 5%"
unidecode("℉℃") == "degFdegC"
unidecode("𝐀𝐚𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗") == "Aa0123456789"
unidecode("ⓐⒶ⑳⒇⒛⓴⓾⓿") == "aA20(20)20.20100"
unidecode("ｔｈｅ ｑｕｉｃｋ") == "the quick"
```

ASCII code points U+0000 through U+007F are preserved exactly and the return
type is always `str`.

## Unmapped characters and errors

Private-use character U+F0000 is an example of an unmapped character. Error
policies apply once per unmapped input character:

- `errors="ignore"` drops it. This is the default.
- `errors="replace"` inserts `replace_str`, whose default is `"?"`.
- `errors="preserve"` retains the original character; this is the one mode
  whose result need not be ASCII.
- `errors="strict"` raises `UnidecodeError` at the first unmapped character.
  The exception `index` is the zero-based position in the original string and
  its message identifies the character and position.
- Any other `errors` value raises `UnidecodeError` when an unmapped character
  is encountered. Its `index` remains `None`.

Examples:

```python
text = "test \U000f0000 test"
unidecode(text) == "test  test"
unidecode(text, errors="replace") == "test ? test"
unidecode(text, errors="replace", replace_str="[?] ") == "test [?]  test"
unidecode(text, errors="preserve") == text

try:
    unidecode(text, errors="strict")
except UnidecodeError as error:
    assert error.index == 5
    assert error.__context__ is None
```

An isolated surrogate code point from U+D800 through U+DFFF has no mapping.
It emits one `RuntimeWarning` containing `"Surrogate character"`, then follows
the selected error policy. Under the default policy it therefore returns an
empty string.

# Lazy Tables And Cache

For a non-ASCII code point, use the high part `codepoint >> 8` as the table
section and the low byte as the table position. Section `1`, for example, is
loaded from `unidecode.x001`, whose module-level `data` sequence contains that
block's replacements.

Tables are loaded only on first use. Before transliterating a character from a
section, its `xNNN` module need not be imported. On first use, import the module
and store its `data` object in `Cache[section]`; later characters from that
section reuse the exact same cached object. If a section module does not exist,
store `None` for that section so later misses do not repeat the import. Clearing
`Cache` resets this loader state.

The following behavior is required in a fresh process:

```python
import sys
from unidecode import Cache, unidecode_expect_nonascii

Cache.clear()
assert "unidecode.x001" not in sys.modules
assert unidecode_expect_nonascii("Č") == "C"
assert "unidecode.x001" in sys.modules
first_table = Cache[1]
assert unidecode_expect_nonascii("Ž") == "Z"
assert Cache[1] is first_table

Cache.clear()
assert unidecode_expect_nonascii("\ua500") == ""
assert Cache[0xA5] is None
```

# Command-Line Interface

Both `python -m unidecode` and the installed `unidecode` console command call
`unidecode.util.main`.

```text
unidecode [-h] [-e ENCODING] [-c TEXT] [FILE]
```

- With `-c TEXT`, transliterate the command-line text and append one newline.
- With `FILE`, read that file as bytes, decode each line using `-e/--encoding`
  (or the locale-preferred encoding), and transliterate it.
- With neither `-c` nor `FILE`, read bytes from standard input using the same
  encoding rule.
- Using `-c` and `FILE` together writes `Can't use both FILE and -c option` to
  standard error and exits with status 1.
- A decoding failure writes a message beginning `Unable to decode input line`
  to standard error and exits with status 1.

For example, `unidecode -c 北京` prints `Bei Jing ` followed by a newline, and
UTF-8 standard input containing `革` produces `Ge `.

# Implementation Notes

- Keep transliteration deterministic and independent of locale except for the
  CLI's input decoding default.
- Mapping strings may contain multiple ASCII characters or trailing spaces.
- A table may contain fewer than 256 entries; an absent position is unmapped.
- Keep trusted tests out of the submitted repository. The repository may have
  its own tests, but grading installs the package and exercises it from a
  separate subprocess verifier.

# Examples

```python
from unidecode import unidecode

assert unidecode("ČŽŠ") == "CZS"
```

```python
from unidecode import unidecode

assert unidecode("test \U000f0000 test", errors="replace") == "test ? test"
```

# Error Handling and Boundary Conditions

ASCII characters pass through unchanged. Unmapped characters obey `ignore`,
`replace`, `preserve`, and `strict`; strict mode reports the original index.
Surrogates emit the documented warning before applying the selected policy,
and unknown table sections are cached as misses.
