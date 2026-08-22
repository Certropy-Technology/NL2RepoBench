# Authoring Wave Handoff: `platformdirs`

## Decision

`platformdirs` is **blocked after static screening**. The requested upstream
revision is identifiable and the public source is a coherent pure-Python
filesystem/platform library, but this lane has no immutable verifier image,
final environment lock, offline dependency closure, authorized private test
bundle, or reviewed separate candidate adapter. No Oracle, control, Docker, or
full test execution was performed.

The only task-local catalog artifact is
[`catalog/tasks/platformdirs/blocked.md`](/tmp/pi-worktree-06b38ff8-113c-4ea-9910-0d8a7ea85ccb-0/catalog/tasks/platformdirs/blocked.md).
No `task.toml`, `instruction.md`, Harbor bundle, verifier, hidden test bytes,
Oracle bytes, or shared index was created.

## Source And License

- Repository: `https://github.com/tox-dev/platformdirs`
- Requested revision: `d3cf61ce5e729f2c35f830b69e14adb7b6970a00`
- Revision tree: `9a2e1a4f3e8bfcda7896d35c4e156e3d90090dbd`
- Commit: `[pre-commit.ci] pre-commit autoupdate (#525)`
- Commit date: `2026-08-17T10:42:19-07:00`
- Submodules: none
- Deterministic unprefixed `git archive --format=tar` size: `358400` bytes
- Deterministic archive SHA-256 (two runs):
  `01837750779cd8f90d271f9b6184cf7d8d78fac37c72ce40ac97ccfb4064d572`
- License: MIT, `LICENSE` Git blob
  `f35fed9191b1142ddaada8a96de4a9461c5d796c`
- `LICENSE` size: `1,089` bytes
- `LICENSE` SHA-256:
  `29e0fd62e929850e86eb28c3fdccf0cefdf4fa94879011cffb3d0d4bed6d4db6`

The source inventory is consistent with the discovery report: 2,305
nonblank/non-comment implementation lines across eight Python modules, 66
static top-level public API symbols, eight test modules, and 105 ordinary test
definitions.

## Filesystem Matrix

Import-time selection is `Windows` on `win32`, `MacOS` on `darwin`, and `Unix`
on other platforms. Android selection additionally checks
`ANDROID_DATA=/data`, `ANDROID_ROOT=/system`, absence of `SHELL`/`PREFIX`, and
an Android application directory resolver (`jnius`, Python-for-Android, or a
recognized `sys.path` layout).

The upstream CI declares 23 test jobs: `ubuntu-24.04`, `windows-2025`, and
`macos-15` across CPython 3.10 through 3.15, free-threaded 3.15t, and
PyPy 3.11 on Unix (Windows/PyPy is excluded). The test suite covers:

- Unix/XDG defaults and overrides, `user-dirs.dirs`, HOME/USERPROFILE,
  path-separator behavior, root/non-root routing, runtime-directory
  writability, BSD fallbacks, and `tmp_path` directory creation;
- macOS Library defaults, XDG overrides, Homebrew prefixes, multipath results,
  and directory creation;
- Windows environment fallback, ctypes known folders, registry access,
  `PUBLIC`/`USERPROFILE`, and `WIN_PD_OVERRIDE_*` paths;
- Android resolver behavior through mocked Java/Python-for-Android modules and
  Android path layouts;
- a child-process `python -m platformdirs` output check.

The macOS and Android classes are mostly exercised through direct construction
and mocks on the host. Real Windows ctypes and registry groups are gated to
Windows. A Linux-only observation cannot establish this matrix's behavior.

## Collection

A temporary wheel was built because the source uses Hatch VCS to generate
`platformdirs.version`; direct `PYTHONPATH=src` collection otherwise fails
with `ModuleNotFoundError: platformdirs.version`. With the temporary wheel
installed into an isolated `/tmp` environment containing CPython `3.13.14`,
`pytest==9.0.2`, `pytest-mock==3.15.1`, and `appdirs==1.4.4`, the following
source-only collection completed without errors:

```text
PYTHONDONTWRITEBYTECODE=1 /tmp/platformdirs-venv/bin/python -m pytest \
  --collect-only -q -p no:cacheprovider /tmp/platformdirs-source/tests
```

