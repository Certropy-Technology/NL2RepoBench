# Project Description

`phonenumbers` is a Python library for parsing, formatting, storing, and validating international phone numbers. It is a Python port of Google's libphonenumber library and provides comprehensive support for phone number manipulation across all countries and regions defined in the International Telecommunication Union (ITU) standards.

The library handles the complexity of international phone numbering plans, including country codes, national prefixes, area codes, and various formatting conventions. It can parse phone numbers from different string representations, validate whether numbers are possible or valid for specific regions, determine phone number types (mobile, fixed-line, toll-free, etc.), and format numbers according to international standards (E.164, ITU-T E.123, RFC 3966).

The primary use cases include validating user input, normalizing phone numbers for storage, formatting numbers for display, and determining the characteristics of phone numbers programmatically.

# Natural Language Instruction

Implement a Python package named `phonenumbers` that provides comprehensive international phone number parsing, formatting, and validation capabilities. The package must:

1. Parse phone numbers from strings with or without country codes, using region hints when necessary
2. Represent phone numbers as structured objects with country code, national number, and metadata
3. Validate phone numbers against ITU standards and country-specific rules
4. Format phone numbers according to E.164, ITU-T E.123 (international and national), and RFC 3966 standards
5. Determine the geographic region and phone number type (mobile, fixed-line, toll-free, etc.)
6. Handle international dialing prefixes, national prefixes, and extensions
7. Support all ITU-defined country codes and region-specific numbering plans
8. Provide detailed error information when parsing fails

The package name is `phonenumbers`, the import name is `phonenumbers`, and it must be installable via pip with setuptools as the build backend. The package depends only on the Python standard library (no external runtime dependencies).

# Supports (Environment Configuration)

- Python: 2.5+ (including 3.x)
- Package Manager: pip
- Build System: setuptools (via pyproject.toml)
- Runtime Dependencies: None (uses only Python standard library)
- Installation: `pip install .` or `python setup.py install`
- Testing: pytest
- No network access required during runtime

# Project Directory Structure

```
workspace/
├── pyproject.toml
├── setup.py
├── phonenumbers/
│   ├── __init__.py
│   ├── phonenumber.py
│   ├── phonenumberutil.py
│   ├── phonemetadata.py
│   ├── asyoutypeformatter.py
│   ├── phonenumbermatcher.py
│   ├── shortnumberinfo.py
│   ├── util.py
│   ├── unicode_util.py
│   ├── re_util.py
│   ├── data/
│   │   └── (metadata files)
│   ├── geodata/
│   │   └── (geocoding data)
│   ├── shortdata/
│   │   └── (short number data)
│   ├── carrierdata/
│   │   └── (carrier data)
│   └── tzdata/
│       └── (timezone data)
```

# API Usage Guide

## Module: `phonenumbers`

The root module exports the primary data classes, enumerations, and functions for phone number operations.

### Primary Data Class: `PhoneNumber`

Represents a phone number with structured metadata.

**Import:** `from phonenumbers import PhoneNumber`

**Attributes:**
- `country_code` (int or None): ITU country calling code (e.g., 1 for US/Canada, 44 for UK, 33 for France)
- `national_number` (long/int or None): National significant number without country code or formatting
- `extension` (str or None): Phone number extension (up to 40 digits)
- `italian_leading_zero` (bool or None): Whether the number has a leading zero that must be retained
- `number_of_leading_zeros` (int or None): Count of leading zeros to retain
- `raw_input` (str or None): Original input string if parsed with `keep_raw_input=True`
- `country_code_source` (int): Source from which country code was derived (CountryCodeSource enum value)
- `preferred_domestic_carrier_code` (str or None): Preferred carrier code for the number

**Example:**
```python
import phonenumbers
num = phonenumbers.parse("+442083661177", None)
print(num.country_code)  # 44
print(num.national_number)  # 2083661177
```

### Enumeration: `CountryCodeSource`

Indicates how the country code was determined during parsing.

**Import:** `from phonenumbers import CountryCodeSource`

