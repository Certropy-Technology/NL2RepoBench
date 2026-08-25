# Emoji 2.15.0

## Project Description

Build an installable Python package named `emoji`. It converts a bounded set of
emoji short names to Unicode, converts Unicode back to names, reports emoji
locations and versions, and represents Unicode emoji matches. The package must
work without network access and must preserve Python string indexes, including
variation selectors, skin-tone modifiers, regional-indicator flags, keycaps,
and zero-width-joiner (ZWJ) sequences.

This task defines a finite compatibility surface. It does not require the full
Unicode emoji database beyond the entries and translations listed below.

## Supports

- Python 3.12.
- An installable `emoji` distribution with version `2.15.0`.
- A `pyproject.toml` build using setuptools. There are no third-party runtime
  dependencies.
- Package data may be Python, JSON, or another local format, but all required
  data must be included in the installed distribution.
- Public imports from `emoji`, `emoji.tokenizer`, and
  `emoji.unicode_codes` as documented below.
- Offline operation after installation.

The root module exposes these metadata values:

```python
emoji.__version__ == "2.15.0"
emoji.__author__ == "Taehoon Kim, Kevin Wurster"
"New BSD License" in emoji.__license__
```

Its `__all__` list, in order, is:

```python
[
    "emojize", "demojize", "analyze", "config", "emoji_list",
    "distinct_emoji_list", "emoji_count", "replace_emoji", "is_emoji",
    "purely_emoji", "version", "Token", "EmojiMatch", "EmojiMatchZWJ",
    "EmojiMatchZWJNonRGI", "EMOJI_DATA", "STATUS", "LANGUAGES",
]
```

## Required Data

`STATUS` and `LANGUAGES` are public constants:

```python
STATUS = {
    "component": 1,
    "fully_qualified": 2,
    "minimally_qualified": 3,
    "unqualified": 4,
}

LANGUAGES = [
    "en", "es", "ja", "ko", "pt", "it", "fr", "de",
    "fa", "id", "zh", "ru", "tr", "ar",
]
```

`EMOJI_DATA` is a dictionary keyed by Unicode emoji. Each required entry has
at least `en`, `E`, and `status`. `E` is numeric and `status` uses `STATUS`.
The following values form the required bounded data set:

| Unicode | English name | E | Extra contract |
| --- | --- | ---: | --- |
| `😁` | `:beaming_face_with_smiling_eyes:` | 0.6 | version lookup |
| `😀` | `:grinning_face:` | 1 | alias `:grinning:` |
| `👍` | `:thumbs_up:` | 0.6 | aliases include `:thumbsup:`; it is the preferred alias |
| `👍🏽` | `:thumbs_up_medium_skin_tone:` | 1 | one emoji spanning two code points |
| `❤️` | `:red_heart:` | 0.6 | alias `:heart:`, `variant=True` |
| `🐍` | `:snake:` | 0.6 | German `:schlange:` |
| `🦋` | `:butterfly:` | 3 | version name lookup |
| `🧠` | `:brain:` | 5 | version filtering |
| `🥣` | `:bowl_with_spoon:` | 5 | version filtering |
| `🦖` | `:T-Rex:` | 5 | name is case-sensitive |
| `🚀` | `:rocket:` | any numeric value | Spanish `:cohete:`, French `:fusée:`, Japanese `:ロケット:` |
| `🇫🇷` | `:France:` | 0.6 | one flag emoji spanning two code points |
| `1️⃣` | `:keycap_1:` | 0.6 | one keycap emoji spanning three code points |
| `👨‍👩‍👧‍👦` | `:family_man_woman_girl_boy:` | 2 | RGI ZWJ sequence |

Every table entry has `status == STATUS["fully_qualified"]`. The individual
people and toned people needed by the non-RGI sequence below use these names:
`:man:`, `:woman_dark_skin_tone:`, `:girl_light_skin_tone:`, and
`:boy_medium-dark_skin_tone:`.

## API Usage Guide

### Conversion

```python
def emojize(
    string: str,
    delimiters: tuple[str, str] = (":", ":"),
    variant: str | None = None,
    language: str = "en",
    version: float | None = None,
    handle_version=None,
) -> str: ...

def demojize(
    string: str,
    delimiters: tuple[str, str] = (":", ":"),
    language: str = "en",
    version: float | None = None,
    handle_version=None,
) -> str: ...
```

`emojize` replaces recognized delimited names and leaves unknown names
unchanged. Names are case-sensitive. Delimiters can contain more than one
character. Adjacent names are converted independently.

```python
emojize("Python :thumbs_up: :red_heart: :missing:")
# "Python 👍 ❤️ :missing:"
emojize("[[snake]]", delimiters=("[[", "]]")) == "🐍"
emojize(":thumbsup:", language="alias") == "👍"
emojize(":thumbsup:") == ":thumbsup:"
```

Supported language values are codes from `LANGUAGES`, plus `"alias"` for
`emojize`. The translations in the data table convert in both directions.
For `demojize(..., language="alias")`, `👍` becomes `:thumbsup:`. An unknown
language raises `NotImplementedError`.

For emoji that support presentation variants, `variant=None` uses the stored
form, `"text_type"` ends in U+FE0E, and `"emoji_type"` ends in U+FE0F.
Therefore the red-heart outputs are `❤️`, `❤︎`, and `❤️`, respectively. Any
other non-`None` variant raises `ValueError` when a recognized variant-capable
name is converted.

