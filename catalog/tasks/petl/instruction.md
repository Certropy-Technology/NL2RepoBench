# Build `petl`: a restricted CSV/JSON table-transform library

This is an authoring-stage specification for the exact upstream project
`petl-developers/petl` at commit
`2e01e169d83e4f66bef108bc2f20cde878d0a8a1` (release `1.7.24`). The catalog
entry is currently **blocked** and is not a publishable Harbor task. The
implementation must still be created from an empty workspace: do not copy the
upstream source, upstream tests, a wheel, or a generated task bundle.

The scored surface is deliberately narrower than the complete petl project.
It measures an installable, lazy table library for local CSV/JSON data and
pure-Python table transforms. Optional database, spreadsheet, remote-storage,
scientific, Avro, interval, search-index, and XML integrations are documented
as provenance evidence but are not part of this task contract.

## Project Description

Build a Python distribution named `petl` (version `1.7.24`) that represents a
table as an iterable whose first row is a header and whose remaining rows are
data. The library must support:

- reading CSV/TSV and JSON/JSON-Lines files into repeatable table views;
- writing CSV/TSV and JSON/JSON-Lines representations;
- converting a table to row, dictionary, column, and materialized views; and
- deterministic structural, selection, value-conversion, sorting, and
  de-duplication transforms.

Views should be lazy where the upstream API is lazy: constructing a view does
not consume the source, and iteration yields tuples without mutating the input
rows. A view backed by a path or a replayable in-memory sequence can be
iterated more than once. A one-shot generator is allowed only where the API
explicitly documents caching/materialization (notably `fromdicts`); the scored
JSON adapter will represent repeatable JSON values rather than Python generator
identity.

The task measures observable behavior, not a particular internal module
layout. The package must nevertheless provide the import paths and root
re-exports listed below so that ordinary users can use either form:

```python
import petl as etl
from petl.io.csv import fromcsv
from petl.transform.selects import selecteq
```

## Supports

### Runtime and packaging

- Target the final verifier's pinned CPython 3.13 environment. The audit also
  exercised CPython 3.14.6; no claim is made for the historical Python 2
  classifiers or for unpinned future interpreters.
- The distribution must be installable with a normal PEP 517 build and must
  expose `petl.__version__ == "1.7.24"`.
- `import petl` must succeed without importing any optional integration package.
  The restricted path has no runtime third-party dependency beyond Python's
  standard library. Build backends and test tools are not runtime APIs.
- The verifier is offline. Do not download packages, call a URL, use a remote
  filesystem, open a database server, read credentials, inspect the host's
  environment for behavior, or depend on current time or random state.
- The final candidate must not include hidden tests, grader code, reward files,
  an Oracle implementation, credentials, or a copied upstream archive.

### Table representation

A table is an iterable of rows. The first row is the header; the header may
contain strings or other JSON-compatible scalar values, although string field
names are the normal form. Data rows may be shorter or longer than the header;
operations that select named fields use `None` as the default missing value
unless an operation exposes a `missing` parameter.

For a table `[['name', 'score'], ['A', 2]]`:

- `header(table)` returns `('name', 'score')` and raises `StopIteration` for
  a completely empty table;
- `fieldnames(table)` returns the header converted to strings;
- `data(table)` is a view over rows after the header;
- `dicts(table)` yields dictionaries keyed by stringified header values and
  pads short rows with `missing` (default `None`);
- `records(table)` yields tuple-like records supporting numeric indexing,
  field-name indexing, and attribute access (`row['name']`, `row.name`);
- `values(table, field, ...)` yields one selected value per data row, or tuples
  when multiple fields are selected;
- `nrows(table)` counts data rows, excluding the header; and
- `listoflists`, `listoftuples`, `tupleoflists`, and `tupleoftuples` materialize
  the requested row shape without silently dropping the header.

Field selectors accept a field name, a non-negative zero-based integer index, or
a sequence of names/indices where the API documents a compound key. A missing
or invalid selector raises `petl.errors.FieldSelectionError` when the view is
first iterated or its header is requested, matching the lazy error timing of
the upstream API.

The selected functions are available both at the module-level and as fluent
methods on `petl.util.base.Table` when the upstream package attaches that
method. For example, `etl.selecteq(table, 'status', 'ok')` and
`table.selecteq('status', 'ok')` have the same observable rows.

## API Usage Guide

The signatures below are the public contract for this restricted task. Keyword
arguments not listed as supported JSON/scalar options are outside the scored
surface, even if the historical implementation accepts them through `**kwargs`.

