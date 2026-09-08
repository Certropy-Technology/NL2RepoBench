# Project Description

The `inflection` package is a Python port of Ruby on Rails' inflector, providing string transformation utilities commonly used in web frameworks and ORMs. It transforms words between singular and plural forms, converts strings between different naming conventions (CamelCase, snake_case), and provides other text processing utilities.

Target users are Python developers building web applications, ORMs, code generators, or any system requiring consistent naming conventions across different contexts. The package operates purely on string inputs and returns string outputs, with no external dependencies, database access, or network communication.

Core capabilities: pluralization/singularization following English grammar rules, case conversions (camelCase, snake_case, dash-case), humanization of technical names, and ordinal number formatting.

Explicitly excluded: non-English language support, custom inflection rule registration beyond the built-in irregular forms, and dynamic locale-based transformations.

# Natural Language Instruction

Build a Python package named `inflection` that provides the following string transformation capabilities:

1. **Pluralization and Singularization**: Convert words between singular and plural forms following English grammar rules, handling regular patterns (box→boxes, category→categories) and common irregular forms (person→people, child→children, mouse→mice).

2. **Case Conversions**: Transform strings between naming conventions including CamelCase (DeviceType), lowerCamelCase (deviceType), snake_case (device_type), and dash-case (device-type).

3. **Humanization**: Convert technical identifiers into human-readable text by capitalizing the first word, converting underscores to spaces, and removing trailing "_id" suffixes.

4. **Parameterization**: Transform strings into URL-safe formats by removing special characters, transliterating Unicode characters, and joining with a separator.

5. **Ordinal Formatting**: Convert integers to ordinal strings (1→"1st", 2→"2nd", 3→"3rd", 4→"4th").

6. **Tableization**: Convert class names to database table names using pluralization and snake_case conventions.

The package name is `inflection`, importable as `import inflection`, and must be installable via `pip install -e .` from a workspace containing `setup.py` or `pyproject.toml`. All functions operate deterministically on string inputs with no side effects, no global state modifications, and no network access. The implementation must handle Unicode strings correctly and preserve case sensitivity where appropriate.

# Environment Configuration

- **Language**: Python 3.12
- **Package Manager**: pip
- **Installation**: `python -m pip install --no-build-isolation --no-deps --no-index -e .`
- **Build Backend**: setuptools (preinstalled in base image)
- **Runtime Dependencies**: None (stdlib only)
- **Development Dependencies**: None required for installation
- **Network Access**: Prohibited during agent, candidate, verifier, and Oracle execution
- **Platform**: Debian 12 (amd64), Python 3.12

The package uses setuptools for installation and has no external runtime dependencies. All dependencies are preinstalled during the Docker image build phase.

# Project Directory Structure

```
workspace/
├── inflection/
│   ├── __init__.py          # Main module with all public functions
│   └── py.typed             # PEP 561 marker for type checking
├── setup.py                 # setuptools configuration
└── LICENSE                  # MIT license file
```

The `inflection/` directory contains the single-module package. All public API functions are defined in `inflection/__init__.py` and are directly importable as `from inflection import function_name` or accessed via `inflection.function_name` after `import inflection`.

# API Usage Guide

All functions are available directly from the `inflection` module:

```python
import inflection
```

## Core Functions

### `camelize(string: str, uppercase_first_letter: bool = True) -> str`

Convert strings to CamelCase.

- **Parameters**:
  - `string`: Input string with underscores or mixed case
  - `uppercase_first_letter`: If `True`, produces UpperCamelCase; if `False`, produces lowerCamelCase (default: `True`)
- **Returns**: CamelCase string
- **Behavior**: Converts underscores to word boundaries and capitalizes each word. With `uppercase_first_letter=False`, the first letter is lowercase.

```python
inflection.camelize("device_type")              # "DeviceType"
inflection.camelize("device_type", False)       # "deviceType"
inflection.camelize("http_server")              # "HttpServer"
```

### `underscore(word: str) -> str`

Convert CamelCase or mixed-case strings to snake_case.

- **Parameters**: `word` - Input string in CamelCase or mixed format
- **Returns**: Lowercase string with underscores between words
- **Behavior**: Inserts underscores before uppercase letters that follow lowercase letters or digits, replaces hyphens with underscores, and converts to lowercase.

```python
inflection.underscore("DeviceType")             # "device_type"
inflection.underscore("IOError")                # "io_error"
inflection.underscore("HTTPServer")             # "http_server"
```

### `dasherize(word: str) -> str`

Replace underscores with dashes.

- **Parameters**: `word` - Input string
- **Returns**: String with underscores replaced by dashes
- **Behavior**: Simple character replacement of `_` to `-`

```python
inflection.dasherize("puni_puni")               # "puni-puni"
inflection.dasherize("my_variable_name")        # "my-variable-name"
```