When `version` is supplied, `emojize` converts only entries whose `E` is at
most that value. `demojize` names only entries whose `E` is at most that value.
A newer entry is removed unless `handle_version` is supplied. A string handler
is inserted literally. A callable handler receives `(unicode_emoji, data)`;
`data` is a copy of the entry plus `match_start` and `match_end` code-point
indexes for the original input.

```python
emojize(":bowl_with_spoon:", version=4) == ""
emojize(":bowl_with_spoon:", version=5) == "🥣"
demojize("A 🦖 B", version=3) == "A  B"
demojize("A 🦖 B", version=5) == "A :T-Rex: B"
```

### Analysis and Replacement

```python
def replace_emoji(string: str, replace="", version: float = -1) -> str: ...
def emoji_list(string: str) -> list[dict[str, object]]: ...
def distinct_emoji_list(string: str) -> list[str]: ...
def emoji_count(string: str, unique: bool = False) -> int: ...
def is_emoji(string: str) -> bool: ...
def purely_emoji(string: str) -> bool: ...
def version(string: str) -> float: ...
```

`replace_emoji` replaces every recognized emoji when `version == -1`. For a
non-negative threshold, it replaces only emoji whose `E` is greater than the
threshold. `replace` may be a string or a callable with the same
`(unicode_emoji, copied_data_with_match_indexes)` convention described above.

```python
replace_emoji("A 🐍 meets 🧠") == "A  meets "
replace_emoji("A 🐍 meets 🧠", "X") == "A X meets X"
replace_emoji("A 🐍 meets 🧠", "N", version=3) == "A 🐍 meets N"
```

`emoji_list` returns one dictionary per emoji in input order with keys
`emoji`, `match_start`, and `match_end`. Indexes are Python string code-point
offsets and `match_end` is exclusive. Complete modifier, flag, keycap, and RGI
ZWJ sequences count as one emoji. `distinct_emoji_list` removes duplicates;
its ordering is unspecified. `emoji_count(..., unique=True)` counts distinct
values.

`is_emoji` is true only when the entire string is one RGI entry.
`purely_emoji` is true when analysis finds no non-emoji tokens; by this
definition it is also true for the empty string.

`version` accepts an exact Unicode emoji, a short name, or text containing an
emoji/name and returns the first recognized entry's `E`. It recognizes aliases
and the listed language names. It raises `ValueError` if no emoji is found.

### Tokens and Match Objects

```python
def analyze(
    string: str, non_emoji: bool = False, join_emoji: bool = True
): ...

class Token(NamedTuple):
    chars: str
    value: str | EmojiMatch

class EmojiMatch:
    def __init__(self, emoji: str, start: int, end: int, data): ...
    def data_copy(self) -> dict: ...
    def is_zwj(self) -> bool: ...
    def split(self): ...
```

`analyze` yields `Token` objects. By default it yields emoji only. With
`non_emoji=True`, each ordinary code point is also yielded as
`Token(character, character)`. Match objects expose `emoji`, `start`, `end`,
and `data`. Their `data_copy()` adds `match_start` and `match_end` without
mutating shared metadata. `repr(EmojiMatch("😀", 2, 3, ...))` is
`"EmojiMatch(😀, 2:3)"`.

For `👨‍👩‍👧‍👦`, analysis yields one `EmojiMatch` spanning indexes 0 through 7.
It reports `is_zwj() == True`. Calling `split()` returns an `EmojiMatchZWJ`
whose `emojis` contain `👨`, `👩`, `👧`, and `👦` at spans 0:1, 2:3, 4:5,
and 6:7; `join()` reconstructs the original sequence.

`emoji.tokenizer.tokenize(string, keep_zwj)` is public and yields all text and
emoji tokens while choosing the longest recognized sequence. Variation
selectors belong to the emoji token rather than becoming separate text.

### Non-RGI ZWJ Configuration

`config.demojize_keep_zwj` defaults to `True`. For the non-RGI sequence
`👨‍👩🏿‍👧🏻‍👦🏾`, keeping ZWJs produces:

```text
:man:‍:woman_dark_skin_tone:‍:girl_light_skin_tone:‍:boy_medium-dark_skin_tone:
```

The characters between names in that line are U+200D. The result round-trips
through `emojize`. When the setting is `False`, those U+200D characters are
removed. `analyze(..., join_emoji=True)` returns one
`EmojiMatchZWJNonRGI`; `join_emoji=False` returns the four constituent emoji
matches. `config.replace_emoji_keep_zwj` is also available and defaults to
`False`.

### Direct Lookup and Language Loading

```python
from emoji.unicode_codes import get_emoji_by_name, load_from_json

get_emoji_by_name(":snake:", "en") == "🐍"
get_emoji_by_name(":thumbsup:", "alias") == "👍"
get_emoji_by_name(":missing:", "en") is None
```

Lookup is case-sensitive and only fully-qualified entries are returned.
`config.load_language(language)` accepts one language code, a list of codes,
or `None` for all languages. Loading an already loaded language is a no-op and
returns `None`. `load_from_json` and `config.load_language` raise
`NotImplementedError` for an unsupported code.

## Implementation Notes

- Unicode positions are Python string indexes, not UTF-8 byte offsets.
- A modifier sequence, regional-indicator pair, keycap sequence, or recognized
  RGI ZWJ sequence must use longest-match tokenization.
- Conversion and analysis must be deterministic. The only ordering explicitly
  left unspecified is `distinct_emoji_list`.
- Candidate code must not need network access or write outside its normal
  installation and runtime locations.
