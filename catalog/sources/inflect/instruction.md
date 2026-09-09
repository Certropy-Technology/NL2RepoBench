# Build inflect Package from Empty Workspace

## Project Description

`inflect` is a comprehensive Python library for generating grammatically correct English language inflections. It provides accurate plural forms, singular forms, ordinals, indefinite articles ("a" vs "an"), and number-to-words conversions. The library follows conventions from the Oxford English Dictionary and Fowler's Modern English Usage.

## Supports

- **License**: MIT License
- **Source**: PyPI package `inflect` version 7.5.0
- **Python Version**: 3.9+
- **Dependencies**: 
  - `more_itertools >= 8.5.0`
  - `typeguard >= 4.0.1`

## Natural Language Instruction

Implement the `inflect` library which provides an `engine()` factory function that returns an inflection engine object with methods for natural language inflection operations. The engine supports plural/singular transformations, indefinite article selection, ordinal generation, number-to-words conversion, and list joining with proper English grammar.

## Environment Configuration

The workspace starts empty. You must create a Python package named `inflect` with the required functionality and make it installable via pip.

### Runtime Environment
- Python 3.12
- All dependencies will be pre-installed in the verification environment
- The package must be installable with: `python -m pip install -e .`

## Project Directory Structure

```
workspace/
├── inflect/
│   └── __init__.py          # Main module with engine() function and Engine class
├── setup.py                 # Package installation configuration
└── (optional) pyproject.toml, README, LICENSE, etc.
```

The `inflect` module must be importable as `import inflect` and provide an `engine()` function that returns an Engine instance.

## API Usage Guide

### Core API

#### Factory Function

```python
import inflect
p = inflect.engine()
```

The `engine()` function returns an `Engine` instance with the following methods:

### Pluralization and Singularization

#### `plural(word, count=None) -> str`

Returns the plural form of a word. If `count` is provided and equals 1, returns the singular form unchanged.

**Parameters:**
- `word` (str): The singular word to pluralize
- `count` (int, optional): If 1, returns singular; otherwise returns plural

**Returns:** Pluralized word string

**Examples:**
```python
p.plural("cat")           # "cats"
p.plural("person")        # "people"
p.plural("knife")         # "knives"
p.plural("cat", 1)        # "cat"  (count=1 returns singular)
p.plural("cat", 2)        # "cats"
```

**Rules:**
- Regular plurals: add "s" (cat → cats, dog → dogs)
- Words ending in s/x/z/ch/sh: add "es" (box → boxes, glass → glasses, quiz → quizzes, bus → buses)
- Words ending in consonant+y: change "y" to "ies" (city → cities)
- Words ending in f/fe: change to "ves" (knife → knives, wife → wives, life → lives)
- Irregular plurals: person → people, child → children, man → men, woman → women, mouse → mice, goose → geese, foot → feet, tooth → teeth, ox → oxen
- Unchanged plurals: sheep → sheep, fish → fish

#### `singular_noun(word, count=None) -> str`

Returns the singular form of a plural noun. If `count` is provided and not 1, returns the plural unchanged.

**Parameters:**
- `word` (str): The plural word to singularize
- `count` (int, optional): If not 1, returns plural unchanged

**Returns:** Singularized word string

**Examples:**
```python
p.singular_noun("cats")      # "cat"
p.singular_noun("people")    # "person"
p.singular_noun("knives")    # "knife"
p.singular_noun("mice")      # "mouse"
p.singular_noun("feet")      # "foot"
p.singular_noun("lives")     # "life"
```

#### `plural_noun(word, count=None) -> str`

Specialized plural for nouns, including pronouns.

**Examples:**
```python
p.plural_noun("cat")         # "cats"
p.plural_noun("I", 2)        # "we"
p.plural_noun("me", 2)       # "us"
p.plural_noun("mine", 2)     # "ours"
```

#### `plural_verb(word, count=None) -> str`

Pluralizes verb forms.

**Examples:**
```python
p.plural_verb("is", 1)       # "is"
p.plural_verb("is", 2)       # "are"
p.plural_verb("was", 1)      # "was"
p.plural_verb("was", 2)      # "were"
```

