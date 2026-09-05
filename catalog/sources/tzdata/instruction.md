# Project Description

Create an installable Python distribution named `tzdata` that provides the
IANA time zone database release `2026c` as package resources. The package is a
fallback data provider for the standard-library `zoneinfo` module when no
system time zone search path is available.

The implementation must be self-contained in the repository and install with
the build tools already present in the environment. Runtime code must not
download, generate, or look up time zone data from the network.

# Natural Language Instruction

Create the installable `tzdata` resource package from an empty workspace.
Provide the frozen IANA zone manifest, TZif hierarchy, ancillary files, version
constants, and standard-library `zoneinfo` fallback behavior below. Keep every
resource local and byte-stable.

# Supports

- CPython 3.12 and ordinary PEP 517 installation with
  `pip install --no-deps --no-build-isolation <repository>`.
- A top-level `tzdata` package with exact string constants `__version__ =
  "2026.3"` and `IANA_VERSION = "2026c"`.
- Distribution metadata with name `tzdata`, version `2026.3`, license
  `Apache-2.0`, `Requires-Python: >=2`, and no runtime `Requires-Dist` entries.
- A newline-delimited `tzdata/zones` resource containing 598 non-empty,
  unique zone names. It includes canonical names and backward-compatible
  aliases. Representative required names include `Africa/Cairo`,
  `Africa/Casablanca`, `Africa/El_Aaiun`, `America/Coyhaique`,
  `America/Edmonton`, `America/Los_Angeles`, `America/New_York`,
  `America/Nuuk`, `Asia/Calcutta`, `Asia/Kathmandu`, `Asia/Seoul`,
  `Australia/Lord_Howe`, `Canada/Mountain`, `Egypt`, `Europe/London`,
  `Hongkong`, `Mexico/BajaNorte`, `Pacific/Chatham`, `Pacific/Kiritimati`,
  `US/Eastern`, and `UTC`.
- A `tzdata.zoneinfo` package-resource tree. Every name in `tzdata/zones`
  maps to a readable TZif resource at the same slash-separated relative path,
  and every such file starts with the four bytes `TZif`. Resource directories,
  including nested America subregions, are importable Python packages.
- The ancillary resources `iso3166.tab`, `leapseconds`, `tzdata.zi`,
  `zone.tab`, `zone1970.tab`, and `zonenow.tab` at the root of
  `tzdata.zoneinfo`. The first line of `tzdata.zi` is `# version 2026c`.
  `posixrules` is intentionally absent.
- Standard-library fallback behavior: after `zoneinfo.reset_tzpath([])`,
  `zoneinfo.available_timezones()` equals the set of names in
  `tzdata/zones`, and `zoneinfo.ZoneInfo(key)` loads those package resources.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── tzdata/
    ├── __init__.py
    ├── zones
    └── zoneinfo/
        ├── __init__.py
        ├── America/
        ├── Europe/
        └── tzdata.zi
```

# API Usage Guide

## Version constants

```python
import tzdata

assert tzdata.__version__ == "2026.3"
assert tzdata.IANA_VERSION == "2026c"
```

Both names are module-level `str` values. Importing `tzdata` has no stateful
side effects.

## Reading the zone manifest and TZif resources

```python
from importlib.resources import files

zones = (files("tzdata") / "zones").read_text(encoding="utf-8").splitlines()
new_york = files("tzdata.zoneinfo").joinpath("America", "New_York")
assert new_york.read_bytes()[:4] == b"TZif"
```

The resource hierarchy must work through the `importlib.resources` Traversable
API after installation, including when installed as a wheel. Missing resource
paths follow the normal `importlib.resources` error behavior.

## Using the package through `zoneinfo`

```python
from datetime import datetime
from zoneinfo import ZoneInfo, reset_tzpath