**Values:**
- `CountryCodeSource.UNSPECIFIED` (0): Not set (parsed without raw input tracking)
- `CountryCodeSource.FROM_NUMBER_WITH_PLUS_SIGN` (1): From leading "+" (e.g., "+33 1 42 68 53 00")
- `CountryCodeSource.FROM_NUMBER_WITH_IDD` (5): From international dialing prefix (e.g., "011 33..." from US)
- `CountryCodeSource.FROM_NUMBER_WITHOUT_PLUS_SIGN` (10): From number without "+" but with country code
- `CountryCodeSource.FROM_DEFAULT_COUNTRY` (20): From default_country parameter (national format parsing)

### Enumeration: `PhoneNumberFormat`

Phone number formatting styles.

**Import:** `from phonenumbers import PhoneNumberFormat`

**Values:**
- `PhoneNumberFormat.E164` (0): E.164 format, no formatting, e.g., "+41446681800"
- `PhoneNumberFormat.INTERNATIONAL` (1): International format with spaces, e.g., "+41 44 668 1800"
- `PhoneNumberFormat.NATIONAL` (2): National format using local conventions, e.g., "044 668 1800"
- `PhoneNumberFormat.RFC3966` (3): RFC 3966 format with "tel:" prefix and hyphens, e.g., "tel:+41-44-668-1800"

### Enumeration: `PhoneNumberType`

Classification of phone number types.

**Import:** `from phonenumbers import PhoneNumberType`

**Values:**
- `PhoneNumberType.FIXED_LINE` (0): Fixed-line telephone
- `PhoneNumberType.MOBILE` (1): Mobile phone
- `PhoneNumberType.FIXED_LINE_OR_MOBILE` (2): Cannot distinguish (e.g., in the USA)
- `PhoneNumberType.TOLL_FREE` (3): Toll-free number
- `PhoneNumberType.PREMIUM_RATE` (4): Premium rate number
- `PhoneNumberType.SHARED_COST` (5): Shared cost between caller and recipient
- `PhoneNumberType.VOIP` (6): Voice over IP number
- `PhoneNumberType.PERSONAL_NUMBER` (7): Personal number routed to mobile or fixed-line
- `PhoneNumberType.PAGER` (8): Pager
- `PhoneNumberType.UAN` (9): Universal Access Number or Company Number
- `PhoneNumberType.VOICEMAIL` (10): Voice mail access number
- `PhoneNumberType.UNKNOWN` (99): Does not match any known pattern

### Exception: `NumberParseException`

Raised when phone number parsing fails.

**Import:** `from phonenumbers import NumberParseException`

**Attributes:**
- `error_type` (int): Error code indicating the failure reason
- `args[0]` (str): Human-readable error message

**Error Codes:**
- `NumberParseException.INVALID_COUNTRY_CODE` (0): Unsupported country code
- `NumberParseException.NOT_A_NUMBER` (1): String is not a valid number format
- `NumberParseException.TOO_SHORT_AFTER_IDD` (2): Too few digits after international prefix
- `NumberParseException.TOO_SHORT_NSN` (3): National number too short
- `NumberParseException.TOO_LONG` (4): Number exceeds maximum length

**Example:**
```python
import phonenumbers
try:
    num = phonenumbers.parse("123", "US")
except phonenumbers.NumberParseException as e:
    print(e.error_type)  # e.g., TOO_SHORT_NSN
    print(str(e))  # Human-readable message
```

### Function: `parse(numobj, region=None, keep_raw_input=False, numobj_type=None)`

Parse a phone number string into a PhoneNumber object.

**Import:** `from phonenumbers import parse`

**Parameters:**
- `numobj` (str): Phone number string to parse. Can include country code with "+" prefix, international dialing prefix (e.g., "011" from US), or be in national format.
- `region` (str or None): Two-letter ISO 3166-1 region code (e.g., "US", "GB", "FR"). Required when `numobj` lacks a country code. Use None when number includes a country code with "+".
- `keep_raw_input` (bool): If True, populates `raw_input` and `country_code_source` fields. Default False.
- `numobj_type` (str or None): Reserved for future use (phone number protocol buffers). Currently unused.

**Returns:** `PhoneNumber` object with parsed components.