#### `plural_adj(word, count=None) -> str`

Pluralizes adjectives, particularly demonstratives and possessives.

**Examples:**
```python
p.plural_adj("my", 1)        # "my"
p.plural_adj("my", 2)        # "our"
p.plural_adj("this", 2)      # "these"
p.plural_adj("that", 2)      # "those"
```

### Indefinite Articles

#### `a(word, count=None) -> str`

Returns the word with the correct indefinite article ("a" or "an") based on pronunciation.

**Parameters:**
- `word` (str): The word to prefix with an article
- `count` (int, optional): Not commonly used for this method

**Returns:** String with "a" or "an" prefix

**Examples:**
```python
p.a("apple")         # "an apple"
p.a("banana")        # "a banana"
p.a("orange")        # "an orange"
p.a("university")    # "a university" (u pronounced as "you")
p.a("hour")          # "an hour" (silent h)
```

**Rules:**
- Use "an" before vowel sounds: a, e, i, o, u
- Use "a" before consonant sounds
- Special cases: "university" (a), "hour" (an), based on pronunciation not spelling

#### `an(word, count=None) -> str`

Alias for `a()` - returns the same result.

**Examples:**
```python
p.an("apple")        # "an apple"
p.an("banana")       # "a banana"
```

### Ordinals

#### `ordinal(num) -> str`

Converts a number to its ordinal form (1st, 2nd, 3rd, etc.).

**Parameters:**
- `num` (int): The number to convert

**Returns:** Ordinal string

**Examples:**
```python
p.ordinal(1)         # "1st"
p.ordinal(2)         # "2nd"
p.ordinal(3)         # "3rd"
p.ordinal(4)         # "4th"
p.ordinal(11)        # "11th"
p.ordinal(21)        # "21st"
p.ordinal(22)        # "22nd"
p.ordinal(23)        # "23rd"
p.ordinal(100)       # "100th"
p.ordinal(101)       # "101st"
```

**Rules:**
- Numbers ending in 1 (except 11): add "st"
- Numbers ending in 2 (except 12): add "nd"
- Numbers ending in 3 (except 13): add "rd"
- All others (including 11, 12, 13): add "th"

### Number to Words

#### `number_to_words(num, **kwargs) -> str`

Converts a number to its English word representation.

**Parameters:**
- `num` (int or float): The number to convert
- `**kwargs`: Additional formatting options (implementation-specific)

**Returns:** English word string

**Examples:**
```python
p.number_to_words(0)          # "zero"
p.number_to_words(1)          # "one"
p.number_to_words(5)          # "five"
p.number_to_words(13)         # "thirteen"
p.number_to_words(42)         # "forty-two"
p.number_to_words(99)         # "ninety-nine"
p.number_to_words(100)        # "one hundred"
p.number_to_words(256)        # "two hundred and fifty-six"
p.number_to_words(1000)       # "one thousand"
p.number_to_words(1234)       # "one thousand, two hundred and thirty-four"
```

**Format:**
- Single digits: "zero", "one", "two", etc.
- Teens: "thirteen", "fourteen", etc.
- Tens: "twenty", "thirty", "forty", etc. with hyphen for compounds ("twenty-one")
- Hundreds: "one hundred", "two hundred", etc. with "and" before tens/ones
- Thousands and above: comma-separated with "and" before the last component

### Numbered Expressions

#### `no(word, count) -> str`

Returns a count with the correctly pluralized word. When count is 0, returns "no" instead of "0".

**Parameters:**
- `word` (str): The word to pluralize
- `count` (int): The count

**Returns:** String with count and pluralized word

**Examples:**
```python
p.no("error", 0)     # "no errors"
p.no("error", 1)     # "1 error"
p.no("error", 2)     # "2 errors"
p.no("error", 5)     # "5 errors"
p.no("cat", 0)       # "no cats"
p.no("cat", 1)       # "1 cat"
```

### Comparison

#### `compare(word1, word2) -> str | bool`

Compares two words for number-insensitive equality (ignoring singular/plural differences).

