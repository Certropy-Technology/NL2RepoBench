# Project Description

`validators` is a Python library that provides simple validation functions for common data types and formats. It addresses the need for reliable, consistent validation of user inputs such as email addresses, URLs, IP addresses, domain names, financial identifiers (IBAN, credit cards), network addresses (MAC), unique identifiers (UUID), and string length constraints. 

The library provides validator functions that return `True` for valid inputs or a `ValidationError` object (which evaluates to `False` in boolean context) for invalid inputs. All validators are decorated with a common `@validator` decorator that handles error wrapping and optionally raises exceptions when requested via the `r_ve` parameter or `RAISE_VALIDATION_ERROR` environment variable.

# Natural Language Instruction

Implement a Python package named `validators` that provides validation functions for common data types. The package must:

1. Provide validation functions for email addresses, URLs, domains, IP addresses (IPv4/IPv6), IBAN codes, UUIDs, MAC addresses, credit card numbers, and string length
2. Return `True` for valid inputs or `ValidationError` objects (that evaluate to `False`) for invalid inputs
3. Support a common `@validator` decorator that handles error wrapping and exception raising
4. Implement a `ValidationError` exception class that stores function name, arguments, and optional reason message
5. Support optional exception raising via `r_ve` keyword argument or `RAISE_VALIDATION_ERROR` environment variable
6. Provide specialized credit card validators for Visa, Mastercard, American Express, Discover, JCB, Diners Club, UnionPay, and Mir
7. Support various validation options (CIDR notation for IPs, private/public IP checks, RFC compliance flags, TLD checking for domains)
8. Include proper packaging with `pyproject.toml` for setuptools-based builds

The package name is `validators`, the import name is `validators`, and it must be installable via pip with no runtime dependencies (uses only Python standard library: re, ipaddress, uuid, functools, inspect, os, pathlib, typing, urllib.parse).

# Supports (Environment Configuration)

- Python: 3.9+
- Package Manager: pip (setuptools build backend)
- Build System: `setuptools`
- Runtime Dependencies: None (uses only Python standard library)
- Installation: `pip install .`
- Testing: pytest
- No network access required during runtime

# Project Directory Structure

```
workspace/
├── pyproject.toml
├── src/
│   └── validators/
│       ├── __init__.py
│       ├── utils.py
│       ├── email.py
│       ├── url.py
│       ├── domain.py
│       ├── ip_address.py
│       ├── uuid.py
│       ├── mac_address.py
│       ├── iban.py
│       ├── card.py
│       ├── length.py
│       ├── between.py
│       └── _tld.txt
```

# API Usage Guide

## Module: `validators.utils`

### Class: `ValidationError`

Exception class raised or returned when validation fails.

```python
class ValidationError(Exception):
    """Exception class when validation failure occurs."""
    
    def __init__(self, function: Callable, arg_dict: Dict[str, Any], message: str = ""):
        """Initialize ValidationError with function, arguments, and optional message."""
        # Stores function as self.func
        # Stores arguments as instance attributes
        # Stores message as self.reason if provided
    
    def __repr__(self) -> str:
        """Returns string like 'ValidationError(func=funcname, args={...})'"""
    
    def __str__(self) -> str:
        """Returns same as __repr__"""
    
    def __bool__(self) -> bool:
        """Returns False so ValidationError evaluates to False in boolean context"""
```

**Behavior:**
- `func` attribute stores the validator function
- All arguments passed to the validator are stored as instance attributes
- If a `message` is provided, it's stored as `reason` attribute
- `__bool__` returns `False` so the error can be used in boolean expressions
- `__repr__` and `__str__` produce formatted error information

### Decorator: `validator`

```python
def validator(func: Callable) -> Callable:
    """Decorator that makes a function a validator.
    
    Wraps the function to:
    - Return True if function returns truthy value
    - Return ValidationError if function returns falsy value
    - Catch ValueError, TypeError, UnicodeError and wrap them in ValidationError
    - Raise ValidationError if r_ve=True kwarg or RAISE_VALIDATION_ERROR=True env var is set
    """
```

**Parameters:**
- `func`: Function to decorate

**Returns:**
- Wrapped function that returns `True` or `ValidationError` (or raises `ValidationError`)

