# `petl` restricted API inventory at `2e01e169d83e4f66bef108bc2f20cde878d0a8a1`

This inventory is a source-observation and scope artifact. It is not a claim
that the complete petl package, its upstream tests, or a production verifier
has been packaged. The public contract is in `instruction.md`; provenance and
execution observations are in `audit.md` and `evidence.json`.

## Inventory method and package boundary

- The detached checkout resolves to the requested full commit, tag
  `v1.7.24`, tree `2de365143871de17aec33b76e3cb2ae677e74505`.
- `git ls-files` reports 230 tracked files. The archive has 252 members,
  including directory entries, and 230 regular files.
- The package tree contains 126 tracked Python files: 59 non-test runtime files
  and 67 files under `petl/test/` (including package test support modules).
- Runtime package size is 20,344 physical Python lines across 59 files;
  15,374 are nonblank and not leading-comment lines under the audit counting
  rule. The in-package test tree is 16,122 physical lines across 67 files.
- The restricted implementation graph uses 16 source modules and 7,661
  physical lines. It is a scope estimate, not a score denominator.
- Runtime introspection sees 327 non-underscore names at the `petl` root,
  because the historical package re-exports several modules and wildcard
  imports. There is no root `__all__`; this count is not a supported-API
  denominator.

The selected graph is:

```text
petl/__init__.py
petl/compat.py                 petl/config.py             petl/errors.py
petl/comparison.py
petl/io/csv.py                 petl/io/csv_py3.py          petl/io/json.py
petl/io/sources.py
petl/util/base.py              petl/util/materialise.py   petl/util/misc.py
petl/util/counting.py          petl/util/lookups.py       petl/util/parsers.py
petl/transform/basics.py       petl/transform/conversions.py
petl/transform/headers.py      petl/transform/selects.py
petl/transform/sorts.py        petl/transform/dedup.py
petl/transform/setops.py
```

The selected path imports Python standard-library modules and local petl
modules. The only non-standard import relevant to the graph is the optional
`asteval` branch used when callers request the upstream untrusted-expression
mode. That branch is excluded from the JSON-safe contract; no third-party
runtime package is required for the selected CSV/JSON path.

## I/O API

The root and module import paths observed at the pinned revision are:

| API | Import path(s) | Signature observed | Contract status |
| --- | --- | --- | --- |
| `fromcsv` | `petl.fromcsv`, `petl.io.csv.fromcsv` | `(source=None, encoding=None, errors='strict', header=None, **csvargs)` | included |
| `fromtsv` | `petl.fromtsv`, `petl.io.csv.fromtsv` | `(source=None, encoding=None, errors='strict', header=None, **csvargs)` | included |
| `tocsv` | `petl.tocsv`, `petl.io.csv.tocsv` | `(table, source=None, encoding=None, errors='strict', write_header=True, **csvargs)` | included |
| `appendcsv` | `petl.appendcsv`, `petl.io.csv.appendcsv` | `(table, source=None, encoding=None, errors='strict', write_header=False, **csvargs)` | included |
| `totsv` | `petl.totsv`, `petl.io.csv.totsv` | `(table, source=None, encoding=None, errors='strict', write_header=True, **csvargs)` | included |
| `appendtsv` | `petl.appendtsv`, `petl.io.csv.appendtsv` | `(table, source=None, encoding=None, errors='strict', write_header=False, **csvargs)` | included |
| `fromjson` | `petl.fromjson`, `petl.io.json.fromjson` | `(source, *args, **kwargs)` | included; `header`, `sample`, `missing`, `lines` only |
| `fromdicts` | `petl.fromdicts`, `petl.io.json.fromdicts` | `(dicts, header=None, sample=1000, missing=None)` | included; JSON values only |
| `tojson` | `petl.tojson`, `petl.io.json.tojson` | `(table, source=None, prefix=None, suffix=None, *args, **kwargs)` | included; JSONEncoder scalar options only |
| `tojsonarrays` | `petl.tojsonarrays`, `petl.io.json.tojsonarrays` | `(table, source=None, prefix=None, suffix=None, output_header=False, *args, **kwargs)` | included; JSONEncoder scalar options only |

`fromjson(..., lines=True)` and `tojson(..., lines=True)` cover the JSON-Lines
mode in the same module; this is not a separate dependency or package.

## Table and view API

| Group | Names |
| --- | --- |
| Header and row views | `header`, `fieldnames`, `data`, `dicts`, `records`, `values`, `nrows` |
| Materialization | `listoflists`, `listoftuples`, `tupleoflists`, `tupleoftuples`, `columns`, `cache` |
| Errors | `ArgumentError`, `DuplicateKeyError`, `FieldSelectionError` |
| Core object seams | `Table`, `Record`, `TableWrapper`, `MemorySource`/`StringSource` |

`Record` is included only as a JSON-observable row-access behavior (index,
field-name, and attribute lookup). The adapter must normalize records to plain
JSON lists/objects and must not expose Python object identity.

## Transform API

### Structural/header transforms included

