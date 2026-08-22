# `pre-commit` Static Authoring Audit - Blocked

**Status: blocked.** This directory is an evidence record only. It is not a
publishable task, public instruction, Harbor bundle, verifier, Oracle bundle,
private test artifact, dependency wheelhouse, or publication approval. No
hidden test bytes, source checkout, generated manifest, legacy projection,
dataset index, shared file, or secret is included.

The candidate was explicitly marked conditional by
`reports/python-package-candidates.v1.json` because its behavior includes
subprocesses and tool downloads. The evidence below confirms that this is a
task-contract blocker, not a missing metadata field that can be filled by
guessing.

## Candidate Identity

- Upstream: `https://github.com/pre-commit/pre-commit`.
- Requested and resolved revision:
  `a9bba55a3f74068b53f4bd4d831d7e05e34eae6c`.
- Commit subject: `Merge pull request #3747 from pre-commit/pre-commit-ci-update-config`
  (`[pre-commit.ci] pre-commit autoupdate`).
- Commit author and committer date: `2026-08-17T19:37:06-04:00`.
- Parent commits:
  `9767b6c8211a6bf683875a0afcf2b390457a4b66` and
  `080ab7071f5dd4da5ecf10cb20e15c5be1c20db2`.
- Revision tree: `708e5ff82c2a410b01c28f1b465d6e213f9dc9f1`.
- Submodules: none.
- The detached source checkout was clean after inspection.

Three independent unprefixed archives from
`git archive --format=tar a9bba55a3f74068b53f4bd4d831d7e05e34eae6c` were
byte-identical:

- archive size: `1,024,000` bytes;
- archive SHA-256:
  `143b9d1dbc08a1edf79ffd947d2f7e847b89495569b6b9566f58a50b39bee6ec`.

The source lock is coherent and uses a full immutable commit. It does not,
by itself, establish an executable verifier image or a frozen benchmark test
bundle.

## License Evidence

`LICENSE` at the pinned revision is the MIT License:

- Git blob: `4a071fc533d4fd07dbe81e1e8f0f0998b17220be`;
- file size: `1,092` bytes;
- file SHA-256:
  `ea2ca27cba7cc35822d95a46d59bcd3cc88e196592e6390d1949a359ffc990e8`.

`setup.cfg:1-11` declares distribution name `pre_commit`, version `4.6.2`,
and license `MIT`. The license is acceptable for source and derived task
materials once the test and verifier provenance gates are satisfied.

## LOC And Package Shape

The pinned tree contains 203 tracked files and 67 Python files below
`pre_commit/`:

| Scope | Files | Physical lines | Nonblank, noncomment lines |
| --- | ---: | ---: | ---: |
| `pre_commit/` Python files, including resource templates | 67 | 7,163 | 5,582 |
| implementation Python files, excluding `resources/*.py` | 65 | 7,159 | 5,580 |
| `pre_commit/resources/*.py` templates | 2 | 4 | 2 |
| `tests/` Python files | 59 | 11,062 | 8,535 |

The implementation count is a package-size observation, not a publication
approval or a difficulty decision. The package also includes 21 language
adapter modules registered by `pre_commit/all_languages.py:4-49`:
`conda`, `coursier`, `dart`, `docker`, `docker_image`, `dotnet`, `fail`,
`golang`, `haskell`, `julia`, `lua`, `node`, `perl`, `pygrep`, `python`, `r`,
`ruby`, `rust`, `swift`, `unsupported`, and `unsupported_script`.

## Test Shape And Collection

The source tree has 59 Python test files and 682 AST-discovered test function
definitions. Static counts are not a frozen denominator because 49
`pytest.mark.parametrize` decorators expand those definitions and the suite
contains platform-dependent markers:

- full source collection: **823 nodes**;
- collection matching the repository's declared `tox.ini:4-10` test command
  (`--ignore=tests/languages`): **651 nodes**;
- `tests/` fixture resources: 31 files under `testing/resources/`;
- parameterization decorators: 49;
- skip/skipif decorators: 2;
- xfail decorators: 5.

