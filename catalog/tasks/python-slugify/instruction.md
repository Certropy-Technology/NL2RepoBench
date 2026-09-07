# python-slugify

## Project Description

Build an installable `python-slugify` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `python-slugify`; public import package begins at `slugify`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Core API`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `1. Module Import`: preserve the documented object or module behavior, including state and side effects.
3. `2. slugify() Function - Unicode String Slugification`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `3. smart_truncate() Function - Intelligent String Truncation`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.10 on the pinned Linux image.
- Distribution identity: `python-slugify`; public import package begins at `slugify`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- No third-party runtime package is declared by the local task metadata; standard-library support is sufficient unless the API section says otherwise.
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── MANIFEST.in
├── README.md
├── format.sh
├── setup.py
├── slugify
│   ├── __init__.py
│   ├── __main__.py
│   ├── __version__.py
│   ├── py.typed
│   ├── slugify.py
│   ├── special.py
├── tea.yaml
└── slugify
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

### Core API

#### 1. Module Import

```python
from slugify import slugify, smart_truncate, DEFAULT_SEPARATOR
from slugify.special import PRE_TRANSLATIONS, CYRILLIC, GERMAN, GREEK
from slugify.__main__ import slugify_params, parse_args
```

#### 2. slugify() Function - Unicode String Slugification

**Function**: Convert any Unicode text into a URL-friendly slug format.

**Function Signature**:
```python
def slugify(
    text: str,
    entities: bool = True,
    decimal: bool = True,
    hexadecimal: bool = True,
    max_length: int = 0,
    word_boundary: bool = False,
    separator: str = DEFAULT_SEPARATOR,
    save_order: bool = False,
    stopwords: Iterable[str] = (),
    regex_pattern: re.Pattern[str] | str | None = None,
    lowercase: bool = True,
    replacements: Iterable[Iterable[str]] = (),
    allow_unicode: bool = False,
) -> str:
```

**Parameter Description**:
- `text` (str): The text string to be converted.
- `entities` (bool): Whether to convert HTML entities to Unicode, default is True.
- `decimal` (bool): Whether to convert HTML decimal encodings, default is True.
- `hexadecimal` (bool): Whether to convert HTML hexadecimal encodings, default is True.
- `max_length` (int): The maximum length of the output string, 0 means no limit.
- `word_boundary` (bool): Whether to truncate at word boundaries, default is False.
- `separator` (str): The separator between words, default is "-".
- `save_order` (bool): Whether to maintain the original order of words, default is False.
- `stopwords` (Iterable[str]): The list of stopwords to be filtered.
- `regex_pattern` (str): The custom regular expression pattern.
- `lowercase` (bool): Whether to convert to lowercase, default is True.
- `replacements` (Iterable[Iterable[str]]): The custom replacement rules, such as [['|', 'or'], ['%', 'percent']].
- `allow_unicode` (bool): Whether to allow Unicode characters, default is False.

**Return Value**: The converted slug string.

#### 3. smart_truncate() Function - Intelligent String Truncation

**Function**: Intelligently truncate a string, supporting word boundaries and order preservation.

**Function Signature**:
```python
def smart_truncate(
    string: str,
    max_length: int = 0,
    word_boundary: bool = False,
    separator: str = " ",
    save_order: bool = False,
) -> str:
```

**Parameter Description**:
- `string` (str): The string to be truncated.
- `max_length` (int): The maximum length, 0 means no truncation.
- `word_boundary` (bool): Whether to truncate at word boundaries.
- `separator` (str): The word separator.
- `save_order` (bool): Whether to maintain the original order of words.

**Return Value**: The truncated string.

#### 4. parse_args() Function - Command Line Parameter Parsing

**Function**: Parse command line parameters and return a dictionary of parameters.

**Function Signature**:
```python
def parse_args() -> dict[str, Any]:
```

**Return Value**: A dictionary of parameters.

#### 5. slugify_params() Function - Command Line Parameter Validation

**Function**: Validate command line parameters and return a dictionary of parameters.

**Function Signature**:
```python
def slugify_params(args: argparse.Namespace) -> dict[str, Any]:
```

**Return Value**: A dictionary of parameters.

#### 6. main() Function - Main Function

**Function**: Main function to run the program.

**Function Signature**:
```python
def main(argv: list[str] | None = None):
```

**Return Value**: None.

#### 7. Constants and Type Aliases

```python

