# Project Description

Faker is a Python package that generates fake data for testing, prototyping, and populating databases. It provides realistic-looking names, addresses, emails, text, numbers, dates, and other data types. The library supports multiple locales for internationalized fake data generation and offers deterministic output through seeding for reproducible test scenarios.

The primary use case is generating test fixtures and mock data without relying on external services or real user information. Faker is locale-aware, supporting dozens of languages and regional formats. It does not require network access at runtime and operates entirely offline once installed.

# Natural Language Instruction

Build a Python package named `faker` (lowercase) that can be installed and imported as `from faker import Faker`. The package must:

1. Provide a `Faker` class that generates fake data through provider methods
2. Support deterministic output via class-level `Faker.seed()` and instance-level `seed_instance()` methods
3. Support multiple locales (e.g., `Faker('zh_CN')`, `Faker(['en_US', 'fr_FR'])`)
4. Include core data providers: person (name, email), address, text/lorem, internet (URL, IP), company, phone, date, color, credit card, Python types (pyint, pystr), and miscellaneous (uuid4, word)
5. Allow weighted multi-locale generators via dict syntax: `Faker({'en_US': 3, 'zh_CN': 1})`
6. Provide a command-line interface via `faker` command or `python -m faker`

The package must be installable with `pip install -e .` from the workspace root and must not fetch external data at runtime. All provider data and templates must be bundled in the package.

# Supports

**Language**: Python 3.12  
**Package Manager**: pip  
**Installation**: `python -m pip install --no-build-isolation --no-deps --no-index -e .`  
**Runtime Dependencies**: None (tzdata is optional for Windows)  
**Build Backend**: setuptools  
**Network Policy**: No network access required at runtime or during testing. All functionality operates offline.

# Project Directory Structure

```
workspace/
├── faker/
│   ├── __init__.py
│   ├── factory.py
│   ├── generator.py
│   ├── proxy.py
│   ├── config.py
│   ├── exceptions.py
│   ├── cli.py
│   ├── __main__.py
│   ├── typing.py
│   ├── documentor.py
│   ├── py.typed
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── address/
│   │   │   ├── __init__.py
│   │   │   └── ...
│   │   ├── person/
│   │   │   ├── __init__.py
│   │   │   └── ...
│   │   ├── internet/
│   │   ├── company/
│   │   ├── phone_number/
│   │   ├── date_time/
│   │   ├── color/
│   │   ├── credit_card/
│   │   ├── lorem/
│   │   ├── python/
│   │   ├── misc/
│   │   └── ...
│   └── utils/
│       ├── __init__.py
│       └── ...
├── setup.py
└── VERSION
```

# API Usage Guide

## Core Entry Point: `Faker` class

**Import**: `from faker import Faker`

**Constructor signature**:
```python
Faker(
    locale: str | Sequence[str] | dict[str, int | float] | None = None,
    providers: list[str] | None = None,
    generator: Generator | None = None,
    includes: list[str] | None = None,
    use_weighting: bool = True,
    **config: Any
) -> Faker
```

- `locale`: Single locale string (e.g., `'en_US'`, `'zh_CN'`), list/tuple of locales, or dict with weights. Default is `'en_US'`.
- Locale codes use underscore format: `'en_US'`, `'zh_CN'`, `'fr_FR'`, etc.
- Weighted locales: `{'en_US': 3, 'zh_CN': 1}` generates English data 75% of the time, Chinese 25%.
- Returns a `Faker` instance with provider methods.

## Seeding for Deterministic Output

### Class-level seed

**Method**: `Faker.seed(seed: int | float | str | bytes | bytearray | None = None) -> None`

Sets the random seed globally for all Faker instances. Calling `Faker.seed(12345)` ensures that subsequent Faker instances produce identical sequences.

**Example**:
```python
Faker.seed(42)
fake1 = Faker()
name1 = fake1.name()  # Deterministic

Faker.seed(42)
fake2 = Faker()
name2 = fake2.name()  # Same as name1
```

### Instance-level seed

**Method**: `fake.seed_instance(seed: int | float | str | bytes | bytearray | None = None) -> None`

Seeds only the specific Faker instance, leaving other instances unaffected.

**Example**:
```python
fake = Faker()
fake.seed_instance(999)
result1 = fake.name()
fake.seed_instance(999)
result2 = fake.name()  # Same as result1
```