### CSV and TSV input

#### `petl.fromcsv`

```python
fromcsv(source=None, encoding=None, errors='strict', header=None, **csvargs)
```

`source` is a local path or an approved in-memory source supplied by the
verifier adapter. `None` denotes standard input only in a local CLI-style
probe; hidden scoring uses a bounded local fixture rather than an inherited
process stream. A path ending in `.gz` may be handled through the standard
library gzip source; URLs and other remote schemes are out of scope.

The result is a lazy table view. By default it uses the Excel CSV dialect and
returns every cell as a string. `header=[...]` prepends an explicit header
instead of consuming the first physical record. `encoding` and `errors` are
passed to the text decoder; the final environment uses UTF-8 and must preserve
Unicode text. The supported `csvargs` are JSON/scalar forms of the standard
library reader options, including `delimiter`, `quotechar`, `quoting`,
`doublequote`, `escapechar`, `skipinitialspace`, and `strict`. Custom dialect
classes, callables, arbitrary objects, and regular-expression delimiters are
out of scope.

The reader must accept `\n`, `\r`, and `\r\n` line endings, honor CSV quoting,
and preserve empty fields. It must not infer numeric types unless the selected
`quoting` mode of the standard CSV reader does so explicitly.

#### `petl.fromtsv`

```python
fromtsv(source=None, encoding=None, errors='strict', header=None, **csvargs)
```

This is `fromcsv` with the standard `excel-tab` dialect as its default. Explicit
`delimiter`/dialect options follow the same restricted rules.

#### `petl.tocsv` and `petl.appendcsv`

```python
tocsv(table, source=None, encoding=None, errors='strict',
      write_header=True, **csvargs)
appendcsv(table, source=None, encoding=None, errors='strict',
          write_header=False, **csvargs)
```

`tocsv` overwrites a local destination; `appendcsv` opens it in append mode and
does not write a header by default. Each row is written with the standard CSV
writer and the selected line terminator. `None` is serialized as an empty CSV
cell. Values are converted using the writer's normal string conversion.
Unicode, quoted delimiters, embedded newlines, and explicit `write_header` must
work. The functions return `None`, as in the upstream API.

`petl.totsv` and `petl.appendtsv` have the same signatures and semantics but use
the `excel-tab` dialect by default:

```python
totsv(table, source=None, encoding=None, errors='strict', write_header=True, **csvargs)
appendtsv(table, source=None, encoding=None, errors='strict', write_header=False, **csvargs)
```

### JSON and JSON-Lines input/output

#### `petl.fromjson`

```python
fromjson(source, *args, **kwargs)
```

The supported keyword options are `header`, `sample`, `missing`, and `lines`.
Without `lines`, the file contains one JSON array whose members are objects;
with `lines=True`, each non-empty physical line is parsed as one JSON object.
The result is a lazy table view. When `header` is omitted, keys are discovered
in first-seen order from up to `sample` objects. An explicit header fixes both
ordering and the output shape. A missing key yields `missing` (default `None`),
and extra object keys are ignored once the header is fixed.

Values remain JSON values: strings, booleans, numbers, null, arrays, and nested
objects must not be coerced to text. Invalid JSON is reported by the standard
JSON decoder exception rather than being silently skipped. JSON object key
ordering must be stable for a fixed input and header policy.

#### `petl.fromdicts`

```python
fromdicts(dicts, header=None, sample=1000, missing=None)
```

`dicts` is a sequence or a JSON-compatible iterable of objects. Header discovery
uses first-seen key order over at most `sample` objects. An explicit `header`
controls order; missing keys receive `missing`. The view exposes the inherited
`dicts()` method. For an input generator, the source may be cached so that the
view can be iterated repeatedly, but the scored adapter only supplies finite
JSON arrays and checks the resulting rows, not generator object identity.

#### `petl.tojson`

```python
tojson(table, source=None, prefix=None, suffix=None, *args, **kwargs)
```

The table header becomes object keys and each data row becomes one JSON object.
The default output is a JSON array. `lines=True` writes one object per line.
`prefix` and `suffix`, when supplied as strings, are written verbatim around the
encoded JSON document. JSONEncoder options such as `sort_keys`, `ensure_ascii`,
`indent`, `allow_nan`, and `separators` may be supplied when they are JSON
scalars/arrays. Callables, custom encoder classes, and non-JSON values are out
of scope. The function writes UTF-8 and returns `None`.

#### `petl.tojsonarrays`

```python
tojsonarrays(table, source=None, prefix=None, suffix=None,
             output_header=False, *args, **kwargs)
```

