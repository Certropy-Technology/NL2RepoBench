# `coxeter` static authoring audit

Status: **blocked**. This task-local directory contains public declarative
metadata, a scope outline, and static provenance/collection evidence only. It
contains no copied upstream tests, hidden assertions, private command plan,
dependency wheels, Docker file, verifier implementation, Oracle solution,
secret, or shared dataset/index edit.

## Decision

Keep this candidate in the blocked authoring state. The exact revision is a
credible hard computational-geometry candidate, but the current evidence is
not a publication gate:

- the source archive contains a mixed-license documentation/paper tree even
  though the runtime package is BSD-3-Clause plus vendored MIT code;
- the package build has stale manifest entries and does not carry the two
  vendored license files into the probed wheel;
- the source's generated requirement files pin versions but not artifact hashes,
  and the CI build policy compiles packages from source, so no offline
  compiler/native dependency closure is frozen;
- the test suite is heavily property-based and numerical, uses unseeded random
  geometry and SciPy/Qhull/miniball paths, and contains skipped and xfailed
  cases whose metric treatment is not approved; and
- the generic candidate subprocess client cannot carry NumPy arrays, custom
  shape objects, paths, or mutable state across its JSON calls. No
  coxeter-specific child-side scenario adapter exists.

No Oracle, full baseline, hidden-test materialization, or publication claim is
made by this audit.

## Candidate identity and exact source

The candidate entry was read from `reports/github-package-candidates.v1.json`:

- task ID: `coxeter`;
- upstream: `https://github.com/glotzerlab/coxeter`;
- requested and resolved revision:
  `9056679b197f0e835c04dd317cc1049359a0ee7c`;
- discovery stars: `25`;
- discovery update date: `2026-07-29`;
- discovery category: `computational-geometry`;
- discovery difficulty: `hard`;
- discovery recommendation: `freeze-pilot`;
- listed risks: floating-point geometry, degenerate shapes, and SciPy.

The detached checkout used for the audit was `/tmp/nl2repo-candidates/coxeter`.
It resolved to the requested SHA and had no submodules. The commit metadata is:

```text
commit:  9056679b197f0e835c04dd317cc1049359a0ee7c
tree:    6b30c7f9037a530aa9ac13e97002dafb55e67266
parent:  b48f6d8b7246cfbdd36f136a796f8b58fbd363c2
date:    2026-07-29T18:15:58Z
subject: Update pypa/gh-action-pypi-publish action to v1.14.2 (#344)
```

The source lock is an unprefixed archive from that detached commit:

```text
command:      git archive --format=tar HEAD
archive bytes: 12,421,120
archive members: 371 (345 tracked files plus directory entries)
sha256:       ffbb73420cc80e12530d37cb2e197d687d432c83a764f2dd3f0d1d7a58c17b12
```

Two independent archive commands produced the same digest. The archive
contains runtime code and family data as well as `doc/`, `.github/`, `paper/`,
and tests; it must not be treated as a redistributable runtime bundle without
filtering its non-runtime content.

## License and archive review

The runtime project's `LICENSE` is BSD 3-Clause:

```text
path:       LICENSE
bytes:      1,566
Git blob:   69f9ed6b977edc38a11c9d9fc9dbb3e2834179ac
sha256:     72843f9fe9d373f3cf9570470d71cf811cbe399fe81f66ebbf2dce0234a0b0b0
```

`pyproject.toml` declares the same license expression. The package also
vendors two separately licensed implementations:

| path | license evidence | bytes | file SHA-256 | Git blob |
| --- | --- | ---: | --- | --- |
| `coxeter/extern/bentley_ottmann/LICENSE` | MIT text | 1,095 | `bcc090b847626a3118b4234c288fe636942183d1c4987e94c410bfde69b29ce2` | `e9e786b7a401d38b79ea483d973524d3c33b9914` |
| `coxeter/extern/polytri/LICENSE` | MIT text | 1,083 | `e2cfa0783b52c21fe19faf582250bf4cad93ae900311e78d71536a1ac07eb2db` | `0f6bff5266efe3bd35964c1f69fe1d4fa5b81310` |