## Core Provider Methods

All provider methods are called on a `Faker` instance. Methods return strings unless otherwise specified.

### Person Provider

- `fake.name() -> str`: Full name (e.g., "John Smith", "李明")
- `fake.first_name() -> str`: First/given name
- `fake.last_name() -> str`: Last/family name
- `fake.email() -> str`: Email address (e.g., "user@example.com")
- `fake.email(domain='example.org') -> str`: Email with custom domain

### Address Provider

- `fake.address() -> str`: Full address (multi-line, locale-specific format)
- `fake.city() -> str`: City name
- `fake.state() -> str`: State/province (if applicable to locale)
- `fake.country() -> str`: Country name
- `fake.postcode() -> str`: Postal/ZIP code
- `fake.street_address() -> str`: Street address without city/state

### Lorem/Text Provider

- `fake.text(max_nb_chars: int = 200) -> str`: Random text paragraph
- `fake.sentence(nb_words: int = 6, variable_nb_words: bool = True) -> str`: Random sentence
- `fake.word() -> str`: Single random word
- `fake.words(nb: int = 3) -> list[str]`: List of random words
- `fake.paragraph(nb_sentences: int = 3, variable_nb_sentences: bool = True) -> str`: Paragraph

### Internet Provider

- `fake.url() -> str`: Random URL (e.g., "http://example.com/")
- `fake.ipv4() -> str`: IPv4 address (e.g., "192.0.2.1")
- `fake.ipv6() -> str`: IPv6 address
- `fake.domain_name() -> str`: Domain name
- `fake.user_name() -> str`: Username

### Company Provider

- `fake.company() -> str`: Company name
- `fake.company_suffix() -> str`: Company suffix (e.g., "Inc.", "Ltd.")
- `fake.catch_phrase() -> str`: Marketing catchphrase

### Phone Number Provider

- `fake.phone_number() -> str`: Phone number (locale-formatted)

### Date/Time Provider

- `fake.date(pattern: str = '%Y-%m-%d') -> str`: Random date
- `fake.date_time() -> datetime.datetime`: Random datetime object
- `fake.time() -> str`: Random time string
- `fake.year() -> str`: Random year (as string)

### Color Provider

- `fake.color_name() -> str`: Color name (e.g., "Blue", "Red")
- `fake.hex_color() -> str`: Hexadecimal color code (e.g., "#3a9f12")
- `fake.rgb_color() -> str`: RGB format "R,G,B"

### Credit Card Provider

- `fake.credit_card_number(card_type: str | None = None) -> str`: Credit card number
- `fake.credit_card_provider(card_type: str | None = None) -> str`: Card provider name (e.g., "Visa", "Mastercard")

### Python Types Provider

- `fake.pyint(min_value: int = 0, max_value: int = 9999, step: int = 1) -> int`: Random integer
- `fake.pystr(min_chars: int = 0, max_chars: int = 20) -> str`: Random alphanumeric string
- `fake.pybool() -> bool`: Random boolean
- `fake.pyfloat(left_digits: int | None = None, right_digits: int | None = None, positive: bool = False, min_value: float | None = None, max_value: float | None = None) -> float`: Random float

### Miscellaneous Provider

- `fake.uuid4() -> str`: UUID4 string (e.g., "12345678-1234-1234-1234-123456789abc")
- `fake.boolean(chance_of_getting_true: int = 50) -> bool`: Boolean with custom probability
- `fake.random_element(elements: Sequence) -> Any`: Pick random element from sequence
- `fake.random_int(min: int = 0, max: int = 9999, step: int = 1) -> int`: Random integer (alias)

## Locale Support

Faker supports multiple locales. Common locales include:
- `en_US` (US English, default)
- `zh_CN` (Simplified Chinese)
- `fr_FR` (French)
- `de_DE` (German)
- `ja_JP` (Japanese)
- `ko_KR` (Korean)
- `es_ES` (Spanish)
- `pt_BR` (Brazilian Portuguese)

When a locale is specified, provider output reflects that locale's conventions (name formats, address formats, phone patterns, etc.).

**Multi-locale example**:
```python
fake_multi = Faker(['en_US', 'zh_CN'])
# Alternates between en_US and zh_CN data
```

**Weighted locale example**:
```python
fake_weighted = Faker({'en_US': 0.8, 'fr_FR': 0.2})
# 80% English, 20% French
```

