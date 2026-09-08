# Trafaret - Data Validation and Transformation Library

## Project Description

Trafaret is a Python data validation and transformation library that provides a declarative way to define schemas for validating and converting data structures. It is designed to work with configuration files, API inputs, and foreign data sources where strict validation and type conversion are required.

The library supports:
- Basic type validators (Int, String, Float, Bool, etc.)
- Type converters (ToInt, ToFloat, ToBool, etc.)
- Container validators (List, Dict, Tuple, Mapping, Iterable)
- Combinators (Or, And, Forward for recursive structures)
- String pattern matching (Regexp, Email, URL, IPv4, IPv6)
- Custom validation functions and transformations
- Detailed error reporting with nested error structures

The project **excludes** runtime network access, database connectors, and async validation (aiohttp integration is not included in this implementation).

## Natural Language Instruction

Build a Python package named `trafaret` that provides comprehensive data validation and transformation capabilities. The package must:

1. **Basic Validators**: Implement `Int`, `Float`, `String`, `Bool`, `Null`, `Any` validators that check types strictly
2. **Type Converters**: Implement `ToInt`, `ToFloat`, `ToBool` that convert string/compatible types to target types
3. **Container Validators**: Implement `List`, `Dict`, `Tuple`, `Mapping`, `Iterable` for validating collections
4. **Combinators**: Implement `Or` (try multiple validators), `And` (chain validators), `Forward` (recursive structures)
5. **String Validators**: Implement `Regexp`, `RegexpRaw`, `Email`, `URL`, `IPv4`, `IPv6`, `Hex` for pattern matching
6. **Dictionary Keys**: Implement `Key` class with `optional`, `default`, and renaming support
7. **Transformations**: Support `>>` operator for transforming validated values
8. **Error Handling**: Implement `DataError` exception with nested error structure and `as_dict()` method
9. **Decorators**: Implement `@guard` decorator for function argument validation
10. **Utilities**: Implement `Call`, `Type`, `Enum`, `Callable` validators

The package must be installable with `pip install -e .` and importable as `import trafaret`.

All validators must work offline (no network access during validation). The library must be deterministic and thread-safe for concurrent validation calls.

## Environment Configuration (Supports)

- **Language**: Python 3.12
- **Package Manager**: pip
- **Build System**: setuptools
- **Installation**: `python -m pip install --no-build-isolation --no-deps --no-index -e .`
- **Runtime Dependencies**: None (pure Python, standard library only)
- **Network Mode**: no-network (all validation runs offline)
- **Python Version Requirement**: >= 3.6 (specified in setup.py)

The package uses a standard `setup.py` with setuptools backend. No external dependencies are required at runtime.

## Project Directory Structure

```
workspace/
├── setup.py                    # Package installation metadata
├── setup.cfg                   # Build configuration
├── LICENSE.txt                 # BSD-2-Clause license
├── README.rst                  # Package documentation
├── MANIFEST.in                 # Package manifest
└── trafaret/                   # Main package directory
    ├── __init__.py             # Package exports and version
    ├── base.py                 # Core Trafaret base class and main validators
    ├── numeric.py              # Numeric validators (Int, Float, ToInt, ToFloat, ToDecimal)
    ├── regexp.py               # Regular expression validators
    ├── internet.py             # Internet validators (Email, URL, IP addresses)
    ├── dataerror.py            # DataError exception class
    ├── keys.py                 # Dict Key class for schema definitions
    ├── utils.py                # Utility functions and helpers
    ├── lib.py                  # Additional library functions
    ├── codes.py                # Error code constants
    ├── constructor.py          # Constructor utilities
    ├── async_mixins.py         # Async support mixins (not tested in this task)
    └── contrib/                # Contrib modules (optional extensions)
        ├── __init__.py
        ├── object_id.py        # MongoDB ObjectId validator (optional)
        └── rfc_3339.py         # RFC 3339 date validator (optional)
```

## API Usage Guide

### Core Trafaret Class

All validators inherit from the `Trafaret` base class which provides:

- `check(value, context=None)`: Validate and return the value, or raise `DataError`
- `__call__(value)`: Shorthand for `check(value)`
- `transform(value, context=None)`: Transform the value (with context support)

### Basic Type Validators

Import from `trafaret`:

```python
import trafaret as t
```

#### Int() - Integer Validator

Validates that value is an integer (not float, not string).

```python
t.Int().check(42)          # Returns: 42
t.Int().check(3.14)        # Raises: DataError("value can't be converted to int")
t.Int().check("42")        # Raises: DataError("value can't be converted to int")
```

Parameters: `gt`, `gte`, `lt`, `lte` for range validation (optional).

#### Float() - Float Validator

Validates floats and accepts integers (converts them to float).

```python
t.Float().check(3.14)      # Returns: 3.14
t.Float().check(42)        # Returns: 42.0
t.Float().check("3.14")    # Raises: DataError
```

Parameters: `gt`, `gte`, `lt`, `lte` for range validation (optional).

#### String() - String Validator

Validates that value is a string (strict type check).

```python
t.String().check("hello")                    # Returns: "hello"
t.String().check(123)                        # Raises: DataError("value is not a string")
t.String(min_length=3).check("hi")           # Raises: DataError
t.String(max_length=5).check("hello")        # Returns: "hello"
t.String(max_length=3).check("hello")        # Raises: DataError
```

Parameters:
- `min_length`: Minimum string length (optional)
- `max_length`: Maximum string length (optional)
- `allow_blank`: Allow empty strings (default: True)

#### Bool() - Boolean Validator

Strictly validates boolean values (True or False only).

```python
t.Bool().check(True)       # Returns: True
t.Bool().check(False)      # Returns: False
t.Bool().check(1)          # Raises: DataError("value should be True or False")
t.Bool().check("yes")      # Raises: DataError
```

#### Null() - None Validator

Validates that value is None.

```python
t.Null().check(None)       # Returns: None
t.Null().check("")         # Raises: DataError
```

#### Any() - Accept Any Value

Accepts any value without validation.

```python
t.Any().check({"any": "thing"})    # Returns: {"any": "thing"}
t.Any().check([1, 2, 3])           # Returns: [1, 2, 3]
t.Any().check(None)                # Returns: None
```

### Type Converters

#### ToInt() - Convert to Integer

Converts strings and compatible types to integers.

```python
t.ToInt().check("42")      # Returns: 42 (int)
t.ToInt().check(42)        # Returns: 42
t.ToInt().check("abc")     # Raises: DataError("value can't be converted to int")
```

#### ToFloat() - Convert to Float

Converts strings and numbers to floats.

```python
t.ToFloat().check("3.14")  # Returns: 3.14 (float)
t.ToFloat().check(42)      # Returns: 42.0
t.ToFloat().check("abc")   # Raises: DataError
```

#### ToBool() - Convert to Boolean

Converts string representations to boolean.

```python
t.ToBool().check("yes")    # Returns: True
t.ToBool().check("no")     # Returns: False
t.ToBool().check("true")   # Returns: True
t.ToBool().check("false")  # Returns: False
t.ToBool().check("1")      # Returns: True
t.ToBool().check("0")      # Returns: False
t.ToBool().check("on")     # Returns: True
t.ToBool().check("off")    # Returns: False
```

Accepted true values: "true", "True", "yes", "Yes", "y", "Y", "1", "on", "On"
Accepted false values: "false", "False", "no", "No", "n", "N", "0", "off", "Off"

### Container Validators

#### List(item_validator) - List Validator

Validates that value is a list and each element matches the item validator.

```python
t.List(t.Int).check([1, 2, 3])           # Returns: [1, 2, 3]
t.List(t.String).check(["a", "b"])       # Returns: ["a", "b"]
t.List(t.Int).check([1, "two", 3])       # Raises: DataError with index 1 error
t.List(t.Int).check([])                  # Returns: []
```

Parameters:
- `min_length`: Minimum list length (optional)
- `max_length`: Maximum list length (optional)

#### Dict({Key: Validator, ...}) - Dictionary Validator

Validates dictionary structure with typed keys.

