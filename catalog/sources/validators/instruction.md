# Build `validators`

## Project Description

Create a complete, installable Python package named `validators`. The package
provides small, composable functions for validating one value at a time without
requiring callers to define a schema or form. It covers common identifiers,
network strings, encodings, payment data, checksummed values, and selected
country-specific identifiers.

All ordinary validator functions share one result model: return the singleton
`True` when the value is valid; otherwise return a false-valued
`ValidationError` object describing the validator and its arguments. Validators
must be deterministic and perform no network access.

## Supports

- Support CPython 3.9 and newer.
- Use an installable `src/validators/` package and expose version `0.35.0` as
  `validators.__version__`.
- Declare no required runtime dependencies. Provide an optional extra named
  `crypto-eth-addresses` with requirement `eth-hash[pycryptodome]>=0.7.0`.
- Package `validators/_tld.txt` for IANA top-level-domain validation and the
  empty `validators/py.typed` marker.
- Do not provide a command-line interface. The public interface is the Python
  package and its documented import paths.
- Re-export the public validators, `ValidationError`, and `validator` from
  `validators`. Also retain the documented submodule imports under
  `validators.crypto_addresses`, `validators.i18n`, and the individual
  validator modules.

## API Usage Guide

### Common result and decorator contract

```python
class ValidationError(Exception):
    def __init__(self, function, arg_dict, message=""): ...

def validator(func): ...
```

`ValidationError` stores the failed callable as `func` and every supplied
argument as an instance attribute. If a failure came from a caught conversion
error, expose its text as `reason`. Its boolean value is always `False`.
`str(error)` and `repr(error)` have the form
`ValidationError(func=<name>, args={<arguments except func>})`.

`validator` preserves the decorated function's metadata. A normal call returns
`True` when the wrapped function returns a truthy value, or a `ValidationError`
when it returns a false value or raises `ValueError`, `TypeError`, or
`UnicodeError`. Passing the control keyword `r_ve=True`, or setting environment
variable `RAISE_VALIDATION_ERROR=True`, changes failure into a raised
`ValidationError`; success remains `True`. The control keyword is not included
in the recorded failed arguments. Other exceptions, including an optional
dependency `ImportError`, propagate.

For example, `email("someone@example.com") is True`, while
`email("bogus@@")` returns a false-valued error whose `func` is the underlying
email validator and whose `value` attribute is `"bogus@@"`.

### Comparison sentinels

```python
from validators._extremes import AbsMax, AbsMin
```

`AbsMin()` and `AbsMax()` are no-argument comparison sentinel objects used for
open-ended ranges. `AbsMin` compares below values of arbitrary types and
`AbsMax` compares above them; comparisons involving the same sentinel remain
well-defined. They are available from `validators._extremes` and are not
re-exported from the package root.

### Ranges and lengths

```python
between(value, /, *, min_val=None, max_val=None)
length(value: str, /, *, min_val: typing.Optional[int] = None,
       max_val: typing.Optional[int] = None)
```

The `typing.Optional` annotation is descriptive; an implementation may use the
equivalent optional type annotation on Python 3.9.

`between` accepts comparable numbers, strings, dates, and similar values. Its
bounds are inclusive; either omitted bound is unbounded, and omitting both
bounds accepts every non-`None` value. Incomparable values and reversed bounds
produce validation failure through the common decorator contract.

`length` applies those inclusive bounds to `len(value)`. A negative explicit
bound is treated as a validation failure by the common decorator (or raises a
`ValidationError` when `r_ve=True`).

### Cards, finance, and IBAN

```python
card_number(value: str, /)
visa(value: str, /); mastercard(value: str, /); amex(value: str, /)
unionpay(value: str, /); diners(value: str, /); jcb(value: str, /)
discover(value: str, /); mir(value: str, /)
cusip(value: str); isin(value: str); sedol(value: str)
iban(value: str, /)
```

