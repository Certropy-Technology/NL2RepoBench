# Project Description

`titlecase` is a Python library that converts text to Title Case format following intelligent capitalization rules. The library implements John Gruber's title casing algorithm, which handles small words (articles, prepositions, conjunctions), acronyms, hyphenated words, and various edge cases according to the New York Times Manual of Style conventions.

The primary goal is to provide a single `titlecase()` function that accepts input text and returns properly capitalized titles, with optional callback support for custom word handling.

# Natural Language Instruction

Implement a Python package named `titlecase` that provides intelligent title casing functionality. The package must:

1. Export a `titlecase()` function that converts input text to Title Case
2. Handle small words (a, an, the, in, of, at, by, for, to, etc.) by keeping them lowercase in the middle of titles
3. Always capitalize the first and last words, even if they are small words
4. Capitalize words after punctuation like colons, question marks, and semicolons
5. Preserve acronyms and abbreviations (e.g., AT&T, CNN, U.S.)
6. Handle hyphenated words by capitalizing each component
7. Handle slashed words (word/word) by capitalizing each component
8. Process names with Mac/Mc prefixes correctly (Macbeth, McDonald)
9. Handle apostrophes in contractions (it's, don't, let's)
10. Support callback functions for custom word handling
11. Support multi-line text processing with optional blank line preservation

The package name is `titlecase`, the import package name is `titlecase`, and it should be installable via pip. The main API is the `titlecase()` function exported from the top-level module.

# Environment Configuration (Supports)

- **Language**: Python 3.7+
- **Package Manager**: pip
- **Installation Command**: `pip install -e .`
- **Runtime Dependencies**: None (optional: `regex` package for enhanced Unicode support, but should work with standard `re` module as fallback)
- **Build Dependencies**: setuptools (for package installation)
- **Network**: No network access required during runtime
- **Platform**: OS-independent, pure Python implementation

# Project Directory Structure

```
workspace/
├── titlecase/
│   └── __init__.py          # Main module with titlecase() function
├── setup.py                 # Installation metadata
└── pyproject.toml           # Build system requirements (optional)
```

The package exposes a single module `titlecase` with the main `titlecase()` function.

# API Usage Guide

## Main Function: `titlecase()`

**Import Path**: `from titlecase import titlecase`

**Signature**:
```python
def titlecase(text, callback=None, small_first_last=True, preserve_blank_lines=False)
```

**Parameters**:
- `text` (str): The input text to be converted to Title Case
- `callback` (callable, optional): A function called for each word to provide custom capitalization. The callback receives the word as the first argument and an `all_caps` keyword argument indicating if the entire line was in all caps. Should return the custom capitalized version or `None` to use default processing.
- `small_first_last` (bool, default=True): Whether to capitalize small words at the start and end of the text
- `preserve_blank_lines` (bool, default=False): Whether to preserve blank lines in multi-line input

**Returns**: `str` - The title-cased text

**Behavior**:
- Converts input text to Title Case
- Small words (a, an, and, as, at, but, by, en, for, if, in, of, on, or, the, to, v, v., via, vs, vs.) are kept lowercase unless they appear at the beginning or end of the text
- Words after colons (`:`) question marks (`?`), semicolons (`;`), and em-dashes are capitalized
- Hyphenated words have each component capitalized (e.g., "end-to-end" → "End-to-End")
- Slashed words have each component capitalized (e.g., "and/or" → "And/or")
- All-caps input is converted to proper case
- Mixed-case words with uppercase letters in the middle are preserved (e.g., "iPhone")
- Words with inline periods are preserved (e.g., "U.S.", "J.R.R.")
- Words consisting entirely of consonants and longer than 2 characters are treated as acronyms and uppercased (e.g., "cnn" → "CNN")
- Names starting with "Mac" or "Mc" are handled specially (e.g., "macbeth" → "Macbeth", "mcdonald" → "McDonald")
- Apostrophes in contractions are handled correctly (e.g., "it's" → "It's", "don't" → "Don't")
- Multi-line text is processed line by line with newlines preserved

**Exceptions**: No exceptions are raised for normal inputs. Invalid types may raise TypeError.

**Example**:
```python
from titlecase import titlecase

# Basic usage
titlecase('hello world')  # Returns: 'Hello World'

# Small words
titlecase('the quick brown fox')  # Returns: 'The Quick Brown Fox'
titlecase('lord of the rings')  # Returns: 'Lord of the Rings'

# Subphrases after punctuation
titlecase('title: a subtitle')  # Returns: 'Title: A Subtitle'

# Hyphenated words
titlecase('end-to-end')  # Returns: 'End-to-End'

# Slashed words
titlecase('a title and/or string')  # Returns: 'A Title and/or String'

# All caps
titlecase('THIS IS A TEST')  # Returns: 'This Is a Test'

# Acronyms
titlecase('what is AT&T\'s problem?')  # Returns: "What Is AT&T's Problem?"
titlecase('words with all consonants like cnn are acronyms')  # Returns: 'Words With All Consonants Like CNN Are Acronyms'

# Callback for custom handling
def abbreviations(word, **kwargs):
    if word.upper() in ('TCP', 'UDP'):
        return word.upper()
    return None

titlecase('a simple tcp and udp wrapper', callback=abbreviations)
# Returns: 'A Simple TCP and UDP Wrapper'
```

# Implementation Notes

## Small Words List

The following words are considered "small words" and are not capitalized unless they appear at the beginning or end of the text or after specific punctuation:
- Articles: a, an, the
- Prepositions: at, by, for, in, of, on, to, via
- Conjunctions: and, as, but, en, if, or
- Versuses: v, v., vs, vs.

## Capitalization Rules

1. **First and Last Words**: Always capitalize, even if they are small words
2. **After Punctuation**: Capitalize words following colons (`:`), question marks (`?`), semicolons (`;`), and em-dashes (`—`, `–`, `‒`, `―`)
3. **Hyphenated Words**: Each component separated by a hyphen is processed recursively
4. **Slashed Words**: Each component separated by a forward slash (`/`) is processed recursively, but `//` (URLs) is preserved
5. **All Caps Detection**: If the entire line is in uppercase, it is treated as unformatted and converted to proper case
6. **Mixed Case Preservation**: Words with uppercase letters not at the beginning are preserved as-is (e.g., "iPhone", "eBay")
7. **Inline Periods**: Words with periods between letters are preserved (e.g., "U.S.", "Ph.D.")
8. **Consonant Acronyms**: Words longer than 2 characters consisting only of consonants are uppercased (e.g., "bbc" → "BBC", but "st" → "St")
9. **Mac/Mc Names**: Words starting with "Mac" or "Mc" have the prefix capitalized and the remainder processed recursively
10. **Apostrophes**: Contractions and possessives starting with d', l', or o' (e.g., "d'arc", "l'amour", "o'brien") have special handling

## Determinism and State

- The function is pure and deterministic: same input produces same output
- No global state is modified
- No file I/O or network access
- Thread-safe

## Multi-line Processing

When processing multi-line text:
- By default, consecutive blank lines are collapsed into a single newline
- With `preserve_blank_lines=True`, blank lines are preserved
- Each line is processed independently
- Newlines are preserved in the output

# Examples

## Basic String Conversion

```python
from titlecase import titlecase

# Simple words
titlecase('hello world')
# 'Hello World'

# Mixed case input
titlecase('Hello World')
# 'Hello World'

# Empty string
titlecase('')
# ''
```

## Small Words Handling

```python
# Small words in middle
titlecase('alice and bob')
# 'Alice and Bob'

titlecase('dance with me')
# 'Dance With Me'

# Small words at boundaries
titlecase('the beginning')
# 'The Beginning'

titlecase('afraid of')
# 'Afraid Of'
```

## Punctuation and Subphrases

```python
# After colon
titlecase('title: a subtitle')
# 'Title: A Subtitle'

# After question mark
titlecase('what is it? a mystery')
# 'What Is It? A Mystery'

# Quotes
titlecase("'by the way, small word at the start but within quotes.'")
# "'By the Way, Small Word at the Start but Within Quotes.'"
```

## Hyphenated and Slashed Words

```python
# Hyphens
titlecase('end-to-end')
# 'End-to-End'

titlecase('one-two-three')
# 'One-Two-Three'

# Slashes
titlecase('word/word')
# 'Word/Word'

titlecase('dance with me/let\'s face the music and dance')
# "Dance With Me/Let's Face the Music and Dance"
```

## Acronyms and Abbreviations

```python
# Mixed case preservation
titlecase('what is AT&T\'s problem?')
# "What Is AT&T's Problem?"

# Consonant acronyms
titlecase('cnn')
# 'CNN'

titlecase('bbc news')
# 'BBC News'

# Inline periods
titlecase('in the U.S. economy')
# 'In the U.S. Economy'

titlecase('J.R.R. tolkien')
# 'J.R.R. Tolkien'
```

## All Caps Handling

```python
# All caps input
titlecase('THIS IS A TEST')
# 'This Is a Test'

# Mixed caps
titlecase('this is a TEST')
# 'This Is a TEST'
```

## Callback Usage

```python
# Custom abbreviations
def my_callback(word, **kwargs):
    if word.upper() in ('TCP', 'UDP', 'HTTP'):
        return word.upper()
    return None

titlecase('a simple tcp and udp wrapper', callback=my_callback)
# 'A Simple TCP and UDP Wrapper'

titlecase('http over tcp', callback=my_callback)
# 'HTTP Over TCP'
```

## Multi-line Text

```python
# Default (collapses blank lines)
titlecase('line one\nline two')
# 'Line One\nLine Two'

# Preserve blank lines
titlecase('line one\n\nline two', preserve_blank_lines=True)
# 'Line One\n\nLine Two'
```

# Error Handling and Boundary Conditions

## Empty and Whitespace

```python
titlecase('')  # Returns: ''
titlecase('   ')  # Returns: '   '
titlecase('\n\n')  # Returns: '\n'
```

## Numbers

```python
titlecase('34th 3rd 2nd')  # Returns: '34th 3rd 2nd'
titlecase('in 2023')  # Returns: 'In 2023'
```

## Special Characters

```python
titlecase('hello world!')  # Returns: 'Hello World!'
titlecase('what is this?')  # Returns: 'What Is This?'
titlecase('oh! what a day.')  # Returns: 'Oh! What a Day.'
```

## Apostrophes and Contractions

```python
titlecase('it\'s')  # Returns: "It's"
titlecase('don\'t')  # Returns: "Don't"
titlecase('steve\'s')  # Returns: "Steve's"
```

## Complex Real-World Cases

```python
titlecase('Q&A with steve jobs: \'that\'s what happens in technology\'')
# "Q&A With Steve Jobs: 'That's What Happens in Technology'"

titlecase('apple deal with AT&T falls through')
# 'Apple Deal With AT&T Falls Through'

titlecase('starting sub-phrase with a small word: a trick, perhaps?')
# 'Starting Sub-Phrase With a Small Word: A Trick, Perhaps?'
```

# Security

- The function only performs string manipulation and does not execute code
- No file system access, network access, or external command execution
- No use of `eval()` or similar unsafe operations
- Callback functions, if provided, are caller-controlled and executed in the caller's security context
- No regular expression complexity attacks: all patterns are fixed and bounded