**Behavior:**
- If decorated function returns truthy value: wrapper returns `True`
- If decorated function returns falsy value: wrapper returns `ValidationError`
- If `r_ve=True` keyword argument is passed: raises `ValidationError` instead of returning it
- If `RAISE_VALIDATION_ERROR` environment variable is `"True"`: raises `ValidationError`
- Catches `ValueError`, `TypeError`, `UnicodeError` and wraps them in `ValidationError`
- The `r_ve` parameter is removed from kwargs before calling the wrapped function

## Module: `validators`

All validator functions are exported from the main module and can be imported as:
```python
from validators import email, url, ipv4, ipv6, domain, uuid, mac_address, iban, length
```

### `email(value: str, /, *, ipv6_address: bool = False, ipv4_address: bool = False, simple_host: bool = False, rfc_1034: bool = False, rfc_2782: bool = False) -> Union[Literal[True], ValidationError]`

Validate an email address.

- **Parameters:**
  - `value` (str): Email string to validate
  - `ipv6_address` (bool): When the domain part is an IPv6 address (default: False)
  - `ipv4_address` (bool): When the domain part is an IPv4 address (default: False)
  - `simple_host` (bool): When the domain part is a simple hostname (default: False)
  - `rfc_1034` (bool): Allow trailing dot in domain name (default: False)
  - `rfc_2782` (bool): Domain name is of type service record (default: False)

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - Must contain exactly one `@` symbol
  - Username part (before @) must be ≤ 64 characters
  - Domain part (after @) must be ≤ 253 characters
  - Domain part must pass hostname validation
  - Username part must match email username regex (supports extended Latin characters, dot-atom, and quoted-string formats)
  - If `ipv6_address` or `ipv4_address` is True, domain must be wrapped in `[...]` brackets
  - Returns `False` for empty values

- **Examples:**
  ```python
  email('someone@example.com')  # True
  email('user@192.168.1.1', ipv4_address=True)  # True if wrapped in brackets
  email('bogus@@')  # ValidationError
  email('')  # ValidationError
  ```

### `url(value: str, /, *, skip_ipv6_addr: bool = False, skip_ipv4_addr: bool = False, may_have_port: bool = True, simple_host: bool = False, strict_query: bool = True, consider_tld: bool = False, private: Optional[bool] = None, rfc_1034: bool = False, rfc_2782: bool = False) -> Union[Literal[True], ValidationError]`

Validate a URL.

- **Parameters:**
  - `value` (str): URL string to validate
  - `skip_ipv6_addr` (bool): Reject IPv6 addresses (default: False)
  - `skip_ipv4_addr` (bool): Reject IPv4 addresses (default: False)
  - `may_have_port` (bool): Allow port numbers (default: True)
  - `simple_host` (bool): URL maybe only hyphens and alpha-numerals (default: False)
  - `strict_query` (bool): Fail on query string parsing error (default: True)
  - `consider_tld` (bool): Restrict domain to IANA TLDs (default: False)
  - `private` (Optional[bool]): IP address is public if False, private if True (default: None)
  - `rfc_1034` (bool): Allow trailing dot in domain/host (default: False)
  - `rfc_2782` (bool): Domain/Host is service record type (default: False)

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - Must not contain whitespace
  - Scheme must be one of: ftp, ftps, git, http, https, irc, rtmp, rtmps, rtsp, sftp, ssh, telnet
  - Netloc must pass hostname validation
  - Path must match allowed path characters (including Unicode)
  - Query string must be parseable (if present)
  - Fragment must match allowed fragment characters (if present)
  - Supports basic authentication (username:password@host)
  - Returns `False` for empty values

- **Examples:**
  ```python
  url('http://example.com')  # True
  url('https://user:pass@example.com:8080/path?query=1#frag')  # True
  url('ftp://ftp.example.com')  # True
  url('not a url')  # ValidationError
  ```

### `domain(value: str, /, *, consider_tld: bool = False, rfc_1034: bool = False, rfc_2782: bool = False) -> Union[Literal[True], ValidationError]`

Validate a domain name.

- **Parameters:**
  - `value` (str): Domain string to validate
  - `consider_tld` (bool): Restrict to IANA TLDs (default: False)
  - `rfc_1034` (bool): Allow trailing dot (default: False)
  - `rfc_2782` (bool): Allow underscores for service records (default: False)

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - Must match domain regex pattern
  - Each label must start and end with alphanumeric
  - Labels can contain hyphens (but not double underscores unless rfc_2782)
  - Supports IDN (internationalized domain names) via IDNA encoding
  - If `consider_tld=True`, TLD must be in IANA list
  - If `rfc_1034=True`, trailing dot is allowed
  - If `rfc_2782=True`, underscores are allowed
  - Returns `False` for empty values