This has the same output and encoding options as `tojson`, but emits each row
as a JSON array. By default the header is omitted; `output_header=True` includes
it as the first JSON array. `lines=True` emits one JSON array per line.
Nested JSON values and Unicode must round-trip without Python `repr` text being
introduced.

### Deterministic table views and materialization

The following functions are in scope with the signatures observed at the
pinned revision:

```python
header(table)
fieldnames(table)
data(table, *sliceargs)
dicts(table, *sliceargs, **kwargs)
records(table, *sliceargs, **kwargs)
values(table, *field, **kwargs)
nrows(table)
listoflists(tbl)
listoftuples(tbl)
tupleoflists(tbl)
tupleoftuples(tbl)
columns(table, missing=None)
cache(table, n=None)
```

`data` and other slice views use Python `islice`-style positional boundaries.
`columns` materializes columns in header order and pads short rows with
`missing`. `cache` creates a repeatable view and may use temporary files when
the source is larger than its in-memory threshold; temporary files must be
owned and cleaned up by the view. No output may depend on hash randomization.

### Structural transforms

These transforms preserve a header row and yield a lazy table unless their
contract explicitly materializes a result. They accept field names or zero-based
indices as documented above.

```python
cut(table, *fields, missing=None)
cutout(table, *fields, missing=None)
cat(*tables, header=None, missing=None)
stack(*tables, header=None, missing=None)
addfield(table, field, value=None, index=None, missing=None)
addfields(table, field_defs, missing=None)
addcolumn(table, field, col, index=None, missing=None)
rowslice(table, *sliceargs)
head(table, n=5)
tail(table, n=5)
addrownumbers(table, start=1, step=1, field='row')
movefield(table, field, index)
```

For this task, `value`, `field_defs`, and `col` must be JSON-compatible constants
or finite JSON arrays. Callable row functions, context callbacks, and arbitrary
Python iterators are not scored. `cut` selects/reorders fields and pads a short
row with `missing`; `cutout` removes selected fields. `cat` aligns tables by
field name and fills absent values with `missing`; `stack` appends rows using the
first/explicit header. `addrownumbers` prepends a generated integer column.
`head`, `tail`, and `rowslice` keep the header while limiting data rows.

### Header transforms

```python
setheader(table, header)
extendheader(table, fields)
pushheader(table, header, *args)
skip(table, n)
rename(table, *args, strict=True)
prefixheader(table, prefix)
suffixheader(table, suffix)
sortheader(table, reverse=False, missing=None)
```

`setheader` replaces the existing header; `extendheader` appends fields;
`pushheader` prepends a header to a headerless/ordinary row stream and also
accepts positional field arguments. `skip` removes the first `n` rows from the
input, including the old header, so the next row becomes the new header.
`rename` accepts one `(old, new)` pair or a mapping; integer selectors refer to
positions. With `strict=True`, an unknown selector raises
`FieldSelectionError`; `strict=False` leaves the header unchanged for unknown
selectors. Prefix/suffix operations transform every header value after string
conversion. `sortheader` orders fields lexically and must keep duplicate header
values paired with their original columns.

### Selection transforms

The scored boundary uses convenience selectors, which are fully JSON-safe and
do not require shipping executable callbacks:

```python
selecteq(table, field, value, complement=False)
selectne(table, field, value, complement=False)
selectlt(table, field, value, complement=False)
selectle(table, field, value, complement=False)
selectgt(table, field, value, complement=False)
selectge(table, field, value, complement=False)
selectin(table, field, values, complement=False)
selectnotin(table, field, values, complement=False)
selectcontains(table, field, value, complement=False)
selecttrue(table, field, complement=False)
selectfalse(table, field, complement=False)
selectnone(table, field, complement=False)
selectnotnone(table, field, complement=False)
rowlenselect(table, n, complement=False)
```

Selectors keep the header and preserve input row order. `complement=True`
returns exactly the rows that would not satisfy the predicate. Comparisons use
Python's ordinary values, with the upstream handling of `None` and short rows.
The generic `select(table, callable_or_expression, ...)` API is not part of the
scored subprocess contract because arbitrary callables and unrestricted
expressions cannot be safely represented in JSON. A future task-specific
adapter may add a reviewed declarative predicate language; it must not use
`eval` on agent-controlled text.

### Value transforms

The following JSON-safe subset is supported:

```python
convert(table, *args, **kwargs)
convertall(table, *args, **kwargs)
replace(table, field, a, b, **kwargs)
replaceall(table, a, b, **kwargs)
update(table, field, value, **kwargs)
convertnumbers(table, strict=False, **kwargs)
format(table, field, fmt, **kwargs)
interpolate(table, field, fmt, **kwargs)
```

`convert` may select a field by name/index and use a string method descriptor
such as `'lower'`, `'strip'`, or `'replace'` with JSON arguments, or a mapping
of JSON input values to JSON output values. Callable converters, expression
strings, `pass_row`, and arbitrary objects are out of scope. `where` may be
omitted; when a future adapter supports it, it must use the same reviewed
predicate plan as selection rather than executable source text. `replace` and
`update` provide constant substitutions. `convertnumbers` recognizes the
numeric text forms documented by petl and leaves non-numeric text unchanged
unless `strict=True` requires an error. `format` and `interpolate` use the
provided Python format/template string on JSON scalar values; no user-supplied
code is evaluated.

For conversion failures, preserve the selected `failonerror`/`errorvalue`
behavior only when both options are JSON scalars. Do not serialize Python
exception objects into a successful JSON result.

### Sorting and de-duplication

```python
sort(table, key=None, reverse=False, buffersize=None, tempdir=None, cache=True)
mergesort(*tables, **kwargs)
issorted(table, key=None, reverse=False, strict=False)
duplicates(table, key=None, presorted=False, buffersize=None, tempdir=None, cache=True)
unique(table, key=None, presorted=False, buffersize=None, tempdir=None, cache=True)
distinct(table, key=None, count=None, presorted=False, buffersize=None, tempdir=None, cache=True)
isunique(table, field)
```

Keys are field names, indices, or compound sequences. `sort` is stable for
records with equal keys and supports ascending/descending order. Missing values
follow the pinned implementation's comparable ordering. `buffersize` may force
a standard-library temporary-file merge; `tempdir` is a verifier-owned local
directory and must not escape the workspace. `mergesort` combines tables whose
headers are aligned by the same rules as `cat`; `presorted=True` is an assertion
about caller input, not an instruction to reorder it. `duplicates` retains all
rows belonging to repeated keys, `unique` retains one row per key, and
`distinct` retains the first occurrence (or the requested count form). These
operations preserve deterministic input order where the upstream API does.

### Errors and edge behavior

The public exception classes for this scope are:

```python
from petl.errors import ArgumentError, DuplicateKeyError, FieldSelectionError
```

Use `FieldSelectionError` for an unknown field/index, `ArgumentError` for an
invalid source or transform option, and `DuplicateKeyError` where a keyed
operation rejects duplicate keys. File decoding errors, `csv.Error`, and
`json.JSONDecodeError` retain their standard exception types. Empty/header-only
and uneven-row behavior must match the function-specific rules above. Do not
turn an exception into a successful empty table merely to continue processing.

## Implementation Notes and explicit exclusions

1. Preserve the root package import/re-export surface for the selected names,
   but do not attempt to recreate every one of petl's 327 observed root public
   attributes. The full upstream API is evidence, not an implicit requirement.
2. Do not implement or score `fromdb`/`todb`, SQLAlchemy/MySQL/PostgreSQL,
   `fromgsheet`/`togsheet`, `RemoteSource`/S3/SFTP/SMB/HTTP, NumPy/Pandas,
   HDF5/PyTables, bcolz, Avro/fastavro, Whoosh, XLS/XLSX, interval-tree
   transforms, XML/HTML, plotting, CLI scripts, or documentation tooling.
   The optional integration matrix in the task-local audit explains these
   boundaries and their dependencies.
3. Do not make `asteval` a runtime dependency for the restricted task. The
   upstream package imports it only for its optional untrusted-expression path;
   executable callbacks and unrestricted expressions are intentionally absent.
4. Do not use `eval`, `exec`, pickle input, network access, subprocesses, or
   ambient credentials to implement the scored JSON transform protocol.
5. The hidden verifier must communicate with candidate code through a reviewed
   child-side adapter that accepts bounded JSON table values and returns bounded
   JSON observations. Trusted tests must not import candidate modules in the
   verifier process. That adapter and its private test bundle are not present
   in this authoring directory yet.
6. Do not claim that the provisional upstream count of 543 is a production
   denominator. The source JUnit report expands to 555 testcase elements while
   pytest reports 543 collection items; a final adapter must freeze one leaf
   model and reject collection mismatch.
7. Keep packaging, source, dependency, test, and license evidence separate
   from the candidate implementation. No private tests, Oracle bytes, wheel
   cache, Docker image, or reward artifact belongs in this public catalog task.