```text
cut, cutout, cat, stack,
addfield, addfields, addcolumn, rowslice, head, tail,
addrownumbers, movefield,
setheader, extendheader, pushheader, skip, rename,
prefixheader, suffixheader, sortheader
```

The task contract limits row callbacks and columns to JSON-safe constants. The
following source-level forms are therefore deliberately not promoted:

- callable values for `addfield`, `addfields`, `addfieldusingcontext`, or
  `addcolumn`;
- arbitrary generators and custom source classes at the subprocess boundary;
- executable expressions or callable predicates;
- unbounded filesystem paths or remote source schemes.

### Selection transforms included

```text
selecteq, selectne, selectlt, selectle, selectgt, selectge,
selectin, selectnotin, selectcontains,
selecttrue, selectfalse, selectnone, selectnotnone, rowlenselect
```

These convenience forms take field selectors, JSON values, and an optional
`complement` boolean. They preserve the header and input order. The generic
`select`/`selectop` callback-or-expression forms are evidence-only until a
reviewed declarative predicate adapter exists.

### Value transforms included

```text
convert, convertall, replace, replaceall, update,
convertnumbers, format, interpolate
```

The adapter may represent method-name conversion (`'lower'`, `'strip'`, or
`'replace'` with JSON arguments) and mapping conversion dictionaries. Callable
converters, `pass_row`, unrestricted `where` expressions, and exception objects
as data are excluded.

### Ordering and de-duplication included

```text
sort, mergesort, issorted,
duplicates, unique, distinct, isunique
```

Keys are names, indices, or JSON arrays of those selectors. Temporary buffered
sorts are verifier-owned local operations. Randomized ordering, custom key
callables, and object-comparison hooks are excluded.

## Explicitly excluded API families

The following are present in the upstream root or modules but are not part of
the restricted task:

- joins, hash joins, interval joins, set operations, reductions, maps, regex,
  reshape, unpack, validation, and arbitrary expression helpers;
- database and SQL helpers (`fromdb`, `todb`, `appenddb`, SQLAlchemy and server
  drivers);
- NumPy, Pandas, HDF5/PyTables, bcolz, Avro/fastavro, XLS/XLSX, Whoosh, Google
  Sheets, and remote filesystem adapters;
- XML/HTML readers/writers, plotting/visualization helpers, CLI scripts,
  documentation builds, linting, and release hooks;
- Python 2 compatibility behavior and unbounded optional extras.

These exclusions are scope decisions, not claims that the upstream APIs do not
exist. They are cross-checked against the optional integration matrix in
`audit.md`.

## Source-test traceability slice

The following exact upstream test files were used for a deterministic,
source-only behavior probe. Their bytes are not copied into this task:

| Behavior family | Upstream test files | Collected leaves in the slice |
| --- | --- | ---: |
| CSV/TSV, Unicode | `petl/test/io/test_csv.py`, `test_csv_unicode.py` | 15 |
| JSON/JSON-Lines, Unicode | `petl/test/io/test_json.py`, `test_json_unicode.py`, `test_jsonl.py` | 31 |
| Structural transforms | `petl/test/transform/test_basics.py` | 45 |
| Value transforms | `petl/test/transform/test_conversions.py` | 18 |
| Header transforms | `petl/test/transform/test_headers.py` | 24 |
| Selection transforms | `petl/test/transform/test_selects.py` | 17 |
| Sorting | `petl/test/transform/test_sorts.py` | 23 |
| De-duplication | `petl/test/transform/test_dedup.py` | 16 |
| Set/table alignment evidence | `petl/test/transform/test_setops.py` | 12 |
| Table views/materialization | `petl/test/util/test_base.py`, `test_materialise.py`, `test_misc.py`, `test_counting.py`, `test_lookups.py` | 53 |
| **Total** | 17 exact files | **254** |

The 254-item slice passed three times under CPython 3.13.14 and once under
CPython 3.14.6 with the same normalized node-ID hash. It contains upstream
callable tests that are useful evidence but cannot be copied unchanged into a
separate verifier. The future private adapter must select only assertions that
are traceable to the JSON-safe contract in `instruction.md`.

## Candidate-boundary plan

The repository's generic Python candidate client serializes function arguments
and return values with JSON. A direct call such as
`candidate_client.call('petl.io.csv', 'fromcsv', ...)` cannot safely carry a
lazy `Table`, a file handle, a generator, a `Record`, or a callback. A
petl-specific child-side adapter is therefore required. The intended shape is:

```json
{
  "input": {
    "format": "csv|tsv|json|jsonl|rows",
    "text_or_rows": "bounded JSON/string payload",
    "header": ["..."],
    "options": {}
  },
  "pipeline": [
    {"op": "selecteq", "field": "status", "value": "ok"},
    {"op": "cut", "fields": ["id", "value"]}
  ],
  "output": {"format": "rows|csv|json|jsonl", "options": {}}
}
```

This JSON shape is a design note, not a committed verifier protocol. It must
be versioned, bounded, validated against an allowlist, and implemented in the
untrusted candidate child before hidden tests or a denominator can be frozen.
