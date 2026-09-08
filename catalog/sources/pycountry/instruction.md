# Implement pycountry Package

## Natural Language Instruction

Your task is to implement a Python package named `pycountry` that provides access to ISO databases for countries, languages, currencies, and scripts. The package should make it easy to look up and retrieve information about these entities using various identifiers.

## Project Description

`pycountry` is a Python library that provides ISO standard databases and their translations. It includes:

- **ISO 3166-1** (Countries): Country codes, names, and numeric identifiers
- **ISO 639-3** (Languages): Language codes and names
- **ISO 4217** (Currencies): Currency codes, names, and numeric identifiers  
- **ISO 15924** (Scripts): Script codes and names

The library provides a simple, consistent interface to query these databases using get(), lookup(), and attribute access patterns.

## Supports

The package must:
- Provide database objects for countries, languages, currencies, and scripts
- Support querying by various fields (alpha codes, names, numeric codes)
- Return data objects with attribute access to fields
- Support both exact (get) and flexible (lookup) query methods
- Work without requiring network access or external databases

## API Usage Guide

### Countries Database

Access via `pycountry.countries`:

```python
import pycountry

# Get country by alpha_2 code
us = pycountry.countries.get(alpha_2='US')
print(us.name)           # "United States"
print(us.alpha_3)        # "USA"
print(us.numeric)        # "840"
print(us.official_name)  # "United States of America"

# Get country by alpha_3 code
germany = pycountry.countries.get(alpha_3='DEU')
print(germany.name)      # "Germany"

# Get country by name
france = pycountry.countries.get(name='France')
print(france.alpha_2)    # "FR"

# Get country by numeric code
japan = pycountry.countries.get(numeric='392')
print(japan.name)        # "Japan"

# Get country by official_name
usa = pycountry.countries.get(official_name='United States of America')

# Lookup (flexible search)
country = pycountry.countries.lookup('Germany')
print(country.alpha_2)   # "DE"

# Handle non-existent entries
result = pycountry.countries.get(alpha_2='ZZ', default=None)
print(result)            # None
```

Country objects may have these attributes:
- `alpha_2`: Two-letter country code (e.g., "US")
- `alpha_3`: Three-letter country code (e.g., "USA")
- `name`: Common country name (e.g., "United States")
- `numeric`: Numeric country code (e.g., "840")
- `official_name`: Official country name (may not be present for all countries)
- `flag`: Unicode flag emoji (e.g., "🇺🇸")

### Languages Database

Access via `pycountry.languages`:

```python
# Get language by alpha_2 code
english = pycountry.languages.get(alpha_2='en')
print(english.name)      # "English"
print(english.alpha_3)   # "eng"

# Get language by alpha_3 code
german = pycountry.languages.get(alpha_3='deu')
print(german.name)       # "German"
print(german.alpha_2)    # "de"

# Get language by name
french = pycountry.languages.get(name='French')
print(french.alpha_2)    # "fr"

# Lookup
lang = pycountry.languages.lookup('English')
print(lang.alpha_3)      # "eng"
```

Language objects have these attributes:
- `alpha_2`: Two-letter language code (ISO 639-1, may not be present)
- `alpha_3`: Three-letter language code (ISO 639-3)
- `name`: Language name
- `scope`: Language scope (typically "I" for individual language)
- `type`: Language type (typically "L" for living language)
- `bibliographic`: Bibliographic code (may not be present)

### Currencies Database

Access via `pycountry.currencies`:

```python
# Get currency by alpha_3 code
usd = pycountry.currencies.get(alpha_3='USD')
print(usd.name)          # "US Dollar"
print(usd.numeric)       # "840"

# Get currency by name
euro = pycountry.currencies.get(name='Euro')
print(euro.alpha_3)      # "EUR"

# Get currency by numeric code
gbp = pycountry.currencies.get(numeric='826')
print(gbp.name)          # "Pound Sterling"

# Lookup
currency = pycountry.currencies.lookup('USD')
print(currency.name)     # "US Dollar"
```

Currency objects have these attributes:
- `alpha_3`: Three-letter currency code (e.g., "USD")
- `name`: Currency name (e.g., "US Dollar")
- `numeric`: Numeric currency code (e.g., "840")

### Scripts Database

Access via `pycountry.scripts`:

```python
# Get script by alpha_4 code
latin = pycountry.scripts.get(alpha_4='Latn')
print(latin.name)        # "Latin"
print(latin.numeric)     # "215"

# Get script by name
arabic = pycountry.scripts.get(name='Arabic')
print(arabic.alpha_4)    # "Arab"

# Lookup
script = pycountry.scripts.lookup('Latin')
print(script.alpha_4)    # "Latn"
```

Script objects have these attributes:
- `alpha_4`: Four-letter script code (e.g., "Latn")
- `name`: Script name (e.g., "Latin")
- `numeric`: Numeric script code (e.g., "215")

## Implementation Notes

### Core Design

1. **Database Classes**: Each database (countries, languages, currencies, scripts) should be implemented as a class that manages a collection of data objects.

2. **Data Objects**: Each entry (country, language, currency, script) should be represented as an object with attribute access to its fields. Consider using a base `Data` class that allows dynamic attribute access from a dictionary of fields.

3. **Query Methods**:
   - `get(**kwargs)`: Return exact match by field, or `default` (None by default) if not found
   - `lookup(value)`: Flexible search that tries multiple fields and returns first match
   - Both methods should be case-insensitive

4. **Module Structure**: The package should export these top-level names:
   - `countries`: ExistingCountries instance
   - `languages`: Languages instance
   - `currencies`: Currencies instance
   - `scripts`: Scripts instance
   - `__version__`: Version string

### Data Storage

You'll need to include the ISO database data within your package. You can:
- Store data as JSON files in a `databases/` subdirectory
- Embed data as Python data structures
- Load data from included resource files

The data should be read-only and not require network access.

### Installation

The package should be installable with:
```bash
pip install -e .
```

And importable as:
```python
import pycountry
```

## Environment Configuration

- **Python Version**: 3.12
- **Dependencies**: No external runtime dependencies required
- **Package Structure**: Standard Python package with setuptools/pyproject.toml
- **Installation**: Should support editable install with `pip install -e .`

## Project Directory Structure

```
workspace/
├── src/
│   └── pycountry/
│       ├── __init__.py          # Main module with database instances
│       ├── db.py                # Database and Data base classes
│       └── databases/           # ISO data files (JSON format)
│           ├── iso3166-1.json   # Countries data
│           ├── iso639-3.json    # Languages data
│           ├── iso4217.json     # Currencies data
│           └── iso15924.json    # Scripts data
├── pyproject.toml               # Package metadata and build config
└── setup.py                     # Alternative setup script (optional)
```

Or a flat structure:
```
workspace/
├── pycountry/
│   ├── __init__.py
│   ├── db.py
│   └── databases/
│       ├── iso3166-1.json
│       ├── iso639-3.json
│       ├── iso4217.json
│       └── iso15924.json
├── pyproject.toml
└── setup.py
```

The package must be importable as `pycountry` after installation.

## Key Requirements

1. All query methods must be case-insensitive
2. Data objects must support attribute access (e.g., `country.name`)
3. Data objects must be convertible to dictionaries for serialization
4. The `get()` method must support a `default` parameter
5. All databases must be accessible immediately after import
6. No network access should be required
7. The package must include all necessary ISO database files