# In __version__.py
__title__ = 'python-slugify'
__author__ = 'Val Neekman'
__author_email__ = 'info@neekware.com'
__description__ = 'A Python slugify application that also handles Unicode'
__url__ = 'https://github.com/un33k/python-slugify'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022 Val Neekman @ Neekware Inc.'
__version__ = '8.0.4'

# In slugify.py

__all__ = ['slugify', 'smart_truncate']

CHAR_ENTITY_PATTERN = re.compile(r'&(%s);' % '|'.join(name2codepoint))
DECIMAL_PATTERN = re.compile(r'&#(\d+);')
HEX_PATTERN = re.compile(r'&#x([\da-fA-F]+);')
QUOTE_PATTERN = re.compile(r'[\']+')
DISALLOWED_CHARS_PATTERN = re.compile(r'[^-a-zA-Z0-9]+')
DISALLOWED_UNICODE_CHARS_PATTERN = re.compile(r'[\W_]+')
DUPLICATE_DASH_PATTERN = re.compile(r'-{2,}')
NUMBERS_PATTERN = re.compile(r'(?<=\d),(?=\d)')
DEFAULT_SEPARATOR = '-'

# In special.py
_CYRILLIC = [      # package defaults:
    (u'ё', u'e'),    # io / yo
    (u'я', u'ya'),   # ia
    (u'х', u'h'),    # kh
    (u'у', u'y'),    # u
    (u'щ', u'sch'),  # sch
    (u'ю', u'u'),    # iu / yu
]
CYRILLIC = add_uppercase_char(_CYRILLIC)

_GERMAN = [        # package defaults:
    (u'ä', u'ae'),   # a
    (u'ö', u'oe'),   # o
    (u'ü', u'ue'),   # u
]
GERMAN = add_uppercase_char(_GERMAN)

_GREEK = [         # package defaults:
    (u'χ', u'ch'),   # kh
    (u'Ξ', u'X'),    # Ks
    (u'ϒ', u'Y'),    # U
    (u'υ', u'y'),    # u
    (u'ύ', u'y'),
    (u'ϋ', u'y'),
    (u'ΰ', u'y'),
]
GREEK = add_uppercase_char(_GREEK)

# Pre translations
PRE_TRANSLATIONS = CYRILLIC + GERMAN + GREEK
```
### Special Character Processing Module

#### 1. Predefined Character Conversion Rules

```python
# Russian character conversion
CYRILLIC = [
    ('ё', 'e'), ('я', 'ya'), ('х', 'h'),
    ('у', 'y'), ('щ', 'sch'), ('ю', 'u')
]

# German character conversion
GERMAN = [
    ('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue')
]

# Greek character conversion
GREEK = [
    ('χ', 'ch'), ('Ξ', 'X'), ('ϒ', 'Y'),
    ('υ', 'y'), ('ύ', 'y'), ('ϋ', 'y'), ('ΰ', 'y')
]

# All predefined conversion rules
PRE_TRANSLATIONS = CYRILLIC + GERMAN + GREEK
```

#### 2. add_uppercase_char() Function

**Function**: Add uppercase character versions to the character conversion list.

**Function Signature**:
```python
def add_uppercase_char(char_list: list[tuple[str, str]]) -> list[tuple[str, str]]:
```

### Practical Usage Patterns

#### Basic Usage

```python
from slugify import slugify

# Simple text conversion
txt = "This is a test ---"
result = slugify(txt)
# Output: "this-is-a-test"

# Chinese text conversion
txt = "影師嗎"
result = slugify(txt)
# Output: "ying-shi-ma"

# French text conversion
txt = "C'est déjà l'été."
result = slugify(txt)
# Output: "c-est-deja-l-ete"

# Russian text conversion
txt = "Компьютер"
result = slugify(txt)
# Output: "kompiuter"
```

#### Advanced Configuration Usage

```python
from slugify import slugify

