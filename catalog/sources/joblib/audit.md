# joblib authoring audit

Status: **controls-passed; awaiting independent Agent Run/review**.

The exact upstream revision is a BSD-3-Clause, pure-Python package with a
setuptools backend and one required runtime dependency (`cloudpickle`). The
task adds NumPy and lz4 to the private build-time closure because the selected
deterministic contract explicitly covers array persistence, memmap behavior,
and compressed persistence. The agent and separate verifier are both
no-network; no source host, package registry, or provider host is in task
metadata.

The upstream pytest tree collected 1540 nodes in the authoring probe, but its
optional Dask/async/plugin/platform behavior is not a stable child-process
denominator. The scored contract therefore uses 33 fixed JSON leaves driven
through a UID-separated candidate subprocess. The verifier owns collection,
JUnit, grading, and reward output. Candidate files cannot write trusted
reports or access the private bundle.

Bounded probes passed for package installation, all 33 private scenarios,
NumPy persistence, compression, cache invalidation, invalid inputs, and local
subprocess helper behavior. Harbor 0.21.0 production compile, Oracle, empty,
stub, forgery, and offline receipts are recorded in production-evidence.json.
