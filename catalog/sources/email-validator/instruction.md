# Project Description

Create a complete, installable Python distribution named `email-validator` from an empty workspace. It must expose a small, dependency-backed library for validating Internet email addresses, normalizing Unicode and IDNA forms, and optionally checking domain deliverability through an injected DNS resolver. The implementation should be pure Python and deterministic when deliverability is disabled or a resolver is supplied.

# Supports

- Support Python 3.10 and newer, including Python 3.12.
- The repository must install from its root with `python -m pip install .` after the build dependencies are available.
- Use distribution name `email-validator`, version `2.3.0`, and an import package named `email_validator` containing a `py.typed` marker.
- Declare runtime dependencies on `dnspython>=2.0.0` and `idna>=2.0.0`. Do not add dependencies for Python standard-library modules.
- Provide the console entry point `email_validator=email_validator.__main__:main`.
- Do not contact the network during normal library calls unless the caller explicitly requests deliverability checking without providing a resolver. The verifier supplies deterministic resolver scenarios and does not use public DNS.

# API Usage Guide

## Package exports and configuration

`email_validator.__all__` must contain, in this order: `validate_email`, `ValidatedEmail`, `EmailNotValidError`, `EmailSyntaxError`, `EmailUndeliverableError`, `caching_resolver`, and `__version__`. The package root must expose those names and the version string `2.3.0`.

The package root also exposes these mutable defaults: `ALLOW_SMTPUTF8=True`, `ALLOW_EMPTY_LOCAL=False`, `ALLOW_QUOTED_LOCAL=False`, `ALLOW_DOMAIN_LITERAL=False`, `ALLOW_DISPLAY_NAME=False`, `STRICT=False`, `GLOBALLY_DELIVERABLE=True`, `CHECK_DELIVERABILITY=True`, `TEST_ENVIRONMENT=False`, and `DEFAULT_TIMEOUT=15`. `SPECIAL_USE_DOMAIN_NAMES` is a mutable list containing at least `invalid`, `local`, `localhost`, `onion`, and `test` (and may include the reserved `arpa` name).

## `validate_email`

Import path: `email_validator.validate_email`.

```python
validate_email(
    email: str | bytes,
    /,
    *,
    allow_smtputf8: bool | None = None,
    allow_empty_local: bool | None = None,
    allow_quoted_local: bool | None = None,
    allow_domain_literal: bool | None = None,
    allow_display_name: bool | None = None,
    strict: bool | None = None,
    check_deliverability: bool | None = None,
    test_environment: bool | None = None,
    globally_deliverable: bool | None = None,
    timeout: int | None = None,
    dns_resolver: object | None = None,
) -> ValidatedEmail
```

The argument is positional-only and must be `str` or ASCII `bytes`; other types raise `TypeError`. The function returns a `ValidatedEmail` object or raises `EmailSyntaxError` for malformed/unsafe syntax and `EmailUndeliverableError` for a failed deliverability check. Both inherit from `EmailNotValidError`, which inherits from `ValueError`.

The returned object has these fields: `original`, `normalized`, `local_part`, `domain`, `domain_address`, `ascii_email`, `ascii_local_part`, `ascii_domain`, `smtputf8`, `mx`, `mx_fallback_type`, and `display_name`. Fields not applicable to an input may be `None` or absent. `normalized` is the canonical local part plus `@` plus the Unicode domain. The domain is lowercased and IDNA-normalized; `ascii_domain` is its IDNA ASCII form. For an ASCII local part, `ascii_email` combines the ASCII local part and domain. A non-ASCII local part sets `smtputf8=True` and `ascii_email=None`.

By default, a domain must contain a period and must not be a special-use/reserved domain. `test_environment=True` allows `test` and its subdomains and disables deliverability checks. `globally_deliverable=False` permits dotless non-reserved domains. `check_deliverability=False` skips DNS. When it is enabled, use the supplied `dns_resolver`; a successful MX response populates sorted `(priority, exchange)` tuples in `mx`, while a global A or AAAA fallback sets `mx_fallback_type` to `A` or `AAAA`. Null MX, NXDOMAIN, and missing non-local records raise `EmailUndeliverableError`. Timeout and no-nameserver conditions produce a valid result with unknown deliverability metadata rather than making syntax validation fail.

Option behavior:

- `allow_smtputf8=False` rejects non-ASCII local parts; the default accepts them.
- `allow_empty_local=True` accepts `@domain`.
- `allow_quoted_local=True` accepts quoted local parts and returns the minimally escaped normalized local part.
- `allow_domain_literal=True` accepts `[IPv4]` and `[IPv6:address]` domains, returns a normalized bracketed domain, and stores an `ipaddress` object in `domain_address` without DNS lookup.
- `allow_display_name=True` accepts `Display Name <local@domain>` and sets `display_name` to the unquoted/unescaped name. It is rejected by default.
- `strict=True` additionally enforces the 64-character local-part limit.
- Explicit option values override the corresponding package defaults; `None` uses the current package default.

Examples:

```python
info = validate_email("User@Example.COM", check_deliverability=False)
assert info.normalized == "User@example.com"
assert info.ascii_email == "User@example.com"

intl = validate_email("\u30c4@example.com", check_deliverability=False)
assert intl.smtputf8 is True and intl.ascii_email is None
```

## `ValidatedEmail`

Import path: `email_validator.ValidatedEmail`. It is a lightweight result object. `repr(result)` is `<ValidatedEmail {normalized}>`. `result.as_dict() -> dict[str, object]` returns the stored fields and represents a domain address safely. `result[key]` supports the compatibility keys `email`, `email_ascii`, `local`, `domain`, `domain_i18n`, `smtputf8`, `mx`, and `mx-fallback`, and emits a `DeprecationWarning`. The deprecated `result.email` property returns `normalized` and emits a `DeprecationWarning`; `result.original_email` is a compatibility alias for `original`. Unknown keys raise `KeyError` and unknown attributes raise `AttributeError`. Equality compares the normalized result data.

## `caching_resolver`

Import path: `email_validator.caching_resolver`.

```python
caching_resolver(*, timeout: int | None = None, cache: object | None = None, dns_resolver: object | None = None) -> object
```

Return a `dnspython` resolver configured with an LRU cache and the requested lifetime. If no timeout is provided, use `DEFAULT_TIMEOUT`. If `dns_resolver` is supplied, configure and return that resolver. The helper is deterministic and does not itself perform a DNS query.

## Exceptions

Import paths: `email_validator.EmailNotValidError`, `email_validator.EmailSyntaxError`, and `email_validator.EmailUndeliverableError`. Preserve the stated inheritance and human-readable messages that identify the relevant reason, such as missing `@`, invalid characters, disallowed display name, special-use domain, or undeliverable domain.

## Command line interface

`python -m email_validator ADDRESS` validates one address and prints a JSON object for success or a human-readable error for failure. With no address argument it reads newline-separated addresses from standard input and prints failures as `ADDRESS message`; valid addresses produce no output. Environment variables named after the package defaults can override CLI options.

# Implementation Notes

Keep the public behavior deterministic and do not retrieve the reference repository at runtime. Separate parsing of display names/quoted locals from local-part and domain validation. Normalize with Unicode NFC and IDNA 2008 semantics, reject unsafe/control characters, enforce address/domain/label length limits, and preserve the option precedence described above. Deliverability is an explicit boundary: all tests must use local deterministic resolver data or disable it. The package should remain importable without eagerly constructing a DNS resolver, and `py.typed` must be included in the built distribution.