The source-only collection command used a temporary audit dependency path
containing the declared test tooling and produced the following stable node
counts:

```text
PYTHONPATH=/tmp/precommit-audit-deps \
  /tmp/pluggy-authoring-env/bin/python -m pytest \
  --collect-only -q -p no:cacheprovider tests
823 tests collected

PYTHONPATH=/tmp/precommit-audit-deps \
  /tmp/pluggy-authoring-env/bin/python -m pytest \
  --collect-only -q -p no:cacheprovider tests --ignore=tests/languages
651 tests collected
```

Repeating each command returned the same node count. The complete collection
command initially failed before collection because `re_assert` was not
installed; the repository's `pytest-env` plugin was also absent from the first
environment. Installing those packages into `/tmp` allowed collection, but
that temporary environment is not a dependency lock or a verifier artifact.
No test bodies, Oracle runs, or benchmark controls were run.

Collection is environment-sensitive. The source has platform markers at:

- `tests/parse_shebang_test.py:97` and `tests/repository_test.py:132` for
  POSIX-only xfail behavior;
- `tests/xargs_test.py:185,234,245` for POSIX/Windows behavior;
- `tests/languages/swift_test.py:11`, `tests/languages/lua_test.py:11`, and
  `tests/main_test.py:62` for executable/platform-dependent skips.

The audit host had Git `2.55.0`, CPython `3.14.6`, Node `22.23.1`, npm
`10.9.8`, Docker `29.7.2`, Cargo and Go available. `rustup`, Ruby, R,
Julia, Lua, Cabal, and Swift were not available. This inventory is not a
portable environment lock and must not be used to infer an effective test
denominator.

## Dependency And Offline Evidence

The source uses legacy `setup.py`/`setup.cfg`; there is no `pyproject.toml`,
`uv.lock`, `poetry.lock`, `Pipfile.lock`, `requirements.lock`, or
`requirements-dev.lock` in the pinned tree.

Runtime requirements in `setup.cfg:18-26` are all range-based or unpinned at
the upper bound:

```text
cfgv>=2.0.0
identify>=1.0.0
nodeenv>=0.11.1
pyyaml>=5.1
virtualenv>=20.10.0
```

Development/test requirements in `requirements-dev.txt:1-6` are also not
hash-locked:

```text
covdefaults>=2.2
coverage
distlib
pytest
pytest-env
re-assert
tox
```

The package contains no task-authorized wheelhouse, base-image digest,
system-package lock, or offline install transcript. `tox.ini:4-15` runs the
test suite through tox and separately runs `pre-commit` itself; its test
environment is not a frozen verifier closure. `tox.ini:20-28` sets
`VIRTUALENV_NO_DOWNLOAD=1`, but that setting does not supply the missing
packages or pin their hashes.

More importantly, pre-commit's normal behavior installs hook environments
after cloning a hook repository. A no-network verifier cannot claim the
normal behavior without a reviewed, content-addressed fixture closure for
every exercised hook language and external executable. Examples in the
pinned source include:

- `pre_commit/store.py:177-210`: `git fetch`, checkout, and recursive
  submodule update for hook repositories;
- `pre_commit/commands/autoupdate.py:38-72`: remote initialization and
  `git fetch origin HEAD --filter=blob:none --tags`;
- `pre_commit/languages/python.py:214-228`: `virtualenv` creation followed
  by `pip install .` and additional dependencies;
- `pre_commit/languages/node.py:76-106`: `nodeenv --prebuilt` and global
  `npm install`, including `git+file://` hook packages;
- `pre_commit/languages/rust.py:83-158`: rustup bootstrap/toolchain and
  `cargo install` paths;
- `pre_commit/languages/r.py:190-253`: R/renv installation paths;
- `pre_commit/languages/docker.py:78-106,159-181`: Docker build/run and
  optional image pull paths;
- `pre_commit/languages/coursier.py`, `dart.py`, `golang.py`, `haskell.py`,
  `julia.py`, `lua.py`, `perl.py`, `ruby.py`, and `swift.py`: additional
  system language managers and package installation paths.