It collected **1,097 parametrized nodes**:

| Test module | Nodes |
| --- | ---: |
| `test_android.py` | 143 |
| `test_api.py` | 272 |
| `test_comp_with_appdirs.py` | 111 |
| `test_macos.py` | 188 |
| `test_main.py` | 2 |
| `test_unix.py` | 212 |
| `test_windows.py` | 169 |
| **Total** | **1,097** |

This is not a frozen denominator. There is no final verifier fixture,
structured final-image collection/JUnit record, explicit skip/xfail metric, or
allowlisted command plan. The discovery value `105` is the static definition
count and must not be used as the score denominator.

## Dependency And Image Lock

The package has no runtime dependencies, but its dynamic VCS build requires:

```text
hatch-vcs>=0.5
hatchling>=1.29
```

The test group requires `appdirs==1.4.4`, `covdefaults>=2.3`,
`diff-cover>=10.2`, `pytest>=9.0.2`, `pytest-cov>=7`, and
`pytest-mock>=3.15.1`. There is no upstream `uv.lock`, hash-bearing
requirements file, complete wheelhouse, or system package lock. `tox.toml`
adds an unpinned `tox>=4.47` runner requirement; CI installs latest `tox`,
`uv`, and managed interpreters.

Neither available conversion-loop state file contains a `platformdirs` entry:

```text
/root/NL2RepoBench/.nl2repo/conversion-loop/state.json
/data/NL2RepoBench-current/.nl2repo/conversion-loop/state.json
```

Therefore no image reference, manifest/config digest, platform, test-layer
inventory, network mode, build history, or final installed package inventory
is available. The dependency and environment locks remain `unknown`; the
unrelated `harbor-runner/uv.lock` entry for platformdirs is not evidence for
this candidate.

## Candidate Boundary

The upstream tests directly import the candidate package and its platform
submodules in the trusted pytest process. They inspect class/function identity,
signatures, properties, `Path` results, metadata, and the
`AppDirs is PlatformDirs` alias. They patch candidate internals and process
state, including `os.pathsep`, `sys.platform`, `sys.prefix`, `sys.modules`,
`builtins.__import__`, `ctypes`, environment variables, UID calls, filesystem
access, and Windows resolvers. They reload modules, inspect mock call counts,
and simulate missing `ctypes`, `jnius`, and Android modules. One test launches
the module as a subprocess.

The generic JSON child boundary cannot transparently preserve in-process
object identity, monkeypatch scope, module-cache behavior, live `Path`
objects, or native API mocks. A task-specific child adapter could expose
normalized directory/path observations and the module CLI, but no such adapter
or behavior mapping exists. Copying these public tests into a trusted verifier
would violate the separate-verifier policy; copying private bytes is also
forbidden.

## Blockers And Reopen Conditions

1. No immutable verifier image or final filesystem/platform lock.
2. No hash-locked offline build/test dependency bundle for the Hatch VCS build
   and test extras.
3. No final-image collection record or frozen effective denominator.
4. No reviewed child-side adapter for direct imports, patches, reloads,
   platform emulation, and the module subprocess contract.
5. No authorized private tests, command plan, Oracle bundle, or controls.

Reopen only after freezing the verifier environment, materializing a complete
offline dependency bundle and private test artifact, recollecting with a
structured report and explicit metric semantics, and reviewing an adapter
that keeps candidate imports out of trusted pytest. Oracle and controls belong
to a later execution lane.

## Commands And Results

- `git clone --filter=blob:none --no-checkout https://github.com/tox-dev/platformdirs /tmp/platformdirs-source` - passed.
- `git checkout --detach d3cf61ce5e729f2c35f830b69e14adb7b6970a00` - passed.
- `git archive --format=tar ... | sha256sum` twice - passed; identical digest.
- License blob/size/SHA and tree/submodule inspection - passed.
- Static AST inventory for implementation/API/test definitions - passed.
- `uv build --wheel --out-dir /tmp/platformdirs-dist /tmp/platformdirs-build` - passed; temporary wheel only.
- Temporary `uv` venv/dependency installation for source collection - passed.
- Direct source collection before VCS version generation - failed as expected with missing `platformdirs.version`; this was resolved only in the temporary wheel environment.
- `pytest --collect-only` with `-p no:cacheprovider` - passed; 1,097 nodes, zero collection errors.
- `git diff --check -- catalog/tasks/platformdirs/blocked.md` - passed.
- Docker, Harbor execution, full pytest, Oracle, empty/stub/forgery/offline controls - not run by lane policy.