reset_tzpath([])
local = datetime.fromisoformat("2024-07-15T12:00:00+00:00").astimezone(
    ZoneInfo("America/New_York")
)
assert local.isoformat() == "2024-07-15T08:00:00-04:00"
assert local.tzname() == "EDT"
```

`ZoneInfo(key).key` preserves the requested name, including aliases such as
`US/Eastern`. A key not present in the manifest, such as
`Mars/Olympus_Mons`, raises `zoneinfo.ZoneInfoNotFoundError`.

The following UTC-to-local observations are part of the required 2026c data
contract. Offset values are shown in seconds; `fold` is the final column.

| Zone | UTC instant | Local ISO value | Abbreviation | Offset | fold |
| --- | --- | --- | --- | ---: | ---: |
| `UTC` | `2030-07-15T12:00:00+00:00` | `2030-07-15T12:00:00+00:00` | `UTC` | 0 | 0 |
| `Etc/GMT+5` | `2030-01-15T12:00:00+00:00` | `2030-01-15T07:00:00-05:00` | `-05` | -18000 | 0 |
| `Etc/GMT-9` | `2030-01-15T12:00:00+00:00` | `2030-01-15T21:00:00+09:00` | `+09` | 32400 | 0 |
| `America/New_York` | `2024-01-15T12:00:00+00:00` | `2024-01-15T07:00:00-05:00` | `EST` | -18000 | 0 |
| `America/New_York` | `2024-07-15T12:00:00+00:00` | `2024-07-15T08:00:00-04:00` | `EDT` | -14400 | 0 |
| `America/New_York` | `2024-11-03T05:30:00+00:00` | `2024-11-03T01:30:00-04:00` | `EDT` | -14400 | 0 |
| `America/New_York` | `2024-11-03T06:30:00+00:00` | `2024-11-03T01:30:00-05:00` | `EST` | -18000 | 1 |
| `Europe/London` | `2024-01-15T12:00:00+00:00` | `2024-01-15T12:00:00+00:00` | `GMT` | 0 | 0 |
| `Europe/London` | `2024-07-15T12:00:00+00:00` | `2024-07-15T13:00:00+01:00` | `BST` | 3600 | 0 |
| `Asia/Kathmandu` | `1970-01-01T00:00:00+00:00` | `1970-01-01T05:30:00+05:30` | `+0530` | 19800 | 0 |
| `Asia/Kathmandu` | `2024-01-15T12:00:00+00:00` | `2024-01-15T17:45:00+05:45` | `+0545` | 20700 | 0 |
| `Australia/Lord_Howe` | `2024-01-15T12:00:00+00:00` | `2024-01-15T23:00:00+11:00` | `+11` | 39600 | 0 |
| `Australia/Lord_Howe` | `2024-07-15T12:00:00+00:00` | `2024-07-15T22:30:00+10:30` | `+1030` | 37800 | 0 |
| `Pacific/Chatham` | `2024-01-15T12:00:00+00:00` | `2024-01-16T01:45:00+13:45` | `+1345` | 49500 | 0 |
| `Pacific/Chatham` | `2024-07-15T12:00:00+00:00` | `2024-07-16T00:45:00+12:45` | `+1245` | 45900 | 0 |
| `America/Edmonton` | `2026-11-01T07:59:59+00:00` | `2026-11-01T01:59:59-06:00` | `MDT` | -21600 | 0 |
| `America/Edmonton` | `2026-11-01T08:00:00+00:00` | `2026-11-01T02:00:00-06:00` | `CST` | -21600 | 0 |
| `America/Edmonton` | `2030-01-15T12:00:00+00:00` | `2030-01-15T06:00:00-06:00` | `CST` | -21600 | 0 |
| `America/Edmonton` | `2030-07-15T12:00:00+00:00` | `2030-07-15T06:00:00-06:00` | `CST` | -21600 | 0 |
| `Canada/Mountain` | `2030-01-15T12:00:00+00:00` | `2030-01-15T06:00:00-06:00` | `CST` | -21600 | 0 |
| `Africa/Casablanca` | `2026-09-20T00:59:59+00:00` | `2026-09-20T01:59:59+01:00` | `+01` | 3600 | 0 |
| `Africa/Casablanca` | `2026-09-20T01:00:00+00:00` | `2026-09-20T01:00:00+00:00` | `+00` | 0 | 1 |
| `Africa/Casablanca` | `2026-09-20T02:00:00+00:00` | `2026-09-20T02:00:00+00:00` | `+00` | 0 | 0 |
| `Africa/Casablanca` | `2030-01-15T12:00:00+00:00` | `2030-01-15T12:00:00+00:00` | `+00` | 0 | 0 |
| `Africa/Casablanca` | `2030-07-15T12:00:00+00:00` | `2030-07-15T12:00:00+00:00` | `+00` | 0 | 0 |
| `Africa/El_Aaiun` | `2026-09-20T01:00:00+00:00` | `2026-09-20T01:00:00+00:00` | `+00` | 0 | 1 |
| `Africa/El_Aaiun` | `2030-07-15T12:00:00+00:00` | `2030-07-15T12:00:00+00:00` | `+00` | 0 | 0 |
| `America/Coyhaique` | `2024-07-15T12:00:00+00:00` | `2024-07-15T08:00:00-04:00` | `-04` | -14400 | 0 |
| `America/Coyhaique` | `2030-07-15T12:00:00+00:00` | `2030-07-15T09:00:00-03:00` | `-03` | -10800 | 0 |
| `America/Asuncion` | `2024-07-15T12:00:00+00:00` | `2024-07-15T08:00:00-04:00` | `-04` | -14400 | 0 |
| `America/Asuncion` | `2030-07-15T12:00:00+00:00` | `2030-07-15T09:00:00-03:00` | `-03` | -10800 | 0 |

The 2026c-specific future rules are significant: Alberta remains at UTC-06
after the modeled 2026-11-01 abbreviation change, while Morocco and Western
Sahara move from UTC+01 to permanent UTC at 2026-09-20 02:00 local time.

# Examples

```python
import tzdata

assert tzdata.__version__ == "2026.3"
assert tzdata.IANA_VERSION == "2026c"
```

```python
from importlib.resources import files

assert (files("tzdata") / "zones").read_text().splitlines()
```

# Error Handling and Boundary Conditions

Zone names are case-sensitive slash-separated keys. Missing or malformed TZif
resources follow normal `importlib.resources` errors, and an unknown key must
raise `zoneinfo.ZoneInfoNotFoundError`; no fallback may silently access the
host's zoneinfo tree.

# Implementation Notes

- Produce a normal source repository, not only an installed tree. Include
  `pyproject.toml` (or an equivalent supported build configuration), package
  metadata, Python modules, the zone manifest, and all package data needed by
  the contract.
- The build environment already contains exact versions of `setuptools` and
  `wheel`. Do not declare runtime dependencies and do not use dynamic build
  requirements that would require package-index access.
- Keep the resource bytes inside the built wheel. Loading a zone must not read
  `/usr/share/zoneinfo`, environment-specific paths, or a remote service at
  runtime.
- Preserve slash-separated zone keys and aliases exactly. Do not normalize
  case, replace underscores, or reverse the sign convention of `Etc/GMT`
  names.
- The package has no CLI and no mutable global configuration. The standard
  library owns `ZoneInfo` caching; the data package only supplies metadata and
  resources.