Both file digests and Git blobs were checked independently. The exact source archive also
contains documentation/paper assets with other terms:

- `ContributorAgreement.md` is marked CC BY-SA 3.0;
- `paper/figure1/shape_images/data/low_poly_stanford_bunny/LICENSE` is CC
  BY-NC 4.0 (268 bytes, SHA-256
  `5a4dd92e67255ef1a58bb86f5efc20c43d046493e71d4f3bfd1721e29fcadfc6`).

Those files are outside the runtime package boundary, but a future source
artifact must not silently distribute the full archive as if every member had
the BSD license. The runtime package build probe included the root license in
`dist-info` but did not include either vendored `coxeter/extern/*/LICENSE` file;
license-notice preservation therefore remains an explicit packaging review
item.

## Package boundary, LOC, and API inventory

The source uses a package-root layout (`coxeter/`), not `src/`. The runtime
boundary has 30 tracked Python files and seven JSON family-data files:

| tree | files | physical lines | nonblank | noncomment | bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| `coxeter/**/*.py` | 30 | 8,914 | 7,374 | 6,780 | 319,162 |
| vendored `coxeter/extern/**/*.py` | 5 | 1,474 | 1,232 | 1,086 | included above |
| non-vendored package `.py` | 25 | 7,440 | 6,142 | 5,694 | included above |
| `coxeter/families/data/*.json` | 7 | — | — | — | 765,572 |

The seven JSON files contain 290 tabulated shape records in total. The package
code plus data and the two vendored license files occupy 1,086,912 tracked
bytes. The report does not provide a LOC/API estimate; the counts above are
reproducible physical/nonblank/noncomment counts from the exact checkout and
are not a frozen benchmark denominator.

A static AST inventory excluding vendored code and the data-conversion helper
found:

- 27 public class definitions: 13 shape/base classes (three abstract/base
  classes and ten concrete shapes) and 14 family classes;
- 51 public module-level declarations across the non-vendored package,
  including re-exports, helper functions, classes, and constants;
- root `coxeter.__all__`: 4 names;
- `coxeter.shapes.__all__`: 13 names;
- `coxeter.families.__all__`: 20 names; and
- 221 unique public class member names in the AST inventory (159 properties
  and 62 methods after collapsing property setters).

The last figure is an inventory aid, not an API-size claim: it includes
abstract/base members and non-root module names, while aliases and inherited
behavior require manual review. The main public behavior groups are analytic
shapes, polygon/polyhedron topology, rounded shapes, bounding objects,
inertia/form factors, shape families, GSD conversion, mesh exporters, and
shape moves.

## Packaging and source-build observations

Relevant metadata from the exact `pyproject.toml` is:

- distribution/version: `coxeter` `0.10.0`;
- build backend: `setuptools.build_meta`, with unbounded `setuptools` and
  `wheel` build requirements;
- Python metadata: `>=3.9` (the README still says the package is tested for
  Python `>=3.8`, which is inconsistent with the project metadata);
- runtime requirements: `numpy>=1.19.0`, `rowan>=1.2.0`, `scipy>1.0.0`;
- optional test requirements are read from `tests/requirements.in`;
- explicit package list includes `coxeter`, `coxeter.shapes`,
  `coxeter.families`, and the two `coxeter.extern` packages; and
- JSON files are brought into the build through `MANIFEST.in` even though
  `coxeter.families.data` is not explicit in the package list.

A temporary packaging probe was run outside this repository with `uv build`
using the source checkout. It did not save an artifact here and did not run
package tests. The probe produced:

```text
wheel: coxeter-0.10.0-py3-none-any.whl
       163,165 bytes
       sha256 2d0208ca42c01c0de9e1ff07a24a288291c2f731ccc6b6d393ca394d30dc751b
sdist: coxeter-0.10.0.tar.gz
       173,091 bytes
       sha256 5ba07ea6ca485e60ad57cb6c28f1f8712282f293d88a45dd7f782ef7eeebfc72
```

The wheel contained all seven JSON files and the runtime Python modules, but
setuptools emitted these warnings:

