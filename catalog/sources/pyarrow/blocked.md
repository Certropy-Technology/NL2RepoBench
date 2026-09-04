# `pyarrow` authoring audit - blocked

**Status: blocked / audit-only.** This record is not a runnable task, public
implementation specification, verifier, Oracle, or Harbor projection. No
`catalog/tasks/pyarrow/` runtime should exist while this blocker remains.

## Assigned Source

- Upstream: `https://github.com/apache/arrow`
- Revision: `287c749468bb0254ca910a9053efd04834ec32d6`
- Git tree: `d7e407b64c5039481a84b048c09875aa1d5c6064`
- License: Apache-2.0
- Required execution policy: `network_mode=no-network` for the Agent,
  candidate, verifier, Oracle, and every control.

The assigned object was fetched exactly and archived. The Python package is a
Cython/C++ binding rather than a self-contained Python project. Its root import
immediately imports `pyarrow.lib`, and the build invokes CMake with
`find_package(Arrow REQUIRED)`. The source also pins the external
`parquet-testing` and `arrow-testing` repositories as Git submodules.

## Bounded Remediation

The authoring probe installed the declared Python build backend plus CMake,
Ninja, Cython, and NumPy in a Python 3.12 environment. Wheel configuration then
failed because no matching `ArrowConfig.cmake` or Arrow C++ SDK was present.
This is not a missing Python build-backend error. A source-only pytest
collection separately exited 4 because `pyarrow.lib` had not been compiled.

The frozen tree contains 23 top-level Cython modules, 17 include fragments,
1,740 C/C++ source or header files under `cpp/src`, 56 CMake projects, and 56
Python test modules with 2,123 statically visible test functions plus 403
parameterization sites. The tested surface includes native arrays, buffers,
schemas, tables, compute kernels, IPC, Parquet, datasets, filesystems, Flight,
CUDA, pandas conversion, memory pools, and extension types. Reducing this to a
small pure-Python compatibility API would require an explicit scope decision
and would not be a faithful projection of the discovered package by default.

## NoNetwork Boundary

No runtime network path is proposed. Production support requires all of these
inputs to be built before runtime and injected as hash-verified private
artifacts: the exact Arrow C++ SDK and native dependency closure, a
source-derived PyArrow wheel, both pinned test-data submodules, hidden tests,
the child-side adapter, and the Oracle payload. A native reference wheel must
remain outside the public generated projection.

No fixed denominator was recorded because collection never started. No
verifier bundle, Oracle receipt, control result, or reward is claimed.

## Remediation

1. Approve a bounded public PyArrow API scope or require the full native
   package contract.
2. Build the exact Arrow C++ SDK and PyArrow wheel for the pinned revision in a
   reproducible Linux/amd64 image, with every native dependency and both
   submodules frozen and hash-locked.
3. Add or use an approved out-of-projection private Oracle payload path for the
   source-derived native wheel.
4. Design and review a child-side protocol for Arrow values and resources;
   trusted verifier code must not import candidate `pyarrow` in-process.
5. Collect a positive denominator in a clean NoNetwork image, compile the
   final task, and run fresh Oracle, empty, installable stub, forgery, and
   offline controls.

Until all five steps succeed, lifecycle remains `blocked`.
