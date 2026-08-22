# `platformdirs` Static Screening Audit

Status: **blocked**. This directory contains an audit record only. It does
not contain a task descriptor, public instruction, Harbor bundle, verifier,
Oracle, private test artifact, dependency wheelhouse, or copied upstream
source/test bytes. No legacy task, dataset, conversion-loop state, or shared
file was changed.

The requested upstream revision is a coherent pure-Python filesystem/platform
candidate, but it cannot advance past static screening. The local authoring
state has no immutable verifier image for `platformdirs`, no final environment
or offline dependency lock, no authorized private test/command artifact, and
no reviewed separate candidate adapter for the direct-import and patch-heavy
test suite.

## Candidate Identity

- Discovery record: `reports/python-package-candidates.v1.json` entry
  `platformdirs`.
- Repository: `https://github.com/tox-dev/platformdirs`.
- Requested detached revision:
  `d3cf61ce5e729f2c35f830b69e14adb7b6970a00`.
- Commit subject: `[pre-commit.ci] pre-commit autoupdate (#525)`.
- Commit author/committer: `pre-commit-ci[bot]` / `GitHub`.
- Commit date: `2026-08-17T10:42:19-07:00`.
- Revision tree: `9a2e1a4f3e8bfcda7896d35c4e156e3d90090dbd`.
- Submodules: none.
- The detached checkout was clean before inspection and remained clean after
  the temporary audit build.

The unprefixed archive was generated twice with
`git archive --format=tar d3cf61ce5e729f2c35f830b69e14adb7b6970a00`:

- archive bytes: `358400`;
- archive SHA-256: `01837750779cd8f90d271f9b6184cf7d8d78fac37c72ce40ac97ccfb4064d572`.

The package source consists of eight Python modules under `src/platformdirs`
plus the empty `py.typed` marker. Static inventory found 2,305 nonblank,
non-comment implementation lines (2,924 physical lines), 54 public root
functions, five public Windows resolver functions, one public module entry
point, and six public classes, for 66 top-level public API symbols. The
discovery report's `medium`, 2,305-SLOC, 66-API characterization is therefore
consistent with the requested tree.

## License And Source Provenance

`LICENSE` at the pinned revision is the MIT License:

- Git blob: `f35fed9191b1142ddaada8a96de4a9461c5d796c`;
- bytes: `1,089`;
- file SHA-256: `29e0fd62e929850e86eb28c3fdccf0cefdf4fa94879011cffb3d0d4bed6d4db6`.

The SPDX mapping is `MIT`, consistent with the `project.license` field and
the MIT classifier in `pyproject.toml`. The source URL, full commit, tree,
archive digest, and license digest are all identified. This does not establish
an image-backed source/test lock because no platformdirs verifier image is
present in either available conversion-loop state record.

## Filesystem And Platform Matrix

The package selects its implementation at import time:

- `sys.platform == "win32"`: `Windows`;
- `sys.platform == "darwin"`: `MacOS`;
- all other platforms: `Unix`;
- Android is selected when `ANDROID_DATA=/data` and `ANDROID_ROOT=/system`,
  without `SHELL` or `PREFIX`, and the Android application directory can be
  resolved through `jnius`, Python-for-Android's `android` module, or a
  recognized `sys.path` layout.

The upstream CI matrix is materially broader than a single Linux verifier:

| Dimension | Declared matrix |
| --- | --- |
| OS | `ubuntu-24.04`, `windows-2025`, `macos-15` |
| CPython | `3.10`, `3.11`, `3.12`, `3.13`, `3.14`, `3.15` |
| Free-threaded | `3.15t` |
| PyPy | `pypy3.11` on Unix; Windows/PyPy excluded |
| Test jobs | 23 matrix jobs after the Windows/PyPy exclusion |

The tests exercise or emulate:

- Unix/XDG defaults, `XDG_*` overrides, `user-dirs.dirs`, `HOME`,
  `USERPROFILE`, `os.pathsep`, UID 0 versus non-root behavior, writable and
  non-writable runtime directories, FreeBSD/NetBSD/OpenBSD fallback paths,
  and creation/no-creation behavior via `tmp_path`;
- macOS `~/Library` conventions, XDG overrides, Homebrew prefix detection,
  multi-path and single-path results, and filesystem directory creation;
- Windows environment-variable fallbacks, `ctypes` known-folder resolution,
  registry lookup, `PUBLIC`/`USERPROFILE` behavior, and
  `WIN_PD_OVERRIDE_*` variables;
- Android application storage resolution, mocked `jnius`/Python-for-Android
  modules, Android `sys.path` layouts, and `ensure_exists` directory creation;
- a subprocess invocation of `python -m platformdirs` in
  `tests/test_main.py`.

Most Windows and macOS behavior is tested through direct construction and
mocking on the host OS. Two Windows groups are genuinely host-dependent:
the real `ctypes` known-folder tests run only on Windows, and live registry
tests run only on Windows. Android tests are emulation/mocking tests rather
than a real Android runtime. Consequently, a Linux collection count alone
does not establish cross-platform execution parity.

## Collection Evidence

The source checkout has eight test Python files and 105 ordinary top-level
`test_*` definitions. After building a temporary wheel to generate the
VCS-derived `platformdirs.version` module, collection was run against the
public upstream tests with:

```text
PYTHONDONTWRITEBYTECODE=1 /tmp/platformdirs-venv/bin/python -m pytest \
  --collect-only -q -p no:cacheprovider /tmp/platformdirs-source/tests
```

The temporary environment used CPython `3.13.14`, `pytest==9.0.2`,
`pytest-mock==3.15.1`, and `appdirs==1.4.4`. Collection completed without
errors and reported **1,097 nodes**. The per-file node counts were:

| Test file | Collected nodes |
| --- | ---: |
| `tests/test_android.py` | 143 |
| `tests/test_api.py` | 272 |
| `tests/test_comp_with_appdirs.py` | 111 |
| `tests/test_macos.py` | 188 |
| `tests/test_main.py` | 2 |
| `tests/test_unix.py` | 212 |
| `tests/test_windows.py` | 169 |
| **Total** | **1,097** |

This is a source-only collection observation. It is not a frozen verifier
denominator: no immutable test fixture, final image, structured final-image
collection record, skip/xfail policy, or approved command plan exists for
this candidate. The discovery report's `105` is a static definition count,
not the effective parametrized test total.

The first direct `PYTHONPATH=src` collection attempt failed because the
source tree intentionally expects Hatch VCS to generate `version.py`; the
temporary wheel build resolved that packaging prerequisite. This packaging
requirement is itself relevant to the eventual candidate install contract.

## Dependency And Image Lock

The pinned `pyproject.toml` declares no runtime dependencies. It uses a
dynamic VCS version and requires this build backend closure:

```text
hatch-vcs>=0.5
hatchling>=1.29
```

The test dependency group declares:

```text
appdirs==1.4.4
covdefaults>=2.3
diff-cover>=10.2
pytest>=9.0.2
pytest-cov>=7
pytest-mock>=3.15.1
```

The repository has no `uv.lock`, hash-bearing requirements file, complete
wheelhouse, system-package lock, or task-authorized private dependency
artifact. `tox.toml` additionally requires unpinned `tox>=4.47` for the
matrix runner and the CI installs the latest `tox`, `uv`, and managed Python
interpreters. The temporary wheel and venv used for collection are validation
artifacts under `/tmp`, not dependency locks.

Neither `/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` nor
`/data/NL2RepoBench-current/.nl2repo/conversion-loop/state.json` contains a
`platformdirs` entry. No immutable verifier image reference, platform/config
digest, image filesystem inventory, protected test copy, build history,
network mode, or final runtime package inventory can therefore be claimed.
The dependency and environment status remains **unknown** and must fail the
publication gate rather than being inferred from the public source or the
unrelated Harbor runner lock.

## Candidate Boundary

The frozen upstream tests are not directly compatible with the required
trusted-root/separate-candidate boundary:

- all test modules directly import `platformdirs` and its `android`, `macos`,
  `unix`, and `windows` submodules in the trusted pytest process;
- tests inspect live classes, functions, signatures, properties, `Path`
  objects, module metadata, and the `AppDirs is PlatformDirs` alias;
- `pytest-mock` patches candidate module functions, `os.pathsep`, `sys.platform`,
  `sys.prefix`, `sys.modules`, `builtins.__import__`, `ctypes`, environment
  variables, UID calls, filesystem access, and the Windows resolver;
- tests reload candidate modules with `importlib.reload`, inspect mock call
  counts/arguments, and deliberately simulate missing `ctypes`, `jnius`, and
  Android modules;
- `test_main.py` also launches `sys.executable -m platformdirs` and checks
  the child output.

These assertions involve in-process object identity, monkeypatch scope,
module cache state, live `Path` values, and platform-specific native APIs. The
generic JSON candidate boundary cannot transparently preserve these semantics.
A task-specific child adapter could normalize the directory/string/path
surface and expose a module command, but that adapter does not exist or have
an approved behavior mapping. Copying the upstream tests into a trusted
verifier would violate the separate-verifier policy; creating an opaque test
reference without its authorized bytes would also be invalid.

## Decision And Reopen Conditions

Keep `platformdirs` **blocked** at static screening. The blockers are:

1. No immutable verifier image or final filesystem/platform lock exists for
   this candidate.
2. No hash-locked offline build/test dependency bundle exists; the package's
   Hatch VCS build backend and test extras are unresolved for no-network
   verification.
3. The observed 1,097-node collection is not a final-image frozen total, and
   its effective behavior varies with OS, Python implementation, native
   Windows APIs, registry, environment, and skip policy.
4. The direct-import, monkeypatch, module-reload, and subprocess tests have
   no reviewed task-specific candidate adapter.
5. No private test bundle, allowlisted command plan, Oracle bundle, or control
   records are authorized in this lane.

To reopen, freeze a final `linux/amd64` or explicitly multi-platform verifier
environment, pin Hatch/build/test dependencies in a complete offline bundle,
materialize private tests without publishing their bytes, recollect the final
fixture with a structured report and explicit skip/xfail metric, and review a
child-side adapter that preserves the API/path and module-CLI behavior without
trusted pytest importing candidate code. Only then should Oracle and control
execution occur in a later lane.

## Static Validation

Completed without Docker, Harbor execution, full pytest execution, Oracle,
negative controls, or shared edits:

- Read `AGENTS.md`, the task-authoring, roadmap, metadata-core, operations,
  and Phase 2 verifier guidance.
- Cloned the public upstream repository, checked out the requested full SHA,
  verified the tree, submodule state, deterministic archive twice, MIT license
  blob/bytes/hash, package size, public API inventory, and test-definition
  inventory.
- Built a temporary wheel and collected the public source tests only to
  establish the 1,097-node static collection shape; no test body was run.
- Inspected `pyproject.toml`, `tox.toml`, CI matrix, platform selectors,
  filesystem/temporary-directory paths, environment handling, subprocess
  usage, and direct candidate imports/patching.
- Confirmed both available conversion-loop state files have no
  `platformdirs` image entry and confirmed the legacy/catalog task directory
  was absent before this audit.

No hidden test bytes, private fixtures, Oracle solution, Harbor Dockerfile,
verifier, shared dataset/index, conversion-loop state, legacy task, or other
task directory was created or changed.