- **Raises:** `UnicodeError` if value cannot be IDNA encoded/decoded

- **Examples:**
  ```python
  domain('example.com')  # True
  domain('sub.example.co.uk')  # True
  domain('xn----gtbspbbmkef.xn--p1ai')  # True (IDN)
  domain('example.com/')  # ValidationError
  domain('')  # ValidationError
  ```

### `ipv4(value: str, /, *, cidr: bool = True, strict: bool = False, private: Optional[bool] = None, host_bit: bool = True) -> Union[Literal[True], ValidationError]`

Validate an IPv4 address.

- **Parameters:**
  - `value` (str): IPv4 string to validate
  - `cidr` (bool): Allow CIDR notation (default: True)
  - `strict` (bool): Require CIDR notation (default: False)
  - `private` (Optional[bool]): Must be public (False) or private (True) (default: None = allow both)
  - `host_bit` (bool): Allow host bits set in CIDR (default: True)

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - Uses Python's `ipaddress.IPv4Address` or `IPv4Network`
  - Leading zeros are not allowed (Python 3.9.5+)
  - If `cidr=True`, allows `/prefix` notation
  - If `strict=True`, requires exactly one `/` in the value
  - If `private=False`, rejects private/local/loopback/broadcast ranges
  - If `private=True`, requires private/local/loopback/broadcast ranges
  - Private ranges: 10.0.0.0/8, 192.168.0.0/16, 172.16.0.0/12, 169.254.0.0/16, 127.0.0.0/8, 224.0.0.0/4
  - If `host_bit=False`, raises error if host bits are set in CIDR
  - Returns `False` for empty values

- **Examples:**
  ```python
  ipv4('192.168.1.1')  # True
  ipv4('10.0.0.0/8')  # True
  ipv4('192.168.1.1', private=True)  # True
  ipv4('8.8.8.8', private=True)  # ValidationError
  ipv4('999.999.999.999')  # ValidationError
  ```

### `ipv6(value: str, /, *, cidr: bool = True, strict: bool = False, host_bit: bool = True) -> Union[Literal[True], ValidationError]`

Validate an IPv6 address.

- **Parameters:**
  - `value` (str): IPv6 string to validate
  - `cidr` (bool): Allow CIDR notation (default: True)
  - `strict` (bool): Require CIDR notation (default: False)
  - `host_bit` (bool): Allow host bits set in CIDR (default: True)

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - Uses Python's `ipaddress.IPv6Address` or `IPv6Network`
  - Supports standard IPv6 notation including `::` compression
  - Supports IPv4-mapped IPv6 addresses (e.g., `::ffff:192.0.2.128`)
  - If `cidr=True`, allows `/prefix` notation
  - If `strict=True`, requires exactly one `/` in the value
  - If `host_bit=False`, raises error if host bits are set in CIDR
  - Returns `False` for empty values

- **Examples:**
  ```python
  ipv6('::1')  # True
  ipv6('2001:db8::8a2e:370:7334')  # True
  ipv6('::ffff:192.0.2.128')  # True (IPv4-mapped)
  ipv6('::1/128')  # True
  ipv6('not-an-ipv6')  # ValidationError
  ```

### `uuid(value: Union[str, UUID], /) -> Union[Literal[True], ValidationError]`

Validate a UUID (any version).

- **Parameters:**
  - `value` (str | uuid.UUID): UUID string or object to validate

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - Accepts `uuid.UUID` objects directly (returns True)
  - Accepts UUID strings in format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
  - Validates using `UUID()` constructor and regex pattern
  - Returns `False` for empty values

- **Examples:**
  ```python
  import uuid
  uuid('2bc1c94f-0deb-43e9-92a1-4775189ec9f8')  # True
  uuid(uuid.uuid4())  # True
  uuid('not-a-uuid')  # ValidationError
  uuid('')  # ValidationError
  ```

### `mac_address(value: str, /) -> Union[Literal[True], ValidationError]`

Validate a MAC address.

- **Parameters:**
  - `value` (str): MAC address string to validate

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - Format: `XX:XX:XX:XX:XX:XX` or `XX-XX-XX-XX-XX-XX`
  - Each `XX` is exactly 2 hexadecimal digits (case-insensitive)
  - Must have exactly 6 groups
  - Returns `False` for empty values

