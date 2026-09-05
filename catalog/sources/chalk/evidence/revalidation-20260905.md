# Chalk instruction-migration revalidation blocker

Status: pending artifact recovery. This record does not change the lifecycle
status or replace the existing production evidence.

## Frozen source

- Task: `chalk`
- Expected catalog source digest: `sha256:e850f0d6f970f1fe3ebb381a6d8a9a3ab5850c8088308204c69953a986836ff9`
- Validation command: `uv run nl2repo task validate-source catalog/sources/chalk`
- Validation result: exit code `0`; source digest matched the expected digest;
  lifecycle remained `controls-passed`.
- Runtime policy: NoNetwork for Agent, candidate, verifier, Oracle, and every
  control. No compile or Harbor run was attempted because the required private
  inputs are unavailable.

## Missing private CAS objects

The following declared artifacts were checked offline under the local private
CAS root `.nl2repo/artifacts/private/sha256/<prefix>/<digest>`. Every expected
path was absent; no registry, source host, DNS, or external service was used.

| Artifact role | SHA-256 | Expected bytes |
| --- | --- | ---: |
| `tests` | `sha256:bd24983738489f856a9498c678ab89ae1c1c7ca3060e979cd62791630da0bca9` | 20480 |
| `dependencies` | `sha256:c3e8dba6d8511f5c2396941f70625aff6d02e64488e12afb30938a00e9a310a1` | 10240 |
| `oracle` | `sha256:d1f8c09e29ccc43c1ffbf316b54ab285c00dd7b66ef6ce0ca73278858cbd9b24` | 81920 |
| `commands` | `sha256:d7bd386cd8ffcabafa9fb1f4488b95dee2e4e6ac0ab1feeb428ad1e8b9c2ef13` | 10240 |

Offline confirmation command:

```bash
for h in \
  bd24983738489f856a9498c678ab89ae1c1c7ca3060e979cd62791630da0bca9 \
  c3e8dba6d8511f5c2396941f70625aff6d02e64488e12afb30938a00e9a310a1 \
  d1f8c09e29ccc43c1ffbf316b54ab285c00dd7b66ef6ce0ca73278858cbd9b24 \
  d7bd386cd8ffcabafa9fb1f4488b95dee2e4e6ac0ab1feeb428ad1e8b9c2ef13; do
  test ! -e ".nl2repo/artifacts/private/sha256/${h:0:2}/$h"
done
```

The exact four-digest check exited `0` after confirming all four paths were
absent.

The existing `production-evidence.json` is historical and was not modified.
Its nine referenced `.nl2repo/runs/...` grading/network paths are absent from
this checkout and are therefore not accepted as durable revalidation receipts.
No new Oracle, control, or offline receipt is claimed by this record.

## Remediation

Recover or reconstruct each artifact from the frozen authoring archive, verify
its exact byte size and SHA-256, and register it in the parent private CAS.
Then the parent must compile twice with `toolchain.node.lock.toml` and the
private CAS, inspect the compiled Oracle for network-fetch behavior, and run a
fresh NoNetwork Oracle plus empty, stub, forgery, and offline controls. Fresh
tracked compact receipts must be added before this task can be considered
revalidated. Do not authorize GitHub, npm, DNS, codeload, or any other runtime
network access as a substitute for the missing artifacts.