# Custom separator
txt = "jaja---lol-méméméoo--a"
result = slugify(txt, separator=".", max_length=20, word_boundary=True)
# Output: "jaja.lol.mememeoo.a"

# Stopword filtering
txt = "the quick brown fox jumps over the lazy dog"
result = slugify(txt, stopwords=['the', 'in', 'a', 'hurry'])
# Output: "quick-brown-fox-jumps-over-lazy-dog"

# Custom replacement rules
txt = "10 | 20 %"
result = slugify(txt, replacements=[['|', 'or'], ['%', 'percent']])
# Output: "10-or-20-percent"

# Regular expression pattern
txt = "___This is a test___"
result = slugify(txt, regex_pattern=r'[^-a-z0-9_]+')
# Output: "___this-is-a-test___"

# Allow Unicode characters
txt = "i love 🦄"
result = slugify(txt, allow_unicode=True)
# Output: "i-love"
```

#### Smart Truncation Usage

```python
from slugify import smart_truncate

# Basic truncation
txt = "jaja---lol-méméméoo--a"
result = smart_truncate(txt, max_length=15, word_boundary=True)
# Output: "jaja-lol-a"

# Truncate while maintaining order
txt = "one two three four five"
result = smart_truncate(txt, max_length=13, word_boundary=True, save_order=True)
# Output: "one-two-three"
```

### Supported Text Types

- **Unicode Character Types**: Chinese, Russian, French, German, Greek, etc.
- **HTML Encoding Types**: HTML entities, decimal encoding, hexadecimal encoding
- **Special Character Handling**: Punctuation marks, numbers, quotation marks, repeated characters

### Error Handling

The system provides a comprehensive error handling mechanism:
- **Encoding Fault Tolerance**: Automatically handle various encoding formats
- **Character Normalization**: Standardize Unicode character formats
- **Fallback Mechanism**: Multiple conversion strategies ensure maximum compatibility
- **Exception Capture**: Gracefully handle conversion failures

### Important Notes

1. **Unicode Handling**: By default, Unicode characters are converted to ASCII. You can retain them by setting `allow_unicode=True`.
2. **Case Sensitivity**: By default, the text is converted to lowercase. You can keep the original case by setting `lowercase=False`.
3. **Separator Handling**: By default, "-" is used as the separator, which can be customized.
4. **Length Limit**: Supports maximum length limit and word boundary truncation.
5. **Stopword Filtering**: Supports customizing the stopword list.
6. **Replacement Rules**: Supports user-defined character replacement rules.

## Detailed Function Implementation Nodes

### Node 1: Unicode Character Normalization

**Function Description**: Process various Unicode characters and standardize them into ASCII-formatted URL-friendly strings. Support complex scenarios such as multi-language character conversion, character normalization, and encoding processing.

**Core Algorithms**:
- Unicode character normalization (NFKC/NFKD)
- Multi-language character transliteration conversion
- HTML entity decoding processing
- Character encoding fault tolerance processing

**Input-Output Examples**:

```python
from slugify import slugify

# Chinese text conversion
txt = '影師嗎'
result = slugify(txt)
# Output: "ying-shi-ma"

# Russian text conversion
txt = 'Компьютер'
result = slugify(txt)
# Output: "kompiuter"

# French text conversion
txt = 'C'est déjà l'été.'
result = slugify(txt)
# Output: "c-est-deja-l-ete"

# German text conversion
txt = 'ÜBER Über German Umlaut'
result = slugify(txt, replacements=[['Ü', 'UE'], ['ü', 'ue']])
# Output: "ueber-ueber-german-umlaut"
```

### Node 2: HTML Entity Parsing

**Function Description**: Intelligently parse HTML entity encodings, including named entities, decimal encodings, and hexadecimal encodings, and convert them to corresponding Unicode characters.

**Core Algorithms**:
- HTML named entity parsing (&amp; → &)
- Decimal encoding parsing (&#381; → Ž)
- Hexadecimal encoding parsing (&#x17D; → Ž)
- Encoding fault tolerance processing

**Input-Output Examples**:

```python
from slugify import slugify

