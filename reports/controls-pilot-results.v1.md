# Legacy Controls Pilot Results

**Status: diagnostic only.** This pilot did not pass the production control
gate. It was run from the canonical checkout after the legacy conversion
closeout, using Harbor `0.21.0` and fresh job directories under
`.nl2repo/runs/controls-pilot-20260822T/`.

## Oracle and Empty Runs

| Task | Oracle trials | Oracle result | Nop result | Interpretation |
| --- | ---: | --- | --- | --- |
| `markupsafe` | 3 | `valid=true`, `39/39`, reward `1.0` in all three | `valid=false`, `junit-missing`, reward `0` | Oracle stable; legacy empty control is verifier-invalid |
| `schedule-master` | 3 | `valid=true`, `81/81`, reward `1.0` in all three | `valid=false`, `collection-mismatch`, reward `0` | Oracle stable; legacy empty control is verifier-invalid |
| `unidecode` | 3 | 2 valid trials at `64/65`, reward `0.984615...`; 1 `VerifierTimeoutError` during verifier image build | `valid=false`, `collection-mismatch`, reward `0` | No stable 3x gate; infrastructure/verifier issue |

The unidecode timeout produced no grading artifact. None of these runs has the
production compiler's trusted `network.json` evidence; that absence is itself
an offline-verifier gap. Nop results are not converted into valid low model
scores: their `valid=false` reasons are preserved exactly.

## Why Stub/Forgery/Call-Hang Were Not Run

The selected legacy projections have no task-local `harbor/controls/*.sh` and
no compiler-generated `bundle.manifest.json`. Their verifier templates execute
pytest in-process, make fixture/report paths candidate-writable, and trust
candidate-produced JUnit. A control result from that boundary would not prove
forgery resistance, call timeout behavior, process cleanup, or fixed-denominator
grading. The static controls plan is recorded in
`reports/controls-pilot-plan.v1.md`.

## Acceptance Decision

No task is promoted to a production controls-passed state. Before retrying,
materialize private test/dependency/Oracle artifacts, migrate the selected
verifiers to the production candidate subprocess/integrity boundary, add
task-specific control scripts in an isolated staging copy, and require three
valid stable Oracle runs plus valid nop/stub/forgery/call-hang/offline evidence.