**Raises:** `NumberParseException` if the string cannot be parsed into a valid phone number structure.

**Behavior:**
- Parses international format: `parse("+442083661177", None)` or `parse("+44 20 8366 1177", None)`
- Parses national format: `parse("020 8366 1177", "GB")` requires region hint
- Normalizes formatting: removes spaces, hyphens, parentheses, and other separators
- Extracts extensions: recognizes "ext", "x", ";ext=", and other extension markers
- Validates basic structure: minimum digit count, maximum length, valid characters

**Example:**
```python
import phonenumbers

# International format with country code
num1 = phonenumbers.parse("+14155552671", None)
# Result: country_code=1, national_number=4155552671

# National format with region hint
num2 = phonenumbers.parse("415-555-2671", "US")
# Result: country_code=1, national_number=4155552671

# With extension
num3 = phonenumbers.parse("+1 415-555-2671 ext 123", None)
# Result: extension="123"

# Parsing error
try:
    phonenumbers.parse("123", "US")  # Too short
except phonenumbers.NumberParseException as e:
    print(e.error_type)  # TOO_SHORT_NSN
```

### Function: `is_valid_number(numobj)`

Check whether a phone number is valid according to region-specific rules.

**Import:** `from phonenumbers import is_valid_number`

**Parameters:**
- `numobj` (PhoneNumber): Phone number object to validate

**Returns:** `bool` - True if the number is valid for its region, False otherwise

**Behavior:**
- Validates against ITU standards and country-specific numbering plans
- Checks digit length ranges defined for the region and number type
- More strict than `is_possible_number()`: validates both format and existence in numbering plan
- Returns False for numbers that are syntactically correct but not assigned in the region

**Example:**
```python
import phonenumbers

num = phonenumbers.parse("+14155552671", None)
is_valid = phonenumbers.is_valid_number(num)  # True for valid US number

invalid_num = phonenumbers.parse("+11234567890", None)
is_valid2 = phonenumbers.is_valid_number(invalid_num)  # False
```

### Function: `is_possible_number(numobj)`

Check whether a phone number is possible (has valid length).

**Import:** `from phonenumbers import is_possible_number`

**Parameters:**
- `numobj` (PhoneNumber): Phone number object to check

**Returns:** `bool` - True if the number length is plausible, False otherwise

**Behavior:**
- Validates only the length of the national significant number
- Less strict than `is_valid_number()`: does not check against numbering plan patterns
- Returns True if the number length falls within possible ranges for any number type in the region
- Faster than full validation when only length checking is needed

**Example:**
```python
import phonenumbers

num = phonenumbers.parse("+14155552671", None)
is_possible = phonenumbers.is_possible_number(num)  # True

short_num = phonenumbers.parse("+1415", None)
is_possible2 = phonenumbers.is_possible_number(short_num)  # False
```

### Function: `format_number(numobj, num_format)`

Format a phone number according to the specified format.

**Import:** `from phonenumbers import format_number, PhoneNumberFormat`

**Parameters:**
- `numobj` (PhoneNumber): Phone number to format
- `num_format` (int): Format style from PhoneNumberFormat enumeration

**Returns:** `str` - Formatted phone number string

**Behavior:**
- `E164` produces compact format without separators: "+41446681800"
- `INTERNATIONAL` adds spaces for readability: "+41 44 668 1800"
- `NATIONAL` uses local conventions (may include trunk prefix): "044 668 1800"
- `RFC3966` produces URI format with "tel:" prefix: "tel:+41-44-668-1800"
- Includes extension if present in the PhoneNumber object
- Deterministic: same input always produces same output for a given format

**Example:**
```python
import phonenumbers
from phonenumbers import PhoneNumberFormat

num = phonenumbers.parse("+442083661177", None)

e164 = phonenumbers.format_number(num, PhoneNumberFormat.E164)
# Result: "+442083661177"

intl = phonenumbers.format_number(num, PhoneNumberFormat.INTERNATIONAL)
# Result: "+44 20 8366 1177"

national = phonenumbers.format_number(num, PhoneNumberFormat.NATIONAL)
# Result: "020 8366 1177"

rfc = phonenumbers.format_number(num, PhoneNumberFormat.RFC3966)
# Result: "tel:+44-20-8366-1177"
```

