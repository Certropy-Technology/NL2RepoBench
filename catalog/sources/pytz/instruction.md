# Project Description

Create an installable Python package named `pytz` for the locked upstream API slice described below. The package must work from an empty workspace and must ship its timezone data as package data; it must not read the host operating system timezone database at runtime.

## Supports

- Python 3.12 on Debian 12.
- A normal `pip install .` (or an equivalent PEP 517/legacy source install).
- No runtime dependency outside the Python standard library.
- The package must include `setup.py`, the `pytz` package, and compiled IANA timezone resources for at least the standard zones named in this document.
- Runtime operation is offline and deterministic. Do not download timezone data or use the host `zoneinfo` database as a fallback.

# API Usage Guide

## `pytz.timezone` and constants

`pytz.timezone(zone: str) -> datetime.tzinfo` returns a cached timezone object for an IANA name. It must support `UTC`, `US/Eastern`, `Europe/London`, and `Asia/Tokyo`. `pytz.utc` is the same object returned by `timezone("UTC")`. `pytz.all_timezones` is a deterministic sequence containing those names and `pytz.all_timezones_set` is the corresponding set. `pytz.__version__` and `pytz.OLSON_VERSION` identify the locked release.

Unknown names raise `pytz.UnknownTimeZoneError`, rather than `KeyError` or an operating-system-specific exception.

## Localizing and converting datetimes

Timezone objects provide `localize(dt: datetime, is_dst=False) -> datetime`. For an unambiguous naive datetime it returns an aware datetime with the correct offset. During a fall-back transition, `is_dst=True` selects the DST occurrence and `is_dst=False` selects standard time; an ambiguous value with `is_dst=None` raises `pytz.AmbiguousTimeError`. During a spring-forward gap, `is_dst=None` raises `pytz.NonExistentTimeError`.

Timezone objects provide `normalize(dt: datetime, is_dst=False) -> datetime` for correcting an aware datetime after arithmetic across a transition. Aware datetimes can be converted with the standard `datetime.astimezone(pytz.utc)` operation.

## Fixed offsets and exceptions

`pytz.FixedOffset(minutes: int) -> datetime.tzinfo` returns a cached fixed offset timezone. Its offset is the requested number of minutes and its `zone` name is stable. `pytz.UTC` is an alias for `pytz.utc`.

Export `UnknownTimeZoneError`, `AmbiguousTimeError`, and `NonExistentTimeError` from the package root.

# Implementation Notes

Use the locked upstream revision public module layout and compatibility behavior where it agrees with the contract. Preserve the import paths `pytz.lazy`, `pytz.tzfile`, and `pytz.tzinfo`; callers may import the public collection helpers and `build_tzinfo` from those modules. Timezone resources must be present under `pytz/zoneinfo` in the installed distribution, including aliases needed by `US/Eastern` and the other named zones. Keep resource lookup inside the installed package so an isolated verifier can run with no network and no preinstalled reference package.

The verifier exercises only this stable API slice. It invokes a JSON-lines client in a separate subprocess, so do not rely on pytest fixtures, a working directory, or environment variables other than the package own resources.
