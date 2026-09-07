# Build `cffi`

Create a complete, installable Python project named `cffi` from an empty
workspace. Implement the deterministic public subset below for CPython 3.12 on
Linux. The evaluator has a C compiler and libffi available during installation,
but runtime execution is local and has no network access. Do not copy an
existing cffi checkout or depend on a preinstalled cffi package.

## Project Description

`cffi` provides a Python-level foreign-function interface. The required slice
parses C declarations, allocates and converts C-like values, creates callbacks,
and accesses a small set of local process symbols. The implementation may use
the real native backend or a faithful compatible implementation, but all
observable behavior in this specification must be deterministic and bounded.

## Natural Language Instruction

Create `cffi` from an empty workspace. Implement the bounded FFI API below for
declaration parsing, C-like values, callbacks, opaque handles, local symbols,
and deterministic code-generation metadata. Keep native objects and callbacks
inside the local implementation boundary.

## Supports or Environment Configuration

- Support CPython 3.12 and provide an installable distribution named `cffi`,
  version `2.2.0.dev0`, requiring Python 3.10 or newer.
- Export `FFI` from `cffi`, plus `CDefError`, `FFIError`, `VerificationError`,
  and `VerificationMissing` from `cffi.error` and the top-level package.
- The package must import without network access and must not perform DNS,
  socket, subprocess, or uncontrolled filesystem operations during ordinary API
  calls. Temporary files created by explicit C-generation methods are allowed.
- Use only the standard library at runtime except for the declared `pycparser`
  dependency. Build tools and native libraries are supplied by the environment.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── cffi/
    ├── __init__.py
    ├── api.py
    ├── error.py
    └── model.py
```

## API Usage Guide

### `cffi.FFI`

Import path: `from cffi import FFI`.

Signature: `FFI(backend=None) -> FFI`. With the default backend it exposes the
native CFFI implementation. `ffi.cdef(csource, override=False, packed=False,
pack=None) -> None` parses C declarations and registers types, functions, and
variables. Invalid declarations raise `cffi.error.CDefError` or a compatible
`FFIError`.

`ffi.typeof(cdecl_or_cdata)` returns a C type object. Its stable properties for
this task include `kind`, `cname`, `item`, `length`, and `args` where applicable.
`ffi.getctype(cdecl_or_type, replace_with='')` returns normalized C declaration
text. `ffi.sizeof(cdecl_or_cdata)` and `ffi.alignof(cdecl_or_cdata)` return
positive platform sizes for the supported primitive and aggregate types.

### C data allocation and conversion

`ffi.new(cdecl, init=None)` allocates a C data object. Support primitive
pointers, fixed and open arrays, structs, and pointers to those values. Pointer
and array indexing, field access, assignment, `len()`, and deterministic
`repr()` follow C semantics. `ffi.cast(cdecl, value)` converts integers,
addresses, and compatible C data. `ffi.string(cdata, maxlen=-1)` reads a NUL-
terminated character array or pointer, and `ffi.buffer(cdata, size=-1)` exposes
the selected bytes through the Python buffer protocol.

`ffi.callback(cdecl, python_callable, error=None, onerror=None)` returns a
callable C callback. Calling it with valid Python arguments returns the declared
C result. If the Python callable raises, the configured `error` value is
returned; `onerror` receives the exception triple when supplied. Callbacks are
local objects and must not spawn threads or contact services.

`ffi.new_handle(obj)` returns an opaque `void *` handle and `ffi.from_handle`
recovers the exact object while the handle is alive. Separate handles for the
same object remain distinct. `ffi.addressof(cdata, *fields)` returns a pointer
to an array or struct field without mutating the original object.

### Local libraries and generated code

`ffi.dlopen(None)` may expose symbols from the current process. For this task,
support declarations and calls for `strlen(const char *)` and `abs(int)` only;
no external library path or network-backed loader is required. `ffi.set_source`
and `ffi.emit_c_code(path)` may generate deterministic local C source for a
declared module; failures use the documented `IOError`/`OSError` contract.
`ffi.list_types()` returns deterministic lists of declared primitive, struct,
union, enum, and typedef names.

## Implementation Notes

Keep the package layout compatible with direct imports of `cffi.api`,
`cffi.error`, and `cffi.model`. Preserve the native-vs-pure implementation
boundary and typed exception relationships. The hidden verifier invokes the
candidate only through a UID-isolated JSON adapter, so native objects never
cross into the evaluation process. Do not add extra test suites, fake reward reports,
vendored wheels, or network fallbacks.

## Examples

```python
from cffi import FFI
ffi = FFI()
ffi.cdef('int abs(int);')
value = ffi.new('int *', 3)
assert value[0] == 3
```

```python
ffi.cdef('size_t strlen(const char *);')
lib = ffi.dlopen(None)
assert lib.strlen(ffi.new('char[]', b'abc')) == 3
```

## Error Handling and Boundary Conditions

Invalid C declarations raise `CDefError` or a compatible `FFIError`. Only
local process symbols and bounded declarations are required; arbitrary shared
libraries and unsupported platform ABI behavior remain outside this project.