```python
from trafaret import Dict, Key, String, Int

schema = Dict({
    Key('name'): String,
    Key('age'): Int
})
schema.check({'name': 'John', 'age': 30})  # Returns: {'name': 'John', 'age': 30}
schema.check({'name': 'John'})              # Raises: DataError (missing 'age')
```

**Key Options:**

- `Key('name', optional=True)`: Key is optional, omitted if not present
- `Key('name', default=value)`: Use default value if key is missing
- `Key('old_name', to_name='new_name')` or `Key('old') >> 'new'`: Rename key in output

**Dict Methods:**

- `.allow_extra(*keys)`: Allow and include extra keys in output
  ```python
  Dict({Key('name'): String}).allow_extra('*').check({'name': 'John', 'extra': 'data'})
  # Returns: {'name': 'John', 'extra': 'data'}
  ```

- `.ignore_extra(*keys)`: Allow but exclude extra keys from output
  ```python
  Dict({Key('name'): String}).ignore_extra('*').check({'name': 'John', 'extra': 'data'})
  # Returns: {'name': 'John'}
  ```

#### Tuple(validator1, validator2, ...) - Tuple Validator

Validates fixed-length tuples with typed positions.

```python
t.Tuple(t.String, t.Int, t.Float).check(('hello', 42, 3.14))
# Returns: ('hello', 42, 3.14)

t.Tuple(t.String, t.Int).check(('hello',))
# Raises: DataError (wrong length)

t.Tuple(t.String, t.Int).check(('hello', 'world'))
# Raises: DataError (type mismatch at position 1)
```

#### Mapping(key_validator, value_validator) - Mapping Validator

Validates dict-like objects where all keys and values match their respective validators.

```python
t.Mapping(t.String, t.Int).check({'a': 1, 'b': 2})
# Returns: {'a': 1, 'b': 2}

t.Mapping(t.String, t.Int).check({123: 1})
# Raises: DataError (key type mismatch)

t.Mapping(t.String, t.Int).check({'a': 'not_int'})
# Raises: DataError (value type mismatch)
```

#### Iterable(item_validator) - Iterable Validator

Like List but accepts any iterable (list, tuple, generator, etc.).

```python
t.Iterable(t.Int).check([1, 2, 3])          # Returns: [1, 2, 3]
t.Iterable(t.String).check(('a', 'b', 'c'))  # Returns: ['a', 'b', 'c']
```

### Combinators

#### Or(validator1, validator2, ...) - Try Multiple Validators

Returns the first successful validation result.

```python
t.Or(t.Int, t.String).check(42)        # Returns: 42
t.Or(t.Int, t.String).check("hello")   # Returns: "hello"
t.Or(t.Int, t.String).check([])        # Raises: DataError (no match)
```

#### And(validator1, validator2) or validator1 & validator2 - Chain Validators

Applies validators in sequence.

```python
(t.Int() & (lambda x: x > 0)).check(5)    # Returns: True
(t.Int() & (lambda x: x > 0)).check(-5)   # Raises: DataError
```

#### Forward() - Recursive Structures

Allows defining recursive schemas.

```python
node = t.Forward()
node << t.Dict({
    Key('value'): t.Int,
    Key('next', optional=True): node
})
node.check({'value': 1, 'next': {'value': 2}})
# Returns: {'value': 1, 'next': {'value': 2}}
```

Use `<<` operator to assign the schema to the Forward reference.

### Transformation (>>)

Use `>>` operator to transform validated values:

```python
upper = t.String() >> (lambda s: s.upper())
upper.check("hello")  # Returns: "HELLO"

double = t.Int() >> (lambda x: x * 2)
double.check(21)  # Returns: 42
```

### String Pattern Validators

#### Regexp(pattern) - Match Regular Expression

Validates string matches the regex pattern.

```python
t.Regexp(r'^[a-z]+$').check("hello")     # Returns: "hello"
t.Regexp(r'^[a-z]+$').check("Hello123")  # Raises: DataError
```

#### RegexpRaw(pattern) - Extract Match Object

Returns the regex match object (useful with transformation).

