# parse5 instruction revalidation checkpoint

Checkpoint classification: `infrastructure-pending` (revalidation intentionally
stopped by the parent orchestrator before a fresh Harbor matrix; no Oracle or
control result is claimed).

## Frozen inputs verified before checkpoint

- Queue source digest: `sha256:594791bff79c840d24f1addf855387e95736132d8279aca9b67f9a32e135eeb3`.
- `validate-source` returned task `parse5`, version `2.0.0`, status
  `controls-passed`, with the same source digest.
- Existing trusted source archive: `3860480` bytes,
  `sha256:27a205e827436e03acc87f91d6b1d57e209bf14267c48ed443813ff734113437`.
- Existing submodule archives: `2355200` bytes,
  `sha256:58c8063ff052b8443e501d42530c23ec4321a9fac448bf3d6c38dbdae4229d`;
  `2273280` bytes,
  `sha256:e2d2c0a0c64d73b13a179dc448bf15443730d051b7f487a2fb954d588a9f1a63`.
- Declared private artifacts were found with exact declared sizes and SHA-256:
  dependency bundle `266240` bytes,
  `sha256:c7f8cec816b6dfc4eb30b391d8cde524c90c2284e83ed3cefe16f0d220914254`;
  commands bundle `10240` bytes,
  `sha256:ff24615a926405b2fa2d1bde2ccbb0816fc0a5d3364f4585da23888979c665cf`;
  test bundle `30720` bytes,
  `sha256:139c4f72fea52dc4823c0be2c99db5bca6df3001772b0c0d69ed27ec2eb79eed`;
  Oracle bundle `8878080` bytes,
  `sha256:2430c9964c8ce92efe00b0235d6b19c197de002d7a5103355b47766d52a97a69`.
- Two local compile commands completed with exit code 0. Their canonical bundle
  manifests were identical. No generated projection or source metadata was
  changed.

## Bounded attempt stopped

- Command: bounded local hash search over trusted integration, artifact, and
  historical worktree roots for exact parse5 payloads.
- Result: timed out after exactly `1200` seconds; no exit code or new artifact
  result was produced by the timed-out process.
- Persisted path normalization: the command and evidence intentionally use
  placeholders rather than machine-specific absolute paths.

## Parent next step

Keep `task.toml`, lifecycle, `production-evidence.json`, generated projection,
CAS, reports, and existing receipts unchanged. If revalidation is resumed,
use the already verified local payloads and run one fresh Harbor 0.21.0
NoNetwork Oracle followed by every supported control, then record fresh
source-local receipts before any parent-side projection or evidence promotion.
