# Instruction revalidation blocker

## Frozen input

- Task: `jsonschema-specifications`
- Queue/current catalog source digest:
  `sha256:27fc999a66326574f4b71031ada13310f75cbe5e7413585ac15448eb9da136e2`
- Upstream revision: `7aee138ac610b09b81aae1d338b8ed4601a01764`
- Frozen source archive SHA-256:
  `07328bc116206bfa14d749cb01ee5039f20e0ed28bdf017bc010101f23a11053`
- Instruction SHA-256:
  `af0696c4668c20bef362e340a4256fedd4354626a54800cd3ebcb7e0ee25daee`

`uv run nl2repo task validate-source
catalog/sources/jsonschema-specifications` confirmed the queue source digest
before any changes. The migrated instruction and task metadata were preserved.

## Artifact and compile checks

All three declared private artifacts exist in the parent private CAS and match
their declared size and SHA-256. The verifier bundle contains only `run.py`.
The Oracle bundle contains only `solve.sh`; it does not contain the frozen
source archive or another installable source payload.

Two authorized offline compiles with `toolchain.lock.toml`, `--allow-private`,
and no `--allow-incomplete` were byte-identical. Their bundle manifest SHA-256
is `16bb50d3a7155a2adffdfb568b06c10494298dbe5b72a91b53aa76617bb8d90e`
and their canonical manifest digest is
`sha256:3ba86ffa1f547414ad30c1f95bf0ec9fbaea763afae647d5edc4f6baad1f94e0`.

## NoNetwork blocker

The Oracle `solve.sh` performs `git clone` and `git fetch` against GitHub at
runtime. This revalidation wave forbids source-host, registry, DNS, or other
external authorization for Oracle and controls. The historical Oracle receipt
used a GitHub host override and therefore cannot be reused for the migrated
instruction manifest.

The bounded trusted-local recovery searched the current Oracle bundle,
checked-in generated runtime, task evidence, original authoring session,
task-specific supervisor compile, retained task runs, local Git objects, Docker
containers/volumes, and local package caches. No bytes matching the frozen
source archive were found. A cached installed wheel has a different provenance
and is not accepted as the frozen source archive.

No replacement bundle was constructed, no shared CAS binding was proposed,
and no Harbor Oracle or control was run. Doing so would require either network
access or source bytes that cannot currently be proven against the immutable
revision and archive digest.

## Required remediation

Recover the exact frozen `source.tar` with SHA-256
`07328bc116206bfa14d749cb01ee5039f20e0ed28bdf017bc010101f23a11053`
from a trusted local archive or handoff. Then construct an Oracle bundle that
contains that archive, verifies it before extraction, applies only the already
documented static-version packaging adaptation, and performs no network
operation. The parent must register the replacement artifact, update the
binding, recompile twice, and rerun Oracle plus the complete supported control
matrix.

Existing lifecycle and production evidence are intentionally unchanged. This
file records that the instruction-migration receipts remain pending; it does
not reclassify the historical task lifecycle.