### Function: `region_code_for_number(numobj)`

Get the region code (ISO 3166-1 two-letter country code) for a phone number.

**Import:** `from phonenumbers import region_code_for_number`

**Parameters:**
- `numobj` (PhoneNumber): Phone number to query

**Returns:** `str` or `None` - Two-letter region code (e.g., "US", "GB", "FR"), or None if the country code does not map to a region (e.g., non-geographic numbers) or is invalid.

**Behavior:**
- Maps country calling code to ISO region code
- Returns the primary region for countries with multiple region codes (e.g., "US" for country code 1)
- Returns None for non-geographic entities (e.g., satellite phones, international toll-free)
- Does not validate whether the number is actually valid for that region

**Example:**
```python
import phonenumbers

num1 = phonenumbers.parse("+442083661177", None)
region1 = phonenumbers.region_code_for_number(num1)  # "GB"

num2 = phonenumbers.parse("+14155552671", None)
region2 = phonenumbers.region_code_for_number(num2)  # "US"

num3 = phonenumbers.parse("+8001234567", None)  # Non-geographic
region3 = phonenumbers.region_code_for_number(num3)  # None
```

### Function: `is_valid_number_for_region(numobj, region)`

Check whether a phone number is valid for a specific region.

**Import:** `from phonenumbers import is_valid_number_for_region`

**Parameters:**
- `numobj` (PhoneNumber): Phone number to validate
- `region` (str): Two-letter ISO 3166-1 region code (e.g., "US", "GB")

**Returns:** `bool` - True if the number is valid for the specified region, False otherwise

**Behavior:**
- Validates that the number's country code matches the region
- Checks that the national number is valid within the region's numbering plan
- More specific than `is_valid_number()`: ensures the number belongs to the queried region
- Returns False if the number's country code does not match the region

**Example:**
```python
import phonenumbers

num = phonenumbers.parse("+442083661177", None)
valid_gb = phonenumbers.is_valid_number_for_region(num, "GB")  # True
valid_us = phonenumbers.is_valid_number_for_region(num, "US")  # False

us_num = phonenumbers.parse("+14155552671", None)
valid_us2 = phonenumbers.is_valid_number_for_region(us_num, "US")  # True
```

### Function: `number_type(numobj)`

Determine the type of a phone number (mobile, fixed-line, toll-free, etc.).

**Import:** `from phonenumbers import number_type, PhoneNumberType`

**Parameters:**
- `numobj` (PhoneNumber): Phone number to classify

**Returns:** `int` - PhoneNumberType enumeration value (0-10 or 99)

**Behavior:**
- Classifies based on the number prefix and region-specific patterns
- Returns `UNKNOWN` (99) if the number does not match any known type pattern
- Returns `FIXED_LINE_OR_MOBILE` (2) when the region does not distinguish (e.g., USA)
- Does not validate whether the number is actually valid; operates on pattern matching
- Deterministic: same number always returns same type

**Example:**
```python
import phonenumbers
from phonenumbers import PhoneNumberType

# US number (cannot distinguish fixed/mobile)
num1 = phonenumbers.parse("+14155552671", None)
type1 = phonenumbers.number_type(num1)
# Result: PhoneNumberType.FIXED_LINE_OR_MOBILE (2)

# UK mobile (identifiable by prefix)
num2 = phonenumbers.parse("+447911123456", None)
type2 = phonenumbers.number_type(num2)
# Result: PhoneNumberType.MOBILE (1)

# US toll-free
num3 = phonenumbers.parse("+18005551234", None)
type3 = phonenumbers.number_type(num3)
# Result: PhoneNumberType.TOLL_FREE (3)
```

# Implementation Notes

## Parsing and Normalization

- The `parse()` function normalizes input by removing whitespace, parentheses, hyphens, dots, and other formatting characters.
- Alpha characters (e.g., "1-800-FLOWERS") can be converted to digits using `convert_alpha_characters_in_number()` before parsing.
- International dialing prefixes (IDD) like "00" (Europe), "011" (US) are recognized and stripped during parsing.
- National prefixes (trunk codes) like "0" in many countries are handled according to region-specific rules.
- Extensions are extracted and stored separately; recognized markers include "ext", "extn", "x", ";ext=", "#", and others.