- `MANIFEST.in` asks for missing `README.md` and `ChangeLog.md` while the
  repository has `README.rst` and `ChangeLog.rst`;
- `coxeter.families.data` is importable but absent from the explicit package
  list; and
- only the root license was installed under `*.dist-info/licenses/`, not the
  two vendored MIT license files.

This is a packaging/provenance observation, not a claim that the wheel is an
approved verifier artifact. A final task must build from a pinned environment,
check package-data and notices, and preserve the exact artifact digest.

## Runtime and SciPy dependency closure

The source import scan found these relevant runtime paths:

- NumPy arrays and linear algebra throughout the shape implementations;
- `rowan` for quaternion rotations and mappings;
- SciPy `constants.golden_ratio`, `sparse.csgraph.connected_components`,
  `spatial.ConvexHull`, `spatial.HalfspaceIntersection`, and
  `special.ellipe`, `ellipeinc`, and `ellipkinc`; and
- optional `miniball` for minimal bounding circles/spheres and lazy
  `matplotlib`/`plato.draw` backends for plotting; and
- dormant `decimal`/`gmpy2` number modes in the vendored Bentley-Ottmann
  module (the default is the native-float mode and the non-native modes are
  marked as not passing upstream tests).

The tests additionally use SciPy `spatial.ConvexHull` and `Delaunay`,
Hypothesis (including its NumPy extra), Matplotlib, `plato-draw`, `miniball`,
pytest plugins, temporary files, and the checked-in mesh control files. The
tracked test requirements are:

```text
docutils
hypothesis[numpy]
matplotlib
miniball
plato-draw
pytest
pytest-cov
pytest-doctestplus
pytest-xdist
setuptools
wheel
```

The revision has four generated uv requirement files for Python 3.10 through
3.13, but no `uv.lock`, hash-pinned wheelhouse, image digest, compiler lock, or
offline artifact bundle. Their selected numerical versions differ:

| target | NumPy | SciPy | Matplotlib |
| --- | --- | --- | --- |
| 3.10 | 2.2.6 | 1.15.3 | 3.10.9 |
| 3.11 | 2.4.6 | 1.17.1 | 3.11.1 |
| 3.12 | 2.5.1 | 1.18.0 | 3.11.1 |
| 3.13 | 2.5.1 | 1.18.0 | 3.11.1 |

The 3.13 generated closure resolved 29 distributions (versions below) in a
temporary environment:

```text
contourpy==1.3.3       coverage==7.15.2       cycler==0.12.1
 docutils==0.23         execnet==2.1.2         fonttools==4.63.0
 hypothesis==6.158.1    iniconfig==2.3.0      kiwisolver==1.5.0
 matplotlib==3.11.1     miniball==1.2.0       numpy==2.5.1
 packaging==26.2        pillow==12.3.0        plato-draw==1.12.0
 pluggy==1.6.0          pygments==2.20.0      pyparsing==3.3.2
 pytest==9.1.1          pytest-cov==7.1.0     pytest-doctestplus==1.7.1
 pytest-xdist==3.8.0    python-dateutil==2.9.0.post0
 rowan==1.3.2           scipy==1.18.0        setuptools==83.0.0
 six==1.17.0             sortedcontainers==2.4.0 wheel==0.47.0
```

This is an observed resolver result, not a lock. SciPy and NumPy are native
packages; the source CI explicitly uses `only-binary: ":none:"`, so a source
build also needs a compiler/Fortran/BLAS toolchain that is not described by the
candidate manifest. A clean-cache offline probe was intentionally run against
the generated 3.13 requirements:

```text
UV_CACHE_DIR=/tmp/coxeter-empty-cache \
  uv pip install --offline --no-cache \
  --python /tmp/coxeter-offline-venv/bin/python \
  -r /tmp/nl2repo-candidates/coxeter/.github/requirements3.13.txt
exit: 1
message: contourpy was not found in the cache; network-disabled resolution
         had no available package
log sha256: 5f855234b50cc798a08dc59e97462895d4b6e0ca88cfd2276642a306a2d5bbf6
```

Therefore `dependencies.status` remains `unknown`; the generated requirement
files cannot be promoted to the required hash-locked offline closure.

