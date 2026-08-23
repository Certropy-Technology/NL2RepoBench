# Run Artifact Storage (Alibaba Cloud OSS)

Task definitions and run artifacts are archived in the shared OSS bucket. The
repository keeps task sources under `catalog/tasks/`; `.nl2repo/runs/` is
gitignored and lives only in OSS.

## Bucket

| Field | Value |
| --- | --- |
| Bucket | `dingshang-sg` |
| Region | `ap-southeast-1` (Singapore) |
| Endpoint | `oss-ap-southeast-1.aliyuncs.com` |
| Public domain | `dingshang-sg.oss-ap-southeast-1.aliyuncs.com` |
| Root prefix | `nl2repobench/` |

Credentials come from `OSS_ACCESS_KEY_ID` and `OSS_ACCESS_KEY_SECRET`. They are
never committed and never written into uploaded files.

## Layout

The layout mirrors `itbench-live/` in the same bucket, so one browsing habit
works across projects. There is no date or campaign level; trial directory
names carry the run identity.

```text
nl2repobench/
├── README.md
├── harbor-tasks/<task>/...                    task definitions
└── runs/
    ├── <model>/<task>/<trial>/...             model runs
    ├── oracle/<task>/<trial>/...              Oracle gate evidence
    ├── unknown/<task>/<trial>/...             early runs, model not recoverable
    └── _queue-logs/<file>                     batch queue logs
```

The trial segment is `<run-root>--<job-dir>`, which keeps repeated runs of the
same task distinguishable while staying stable across re-uploads.

Model scores and Oracle evidence are deliberately separated: an Oracle result
validates the environment and is never a model score. `unknown/` is preserved
rather than guessed so nothing is misattributed to a model.

## Upload

```bash
export OSS_ACCESS_KEY_ID=...
export OSS_ACCESS_KEY_SECRET=...

# Inspect planned object keys without transferring anything
python scripts/upload_runs_to_oss.py --dry-run \
  --manifest reports/oss-objects.json \
  --remote-manifest-key nl2repobench/_manifests/oss-objects.json

# Upload task definitions + runs + README and checksum metadata
python scripts/upload_runs_to_oss.py --workers 16 --readme docs/oss-readme.md \
  --manifest reports/oss-objects.json \
  --remote-manifest-key nl2repobench/_manifests/oss-objects.json

# Only runs, or only task definitions
python scripts/upload_runs_to_oss.py --skip-tasks
python scripts/upload_runs_to_oss.py --skip-runs
```

The script needs the `oss2` package. It is safe to re-run only when an existing
object has the same size and SHA-256 metadata; a same-key collision fails closed.
Use `--overwrite` only for an explicitly approved archive migration.
The uploader scans the exact files selected for transfer before contacting OSS;
secret-shaped content or symlinked files stop the upload. Public upstream
fixture credentials still require an explicit review and exclusion/allowlist,
not a blanket regex bypass.

After upload, verify remote payload bytes before cleaning local runs:

The campaign JSON is initially a below-target planning state. Run these commands
only after the integrator has populated its `archive` section with the generated
local manifest and remote manifest key.

```bash
python scripts/verify_oss_archive.py \
  --manifest reports/package-expansion-campaign.json
python scripts/verify_oss_archive.py \
  --manifest reports/package-expansion-campaign.json --delete-local
```

The second command is the only supported local raw-run deletion path. It
requires a campaign archive section, a remote checksum manifest, and a local
run directory below `.nl2repo/runs/`. Local脱敏 manifest and aggregate reports
remain after cleanup.

## Before Uploading

Harbor `config.json` files record the agent environment. Harbor already redacts
the API key to a `sk-R****DeI` form, but verify before every upload:

```bash
# Substitute the real key prefixes in use; expect zero matches
grep -rla 'sk-<your-key-prefix>' .nl2repo/runs | head
```

Do not upload if a full key appears; rotate the key first.

## Retrieval

```bash
# Task definitions
ossutil ls oss://dingshang-sg/nl2repobench/harbor-tasks/ -d
ossutil cp -r oss://dingshang-sg/nl2repobench/harbor-tasks/ftfy/ ./ftfy/

# One model on one task
ossutil cp -r oss://dingshang-sg/nl2repobench/runs/gpt-5.6-sol/ftfy/ ./

# Oracle evidence for one task
ossutil cp -r oss://dingshang-sg/nl2repobench/runs/oracle/ftfy/ ./
```

Authoritative scoring lives in each trial's `verifier/grading.json`; treat
`valid: false` as a task/environment result, not a model score.

## Historical Archive Snapshot

The following figures are a historical snapshot from the previous archive
campaign, not a current release gate. Regenerate a versioned OSS inventory
before using them in a report.

| Field | Value |
| --- | --- |
| Task definitions | 683 objects (~12 MB), 64 task directories (historical) |
| Run artifacts | 37,362 objects (~514 MB) (historical) |
| Models | `gpt-5.6-sol`, `claude-fable-5`, plus Oracle and `unknown` |
