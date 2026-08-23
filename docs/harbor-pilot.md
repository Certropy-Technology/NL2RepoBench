# NL2RepoBench Harbor Pilot (Historical)

> This document describes the historical Harbor pilot. The current Package
> campaign uses a one-run Oracle gate and skips model/Oracle reruns when an
> OSS run inventory already contains the task/model pair. See
> `docs/authoring-pipeline-ast.zh-CN.md` for the active workflow.

## What This Benchmark Measures

NL2RepoBench evaluates whether an agent can create a complete, installable
Python repository from a natural-language specification and an empty
`/workspace`. The score is a fixed-test pass rate produced by a separate
Harbor verifier.

## Source Of Truth And Layout

Human-edited task sources now live in the catalog:

```text
catalog/
├── datasets/nl2repobench-harbor-pilot/
│   └── dataset.toml
└── tasks/<task-id>/
    ├── task.toml             # catalog metadata and lifecycle
    ├── instruction.md        # public agent specification
    └── harbor/               # reviewed Harbor task assets
        ├── task.toml
        ├── environment/
        ├── solution/
        └── tests/
```

`examples/harbor/ministats/` is only the small infrastructure example.
Benchmark task assets do not belong under `examples/harbor/`. Run outputs are
stored under `.nl2repo/runs/` and are ignored by Git.

## Why Legacy Images Are Used

The original `test_files/<task-id>/` runner used frozen verifier images such as
`ghcr.io/multimodal-art-projection/nl2repobench/ftfy:1.0`. Those images contain
the historical test dependencies and test fixtures. The Harbor verifier uses
the same image as its base, saves the fixtures before Harbor mounts the agent
workspace, and injects the candidate source through a temporary `.pth` file.
This avoids downloading build dependencies during verification and preserves
the old environment contract.

The verifier writes structured `reward.json` and `grading.json`. A result is
valid only when the effective collection count matches the frozen denominator.
Skipped tests are recorded separately and do not silently inflate the score.

## Generate A Task

```bash
python scripts/convert_testfiles_to_harbor.py <task-id> \
  --upstream-url https://github.com/<org>/<repo> \
  --output catalog/tasks
python scripts/batch_convert.sh migration_tasks.txt catalog/tasks
python scripts/freeze_harbor_sources.py --root catalog/tasks --cache /tmp
python scripts/gen_harbor_from_legacy.py
```

The converter preserves the exact legacy test paths. It does not assume every
project has a `test/` directory; root test files, `src/` tests and nested
project paths are retained.

Validate catalog sources and the pilot dataset:

```bash
for task in aiofiles arguably autopep8 boto box bleach cerberus decouple deepdiff docopt-ng asteval emoji freezegun fastapi-users funcy fuzzywuzzy ftfy jsonlines parse pypinyin python-pathspec python-slugify schema six typing_extensions sortedcontainers more-Itertools math-verify mechanicalsoup paillier pdfplumber-stable sqlparse stamina tinydb tqdm rich-click; do
  uv run nl2repo task validate-source catalog/tasks/$task
done
uv run nl2repo dataset compile \
  catalog/datasets/nl2repobench-harbor-pilot/dataset.toml \
  --output build/catalog/nl2repobench-harbor-pilot
```

## Oracle Gate

Run a task directly through Harbor:

```bash
cd harbor-runner
uv run --frozen harbor run \
  -p ../catalog/tasks/ftfy/harbor \
  -a oracle \
  --jobs-dir ../.nl2repo/runs/oracle/ftfy
```

Only valid Oracle results are candidates for model evaluation. Environment,
dependency, test-asset and verifier failures must be fixed or marked blocked;
they must not be reported as model scores. For the current Package campaign,
require one valid run with collection equal to the frozen denominator and
reward >= 0.80; record the Oracle ceiling and failed tests when the baseline is
below 1.0. Cross-run stability is a separate historical experiment, not a
requirement for this campaign.

## OpenHands Model Run

Use the file-backed Harbor OpenHands SDK adapter for long specifications. It
avoids the host `ARG_MAX` failure caused by passing a large instruction in the
Docker command line and forwards the requested reasoning effort to the SDK.

```bash
TASK_ID=ftfy \
MODEL=openai/gpt-5.6-sol \
LLM_BASE_URL=https://z.open-api.ai/v1 \
LLM_API_KEY="$GPT_KEY" \
AGENT_TIMEOUT_SECONDS=18000 \
REASONING_EFFORT=max \
scripts/run_harbor_model.sh
```

The runner gives the agent phase five hours through Harbor's native timeout
multiplier. It does not wrap the complete trial with GNU `timeout`, so image
build/setup and the separate verifier keep their own task-defined budgets. The
run directory is printed by the script and remains outside the task source.

## Current Pilot State

Valid Oracle baselines currently include 37 active tasks in
`catalog/datasets/nl2repobench-harbor-pilot/dataset.toml`. Representative
fully gated baselines include:

- `aiofiles`: 1.0 after legacy-image verifier repair;
- `arguably`: 1.0;
- `cerberus`: 1.0 after accounting for one skipped test;
- `decouple`: 1.0;
- `parse`: 1.0;
- `six`: 1.0;
- `ftfy`: 1.0 after restoring its CLI entry point in the verifier environment;
- `jsonlines`: 1.0;
- `freezegun`: 1.0 after accounting for skipped tests;
- `tinydb`: 1.0.
- `boto`: 1.0 after freezing the effective 1009-test denominator;
- `deepdiff`: 1.0 (970 effective tests);
- `docopt-ng`: 1.0 (614 tests);
- `math-verify`: 1.0 (192 tests);
- `mechanicalsoup`: 1.0 (127 effective tests, three independent runs);
- `paillier`: 1.0 (234 tests);
- `pypinyin`: 1.0 (964 effective tests, two explicit skipped cases);
- `sqlparse`: 1.0 (462 effective tests, three independent runs);
- `typing_extensions`: 1.0 (535 effective tests);
- `unittest-parametrize`: 1.0 (26 tests).

`boltons`, `humanize`, and `tenacity` remain blocked because their selected
source revisions do not match the frozen legacy tests. `pytz` remains blocked
because its source build requires generated timezone data while the legacy
image stores the installed package as an egg. These are task/environment
blockers, not model failures.

## Reusable Rules

1. Freeze the upstream commit and use the corresponding legacy test image.
2. Preserve exact test paths and the original test selection.
3. Keep verifier dependencies and fixtures out of the agent image.
4. Validate Oracle before spending model budget.
5. Record `valid`, collection, skipped, failure reason and reward together.
6. Keep every run under `.nl2repo/runs/`, never inside `catalog/tasks`.
7. Treat API gateway errors, setup failures and timeouts as infrastructure or
   environment evidence, not model scores.