## Test collection and geometry coverage

No test body was executed. The collect-only probes used the exact detached
source and the tracked generated requirements:

```text
CPython 3.13.14 / pytest 9.1.1 / NumPy 2.5.1 / SciPy 1.18.0
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD \
  /tmp/coxeter-audit-venv/bin/python -m pytest tests \
  --collect-only -q -p no:cacheprovider
exit: 0
summary: 2,943 tests collected
```

A second 3.13 run had the same node set. CPython 3.12.11 with the 3.12
requirement file also collected 2,943 nodes. The normalized test-node list
(the timing line and warning text removed) has SHA-256
`7cd7d151febd4164efcfbb20b0857716611ddf098bc988abf134ba28234d35be` in all
of these probes. Repeating the 3.13 collection with `PYTHONHASHSEED=0`, `1`,
and `random` kept both the 2,943 count and that node-list digest. Raw stdout
hashes differ only because the elapsed-time summary changes.

The intended `tests` path has these observed node totals:

| module | nodes |
| --- | ---: |
| `test_circle.py` | 21 |
| `test_ellipse.py` | 22 |
| `test_ellipsoid.py` | 21 |
| `test_io.py` | 14 |
| `test_plato.py` | 6 |
| `test_polygon.py` | 150 |
| `test_polyhedron.py` | 2,305 |
| `test_shape_families.py` | 331 |
| `test_shape_getters.py` | 7 |
| `test_shapemoves.py` | 5 |
| `test_sphere.py` | 22 |
| `test_spheropolygon.py` | 24 |
| `test_spheropolyhedron.py` | 15 |
| **total** | **2,943** |

The source files contain 265 ordinary `test*` definitions; parametrization and
Hypothesis expand this to the observed node count. Coverage is geometry-heavy:

- analytic circle/ellipse/sphere/ellipsoid properties and invalid-parameter
  errors;
- polygon and polyhedron construction, orientation, faces/edges, volumes,
  surface areas, centroids, inertia tensors, bounding circles/spheres,
  containment, form factors, and rotations;
- rounded shapes and their volume, area, curvature, containment, and GSD/HOOMD
  conversions;
- tabulated and continuous shape families, including 145 records in the
  Science family data; and
- exact text comparisons for OBJ/OFF/STL/PLY/X3D/VTK/HTML exporters plus six
  optional Matplotlib/Plato smoke tests using temporary PNG files.

The suite has 125 direct `@given` decorators in the AST inventory (including two nested rotation checks) and 35
`pytest.mark.parametrize` decorators. Five polyhedron tests are unconditionally
skipped with “Need test data”; six Plato tests are conditional on Matplotlib and
Plato; one polyhedron test is xfailed for known miniball numerical precision;
and one spheropolyhedron test is xfailed because the maximum rounding radius is
shape-dependent. There are also 20 pytest collection deprecation warnings about
passing generators/non-collection iterables to `parametrize`. The frozen metric
must decide how skips, xfails, and collection warnings are represented before
any denominator is accepted.

## Floating-point, randomness, and geometry determinism

Collection stability is not behavioral determinism. Static review found:

- `tests/conftest.py` uses unseeded `np.random.normal` for ellipsoid surface
  strategies and unseeded `np.random.shuffle` for unordered cube faces;
- polygon tests use `rowan.random.rand` to generate rotation quaternions;
- the polyhedron suite uses an unseeded `random.sample` subset of the 145-shape
  family and Monte Carlo helpers based on `np.random.rand`; one inertia test
  calls `np.random.seed(0)`, but neighboring paths are not globally seeded;
- the implementation itself retries `miniball` after `np.linalg.LinAlgError` by
  applying a random `rowan` rotation, so even a fixed input can take a
  randomized fallback path;
- `is_not_ci()` changes Hypothesis workload based on `CI`/`GITHUB_ACTIONS`, and
  the upstream CI runs `pytest -n auto`; and
- Qhull/Scipy triangulation, `np.linalg.lstsq`, `miniball`, quaternion rotation,
  and native BLAS all have platform/version-sensitive ordering or rounding
  behavior.