# HTML named entity
txt = 'foo &amp; bar'
result = slugify(txt)
# Output: "foo-bar"

# Decimal encoding
txt = '&#381;'
result = slugify(txt, decimal=True)
# Output: "z"

# Hexadecimal encoding
txt = '&#x17D;'
result = slugify(txt, hexadecimal=True)
# Output: "z"

# Disable entity parsing
txt = 'foo &amp; bar'
result = slugify(txt, entities=False)
# Output: "foo-amp-bar"
```

### Node 3: Special Character Processing

**Function Description**: Intelligently handle special characters such as punctuation marks, numbers, and quotation marks, and automatically convert them to separators or retain valid characters.

**Core Algorithms**:
- Convert punctuation marks to separators
- Retain numeric characters
- Clean up quotation marks
- Merge repeated separators

**Input-Output Examples**:

```python
from slugify import slugify

# Punctuation mark handling
txt = "This -- is a ## test ---"
result = slugify(txt)
# Output: "this-is-a-test"

# Number handling
txt = '10 amazing secrets'
result = slugify(txt)
# Output: "10-amazing-secrets"

# Numbers and symbols
txt = '1,000 reasons you are #1'
result = slugify(txt)
# Output: "1000-reasons-you-are-1"

# Quotation mark handling
txt = "___This is a test___"
result = slugify(txt)
# Output: "this-is-a-test"
```

### Node 4: Length Limitation and Truncation

**Function Description**: Support maximum length limit and smart truncation, including word boundary truncation and order preservation.

**Core Algorithms**:
- Maximum length limit check
- Smart word boundary truncation
- Original order preservation
- Separator handling

**Input-Output Examples**:

```python
from slugify import slugify

# Basic length limit
txt = 'jaja---lol-méméméoo--a'
result = slugify(txt, max_length=9)
# Output: "jaja-lol"

# Word boundary truncation
txt = 'jaja---lol-méméméoo--a'
result = slugify(txt, max_length=15, word_boundary=True)
# Output: "jaja-lol-a"

# Truncate while maintaining order
txt = 'one two three four five'
result = slugify(txt, max_length=13, word_boundary=True, save_order=True)
# Output: "one-two-three"
```

### Node 5: Custom Separator

**Function Description**: Support customizing the separator between words, including single-character and multi-character separators.

**Core Algorithms**:
- Separator replacement processing
- Support for multi-character separators
- Separator boundary processing

**Input-Output Examples**:

```python
from slugify import slugify

# Custom separator
txt = 'jaja---lol-méméméoo--a'
result = slugify(txt, separator=".", max_length=20, word_boundary=True)
# Output: "jaja.lol.mememeoo.a"

# Multi-character separator
txt = 'jaja---lol-méméméoo--a'
result = slugify(txt, separator="ZZZZZZ", max_length=20, word_boundary=True)
# Output: "jajaZZZZZZlolZZZZZZmememeooZZZZZZa"
```

### Node 6: Stopword Filtering

**Function Description**: Support customizing the stopword list and automatically filter specified words. Support both case-sensitive and case-insensitive modes.

**Core Algorithms**:
- Stopword list matching
- Case sensitivity processing
- Support for multiple stopwords
- Separator compatibility processing

**Input-Output Examples**:

```python
from slugify import slugify

# Basic stopword filtering
txt = 'this has a stopword'
result = slugify(txt, stopwords=['stopword'])
# Output: "this-has-a"

# Multiple stopword filtering
txt = 'the quick brown fox jumps over the lazy dog in a hurry'
result = slugify(txt, stopwords=['the', 'in', 'a', 'hurry'])
# Output: "quick-brown-fox-jumps-over-lazy-dog"

# Case sensitivity
txt = 'thIs Has a stopword Stopword'
result = slugify(txt, stopwords=['Stopword'], lowercase=False)
# Output: "thIs-Has-a-stopword"
```

### Node 7: Custom Replacement Rules

**Function Description**: Support user-defined character replacement rules to achieve flexible character conversion and symbol replacement. Replacement rules are applied twice: once at the beginning (before text processing) and once at the end (after all processing but before truncation), ensuring consistent replacement behavior.

**Core Algorithms**:
- Apply replacement rules before text normalization
- Process multiple rules sequentially
- Replace special characters
- Handle emojis
- Re-apply replacements after processing to ensure consistency

**Input-Output Examples**:

```python
from slugify import slugify