- **Examples:**
  ```python
  mac_address('01:23:45:67:ab:CD')  # True
  mac_address('01-23-45-67-ab-CD')  # True
  mac_address('00:00:00:00:00')  # ValidationError (5 groups)
  mac_address('')  # ValidationError
  ```

### `iban(value: str, /) -> Union[Literal[True], ValidationError]`

Validate an IBAN (International Bank Account Number).

- **Parameters:**
  - `value` (str): IBAN string to validate

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - Format: 2 letters (country code) + 2 digits (check digits) + 11-30 alphanumeric characters
  - Must pass mod-97 checksum validation
  - Case-insensitive
  - Returns `False` for empty values

- **Examples:**
  ```python
  iban('DE29100500001061045672')  # True
  iban('GB82WEST12345698765432')  # True
  iban('123456')  # ValidationError
  iban('')  # ValidationError
  ```

### `card_number(value: str, /) -> Union[Literal[True], ValidationError]`

Validate a generic credit card number using Luhn algorithm.

- **Parameters:**
  - `value` (str): Card number string to validate

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - Must contain only digits
  - Must pass Luhn checksum algorithm
  - Returns `False` for empty values

- **Examples:**
  ```python
  card_number('4242424242424242')  # True
  card_number('4242424242424241')  # ValidationError (wrong checksum)
  card_number('')  # ValidationError
  ```

### Credit Card Brand Validators

Each brand validator checks both Luhn validity and brand-specific patterns:

#### `visa(value: str, /) -> Union[Literal[True], ValidationError]`

- Must start with `4`
- Must be exactly 16 digits
- Must pass Luhn algorithm

#### `mastercard(value: str, /) -> Union[Literal[True], ValidationError]`

- Must start with `51-55` or `22-27`
- Must be exactly 16 digits
- Must pass Luhn algorithm

#### `amex(value: str, /) -> Union[Literal[True], ValidationError]`

- Must start with `34` or `37`
- Must be exactly 15 digits
- Must pass Luhn algorithm

#### `discover(value: str, /) -> Union[Literal[True], ValidationError]`

- Must start with `60`, `64`, or `65`
- Must be exactly 16 digits
- Must pass Luhn algorithm

#### `jcb(value: str, /) -> Union[Literal[True], ValidationError]`

- Must start with `35`
- Must be exactly 16 digits
- Must pass Luhn algorithm

#### `diners(value: str, /) -> Union[Literal[True], ValidationError]`

- Must start with `30`, `36`, `38`, or `39`
- Must be 14 or 16 digits
- Must pass Luhn algorithm

#### `unionpay(value: str, /) -> Union[Literal[True], ValidationError]`

- Must start with `62`
- Must be exactly 16 digits
- Must pass Luhn algorithm

#### `mir(value: str, /) -> Union[Literal[True], ValidationError]`

- Must start with `2200-2204`
- Must be exactly 16 digits
- Must pass Luhn algorithm

**Examples:**
```python
visa('4242424242424242')  # True
mastercard('5555555555554444')  # True
amex('378282246310005')  # True
visa('5555555555554444')  # ValidationError (not a Visa pattern)
```

### `length(value: str, /, *, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Union[Literal[True], ValidationError]`

Validate string length is within range.

- **Parameters:**
  - `value` (str): String to validate
  - `min_val` (Optional[int]): Minimum length (default: None = no minimum)
  - `max_val` (Optional[int]): Maximum length (default: None = no maximum)

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - If `min_val` is set, `len(value)` must be >= `min_val`
  - If `max_val` is set, `len(value)` must be <= `max_val`
  - Both can be set simultaneously

- **Raises:** `ValueError` if `min_val` or `max_val` is negative

- **Examples:**
  ```python
  length('hello', min_val=2)  # True
  length('hello', min_val=5, max_val=5)  # True
  length('hello', max_val=3)  # ValidationError
  length('test', min_val=-1)  # Raises ValueError
  ```

### `between(value: Union[int, float], /, *, min_val: Optional[Union[int, float]] = None, max_val: Optional[Union[int, float]] = None) -> Union[Literal[True], ValidationError]`

Validate a number is within range.

- **Parameters:**
  - `value` (int | float): Number to validate
  - `min_val` (Optional[int | float]): Minimum value (default: None = no minimum)
  - `max_val` (Optional[int | float]): Maximum value (default: None = no maximum)