Assertions mix default `np.isclose`/`np.allclose` and `pytest.approx` with
explicit tolerances including approximately `1e-15`, `1e-12`, `1e-7`, `1e-5`,
`1e-2`, `1e-1`, and `2e-1`; some family/data checks use exact array equality,
and exporter tests compare generated files to checked-in controls. The tests
also deliberately generate duplicate, identical, non-planar, near-degenerate,
ill-conditioned, and invalid-radius inputs; some triangulation failures are
assumed away or accepted as known limitations. Several Monte Carlo checks have
large dynamic sample loops and broad tolerances.

A final task would need a pinned interpreter, NumPy/SciPy/miniball/rowan build,
BLAS and Qhull policy, explicit random seed and Hypothesis profile, stable
single-process policy (or an approved parallel policy), and a documented
skipped/xfail/known-failure metric. None of those choices is made here, and no
full baseline or Oracle run was performed.

## Candidate subprocess boundary

The repository's generic `candidate_client` sends one JSON request to a fresh
unprivileged child process per call and JSON-encodes the return value. That
contract is not a transparent boundary for this package:

- constructors require NumPy-like vertex/point/face arrays and return custom
  shape instances;
- properties return arrays, lists of arrays, complex form-factor values, and
  custom `Circle`/`Sphere`/family objects;
- tests mutate a shape and then inspect several dependent properties, so state
  must survive multiple operations in one child process;
- `to_plato_scene` returns a backend scene object, while I/O methods accept
  `PathLike` destinations and write files that must be inspected;
- shape-family objects load bundled JSON data and expose iteration/lookup state;
  and
- `coxeter/families/data/MathematicaToPython.py` can invoke an external
  `wolframscript` subprocess and rewrite JSON files if called, which is not an
  allowed ordinary verifier side effect.

Passing Python lists instead of arrays would not solve the boundary: a generic
JSON response still cannot serialize NumPy arrays or custom shape instances,
and each `candidate_client.call` starts a new child. A trusted pytest suite that
imports the candidate directly would violate the separate-verifier contract.

The required future design is a coxeter-specific child-side scenario adapter:
trusted tests send declarative JSON shape descriptions and operation sequences;
the child reconstructs arrays and maintains object handles; responses encode
array dtype/shape/data, scalar/complex values, serialized geometry objects,
exceptions, and approved file artifacts; and the adapter rejects external
network/process access. Hidden expected values and private assertions remain
outside the child. No such adapter, private test bundle, or command artifact
exists in this pilot.

## Reopen conditions

Do not compile or publish this task until all of the following are separately
evidenced:

1. an owner-approved runtime package boundary that excludes or accounts for the
   mixed-license paper/documentation assets;
2. a reproducible build whose package data and vendored license notices are
   checked, with a final image digest and source/build logs;
3. a complete hash-locked offline closure for NumPy, SciPy, rowan, miniball,
   test plugins, native wheels or compiler/BLAS/Qhull dependencies, and the
   selected Python/OS platform;
4. a fresh collection in that final image with an explicit skipped/xfail policy
   and stable structured denominator;
5. repeated numerical/randomness probes and three valid Oracle baselines that
   establish an Oracle ceiling rather than assuming reward 1.0; and
6. a reviewed child-side stateful JSON adapter, followed by empty, stub,
   forgery, and offline controls.

No Docker build, hidden-test materialization, candidate behavior suite,
Oracle, secret use, or shared catalog/index mutation was performed for this
pilot. The only repository files written by this task are the three files in
`catalog/tasks/coxeter/`.

## Static validation commands

The evidence above was obtained with the following classes of commands:

- `git clone`/detached checkout and `git rev-parse`/`git submodule status`;
- repeated `git archive --format=tar HEAD` hashing and license-file hashing;
- AST/line-count/import scans over `coxeter/` and `tests/`;
- `uv` temporary environments from the tracked 3.12/3.13 requirement files;
- `pytest --collect-only` only (no test bodies);
- `uv build --wheel` and `uv build --sdist` in `/tmp` only; and
- a clean-cache `uv pip install --offline --no-cache` probe that failed closed
  because package artifacts were not available.