## Country Codes and Regions

- Country calling codes are defined by the ITU (International Telecommunication Union).
- Some country codes map to multiple regions (e.g., 1 for US, Canada, Caribbean; 44 for UK, Jersey, Guernsey).
- Non-geographic entities (e.g., satellite phones with +881) do not have region codes.
- The library includes comprehensive metadata for all ITU-defined country codes and regions.

## Validation Rules

- `is_possible_number()` checks only length constraints (fast, loose validation).
- `is_valid_number()` checks length and matches against region-specific patterns (slower, strict validation).
- A number can be possible but not valid (correct length, wrong pattern).
- A number cannot be valid if it is not possible.
- Validation does not verify whether a number is currently assigned or in service, only whether it conforms to the numbering plan.

## Number Types

- Number type classification is based on prefix patterns defined in regional metadata.
- In some regions (notably the USA and Canada), fixed-line and mobile numbers are indistinguishable by prefix alone.
- The returned type indicates what type the number could be, not definitively what it is.
- Type classification does not require the number to be valid; it works on any parseable number.

## Formatting Behavior

- E.164 format is the canonical international format: "+" followed by country code and national number, no spaces or separators.
- INTERNATIONAL format adds spaces for readability, following ITU-T E.123 recommendations adapted for local conventions.
- NATIONAL format represents how the number would be dialed domestically within its region (may include trunk prefix).
- RFC 3966 format is designed for use in URIs and includes the "tel:" scheme prefix.
- Formatting is deterministic and idempotent: formatting the same PhoneNumber multiple times produces identical output.

## PhoneNumber Object Immutability

- PhoneNumber objects are mutable Python objects but should be treated as immutable after parsing.
- Manually modifying attributes (country_code, national_number) can produce inconsistent state.
- Use `parse()` to create new PhoneNumber objects rather than modifying existing ones.

## Thread Safety

- The phonenumbers library is generally thread-safe for read operations (parsing, formatting, validation).
- Metadata is loaded lazily but is cached after first use.
- No global mutable state is modified during normal operations.

## Performance Considerations

- Parsing includes regex matching and metadata lookups; cache parsed PhoneNumber objects when possible.
- `is_possible_number()` is faster than `is_valid_number()` and sufficient for many use cases.
- Metadata for all regions is included in the package; the library does not require network access.

# Examples

## Basic Parsing and Formatting

```python
import phonenumbers
from phonenumbers import PhoneNumberFormat

# Parse international format
num = phonenumbers.parse("+14155552671", None)
print(num.country_code)        # 1
print(num.national_number)     # 4155552671

# Format in different styles
print(phonenumbers.format_number(num, PhoneNumberFormat.E164))
# Output: +14155552671

print(phonenumbers.format_number(num, PhoneNumberFormat.INTERNATIONAL))
# Output: +1 415-555-2671

print(phonenumbers.format_number(num, PhoneNumberFormat.NATIONAL))
# Output: (415) 555-2671
```

## Parsing National Format with Region

```python
import phonenumbers

# Parse national format (requires region)
num = phonenumbers.parse("020 8366 1177", "GB")
print(num.country_code)        # 44
print(num.national_number)     # 2083661177

# Get region from parsed number
region = phonenumbers.region_code_for_number(num)
print(region)  # GB
```

## Validation

```python
import phonenumbers

# Valid number
num1 = phonenumbers.parse("+442083661177", None)
print(phonenumbers.is_valid_number(num1))  # True
print(phonenumbers.is_possible_number(num1))  # True

# Invalid number (correct format, not in numbering plan)
num2 = phonenumbers.parse("+441111111111", None)
print(phonenumbers.is_valid_number(num2))  # False
print(phonenumbers.is_possible_number(num2))  # True (correct length)

# Too short number
num3 = phonenumbers.parse("+1415", None)
print(phonenumbers.is_possible_number(num3))  # False
```