The unresolved closure is a **blocker**, not an optional optimization. A
future task must either freeze the complete offline closure and allowlisted
toolchain or explicitly define a narrower behavior contract that excludes
the download/install language surface.

## Subprocess, Git, Filesystem, And Environment Risks

Static source measurements found:

- 112 implementation subprocess/cmd-output call sites under `pre_commit/`;
- 63 implementation Git command/reference call sites under `pre_commit/`;
- 22 of 59 test files using subprocess or command-output helpers;
- 10 of 59 test files using Git helpers directly;
- 45 of 59 test files using filesystem, temporary-directory, file, or
  environment operations.

The behavior is stateful and mutating:

- `pre_commit/git.py:51-207` reads Git root/index/merge state, staged and
  changed files, refs, submodules, and repository configuration through
  child Git commands.
- `pre_commit/commands/run.py:253-322,338-445` chooses files from Git state,
  may stash/restore changes, installs hook environments, runs hooks, and may
  invoke `git diff`.
- `pre_commit/repository.py:65-106,171-229` creates cached environments,
  writes install state, removes/rebuilds environments, and runs language
  installers.
- `pre_commit/commands/install_uninstall.py:64-141,149-167` writes
  `.git/hooks/<hook-type>`, moves an existing hook to `.legacy`, changes
  executable mode, removes hooks, and restores legacy hooks.
- `pre_commit/commands/try_repo.py:21-77` can clone a local repository,
  create a shadow branch/commit, materialize a temporary config, and invoke
  the normal run path.
- `pre_commit/staged_files_only.py:37-105` writes patch files and uses Git
  checkout to temporarily restore the worktree.
- `pre_commit/store.py:32-35,89-175` selects a user/XDG cache, creates a
  SQLite state database and per-repository temporary directories, and keeps
  cached paths across calls.

The upstream tests exercise these side effects rather than merely parsing
pure values. `tests/repository_test.py`, `tests/store_test.py`,
`tests/staged_files_only_test.py`, `tests/git_test.py`, and the command tests
construct temporary Git repositories, commit files, inspect hook files,
patch environment variables, and assert process output. The language tests
also probe the presence and health of external executables.

The project-level environment contract in `tox.ini:20-28` fixes Git identity,
allows the `file` Git protocol, disables virtualenv downloads, and disables
pre-commit concurrency. Those settings are test conveniences, not a complete
security boundary. The implementation reads ambient `HOME`, XDG cache paths,
`PATH`, Git variables, language-manager variables, terminal state, and other
environment values. A verifier must explicitly sanitize and record them.

## API Scope And Candidate Boundary

There is no `__all__` declaration in the package. An AST inventory finds 200
non-underscore top-level functions/classes across implementation modules, but
that is not a stable public API: it includes command helpers, Git/store
objects, language adapters, and test-facing internals. The observable entry
surfaces include:

- console entry point `pre-commit = pre_commit.main:main` from
  `setup.cfg:33-35`;
- `python -m pre_commit` via `pre_commit/__main__.py:1-7`;
- 14 operational CLI commands in `pre_commit/main.py:220-347`:
  `autoupdate`, `clean`, `gc`, `hazmat`, `init-templatedir`, `install`,
  `install-hooks`, `migrate-config`, `run`, `sample-config`, `try-repo`,
  `uninstall`, `validate-config`, and `validate-manifest`;
- a `help` command and internal `hook-impl` entry at
  `pre_commit/main.py:350-365`;
- configuration/manifest validation in `pre_commit/clientlib.py`;
- Git, cache/store, hook, staged-files, subprocess, YAML, and 21 language
  adapter modules.

The existing generic candidate boundary is insufficient for the complete
upstream behavior. Its `candidate_client.call` contract accepts JSON-shaped
arguments, imports the candidate only in a fresh unprivileged child, and
cannot transport live `Store`, `Prefix`, `Hook`, `argparse.Namespace`, file,
Git repository, subprocess, or language-manager objects. Its
`run_console` operation can launch the `pre-commit` entry point, but a fresh
process per operation cannot preserve the cache database, worktree state,
hook installation, environment creation, or repeated invocation state that
the tests assert.

