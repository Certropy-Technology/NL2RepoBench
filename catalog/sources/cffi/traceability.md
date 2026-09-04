# cffi contract traceability

The hidden verifier runs 28 deterministic scenarios through a UID-isolated
child-side adapter. The trusted process compares only JSON-safe projections and
owns collection, JUnit, grading, reward, and network evidence.

| Scenario group | Public behavior |
| --- | --- |
| `exports-version`, `ffi-construction`, `error-hierarchy` | package identity and exception exports |
| `primitive-type`, `pointer-new`, `array-new`, `struct-new` | type parsing and allocation |
| `cast-and-size`, `getctype-normalization`, `null-and-bool` | C conversion, size, alignment, and constants |
| `string-read`, `buffer-read`, `pointer-arithmetic`, `addressof-array`, `struct-field` | local memory and buffer operations |
| `callback-success`, `callback-error`, `callback-onerror` | callback result and error contract |
| `handle-roundtrip`, `handle-identity` | opaque handle lifetime and identity |
| `cdef-types`, `cdef-invalid`, `list-types` | declaration parsing and named type inventory |
| `dlopen-abs`, `dlopen-strlen` | bounded access to local process symbols |
| `emit-c-code`, `set-source` | deterministic local code-generation metadata |
| `deterministic-repeat` | stable repeated observations |

The verifier intentionally excludes embedding executables, arbitrary shared
libraries, platform-specific ABI details, thread scheduling, and unsupported
free-threaded builds. No scenario inspects private implementation names,
generated filenames, hidden files, or candidate-written grading data.