## Command-Line Interface

The package provides a CLI for generating fake data from the command line:

```bash
faker <provider_method> [options]
```

Or via module:
```bash
python -m faker <provider_method>
```

**Examples**:
```bash
faker name
faker address
faker --seed=12345 email
```

The CLI uses `faker.cli` module with an `execute_from_command_line` function as the entry point.

# Implementation Notes

1. **Determinism**: When a seed is set via `Faker.seed()` or `seed_instance()`, all subsequent calls to provider methods must produce the same output given the same seed and call sequence. Use Python's `random.Random` class for internal randomness.

2. **Locale handling**: Locale strings with hyphens (e.g., `'en-US'`) should be normalized to underscores (`'en_US'`). If an unsupported locale is requested, fall back to a default or raise an informative error.

3. **Provider architecture**: Providers are modular. The base `Provider` class should be located in `faker.providers`. Each category (person, address, internet, etc.) is a submodule under `faker.providers/` with its own `__init__.py` and locale-specific data files.

4. **Factory and Generator**: The `Faker` class is a proxy that delegates to `Generator` instances created by `Factory.create()`. The proxy supports dynamic attribute lookup to provider methods.

5. **Uniqueness**: Do not implement advanced uniqueness features (e.g., `.unique` proxy) unless required by hidden tests. Focus on core generation and seeding.

6. **No external data fetching**: All word lists, name databases, address templates, and other data must be included in the package at install time. No HTTP requests or file downloads at runtime.

7. **Error handling**: Methods should raise `TypeError` for invalid argument types and `ValueError` for out-of-range parameters (e.g., `pyint(min_value=10, max_value=5)`).

8. **Return types**: Most provider methods return strings. Date/time methods may return `datetime` objects where documented. `pyint` returns `int`, `pybool`/`boolean` return `bool`, etc.

9. **Reproducibility**: After `Faker.seed(N)`, creating a new `Faker()` instance and calling methods in the same order must produce identical results.

10. **Testing**: The package should be testable without network access. All tests and verifiers run offline.

# Examples

## Basic usage
```python
from faker import Faker
fake = Faker()

print(fake.name())       # "John Doe"
print(fake.address())    # "123 Main St\nAnytown, NY 12345"
print(fake.email())      # "user@example.com"
```

## Seeded deterministic generation
```python
from faker import Faker

Faker.seed(0)
fake1 = Faker()
name_a = fake1.name()

Faker.seed(0)
fake2 = Faker()
name_b = fake2.name()

assert name_a == name_b  # Always true
```

## Locale-specific data
```python
from faker import Faker

fake_cn = Faker('zh_CN')
print(fake_cn.name())      # Chinese name (e.g., "王芳")
print(fake_cn.address())   # Chinese-formatted address

fake_fr = Faker('fr_FR')
print(fake_fr.name())      # French name (e.g., "Jean Dupont")
```

## Multi-locale with weights
```python
from faker import Faker

fake = Faker({'en_US': 3, 'es_ES': 1})
# Generates English data 75% of the time, Spanish 25%
for _ in range(10):
    print(fake.name())
```

# Error Handling and Boundary Conditions

1. **Invalid locale**: If a locale string is not recognized, the implementation may either fall back to `en_US` or raise a clear error. Document the chosen behavior.

2. **Invalid parameter types**: Methods like `pyint(min_value="abc")` should raise `TypeError`.

3. **Invalid ranges**: `pyint(min_value=10, max_value=5)` should raise `ValueError`.

4. **Empty sequences**: `random_element([])` should raise `IndexError` or return `None` with documented behavior.

5. **Seed types**: `Faker.seed()` and `seed_instance()` accept `int`, `float`, `str`, `bytes`, `bytearray`, or `None`. `None` uses system randomness.

6. **Unicode safety**: All text generation must handle Unicode correctly for non-Latin locales (Chinese, Japanese, Korean, Arabic, etc.).

7. **Thread safety**: The implementation does not need to be thread-safe; calling `Faker.seed()` from multiple threads is undefined behavior.

# Security

Faker is intended for development and testing only, not for generating secure tokens, passwords, or cryptographic keys. The `uuid4()` method and other random outputs use pseudo-random generators seeded by the user or system time, not cryptographically secure sources. Do not use Faker-generated data for authentication, authorization, or any security-critical purpose.