Directly running the upstream tests in trusted pytest is also disallowed by
the separate-verifier policy: the tests import `pre_commit.*` directly,
monkeypatch candidate internals, create Git repositories, and inspect local
filesystem/process effects. No reviewed pre-commit-specific child adapter,
scenario DSL, persistent-session contract, command allowlist, or normalized
side-effect response schema exists in this task lane.

Narrowing the task to pure config/manifest parsing or a fixed local-hook
scenario could be feasible, but that would be a new task contract and must
not be presented as full pre-commit API or upstream-test parity.

## Blockers And Reopen Conditions

Keep `pre-commit` **blocked**. The blockers are:

1. No immutable verifier image, base-image digest, or final environment lock
   exists for this candidate.
2. Runtime and development dependencies are unpinned; no hash-locked offline
   wheelhouse or complete build/test closure exists.
3. The observed 823/651 collection counts are source observations, not a
   final-image frozen collection with structured report, skip policy, and
   fixed denominator.
4. The complete behavior depends on Git, subprocesses, mutable filesystem and
   environment state, external language runtimes, and possible network/tool
   downloads.
5. The generic JSON subprocess boundary cannot represent the in-process and
   persistent state exercised by the tests; no task-specific adapter is
   approved.
6. No private test bundle, allowlisted command plan, Oracle bundle, verifier,
   or empty/stub/forgery/offline control record exists.

Before reopening, an owner must approve a task version and one of these
scopes:

- **Full behavior:** freeze a complete multi-tool offline image/closure,
  isolate and allowlist Git/subprocess/filesystem operations, and provide a
  persistent child adapter that preserves the tested state transitions; or
- **Narrow behavior:** publish a new explicit contract for a deterministic
  local-only subset such as config/manifest validation, with a new adapted
  private suite and denominator. It must not claim upstream parity.

For either scope, the next stages must freeze the final image and dependency
artifacts, collect private tests in that image, generate structured JUnit or
JSON results, and run three valid Oracle trials followed by empty, stub,
forgery, and offline controls. Do not create a `task.toml`, instruction,
Harbor tree, or private artifact reference until those gates are authorized.

## Static Validation Record

Commands and outcomes:

- `git clone --filter=blob:none --no-checkout --depth=1
  https://github.com/pre-commit/pre-commit.git` followed by detached checkout
  at the full SHA: **passed**; clean source checkout.
- `git archive --format=tar HEAD` run three times: **passed**; all archives
  identical at 1,024,000 bytes and SHA-256
  `143b9d1dbc08a1edf79ffd947d2f7e847b89495569b6b9566f58a50b39bee6ec`.
- `git show HEAD:LICENSE | sha256sum`, `git cat-file`, and `git ls-tree`:
  **passed**; MIT evidence and hashes above.
- Shell line inventory and Python AST inventory: **passed**; LOC, file,
  public-definition, test-definition, marker, and resource counts above.
- Initial collection without temporary test extras: **failed as expected**;
  four collection imports reported missing `re_assert` and the first
  environment lacked `pytest-env`.
- Temporary audit dependency installation and complete source collection:
  **passed**; 823 nodes collected, then 651 with `--ignore=tests/languages`.
  The temporary packages were not copied into this repository.
- Repeated collection runs: **passed for count stability**; each repeated
  command returned the same node count. Wall-clock duration text differed,
  so full console-output hashes are not treated as test identity.
- Docker/Harbor execution, full test execution, Oracle, negative controls,
  offline verifier, and candidate adapter validation: **not run**; required
  assets and gates are absent.

No tests were added or modified. No task descriptor, public instruction,
Harbor asset, hidden/private test, dependency cache, Oracle, Docker artifact,
shared dataset/index, legacy task, conversion-loop state, or secret was
created or changed.