### `humanize(word: str) -> str`

Convert technical identifiers to human-readable text.

- **Parameters**: `word` - Input string, typically a snake_case identifier
- **Returns**: Capitalized human-readable string
- **Behavior**: Removes trailing "_id" suffix, replaces underscores with spaces, converts to lowercase, then capitalizes the first letter.

```python
inflection.humanize("employee_salary")          # "Employee salary"
inflection.humanize("author_id")                # "Author"
inflection.humanize("first_name")               # "First name"
```

### `titleize(word: str) -> str`

Convert strings to title case with all words capitalized.

- **Parameters**: `word` - Input string
- **Returns**: Title case string with each word capitalized
- **Behavior**: Applies `underscore` and `humanize` transformations, then capitalizes each word including words after special characters.

```python
inflection.titleize("man from the boondocks")   # "Man From The Boondocks"
inflection.titleize("x-men: the last stand")    # "X Men: The Last Stand"
inflection.titleize("TheManWithoutAPast")       # "The Man Without A Past"
```

### `pluralize(word: str) -> str`

Return the plural form of a word.

- **Parameters**: `word` - Singular noun (case-sensitive)
- **Returns**: Plural form of the word
- **Behavior**: Applies English pluralization rules including regular patterns (s, es, ies) and irregular forms. Uncountable words (fish, sheep, information) return unchanged. Preserves case in the result.

```python
inflection.pluralize("post")                    # "posts"
inflection.pluralize("octopus")                 # "octopi"
inflection.pluralize("sheep")                   # "sheep"
inflection.pluralize("person")                  # "people"
inflection.pluralize("CamelOctopus")            # "CamelOctopi"
```

### `singularize(word: str) -> str`

Return the singular form of a word.

- **Parameters**: `word` - Plural noun (case-sensitive)
- **Returns**: Singular form of the word
- **Behavior**: Reverses pluralization. Handles regular patterns and irregular forms. Uncountable words return unchanged.

```python
inflection.singularize("posts")                 # "post"
inflection.singularize("octopi")                # "octopus"
inflection.singularize("sheep")                 # "sheep"
inflection.singularize("people")                # "person"
```

### `ordinal(number: int) -> str`

Return the ordinal suffix for a number.

- **Parameters**: `number` - Integer (negative values are converted to absolute)
- **Returns**: Ordinal suffix string: "st", "nd", "rd", or "th"
- **Behavior**: Returns appropriate suffix based on the last one or two digits. Handles special cases for 11, 12, 13 (all "th"). Uses absolute value of negative numbers.

```python
inflection.ordinal(1)                           # "st"
inflection.ordinal(2)                           # "nd"
inflection.ordinal(3)                           # "rd"
inflection.ordinal(4)                           # "th"
inflection.ordinal(11)                          # "th"
inflection.ordinal(-21)                         # "st"
```

### `ordinalize(number: int) -> str`

Convert a number to an ordinal string.

- **Parameters**: `number` - Integer
- **Returns**: Number with ordinal suffix (e.g., "1st", "2nd")
- **Behavior**: Combines the number with its ordinal suffix. Preserves negative sign.

```python
inflection.ordinalize(1)                        # "1st"
inflection.ordinalize(2)                        # "2nd"
inflection.ordinalize(1003)                     # "1003rd"
inflection.ordinalize(-11)                      # "-11th"
```

### `parameterize(string: str, separator: str = '-') -> str`

Convert strings to URL-safe format.

- **Parameters**:
  - `string`: Input string with Unicode or special characters
  - `separator`: Character to join words (default: '-')
- **Returns**: Lowercase ASCII string with only alphanumerics, hyphens, and underscores
- **Behavior**: Transliterates Unicode to ASCII, replaces non-alphanumeric characters with separator, removes consecutive separators, removes leading/trailing separators, converts to lowercase.

```python
inflection.parameterize("Donald E. Knuth")      # "donald-e-knuth"
inflection.parameterize("Hello World!", "_")    # "hello_world"
inflection.parameterize("Ærøskøbing")          # "rskbing"
```

### `transliterate(string: str) -> str`

Replace non-ASCII characters with ASCII approximations.

- **Parameters**: `string` - Unicode string
- **Returns**: ASCII string with approximations or omissions
- **Behavior**: Uses Unicode NFKD normalization, then encodes to ASCII with 'ignore' error handling, discarding characters without ASCII equivalents.

```python
inflection.transliterate('älämölö')             # "alamolo"
inflection.transliterate('Ærøskøbing')         # "rskbing"
```

### `tableize(word: str) -> str`

Convert model class names to database table names.

- **Parameters**: `word` - Class name in CamelCase
- **Returns**: Plural snake_case table name
- **Behavior**: Applies `underscore` followed by `pluralize`.