`card_number` accepts decimal strings satisfying the Luhn checksum. Brand
validators also require the brand prefix and length: Visa `4`/16, Mastercard
`51`-`55` or `22`-`27`/16, Amex `34` or `37`/15, UnionPay `62`/16, Diners
`30`, `36`, `38`, or `39`/14 or 16, JCB `35`/16, Discover `60`, `64`, or
`65`/16, and Mir `2200` through `2204`/16.

`cusip`, `isin`, `sedol`, and `iban` validate their standard length, character,
and checksum rules. CUSIP has 9 characters, ISIN has 12, SEDOL has 7 and
rejects vowels, and IBAN has 15 through 34 alphanumeric characters beginning
with a two-letter country code and two check digits and passing mod 97.

### Encodings, hashes, UUIDs, MAC addresses, and slugs

```python
base16(value: str, /); base32(value: str, /)
base58(value: str, /); base64(value: str, /)
md5(value: str, /); sha1(value: str, /); sha224(value: str, /)
sha256(value: str, /); sha384(value: str, /); sha512(value: str, /)
uuid(value: typing.Union[str, uuid.UUID], /)
mac_address(value: str, /)
slug(value: str, /)
```

- Base16 accepts nonempty hexadecimal text in either case. Base32 accepts
  uppercase `A-Z`, digits `2-7`, and trailing `=` padding. Base58 excludes
  ambiguous `0OIl` characters. Base64 requires canonical four-character
  groups with zero, one, or two terminal padding characters.
- Hash validators accept hexadecimal text in either case at the standard
  lengths: 32, 40, 56, 64, 96, and 128 characters respectively.
- `uuid` accepts either a `uuid.UUID` object or a string accepted by the
  standard-library UUID parser, including hyphenated and compact forms.
- `mac_address` accepts exactly six hexadecimal octets separated consistently
  by either colons or hyphens.
- `slug` accepts one or more lowercase alphanumeric groups separated by single
  hyphens; it rejects uppercase, whitespace, punctuation, and empty groups.

### Domains, hosts, email, URLs, and addresses

```python
domain(value: str, /, *, consider_tld=False, rfc_1034=False, rfc_2782=False)
hostname(value: str, /, *, skip_ipv6_addr=False, skip_ipv4_addr=False,
         may_have_port=True, maybe_simple=True, consider_tld=False,
         private=None, rfc_1034=False, rfc_2782=False)
email(value: str, /, *, ipv6_address=False, ipv4_address=False,
      simple_host=False, rfc_1034=False, rfc_2782=False)
ipv4(value: str, /, *, cidr=True, strict=False, private=None, host_bit=True)
ipv6(value: str, /, *, cidr=True, strict=False, host_bit=True)
url(value: str, /, *, skip_ipv6_addr=False, skip_ipv4_addr=False,
    may_have_port=True, simple_host=False, strict_query=True,
    consider_tld=False, private=None, rfc_1034=False, rfc_2782=False,
    validate_scheme=<built-in scheme predicate>)
```

`domain` supports IDNA names. `rfc_1034` permits a trailing dot,
`rfc_2782` permits service-record underscores, and `consider_tld` checks the
packaged IANA list. Setting `PYVLD_CACHE_TLD=True` may cache that list in
memory but must not change results.

`hostname` accepts simple host names, domains, IPv4, and IPv6, with an optional
port from 1 through 65535. Its switches disable address families, simple names,
or ports; `private=True` requires a private/local/broadcast IPv4 address and
`private=False` requires a public one.

`email` requires exactly one `@`, a local part no longer than 64 characters,
and a domain no longer than 253. It supports extended Latin and quoted local
parts. Bracketed IP domains are allowed only when the corresponding address
flag is enabled.

`ipv4` and `ipv6` use standard-library address/network semantics. CIDR is
allowed by default; `strict=True` requires CIDR notation; `host_bit=False`
requires host bits to be clear. `private` applies only to IPv4.

`url` validates a complete parsed URL, including authentication, host/port,
Unicode path, query, and fragment. Its default schemes are `ftp`, `ftps`,
`git`, `http`, `https`, `irc`, `rtmp`, `rtmps`, `rtsp`, `sftp`, `ssh`, and
`telnet`. `validate_scheme` may be replaced with a caller-supplied predicate.
Validation is syntactic only and never connects to the target.

