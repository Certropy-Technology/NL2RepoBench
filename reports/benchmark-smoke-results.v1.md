# Fresh Benchmark Smoke Results

**Scope:** one-task smoke cells only. These results are separate from the
interrupted `new6` campaign and are not a complete model comparison.

## GPT-5.6

Task `markupsafe` was run with a fresh root:

```text
.nl2repo/runs/smoke-gpt-final-20260822T050106Z/
```

Acceptance passed:

- Harbor `0.21.0`, one completed trial, zero Harbor errors;
- `grading.valid=true`;
- fixed denominator `39`, collected `80`, skipped `41`, effective total `39`;
- `39` passed, reward `1.0`;
- full trial-root credential scan found no matching API-key patterns;
- local OSS manifest contained 65 files and 81 objects including directories;
- remote prefix collision check found no existing `gpt56-markupsafe` objects;
- the accepted 65-file smoke artifact was uploaded without overwrite.

One earlier retry root,
`.nl2repo/runs/smoke-gpt-retry-20260822T041623Z/`, produced the same valid
`39/39` grading but exposed a launcher path bug: an absolute `RUN_ROOT` was
prefixed a second time after `cd harbor-runner`. It is retained as a harness
diagnostic and is not counted or uploaded. The launcher was fixed and the
absolute-path regression test was added before the accepted run.

## Fable5

Task `markupsafe` was run once at:

```text
.nl2repo/runs/smoke-fable-final-20260822T052905Z/
```

The trial is terminal but invalid and is not a model score:

- `NonZeroAgentExitCodeError` from the OpenHands agent;
- upstream relay returned an HTML “New API” page instead of an LLM response;
- no trajectory was produced;
- verifier grading was `valid=false`, `junit-missing`, reward `0`;
- no credential pattern was found in the full trial root.

The Fable lane is stopped pending provider/endpoint repair or an explicitly
versioned provider change. No retry was launched after this failure.

## GPT-5.6 Tablib Attempt

The next fresh GPT root was started at:

```text
.nl2repo/runs/smoke-gpt-tablib-20260822T072530Z/
```

It is an infrastructure failure, not a model score. Harbor built the tablib
image, then Docker failed to create the default network with:
`all predefined address pools have been fully subnetted`. The trial has
`n_errored_trials=1`, no verifier grading, and no trajectory. Stop the model
lane until Docker network-pool capacity is repaired; do not retry this root.

## Next Gate

The next GPT task must use a new root and the same per-task acceptance gate:
terminal Harbor result, `valid=true`, fixed denominator and reward consistency,
zero infrastructure exceptions, and a full artifact secret scan. Do not append
to any existing root and do not use `--overwrite` for OSS upload.

## Later Infrastructure Attempts

- A GPT `tablib` attempt at
  `.nl2repo/runs/smoke-gpt-tablib-20260822T072530Z/` failed before the agent
  phase because Docker could not create its default network:
  `all predefined address pools have been fully subnetted`.
- A Fable attempt using the configured Pi provider
  `z-open-api-opus5-fable5-anthropic` at
  `.nl2repo/runs/smoke-fable-pi-20260822T075614Z/` failed before the agent phase
  because Docker Hub returned HTTP `429` while resolving the pinned Python base
  image. No model response or score was produced.

Both are infrastructure artifacts and are excluded from model scoring. The
stale Harbor containers/networks from the local smoke runs were scoped and
removed; unrelated Frontier compose workloads were left untouched.