No hidden bytes, private fixture, Oracle solution, Dockerfile, verifier, shared
index, conversion-loop state, legacy task, or unrelated task directory was
created or changed.

## Acceptance Evidence

Changed files are the task-local blocked audit plus this required report. No
test files were added or updated. The current isolated worktree has no staged
files.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Static screening was implemented only as a task-local blocked audit for catalog/tasks/platformdirs; no shared code, hidden bytes, Docker, Oracle, or scope-expanding Harbor assets were added."
    }
  ],
  "changedFiles": [
    "catalog/tasks/platformdirs/blocked.md",
    "/root/NL2RepoBench/reports/authoring-wave-platformdirs.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git clone --filter=blob:none --no-checkout https://github.com/tox-dev/platformdirs /tmp/platformdirs-source",
      "result": "passed",
      "summary": "Public source clone completed."
    },
    {
      "command": "git -C /tmp/platformdirs-source checkout --detach d3cf61ce5e729f2c35f830b69e14adb7b6970a00",
      "result": "passed",
      "summary": "Detached checkout resolved at the requested full revision."
    },
    {
      "command": "git archive --format=tar d3cf61ce5e729f2c35f830b69e14adb7b6970a00 | sha256sum",
      "result": "passed",
      "summary": "Two runs produced archive SHA-256 01837750779cd8f90d271f9b6184cf7d8d78fac37c72ce40ac97ccfb4064d572."
    },
    {
      "command": "git show d3cf61ce5e729f2c35f830b69e14adb7b6970a00:LICENSE | sha256sum",
      "result": "passed",
      "summary": "MIT license bytes were hashed and matched the recorded provenance."
    },
    {
      "command": "uv build --wheel --out-dir /tmp/platformdirs-dist /tmp/platformdirs-build",
      "result": "passed",
      "summary": "Temporary VCS-versioned wheel built successfully; not retained as a task artifact."
    },
    {
      "command": "PYTHONDONTWRITEBYTECODE=1 /tmp/platformdirs-venv/bin/python -m pytest --collect-only -q -p no:cacheprovider /tmp/platformdirs-source/tests",
      "result": "passed",
      "summary": "Source-only collection completed with 1,097 nodes and no collection errors."
    },
    {
      "command": "git diff --check -- catalog/tasks/platformdirs/blocked.md",
      "result": "passed",
      "summary": "Task-local audit has no whitespace errors."
    },
    {
      "command": "git diff --cached --name-only",
      "result": "passed",
      "summary": "No staged files in the isolated worktree."
    }
  ],
  "validationOutput": [
    "Requested commit, tree, deterministic archive, MIT license hash, platform matrix, source API/test inventory, and source-only collection shape are recorded.",
    "No platformdirs immutable verifier image entry exists in either available conversion-loop state file.",
    "The candidate remains blocked because environment/dependency locks, frozen final collection, private artifacts, and a separate candidate adapter are absent."
  ],
  "residualRisks": [
    "The 1,097-node count is not a final-image frozen denominator and may vary with OS, interpreter, plugins, skip policy, and generated VCS version metadata.",
    "Windows native ctypes/registry behavior and Android runtime behavior were not executed in this Linux static lane.",
    "The Hatch build backend and test dependency closure are not hash-locked or offline-resolvable."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added one task-local static blocked audit; wrote the required absolute handoff report; no production task or verifier assets were created.",
  "reviewFindings": [
    "blocker: no immutable platformdirs verifier image or final environment lock is available",
    "blocker: no complete offline hash-locked build/test dependency bundle is available",
    "blocker: direct-import and patch-heavy tests have no reviewed separate candidate adapter",
    "blocker: source collection is not a frozen final verifier denominator"
  ],
  "manualNotes": "No Docker, Harbor, full pytest, Oracle, or controls were run. The task-local handoff is intentionally blocked and contains no hidden test bytes."
}
```