```python
extractor = t.RegexpRaw(r'name=(\w+)') >> (lambda m: m.group(1))
extractor.check('name=Alice')  # Returns: "Alice"
```

#### Email - Email Validator

Validates email addresses (class property, not instantiated).

```python
t.Email.check('user@example.com')    # Returns: 'user@example.com'
t.Email.check('not_an_email')        # Raises: DataError
```

#### URL - URL Validator

Validates URLs (class property, not instantiated).

```python
t.URL.check('https://example.com')   # Returns: 'https://example.com'
t.URL.check('not a url')             # Raises: DataError
```

#### IPv4 - IPv4 Address Validator

Validates IPv4 addresses.

```python
t.IPv4.check('192.168.1.1')          # Returns: '192.168.1.1'
t.IPv4.check('999.999.999.999')      # Raises: DataError
```

#### IPv6 - IPv6 Address Validator

Validates IPv6 addresses.

```python
t.IPv6.check('2001:0db8:85a3:0000:0000:8a2e:0370:7334')  # Returns: valid IPv6
t.IPv6.check('invalid')              # Raises: DataError
```

#### Hex() - Hexadecimal String Validator

Validates hexadecimal strings.

```python
t.Hex().check('deadbeef')            # Returns: 'deadbeef'
t.Hex().check('not_hex')             # Raises: DataError
```

### Other Validators

#### Enum(value1, value2, ...) - Enumeration Validator

Validates value is one of the allowed values.

```python
t.Enum('apple', 'banana', 'cherry').check('apple')    # Returns: 'apple'
t.Enum('apple', 'banana').check('orange')             # Raises: DataError("value doesn't match any variant")
t.Enum(1, 2, 3).check(2)                               # Returns: 2
```

#### Type(type_class) - Type Check Validator

Validates value is an instance of the specified type.

```python
t.Type(int).check(42)            # Returns: 42
t.Type(str).check("hello")       # Returns: "hello"
t.Type(int).check("not_int")     # Raises: DataError
```

#### Callable() - Callable Validator

Validates value is callable (function, lambda, method, callable object).

```python
def f(): pass
t.Callable().check(f)            # Returns: f (the function object)
t.Callable().check(lambda: None) # Returns: the lambda function
t.Callable().check(42)           # Raises: DataError
```

#### Call(function) - Custom Validation Function

Applies a custom function for validation/transformation.

```python
def double(x):
    return x * 2

t.Call(double).check(21)  # Returns: 42
```

The function can return a value (success) or return/raise `DataError(message)` for failure.

```python
def check_positive(x):
    if x > 0:
        return x
    return t.DataError('must be positive')

t.Call(check_positive).check(5)    # Returns: 5
t.Call(check_positive).check(-5)   # Raises: DataError('must be positive')
```

### Utilities and Decorators

#### @guard Decorator

Validates function arguments using trafarets.

```python
@t.guard(x=t.Int, y=t.String)
def my_function(x, y):
    return f"{y}: {x}"

my_function(x=42, y="answer")     # Returns: "answer: 42"
my_function(x="invalid", y="answer")  # Raises: DataError
```

The decorator validates arguments before the function executes.

#### DataError Exception

Raised when validation fails. Contains:
- `error`: The error value or nested error dict
- `value`: The value that failed validation
- `trafaret`: The trafaret that raised the error
- `.as_dict()`: Returns a dictionary representation of nested errors

```python
try:
    t.Dict({Key('age'): t.Int}).check({'age': 'invalid'})
except t.DataError as e:
    print(e)              # {'age': DataError("value can't be converted to int")}
    print(e.as_dict())    # {'age': "value can't be converted to int"}
```

## Implementation Notes

### Type Validation Strictness

- `Int()` only accepts actual integers, not floats or strings
- `String()` only accepts strings, not integers or other types
- `Bool()` only accepts True or False, not 1/0 or "yes"/"no"
- Use `ToInt()`, `ToFloat()`, `ToBool()` for type conversion

### Error Handling

DataError exceptions contain nested error structures for containers:
- Dict errors: `{'key_name': DataError(...)}`
- List errors: `{index: DataError(...)}`
- Use `.as_dict()` method to get a serializable error structure

