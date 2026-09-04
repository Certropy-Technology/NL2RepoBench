# API Inventory

Frozen revision: `806dba9d9642fbec4c8538b625494c96b288ce59`.

Public package modules: `pythonjsonlogger`, `core`, `defaults`, `exception`, `json`, `jsonlogger`, `utils`; optional `orjson` and `msgspec` modules are guarded by availability flags.

Core symbols covered by the contract:

- `pythonjsonlogger.ORJSON_AVAILABLE`, `MSGSPEC_AVAILABLE`
- `core.RESERVED_ATTRS`, `core.merge_record_extra`, `core.BaseJsonFormatter`
- `json.JsonEncoder`, `json.JsonFormatter`
- `defaults.unknown_default`, type/dataclass/date/time/datetime/exception/traceback/enum/UUID/bytes predicate and encoder pairs
- `utils.package_is_available`
- `exception.MissingPackageError`
- deprecated `jsonlogger.JsonFormatter` and `json.RESERVED_ATTRS`

The upstream suite has four test modules and collects 218 tests under Python 3.12 with the root pytest configuration disabled. The production verifier reduces this to 50 deterministic child-process leaves while preserving the public behavior categories: metadata and imports, field extraction and renaming, record/exception/stack handling, serializer options, type fallback encoding, optional-package errors, and deprecation compatibility.