## Number Type Classification

```python
import phonenumbers
from phonenumbers import PhoneNumberType

# US number (indistinguishable)
us_num = phonenumbers.parse("+14155552671", None)
us_type = phonenumbers.number_type(us_num)
print(us_type == PhoneNumberType.FIXED_LINE_OR_MOBILE)  # True

# UK mobile (identifiable)
uk_mobile = phonenumbers.parse("+447911123456", None)
uk_type = phonenumbers.number_type(uk_mobile)
print(uk_type == PhoneNumberType.MOBILE)  # True

# Toll-free
tollfree = phonenumbers.parse("+18005551234", None)
tollfree_type = phonenumbers.number_type(tollfree)
print(tollfree_type == PhoneNumberType.TOLL_FREE)  # True
```

## Region-Specific Validation

```python
import phonenumbers

# Parse number and validate for specific regions
num = phonenumbers.parse("+442083661177", None)

print(phonenumbers.is_valid_number_for_region(num, "GB"))  # True
print(phonenumbers.is_valid_number_for_region(num, "US"))  # False
print(phonenumbers.is_valid_number_for_region(num, "FR"))  # False
```

# Error Handling and Boundary Conditions

## Parsing Errors

```python
import phonenumbers
from phonenumbers import NumberParseException

# Too short number
try:
    phonenumbers.parse("123", "US")
except NumberParseException as e:
    print(e.error_type == NumberParseException.TOO_SHORT_NSN)  # True
    print(str(e))  # Descriptive error message

# Invalid country code
try:
    phonenumbers.parse("+999123456789", None)
except NumberParseException as e:
    print(e.error_type == NumberParseException.INVALID_COUNTRY_CODE)  # True

# Not a number
try:
    phonenumbers.parse("abc", "US")
except NumberParseException as e:
    print(e.error_type == NumberParseException.NOT_A_NUMBER)  # True

# Missing region for national format
try:
    phonenumbers.parse("4155552671", None)
except NumberParseException as e:
    print(e.error_type)  # Error type varies by exact input
```

## Empty and Invalid Inputs

```python
import phonenumbers

# Empty string
try:
    phonenumbers.parse("", "US")
except phonenumbers.NumberParseException:
    print("Cannot parse empty string")

# Only whitespace
try:
    phonenumbers.parse("   ", "US")
except phonenumbers.NumberParseException:
    print("Cannot parse whitespace-only string")

# Invalid region code
try:
    phonenumbers.parse("123456789", "XX")  # XX is not a valid region
except phonenumbers.NumberParseException:
    print("Invalid region code")
```

## Extensions

```python
import phonenumbers

# Number with extension
num = phonenumbers.parse("+1 415-555-2671 ext 123", None)
print(num.extension)  # "123"

# Extensions are included in formatted output
formatted = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
print(formatted)  # "+1 415-555-2671 ext. 123"
```

## Edge Cases

```python
import phonenumbers

# Very long extension
num1 = phonenumbers.parse("+14155552671 ext 1234567890123456789012345678901234567890", None)
print(num1.extension)  # Extensions up to 40 digits

# Leading zeros (Italian numbers)
num2 = phonenumbers.parse("+390612345678", None)
print(num2.italian_leading_zero)  # May be True for Italian fixed-line

# Numbers at maximum length
num3 = phonenumbers.parse("+123456789012345", None)  # 15 digits (ITU maximum)
print(phonenumbers.is_possible_number(num3))  # Depends on country code
```

## CountryCodeSource Tracking

```python
import phonenumbers
from phonenumbers import CountryCodeSource

# Parse with raw input tracking
num1 = phonenumbers.parse("+442083661177", None, keep_raw_input=True)
print(num1.country_code_source == CountryCodeSource.FROM_NUMBER_WITH_PLUS_SIGN)  # True
print(num1.raw_input)  # "+442083661177"

num2 = phonenumbers.parse("020 8366 1177", "GB", keep_raw_input=True)
print(num2.country_code_source == CountryCodeSource.FROM_DEFAULT_COUNTRY)  # True
print(num2.raw_input)  # "020 8366 1177"
```
