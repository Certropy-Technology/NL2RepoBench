# Rich candidate audit (evidence-first, blocked)

## Scope and provenance

- Candidate: `Textualize/rich`
- Upstream: <https://github.com/Textualize/rich>
- Revision resolution: detached full commit
  `9d8f9a372cc5916fd4781fec207ced7ddac2f08f`, resolved from `refs/heads/main`
  on 2026-08-23. The revision is immutable for this candidate; the branch name
  is provenance only and must not be used by a compiler.
- Commit date: `2026-06-23T10:10:17+07:00`.
- Upstream package version in `pyproject.toml`: `15.0.0`.
- Source archive evidence: `git archive --format=tar HEAD` SHA-256
  `f921363393f98d285226590333b41bf254dd311de46422d9a9d39f97deab25dd`.
- Submodules: none observed in the detached tree.

## License evidence

`LICENSE` is present at the repository root and is the standard MIT grant. Its
SHA-256 is `deed7c17a4318158190a3ea239cc879a5a50271cebb98ae7025f48fbe58dca15`.
The file grants use, modification, distribution, and sublicensing subject to
retaining the copyright and permission notice, and includes the standard
warranty/liability disclaimer. `pyproject.toml` independently declares
`license = "MIT"`. This is sufficient license evidence for candidate review;
no license approval or publication decision is implied.

## Source-only size

The source-only measurement was made on the detached tree with:

```text
git ls-files 'rich/**/*.py' 'rich/*.py' | xargs wc -l
```

Result: **100 Python source files, 38,515 physical lines**. Tests, docs,
examples, assets, lockfiles, and packaging files are excluded. This is a
physical-LOC inventory, not a complexity or generated-code estimate.

## Official test evidence

The detached tree contains **67 files under `tests/`**. A Python AST inventory
found **721 test-function nodes in 63 modules**. The official pytest command
specified by the source is:

```text
python -m pytest --continue-on-collection-errors -q tests
```

A real collect-only run was **not completed** in this lane because the checkout
image has no `pytest`, `pygments`, or `markdown-it-py` installed (only `python3`
and `uv` are available). Therefore 721 is a static inventory, not a frozen
pytest denominator. Parametrization, fixtures, unittest subtests, and
platform-specific skips may change the collected node count. The candidate
must remain `blocked` until a clean final environment records collection,
JUnit/JSON results, and a stable denominator.

Representative official coverage includes `test_console.py` (97 static test
functions), `test_text.py` (91), `test_pretty.py` (52), `test_progress.py` (35),
`test_segment.py` (31), `test_style.py` (27), `test_markup.py` (21),
`test_syntax.py` (25), `test_traceback.py` (22), plus tests for tables, panels,
layouts, markdown, JSON, live rendering, prompts, Unicode, and Windows
renderers. No hidden tests or test bytes are copied into this candidate.

## Runtime and offline dependency review

The source declares these core runtime roots:

- `pygments ^2.13.0`; lock evidence: `2.19.2`, wheel hash
  `sha256:86540386c03d588bb81d44bc3928634ff26449851e99741617ecb9037ee5ec0b`;
- `markdown-it-py >=2.2.0`; lock evidence: `3.0.0`, wheel hash
  `sha256:355216845c60bd96232cd8d8c40e8f9765cc86f46880e43a8fd22dc1a1a8cab1`;
- `mdurl >=0.1,<1.0`, required by markdown-it-py; lock evidence: `0.1.2`,
  wheel hash
  `sha256:84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8`.

The optional `jupyter` extra adds `ipywidgets` and its notebook ecosystem and
is outside the core candidate. The source build backend is `poetry-core>=1.0.0`
and is not hash-pinned by the source declaration. No verified wheelhouse,
source-distribution closure, or final image digest exists in this task-local
candidate. Offline install, import, and test execution are consequently
unproven and publication-blocking. Do not treat the checked-in `poetry.lock`
as an installed or content-addressed dependency bundle.

## Terminal/rendering risks

The project is terminal-facing and has behavior that can vary with environment:

- ANSI/color decisions, terminal width, `TERM`, `COLUMNS`, `LINES`, locale, and
  Unicode cell width;
- `Live`, `Progress`, `Spinner`, `Status`, cursor controls, refresh timing, and
  real TTY/file descriptors;
- platform-specific `test_win32_console.py` and `test_windows_renderer.py`;
- optional Jupyter integration in `test_jupyter.py`;
- traceback locals, logging timestamps, temporary files, and tests that touch
  clocks or random values.

The proposed deterministic policy is Linux CPython with `TERM=dumb`,
`COLUMNS=80`, `LINES=24`, `LC_ALL=C.UTF-8`, `PYTHONHASHSEED=0`, explicit
`Console(file=StringIO(), width=80, color_system=None, force_terminal=False)`
for plain-text checks, and explicit `force_terminal=True` only for ANSI checks.
Live/timing/TTY and Windows cases need a reviewed inclusion or exclusion policy;
no baseline is claimed here. The child-side JSONL/text boundary is recorded in
`candidate-boundary.json` so an eventual separate verifier can normalize text
without parsing terminal control streams.

## Determinism and contamination controls

The future verifier must run from an empty candidate workspace, keep official
tests outside that workspace, disable network, and reject candidate-written
result/reward files. Inputs crossing the adapter boundary are JSON-compatible
values only. Canonical JSON uses UTF-8, sorted keys, compact separators, and
`allow_nan=false`; captured text uses LF line endings and exactly one trailing
newline. Object addresses, timestamps, progress frames, and host-derived
terminal dimensions are not valid deterministic evidence.

## Status

`blocked`. This file records audit evidence and unresolved gates only. It does
not contain hidden tests, a Harbor task, an Oracle/reference solution, a
wheelhouse, a cache, or a publication approval.