- **Returns:** `True` if valid, `ValidationError` if invalid

- **Validation Rules:**
  - If `min_val` is set, `value` must be >= `min_val`
  - If `max_val` is set, `value` must be <= `max_val`
  - Both can be set simultaneously

- **Examples:**
  ```python
  between(5, min_val=1, max_val=10)  # True
  between(5, min_val=10)  # ValidationError
  between(5.5, min_val=5.0, max_val=6.0)  # True
  ```

# Implementation Notes

## Validator Decorator Pattern

The `@validator` decorator provides consistent error handling across all validators:

1. Wraps validator functions to return `True` or `ValidationError`
2. Catches common exceptions (`ValueError`, `TypeError`, `UnicodeError`) and wraps them
3. Supports exception raising mode via `r_ve` parameter or environment variable
4. The `r_ve` keyword is consumed by the decorator and not passed to the wrapped function

## ValidationError Behavior

The `ValidationError` class has special behaviors:

- `__bool__` returns `False` so it can be used directly in conditionals
- Stores the validator function and all arguments as instance attributes
- Optional `reason` attribute for exception messages
- String representation shows function name and arguments

## Module Exports

The `__init__.py` must export all validator functions and the utility classes:

```python
from .utils import ValidationError, validator
from .email import email
from .url import url
from .domain import domain
from .ip_address import ipv4, ipv6
from .uuid import uuid
from .mac_address import mac_address
from .iban import iban
from .card import card_number, visa, mastercard, amex, discover, jcb, diners, unionpay, mir
from .length import length
from .between import between

__all__ = (
    "ValidationError", "validator",
    "email", "url", "domain",
    "ipv4", "ipv6", "uuid", "mac_address", "iban",
    "card_number", "visa", "mastercard", "amex", "discover", "jcb", "diners", "unionpay", "mir",
    "length", "between"
)

__version__ = "0.35.0"
```

## IBAN Mod-97 Validation

IBAN validation uses the mod-97 checksum algorithm:

1. Rearrange: move first 4 characters to the end
2. Replace each letter with its numeric value (A=10, B=11, ..., Z=35)
3. Calculate the resulting integer modulo 97
4. Valid if result equals 1

## Luhn Algorithm for Credit Cards

The Luhn checksum algorithm for card validation:

1. From rightmost digit, double every second digit
2. If doubling results in two digits, add them together
3. Sum all digits (doubled and non-doubled)
4. Valid if sum modulo 10 equals 0

## IP Address Private Ranges

IPv4 private/local ranges that affect `private` parameter:

- `10.0.0.0/8` - Private
- `192.168.0.0/16` - Private
- `172.16.0.0/12` - Private (172.16-172.31)
- `169.254.0.0/16` - Link-local
- `127.0.0.0/8` - Localhost/loopback
- `224.0.0.0/4` - Multicast/broadcast (224-255)

## TLD Validation

When `consider_tld=True` in domain/url validators:

- Reads TLD list from `_tld.txt` file
- Checks if domain's TLD is in IANA registry
- Popular TLDs are cached for performance
- Full TLD list can be cached via `PYVLD_CACHE_TLD=True` environment variable

## URL Scheme Validation

Valid URL schemes: `ftp`, `ftps`, `git`, `http`, `https`, `irc`, `rtmp`, `rtmps`, `rtsp`, `sftp`, `ssh`, `telnet`

## Exception Raising Mode

Two ways to make validators raise exceptions instead of returning ValidationError:

1. Pass `r_ve=True` keyword argument: `email('bad@', r_ve=True)`  # Raises
2. Set `RAISE_VALIDATION_ERROR=True` environment variable (affects all validators)

## Type Validation

Validators are strict about input types:

- String validators (`email`, `url`, etc.) expect string input
- Number validators (`between`) expect int or float
- `uuid` accepts both string and `uuid.UUID` object
- Wrong types result in `ValidationError` (caught `TypeError` or explicit check)

## Empty Input Handling

All validators return `False` (wrapped as `ValidationError`) for empty strings, None, or missing values.

## Dependency on Other Validators

Some validators call other validators internally:

- `email` calls `hostname` for domain validation
- `url` calls `hostname` for netloc validation
- `length` calls `between` for range checking
- Card brand validators (`visa`, `mastercard`, etc.) call `card_number` for Luhn validation

## IDNA Encoding for Domains

Domains with international characters are validated by:

1. Encoding to IDNA (ASCII-compatible encoding)
2. Decoding back to UTF-8
3. Applying regex validation on the result
4. If encoding/decoding fails, raises `UnicodeError`

# Examples

## Basic Validation

```python
import validators

# Email validation
if validators.email('user@example.com'):
    print("Valid email")

# URL validation
result = validators.url('https://example.com/path')
if result:
    print("Valid URL")
else:
    print(f"Invalid: {result}")  # Prints ValidationError details
```

## Using Exception Mode

```python
import validators

try:
    validators.email('bad-email', r_ve=True)
except validators.ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Function: {e.func.__name__}")
    print(f"Value: {e.value}")
```

## IP Address with Private Check

```python
import validators

# Accept only public IPs
validators.ipv4('8.8.8.8', private=False)  # True
validators.ipv4('192.168.1.1', private=False)  # ValidationError

# Accept only private IPs
validators.ipv4('192.168.1.1', private=True)  # True
validators.ipv4('8.8.8.8', private=True)  # ValidationError
```

## Credit Card Validation

```python
import validators

# Generic card validation
validators.card_number('4242424242424242')  # True

# Brand-specific validation
validators.visa('4242424242424242')  # True
validators.mastercard('4242424242424242')  # ValidationError (wrong prefix)

# American Express has 15 digits
validators.amex('378282246310005')  # True
```

## String Length Validation

```python
import validators

# Minimum length
validators.length('hello', min_val=3)  # True
validators.length('hi', min_val=3)  # ValidationError

# Exact length
validators.length('test', min_val=4, max_val=4)  # True

# Maximum length
validators.length('short', max_val=10)  # True
validators.length('very long string', max_val=5)  # ValidationError
```

# Error Handling and Boundary Conditions

## Empty and None Values

```python
import validators

validators.email('')  # ValidationError
validators.email(None)  # ValidationError (caught TypeError)
validators.ipv4('')  # ValidationError
validators.uuid('')  # ValidationError
```

## Invalid Types

```python
import validators

validators.email(123)  # ValidationError (caught TypeError)
validators.ipv4(['not', 'a', 'string'])  # ValidationError
validators.length(123, min_val=1)  # ValidationError (expects string)
```

## Edge Cases for IP Addresses

```python
import validators

# CIDR notation
validators.ipv4('192.168.1.0/24')  # True
validators.ipv4('192.168.1.1', cidr=False)  # True
validators.ipv4('192.168.1.1', strict=True)  # ValidationError (strict requires /)

# IPv6 compression
validators.ipv6('::1')  # True (localhost)
validators.ipv6('2001:db8::1')  # True (compressed)
validators.ipv6('::ffff:192.0.2.1')  # True (IPv4-mapped)
```

## IBAN Checksum Validation

```python
import validators

# Valid IBAN with correct checksum
validators.iban('DE89370400440532013000')  # True

# Invalid checksum
validators.iban('DE00370400440532013000')  # ValidationError

# Wrong format
validators.iban('DEXX370400440532013000')  # ValidationError (check digits must be numeric)
```

## Domain TLD Validation

```python
import validators

# Without TLD checking
validators.domain('example.xyz')  # True

# With TLD checking (if xyz is in IANA list)
validators.domain('example.xyz', consider_tld=True)  # True if xyz is valid TLD

# Invalid TLD
validators.domain('example.invalidtld', consider_tld=True)  # ValidationError if not in IANA
```

## URL Special Characters

```python
import validators

# Unicode in path
validators.url('http://example.com/путь')  # True

# Query string with special characters
validators.url('http://example.com/path?key=value&foo=bar')  # True

# Fragment
validators.url('http://example.com/path#section')  # True

# Basic auth
validators.url('http://user:password@example.com')  # True

# Whitespace not allowed
validators.url('http://example.com/path with spaces')  # ValidationError
```

## Length Validator Edge Cases

```python
import validators

# Negative min/max raises ValueError
try:
    validators.length('test', min_val=-1)
except ValueError as e:
    print("Cannot use negative length")

# None means no constraint
validators.length('any', min_val=None, max_val=None)  # True
validators.length('', min_val=0, max_val=0)  # True (empty string has length 0)
```

## ValidationError Boolean Behavior

```python
import validators

result = validators.email('invalid')
print(bool(result))  # False
print(result == False)  # False (ValidationError is not False, just falsy)
print(not result)  # True

if not validators.email('bad'):
    print("Validation failed")  # This prints
```