```python
inflection.tableize('RawScaledScorer')          # "raw_scaled_scorers"
inflection.tableize('fancyCategory')            # "fancy_categories"
inflection.tableize('Person')                   # "people"
```

# Implementation Notes

## Pluralization and Singularization Rules

The package includes predefined rule sets for English pluralization:
- Regular patterns: s, es, ies endings based on word structure
- Irregular mappings: person/people, man/men, child/children, mouse/mice, ox/oxen
- Uncountable words that remain unchanged: fish, sheep, information, equipment, money, rice, series, species, jeans

Rules are applied in order until the first match. Words already in the target form (e.g., pluralizing an already-plural word) may return unchanged or apply the first matching rule.

## Case Sensitivity

Functions preserve the case pattern of input strings:
- `pluralize("CamelWord")` maintains CamelCase in output
- `underscore` and `humanize` produce lowercase output
- `titleize` capitalizes each word
- `camelize` can produce either UpperCamelCase or lowerCamelCase

## Determinism and Purity

All functions are pure and deterministic:
- Same input always produces the same output
- No file I/O, network access, or database operations
- No modification of global state or input strings
- No random number generation or time-based behavior

## Unicode Handling

Functions accept Unicode strings:
- `transliterate` and `parameterize` convert Unicode to ASCII
- Other functions preserve Unicode characters in output
- String operations use Python's Unicode-aware string methods

## Edge Cases

- Empty strings: Most functions return empty string unchanged
- Whitespace: Functions do not trim leading/trailing whitespace unless part of their specification
- Numeric strings: Processed as regular strings, not parsed as numbers (except `ordinal` and `ordinalize`)
- Special characters in `underscore`: Hyphens converted to underscores
- `camelize` on already-CamelCase strings: May not be idempotent with `underscore` for all inputs

# Examples

## Basic String Transformations

```python
import inflection

# Converting naming conventions
class_name = "UserAccount"
table_name = inflection.tableize(class_name)
# table_name == "user_accounts"

field_name = inflection.underscore(class_name)
# field_name == "user_account"

# URL generation
title = "The Quick Brown Fox"
slug = inflection.parameterize(title)
# slug == "the-quick-brown-fox"
```

## Pluralization in ORM Contexts

```python
# Model name to table name
model = "Category"
table = inflection.tableize(model)
# table == "categories"

# Singular/plural conversions
singular = "person"
plural = inflection.pluralize(singular)
# plural == "people"

back_to_singular = inflection.singularize(plural)
# back_to_singular == "person"
```

## Human-Readable Output

```python
# Converting field names for display
db_column = "created_at"
label = inflection.humanize(db_column)
# label == "Created at"

# Title case for headers
page_title = inflection.titleize("the_user_guide")
# page_title == "The User Guide"
```

## Ordinal Numbers

```python
# Generating ordinal strings for rankings
for rank in [1, 2, 3, 11, 21, 22]:
    print(f"{rank} -> {inflection.ordinalize(rank)}")
# Output:
# 1 -> 1st
# 2 -> 2nd
# 3 -> 3rd
# 11 -> 11th
# 21 -> 21st
# 22 -> 22nd
```

# Error Handling and Boundary Conditions

## Type Errors

Functions expect string inputs (or int for ordinal functions). Passing non-string types to string functions or non-int types to ordinal functions will raise:
- `TypeError` or `AttributeError` for incompatible types

## Empty and Whitespace Strings

```python
inflection.pluralize("")                  # ""
inflection.underscore("")                 # ""
inflection.camelize("")                   # ""
inflection.humanize("   ")                # "   " (whitespace preserved)
```

## Unicode and Special Characters

```python
# Unicode is preserved where not explicitly transliterated
inflection.pluralize("café")              # "cafés"
inflection.humanize("ñoño")               # "Ñoño"

# Transliteration removes non-ASCII
inflection.transliterate("café")          # "cafe"
inflection.parameterize("café")           # "cafe"
```

## Ordinal Edge Cases

```python
# Negative numbers use absolute value for suffix
inflection.ordinal(-1)                    # "st"
inflection.ordinalize(-1)                 # "-1st"

# Special cases for 11, 12, 13
inflection.ordinalize(11)                 # "11th"
inflection.ordinalize(111)                # "111th"
inflection.ordinalize(21)                 # "21st"
```

## Idempotency Limitations

Some transformations are not perfectly reversible:

```python
# camelize and underscore are not perfect inverses
original = "IOError"
underscored = inflection.underscore(original)  # "io_error"
camelized = inflection.camelize(underscored)   # "IoError" (not "IOError")

# Pluralizing already-plural words
inflection.pluralize("posts")              # "posts" (unchanged)
inflection.pluralize("data")               # "data" (unchanged, irregular)
```

## Non-English Words

The package is designed for English:
- Non-English words may not pluralize/singularize correctly
- Irregular forms are limited to common English words
- Unicode characters in words are preserved but rules are English-based