# Basic replacement rules
txt = '10 | 20 %'
result = slugify(txt, replacements=[['|', 'or'], ['%', 'percent']])
# Output: "10-or-20-percent"

# Emoji replacement
txt = 'I ♥ 🦄'
result = slugify(txt, replacements=[['♥', 'amour'], ['🦄', 'licorne']])
# Output: "i-amour-licorne"

# German umlauts
txt = 'ÜBER Über German Umlaut'
result = slugify(txt, replacements=[['Ü', 'UE'], ['ü', 'ue']])
# Output: "ueber-ueber-german-umlaut"
```

### Node 8: Regular Expression Pattern

**Function Description**: Support customizing regular expression patterns to achieve precise character filtering and retention control. The regex pattern determines which characters are replaced with the default separator ('-'). If a custom separator is used, it replaces the default separator after pattern matching. Note: When using a custom separator that conflicts with characters allowed by the regex pattern, the behavior may not be as expected - the caller must ensure the separator doesn't clash with the regex pattern.

**Core Algorithms**:
- Regular expression matching (replaces non-matching characters with default separator)
- Character retention control
- Separator replacement after pattern matching
- Pattern priority

**Input-Output Examples**:

```python
from slugify import slugify

# Retain underscores (regex allows underscores, spaces are replaced with dashes)
txt = "___This is a test___"
result = slugify(txt, regex_pattern=r'[^-a-z0-9_]+')
# Output: "___this-is-a-test___"

# Custom pattern with underscore separator (note: may not work as expected due to pattern conflict)
txt = "___This is a test___"
result = slugify(txt, separator='_', regex_pattern=r'[^-a-z0-9_]+')
# Output: May not be "_this_is_a_test_" due to pattern/separator interaction
```

### Node 9: Unicode Character Preservation

**Function Description**: Support retaining Unicode characters, allowing the original Unicode characters to be retained in the slug without conversion to ASCII. When `allow_unicode=True`, the function uses NFKC normalization instead of NFKD and skips the ASCII transliteration step, preserving Unicode characters while still normalizing them.

**Core Algorithms**:
- Unicode character detection
- Character retention control (NFKC normalization instead of NFKD + transliteration)
- Emoji handling (emojis are still removed by the disallowed pattern)
- Encoding compatibility

**Input-Output Examples**:

```python
from slugify import slugify

# Retain Unicode characters
txt = 'C'est déjà l'été.'
result = slugify(txt, allow_unicode=True)
# Output: "c-est-déjà-l-été"

# Retain Chinese Unicode (preserved as-is, not transliterated)
txt = '影師嗎'
result = slugify(txt, allow_unicode=True)
# Output: "影師嗎"

# Emoji handling (emojis are removed even with allow_unicode=True)
txt = 'i love 🦄'
result = slugify(txt, allow_unicode=True)
# Output: "i-love"
```

### Node 10: Case Control

**Function Description**: Support case conversion control, either keeping the original case or converting to lowercase uniformly.

**Core Algorithms**:
- Case detection
- Conversion control
- Stopword case matching
- Character normalization

**Input-Output Examples**:

```python
from slugify import slugify

# Default lowercase conversion
txt = 'This Is A Test'
result = slugify(txt)
# Output: "this-is-a-test"

# Keep the original case
txt = 'thIs Has a stopword Stopword'
result = slugify(txt, stopwords=['Stopword'], lowercase=False)
# Output: "thIs-Has-a-stopword"

# Case-sensitive stopwords
txt = 'Foo A FOO B foo C'
result = slugify(txt, stopwords=['foo'])
# Output: "a-b-c"
```

### Node 11: Smart Truncation Utility

**Function Description**: Provide an independent smart truncation function that supports word boundary truncation and order preservation. The function operates on already-processed strings and requires the separator parameter to match the actual separator used in the input string. If the separator is not found in the string, it will truncate at the max_length position without word boundary consideration.

**Core Algorithms**:
- Length calculation
- Word boundary detection (requires separator to be present in string)
- Order preservation logic
- Separator handling (default separator is space " ")

**Input-Output Examples**:

```python
from slugify import smart_truncate

