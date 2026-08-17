# Legacy Metadata Gap Baseline v1

Generated from the 104 task directories under `test_files/` with:

```bash
uv run nl2repo task import-legacy \
  --legacy-root test_files \
  --output /tmp/nl2repobench-authoring \
  --artifact-root /tmp/nl2repobench-artifacts \
  --state-db /tmp/nl2repobench-state.db \
  --difficulty-file test_files/task_difficulty.csv \
  --report reports/legacy-metadata-gap.v1.json
```

## Summary

| Field | Tasks missing | Release implication |
| --- | ---: | --- |
| `source_lock.upstream_url` | 104 | Cannot verify source provenance |
| `source_lock.revision` | 104 | Source is not immutable |
| `source_lock.license_spdx` | 104 | Distribution rights are unknown |
| `environment_lock.python_version` | 104 | Runtime cannot be reproduced |
| `environment_lock.base_image_digest` | 104 | Base environment is mutable/unknown |
| `dependency_bundle.artifact` | 104 | Offline dependency closure is absent |
| `tests.test_bundle` | 104 | Test bundle provenance is absent |
| frozen collection evidence | 104 | Existing denominator is only a legacy file |
| `harbor` | 104 | Harbor execution profile has not been authored |
| `oracle_bundle` | 104 | No immutable reference implementation bundle |

No legacy task currently satisfies the new publication metadata gate. This is
expected: the importer records what the old format actually contains and does
not infer missing values from instructions or image names.

The machine-readable per-task record is
[`legacy-metadata-gap.v1.json`](legacy-metadata-gap.v1.json). It contains task
IDs, missing field paths, and migration warnings only. Private command/test
bytes remain in the temporary content-addressed artifact store and are not
committed.

## Migration order

1. Recover upstream URL, immutable commit, license evidence, and source hash.
2. Rebuild the ground-truth environment and record Python/OS/image digest.
3. Freeze an offline dependency bundle and the complete hidden test bundle.
4. Collect tests in the locked environment and replace `legacy-file` evidence.
5. Compile the Human-facing `catalog/tasks/<task-id>/task.toml` source.
6. Run Oracle, negative controls, blind review, and traceability review.
7. Publish only after `TaskLifecycleRecord` can transition to `published`.
