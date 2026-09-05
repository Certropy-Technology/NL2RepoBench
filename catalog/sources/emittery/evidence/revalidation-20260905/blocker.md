# Emittery Revalidation Blocker

## Frozen input

- Task source digest (validated): `sha256:07a69bf3986acd42dd7248e81b4eb8ec3e1e27c81a341566be695c6b7a98f4ca`.
- Upstream revision: `147a8591045e00d0fe8088e2393e3eefea3aa4a5`.
- Upstream archive digest: `sha256:b650e76fc6fb9b6dc3ed45c5456b3226f1c05e3cf06e376f47d8b647a92ae138`.
- Frozen denominator: `44` Node `node:test` leaves.
- Runtime: Node `24.19.0`, npm `11.17.0`, `linux/amd64`, locked
  `toolchain.node.lock.toml`, Harbor `0.21.0`.

## Revalidation checks

- `uv run nl2repo task validate-source catalog/sources/emittery`: exit `0`;
  validated source digest is the expected digest above.
- `uv run nl2repo task lint-network --tasks-root catalog/sources`: exit `0`;
  `tasks_scanned=480`, `error_count=0`, and Emittery findings `0`.
- `uv run python scripts/validate_instruction_quality.py`: passed.
- JSON/TOML parsing and `bash -n` for all eight task-local controls: passed.
- Two production compiles using `toolchain.node.lock.toml`, the private
  artifact store, `--allow-private`, and no `--allow-incomplete`: both exited
  `0` and were byte-identical. The generated bundle contains `76` files and
  all eight declared controls. Its canonical manifest digest is
  `sha256:923a71994546ff17ae38ed05262620f19969c96a4da2c38d46d3eaae04f0aace`;
  the raw bundle manifest digest is
  `sha256:b16b5c32e37a55b659d45f4c0d7ae8cf5858006f7d4758df3558acfaccb0c0eb`.

## Blocker

The inspected Oracle artifact is
`sha256:0cc2efcd1424bd7adc8edc059018629236cd8e26c61119d34229686b86ea1b6c`.
It contains only `solve.sh`, whose pinned-source setup performs
`git fetch --depth=1 origin 147a8591045e00d0fe8088e2393e3eefea3aa4a5` from
`https://github.com/sindresorhus/emittery` at runtime. The required policy
denies all source-host, DNS, and external-service authorization to the Agent,
candidate, verifier, Oracle, and controls. Running this Oracle would therefore
violate the task contract; no Oracle or control receipt is claimed from this
revalidation.

The existing `production-evidence.json` still points to ignored historical
`.nl2repo` run paths and is intentionally unchanged. No current revalidation
receipt is durable enough to replace it.

## Remediation

Provide a private Oracle bundle whose `solve.sh` uses the frozen source bytes
from the authorized artifact store, or otherwise reconstruct the same pinned
source archive offline and verify its revision and archive digest. Then run the
single Harbor Oracle and the complete declared control matrix in a fresh bundle,
persist compact result, grading, collection, network, and failure-set summaries
under this directory, and bind every path to its SHA-256 before updating
production evidence. Do not authorize GitHub or any other external host at
runtime.