# Basic truncation with dash separator (must specify separator parameter)
txt = 'jaja-lol-mememeoo-a'
result = smart_truncate(txt, max_length=15, word_boundary=True, separator='-')
# Output: "jaja-lol-a"

# Truncate while maintaining order (space is default separator)
txt = 'one two three four five'
result = smart_truncate(txt, max_length=13, word_boundary=True, save_order=True)
# Output: "one two three"

# When separator not found in string, truncates at max_length
txt = '1,000 reasons you are #1'
result = smart_truncate(txt, max_length=10, separator='_')
# Output: "1,000 reas"
```

### Node 12: Command Line Interface

**Function Description**: Provide a complete command-line tool that supports reading text from standard input or command-line parameters and all the parameter options of the slugify function.

**Core Algorithms**:
- Parameter parsing processing
- Standard input reading
- Error handling mechanism
- Parameter validation

**Input-Output Examples**:

```bash
# Basic command-line usage
$ slugify "This is a test"
# Output: "this-is-a-test"

# Read from standard input
$ echo "Taking input from STDIN" | slugify --stdin
# Output: "taking-input-from-stdin"

# Custom parameters
$ slugify --stopwords the in a hurry -- "the quick brown fox jumps over the lazy dog in a hurry"
# Output: "quick-brown-fox-jumps-over-lazy-dog"

# Replacement rules
$ slugify --replacements "|->or" "%%->percent" -- "10 | 20 %"
# Output: "10-or-20-percent"
```

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
backports.tarfile  1.2.0
certifi            2025.8.3
cffi               1.17.1
charset-normalizer 3.4.2
colorama           0.4.6
cryptography       45.0.6
docutils           0.22
exceptiongroup     1.3.0
flake8             4.0.1
idna               3.10
importlib_metadata 8.7.0
iniconfig          2.1.0
jaraco.classes     3.4.0
jaraco.context     6.0.1
jaraco.functools   4.2.1
jeepney            0.9.0
keyring            25.6.0
mccabe             0.6.1
more-itertools     10.7.0
nh3                0.3.0
packaging          25.0
pip                23.0.1
pkginfo            1.12.1.2
pluggy             1.6.0
pycodestyle        2.8.0
pycparser          2.22
pyflakes           2.4.0
Pygments           2.19.2
pytest             8.4.1
readme_renderer    44.0
requests           2.32.4
requests-toolbelt  1.0.0
rfc3986            2.0.0
SecretStorage      3.3.3
setuptools         65.5.1
text-unidecode     1.3
tomli              2.2.1
tqdm               4.67.1
twine              3.4.1
typing_extensions  4.14.1
urllib3            2.5.0
wheel              0.40.0
zipp               3.23.0
```

### Example 2: ordinary usage
```text
workspace/
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── MANIFEST.in
├── README.md
├── format.sh
├── setup.py
├── slugify
│   ├── __init__.py
│   ├── __main__.py
│   ├── __version__.py
│   ├── py.typed
│   ├── slugify.py
│   ├── special.py
├── tea.yaml
└── slugify
```

### Example 3: boundary or error behavior
```text
from slugify import slugify, smart_truncate, DEFAULT_SEPARATOR
from slugify.special import PRE_TRANSLATIONS, CYRILLIC, GERMAN, GREEK
from slugify.__main__ import slugify_params, parse_args
```

### Example 4: boundary or error behavior
```text
def slugify(
    text: str,
    entities: bool = True,
    decimal: bool = True,
    hexadecimal: bool = True,
    max_length: int = 0,
    word_boundary: bool = False,
    separator: str = DEFAULT_SEPARATOR,
    save_order: bool = False,
    stopwords: Iterable[str] = (),
    regex_pattern: re.Pattern[str] | str | None = None,
    lowercase: bool = True,
    replacements: Iterable[Iterable[str]] = (),
    allow_unicode: bool = False,
) -> str:
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