### Dict Key Behavior

- Keys without `optional=True` are required
- Keys with `default=value` insert the default if missing
- Keys with `optional=True` are omitted from output if not present
- Use `.allow_extra('*')` to include extra keys
- Use `.ignore_extra('*')` to silently drop extra keys
- By default, extra keys raise validation errors

### Determinism and State

All validators are stateless and deterministic:
- Same input always produces same output
- No hidden state or caching between calls
- Thread-safe for concurrent validation

### No Network Access

All validators work offline:
- Email/URL validation is pattern-based (regex)
- No DNS lookups, no external service calls
- IPv4/IPv6 validation is format-based only

## Examples

### Basic Schema Validation

```python
import trafaret as t

user_schema = t.Dict({
    t.Key('username'): t.String(min_length=3, max_length=20),
    t.Key('email'): t.Email,
    t.Key('age'): t.Int(gte=0, lte=150),
    t.Key('active', default=True): t.Bool,
    t.Key('tags', optional=True): t.List(t.String)
})

# Valid input
user = user_schema.check({
    'username': 'john_doe',
    'email': 'john@example.com',
    'age': 30
})
# Returns: {'username': 'john_doe', 'email': 'john@example.com', 'age': 30, 'active': True}

# Invalid input
try:
    user_schema.check({'username': 'jd', 'email': 'invalid', 'age': -5})
except t.DataError as e:
    print(f"Validation errors: {e.as_dict()}")
```

### Nested Schema

```python
import trafaret as t

address_schema = t.Dict({
    t.Key('street'): t.String,
    t.Key('city'): t.String,
    t.Key('zipcode'): t.String
})

person_schema = t.Dict({
    t.Key('name'): t.String,
    t.Key('address'): address_schema,
    t.Key('phones'): t.List(t.String)
})

person = person_schema.check({
    'name': 'Alice',
    'address': {
        'street': '123 Main St',
        'city': 'Boston',
        'zipcode': '02101'
    },
    'phones': ['555-1234', '555-5678']
})
```

### Type Conversion

```python
import trafaret as t

# Convert form data to proper types
form_schema = t.Dict({
    t.Key('quantity'): t.ToInt(),
    t.Key('price'): t.ToFloat(),
    t.Key('enabled'): t.ToBool()
})

result = form_schema.check({
    'quantity': '5',
    'price': '19.99',
    'enabled': 'yes'
})
# Returns: {'quantity': 5, 'price': 19.99, 'enabled': True}
```

### Polymorphic Data

```python
import trafaret as t

# Accept either a string ID or an integer ID
id_validator = t.Or(t.Int, t.String)

id_validator.check(123)      # Returns: 123
id_validator.check("abc-def") # Returns: "abc-def"
```

## Error Handling and Boundary Conditions

### Empty Inputs

- Empty strings: `String().check("")` succeeds by default
- Empty lists: `List(T).check([])` succeeds
- Missing optional keys: Omitted from output if `optional=True`
- None values: Only `Null()` or `Any()` accept None

### Invalid Types

All strict validators raise `DataError` when type doesn't match:
```python
t.Int().check("42")          # DataError: "value can't be converted to int"
t.String().check(42)         # DataError: "value is not a string"
t.Bool().check(1)            # DataError: "value should be True or False"
```

### Range Violations

Validators with range constraints raise errors:
```python
t.String(max_length=5).check("toolong")  # DataError
t.Int(gt=0).check(-5)                    # DataError
t.List(max_length=3).check([1,2,3,4])    # DataError
```

### Nested Errors

Container validators preserve error location:
```python
try:
    t.List(t.Int).check([1, "invalid", 3])
except t.DataError as e:
    print(e.as_dict())  # {1: "value can't be converted to int"}
```

### Pattern Mismatch

String pattern validators raise on mismatch:
```python
t.Email.check("not_an_email")          # DataError
t.IPv4.check("999.999.999.999")        # DataError
t.Regexp(r'^\d+$').check("abc")        # DataError
```
