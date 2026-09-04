# Project Description

Create a complete, installable pure-Python package named `pyasn1` from an empty
workspace. The package models ASN.1 values and metadata and provides deterministic
BER, DER, and native codecs. Implement the documented public behavior as a real
package, not as a single script or a collection of test-specific constants.

# Supports

- Support CPython 3.8 and newer, including Python 3.12.
- Provide an installable `pyproject.toml` using the standard setuptools build backend.
- The package has no third-party runtime dependencies.
- Preserve the package import layout `pyasn1`, `pyasn1.type`, and
  `pyasn1.codec.{ber,cer,der,native}`.
- Do not contact a network, launch external processes, or require external services
  during import or ordinary API use.
- Keep public module names and documented re-exports available to callers.

# API Usage Guide

All signatures below use ordinary Python objects and return the indicated pyasn1
object or built-in value. ASN.1 value objects are generally immutable in their
scalar operations and support `clone(value)` to produce a value with the same
type metadata and a new value. Constructed values support component assignment.

## Tags and named metadata

- `pyasn1.type.tag.Tag(tagClass, tagFormat, tagId)` creates a tag. The three
  arguments are integers; `tuple(tag)` yields `[tagClass, tagFormat, tagId]` and
  the read-only properties `tagClass`, `tagFormat`, and `tagId` expose them.
  Tags compare by their three fields and support `&` and `|` composition.
- `pyasn1.type.tag.initTagSet(tag)` creates a `TagSet` containing a base tag.
  `TagSet.tagExplicitly(superTag)` adds a constructed super-tag while retaining
  the base tag; `TagSet.tagImplicitly(superTag)` replaces the effective base tag.
  `baseTag`, `superTags`, and `len(tagSet)` expose deterministic metadata.
- `pyasn1.type.namedval.NamedValues(*names, **kwargs)` accepts `(name, value)`
  pairs and bare names. It provides ordered `keys()`, `values()`, `items()`,
  name/value indexing, `getName(value)`, `getValue(name)`, `clone(...)`, and
  addition of two mappings. Missing lookups return `None`.

## Constraints

- `pyasn1.type.constraint.ValueRangeConstraint(lower, upper)` validates numeric
  values inclusively when called. `ValueSizeConstraint(lower, upper)` validates
  the length of a value. `SingleValueConstraint(*values)` validates membership.
  A valid call returns `None`; a violation raises `ValueConstraintError`.
- `ConstraintsUnion(...)` accepts a value if one member accepts it;
  `ConstraintsIntersection(...)` requires every member to accept it. Constraint
  failures are deterministic and may include nested diagnostic text.

## Scalar types

Expose `Integer`, `Boolean`, `OctetString`, `BitString`, `ObjectIdentifier`,
`Real`, `Any`, and `Null` from `pyasn1.type.univ`, plus character classes such as
`UTF8String` and `NumericString` from `pyasn1.type.char`, and `GeneralizedTime`
from `pyasn1.type.useful`.

- `Integer(value=noValue, **kwargs)` supports `int(value)`, boolean conversion,
  arithmetic with integers, `prettyPrint()`, and `clone(value)`. Named values
  supplied through `namedValues=NamedValues(...)` accept names and print known
  names.
- `Boolean(value)` converts to `bool` and integer 0/1. `OctetString(value,
  encoding=...)` supports text or bytes, `asOctets()`, `asNumbers()`, and
  `prettyPrint()`. `BitString("'10110'B")` supports iteration, `len`,
  `asBinary()`, and `asInteger()`.
- `ObjectIdentifier(value)` is iterable as arcs, has `prettyPrint()`, and
  `isPrefixOf(other)`. `Real((mantissa, base, exponent))` converts to `float`.
  `Any(octets)` preserves encoded bytes through `asOctets()`; `Null("")` is the
  empty ASN.1 NULL value.
- Character values preserve their text and expose encoded UTF-8 bytes through
  `asOctets()` where supported. `GeneralizedTime(text).asDateTime` returns an
  aware UTC `datetime` and `prettyPrint()` preserves the canonical text form.

## Constructed types

- `Sequence(componentType=NamedTypes(...))` stores named components. Assign and
  read components by name, use `keys()`, `items()`, `len`, and `prettyPrint()`.
  `NamedType`, `OptionalNamedType`, and `DefaultedNamedType` describe required,
  optional, and defaulted fields. `NamedTypes.keys()` and
  `getPositionByName(name)` expose the declared positions.
- `SequenceOf(componentType=...)` and `SetOf(componentType=...)` are mutable
  typed collections supporting `extend`, indexed assignment, iteration, and
  length. DER encoding of `SetOf` is deterministic and canonical.
- `Choice(componentType=NamedTypes(...))` selects one named component through
  `value[name] = item`; `getName()` and `getComponent()` report the selection.
- `subtype(subtypeSpec=...)` attaches a constraint to a value type. A violating
  `clone(value)` raises `ValueConstraintError`; a valid clone retains compatible
  type metadata and `isSameTypeWith()` returns true for compatible values.

## Codecs

- `pyasn1.codec.ber.encoder.encode(value)` returns BER bytes. The matching
  `pyasn1.codec.ber.decoder.decode(substrate, asn1Spec=...)` returns
  `(decodedValue, remainingBytes)` and accepts BER trailing bytes.
- `pyasn1.codec.der.encoder.encode(value)` returns canonical DER bytes.
  `pyasn1.codec.der.decoder.decode(substrate, asn1Spec=...)` returns the decoded
  value and remaining bytes; malformed or truncated input raises a pyasn1 error.
- `pyasn1.codec.native.encoder.encode(value)` converts a constructed ASN.1 value
  into a built-in mapping/list/scalar representation. Native decoder `decode(value,
  asn1Spec=...)` reconstructs the corresponding ASN.1 value.

# Implementation Notes

- Keep `pyasn1.__version__` equal to `0.6.4` and preserve the package's module
  hierarchy and public class names.
- Preserve deterministic exception classes for invalid constraints and malformed
  codec input. Do not replace all errors with a generic exception.
- Keep BER/DER tag, length, constructed-value, and trailing-substrate behavior
  consistent across the type and codec modules.
- Implement public behavior with normal Python data structures and no network or
  process-global mutable state. Hidden verification invokes the candidate only
  through a separate child process and checks the behavior described here.
