# Blocked Task Remediation Log

This report records the remediation lane for existing `catalog/tasks/*/blocked.md`
entries. It is separate from the agent-run campaign: no GPT/Fable model run is
started by this lane, and a task is not promoted to a published dataset from a
worker smoke alone.

## Current Gates

The current Package campaign Oracle contract is one bounded generic compiled
run with `valid=true`, collection equal to the fixed denominator, and reward at
least `0.80`. Private tests, adapters, dependency closure and Oracle bytes stay
behind content-addressed artifact refs. Every remediation records the exact
revision, license, runtime/image, dependency attempts, verifier boundary,
failure classification and next gate in task-local provenance.

## Completed In This Lane

| Task | Revision | Frozen total | Generic Oracle | Controls | Remaining |
| --- | --- | ---: | --- | --- | --- |
| `pyperclip` | `f5326bfd7c5448b40051dd261a7304657977b838` | 10 | `10/10`, reward `1.0` | empty, stub, forgery, offline | timeout, review, pilot |
| `httpx` | `b5addb64f0161ff6bfe94c124ef76f6a1fba5254` | 24 | `24/24`, reward `1.0` | empty, stub, forgery, offline | timeout, review, pilot |
| `pytz` | `661bca921e29dc3eedd4430bac70816c9154c05e` | 15 | `15/15`, reward `1.0` | empty, stub, forgery, offline | timeout, review, pilot |
| `docstring-parser` | `8347d8fb347bd66e4bf5711d3df586357166944a` | 20 | `20/20`, reward `1.0` | empty, stub, forgery, offline | timeout, review, pilot |
| `icecream` | `816e6c6bbac50f16fda8f801c658fe5ebcfd50bc` | 20 | `20/20`, reward `1.0` | empty, stub, forgery, offline | timeout, review, pilot |
| `platformdirs` | `d3cf61ce5e729f2c35f830b69e14adb7b6970a00` | 20 | `20/20`, reward `1.0` | empty, stub, forgery, offline | timeout, review, pilot |
| `marshmallow` | `c7b559a1fa3aba57ca6dba0ab336841c5038a782` | 33 | `33/33`, reward `1.0` | empty, stub, forgery, offline | timeout, review, pilot |

Evidence paths and structured grading details are recorded in:

- `reports/python-remediation-oracle-gate-20260824.json`
- `reports/python-remediation-controls-20260824.json`
- each task's `provenance/oracle.md`

The `pytz` denominator is the documented stable API slice, not the historical
235-node legacy fixture. The `httpx` denominator is a deterministic offline
MockTransport slice, not live network/httpbin behavior. The `pyperclip`
denominator uses a fixture adapter and does not claim a desktop clipboard.

## Active Repairs

The next task-local workers are now free to select the next entries from
`catalog/tasks/*/blocked.md`. Each worker must leave `packaged` evidence if the generic image
or verifier gate is still open; missing artifacts alone are not a final
`blocked` decision. Integration into the shared catalog and reports is
serialized after worker validation.

## Not Yet Published

These repaired tasks are not in a formal published dataset or campaign
projection. Timeout controls, blind/spec traceability review, pilot runs,
dataset manifest generation and final archive validation remain separate gates.