### Country and schedule values

```python
calling_code(value: str, /)
country_code(value: str, /, *, iso_format="auto", ignore_case=False)
currency(value: str, /, *, skip_symbols=True, ignore_case=False)
cron(value: str, /)
```

`calling_code` accepts assigned international calling codes including their
leading `+`. `country_code` accepts ISO 3166 alpha-2, alpha-3, or three-digit
numeric codes. `iso_format="auto"` derives the form from the value; named
forms are `alpha2`, `alpha3`, and `numeric`. Alphabetic matching is
case-sensitive unless `ignore_case=True`.

`currency` accepts ISO 4217 three-letter codes; it additionally accepts known
currency symbols only when `skip_symbols=False`. Case is significant unless
`ignore_case=True`.

`cron` accepts exactly five fields in minute, hour, day-of-month, month, and
weekday order. Each field supports `*`, an in-range decimal, `*/step` or
`value/step` with positive step, an ascending range, or a comma-separated list.
Field ranges are 0-59, 0-23, 1-31, 1-12, and 0-6.

### Cryptographic addresses

```python
bsc_address(value: str, /); btc_address(value: str, /)
eth_address(value: str, /); trx_address(value: str, /)
```

- BSC accepts `0x` followed by exactly 40 hexadecimal characters.
- BTC validates P2PKH/P2SH Base58Check addresses and applies the package's
  deterministic Bech32/segwit-style regular-expression check to prefixed
  segwit-like values.
- ETH accepts all-lowercase or all-uppercase 40-hex addresses and validates
  mixed-case EIP-55 checksums. Calling it without the `crypto-eth-addresses`
  extra raises `ImportError` with installation guidance.
- TRX accepts 34-character `T`-prefixed Base58Check addresses with the Tron
  network byte and checksum.

### International identifiers

```python
es_cif(value: str, /); es_nif(value: str, /); es_nie(value: str, /)
es_doi(value: str, /)
fi_business_id(value: str, /); fi_ssn(value: str, /, *, allow_temporal_ssn=True)
fr_department(value: typing.Union[str, int]); fr_ssn(value: str)
ind_aadhar(value: str); ind_pan(value: str); ru_inn(value: str)
```

Implement the documented national formats and control digits: Spanish company,
citizen, foreigner, and combined IDs; Finnish business and personal IDs;
French department and social-security IDs; Indian Aadhaar/PAN formats; and
10- or 12-digit Russian taxpayer IDs. Spanish CIF/NIF/NIE input is normalized
to uppercase. Finnish temporal SSNs use serials 900-999 and are rejected when
`allow_temporal_ssn=False`. French SSN control keys are optional, Corsican
departments are `2A`/`2B`, and overseas departments are 971-976.

### URI dispatch

```python
from validators.uri import uri

uri(value: str, /)
```

`uri` is a submodule API and is not re-exported from `validators`. It accepts
the URL schemes supported by `url`, `mailto:` values checked as email addresses,
`file:///` and `ipfs://` forms, and the package's syntactic `magnet:?`, `tel:`,
`data:`, `urn:`, and `urc:` forms. It returns the same `True` or
`ValidationError` result model as the other validators and never performs I/O.

## Implementation Notes

- Keep validation pure and deterministic. Apparent URLs in inputs are strings
  to inspect, never resources to fetch.
- Preserve function signatures, positional-only markers, keyword defaults,
  re-exports, and the common `ValidationError` behavior. Some callers inspect
  the stored argument attributes and function name, not just truthiness.
- Treat Unicode, empty strings, malformed types, checksums, case sensitivity,
  and boundary values as part of the public contract.
- The package also implements `validators.uri.uri(value, /)` for URL,
  `mailto:`, `file:///`, `ipfs://`, `magnet:?`, `tel:`, `data:`, `urn:`, and
  `urc:` dispatch as described above; it is not a root re-export.
- Do not include evaluator tests or depend on evaluator files being present in
  the generated workspace.