**Parameters:**
- `word1` (str): First word
- `word2` (str): Second word

**Returns:**
- `"eq"`: Both words are identical
- `"s:p"`: word1 is singular, word2 is its plural
- `"p:s"`: word1 is plural, word2 is its singular
- `"p:p"`: Both are different plurals of the same word
- `False`: No relationship between the words

**Examples:**
```python
p.compare("cat", "cat")            # "eq"
p.compare("cat", "cats")           # "s:p"
p.compare("cats", "cat")           # "p:s"
p.compare("person", "people")      # "s:p"
p.compare("people", "persons")     # False (different plurals, not recognized)
p.compare("dog", "cat")            # False
```

### List Joining

#### `join(words, **kwargs) -> str`

Joins a list of words with proper English grammar (commas and "and").

**Parameters:**
- `words` (list): List of strings to join
- `**kwargs`: Additional formatting options (implementation-specific)

**Returns:** Grammatically correct joined string

**Examples:**
```python
p.join(["apple"])                              # "apple"
p.join(["apple", "banana"])                    # "apple and banana"
p.join(["apple", "banana", "cherry"])          # "apple, banana, and cherry"
p.join(["red", "green", "blue", "yellow"])     # "red, green, blue, and yellow"
```

**Format:**
- 1 item: return as-is
- 2 items: join with " and "
- 3+ items: comma-separated with ", and " before the last item (Oxford comma)

## Implementation Notes

### Key Behavioral Requirements

1. **Plural Formation Rules**: The library must handle regular plurals, irregular plurals, and special cases according to English grammar rules
2. **Singular Formation**: Must correctly reverse pluralization for all supported plural forms
3. **Pronunciation-based Articles**: The `a()`/`an()` methods must consider pronunciation, not just spelling (e.g., "a university", "an hour")
4. **Ordinal Suffixes**: Must correctly apply -st, -nd, -rd, -th based on the last digit(s)
5. **Number Words Format**: Must use hyphens for compound numbers (twenty-one), "and" before final component in hundreds/thousands, and comma separators for thousands
6. **Zero Handling**: The `no()` method must replace 0 with "no"
7. **Oxford Comma**: The `join()` method must use the Oxford comma (serial comma) for 3+ items

### Edge Cases and Special Handling

- **Irregular Plurals**: person/people, child/children, man/men, woman/women, mouse/mice, goose/geese, foot/feet, tooth/teeth, ox/oxen
- **Unchanged Plurals**: sheep, fish
- **F/Fe to Ves**: knife/knives, wife/wives, life/lives
- **Consonant+Y to IES**: city/cities
- **Silent H**: hour uses "an"
- **Consonant U sound**: university uses "a"
- **Ordinal Teens**: 11th, 12th, 13th (not 11st, 12nd, 13rd)

### Verification Contract

The implementation will be tested with a custom JSON-based verifier that:
1. Executes test scripts in an isolated environment
2. Verifies exact string matches for returned values
3. Tests all major API methods with diverse inputs
4. Validates edge cases and irregular forms
5. Checks conditional behavior (count-based pluralization)

Each test scenario imports inflect, creates an engine, calls a method, and compares the result against the expected value.

### Performance and Resource Constraints

- The implementation should complete typical operations in milliseconds
- No external network access is required or permitted
- All dependencies are pre-installed in the verification environment
- The package must install successfully with pip in under 2 minutes

## Testing

The verifier will test 90 distinct scenarios covering:
- Basic plurals (cats, dogs, boxes)
- Irregular plurals (people, children, mice, feet, geese)
- Singularization (reverse of plurals)
- Conditional plurals with counts
- Indefinite articles (a/an) with various words
- Ordinals (1st through 101st and beyond)
- Number-to-words conversion (0 through 1234 and beyond)
- The `no()` method with zero and non-zero counts
- Comparison operations (eq, s:p, p:s, False)
- List joining (1 through 4+ items)
- Specialized methods (plural_noun, plural_verb, plural_adj)
- Complex plurals (women, sheep, oxen, buses, glasses, quizzes, lives, wives, cities)

All test scenarios must produce exact string matches with the expected outputs.
