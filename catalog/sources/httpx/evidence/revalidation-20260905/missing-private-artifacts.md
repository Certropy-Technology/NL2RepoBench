# HTTPX Revalidation Remediation

Revalidation stopped before compile or Harbor because the private artifacts
declared by `catalog/sources/httpx/task.toml` are not present in the configured
local CAS. The task lifecycle and existing production evidence were preserved.

## Frozen identity

- Task: `httpx` `0.2.0`
- Source revision: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Current post-instruction-migration source digest: `sha256:53860cf39e8c438fc52b41ec2345a07d43273a417e8e6610ecf6c3234469d042`
- Queue instruction digest: `sha256:ef1ff3ed2f6c3cf21a53b4b1da41444f156b3dfcf5e621a82a01c3aa96a995b4`

## Missing declarations

| TOML reference | Digest | Expected bytes | Checked CAS path |
| --- | --- | ---: | --- |
| `oracle_bundle` | `sha256:de3d266d324ff365adfecfff4728ef8eae5c6d5df266eb28684c59a117083f66` | 3430400 | `.nl2repo/artifacts/private/sha256/de/de3d266d324ff365adfecfff4728ef8eae5c6d5df266eb28684c59a117083f66` |
| `dependencies.lock_artifact` | `sha256:8f35c08665ed4c75ca58caf51de225dfdbeb95ca5a66057adeebfa14c408d6cd` | 4774 | `.nl2repo/artifacts/private/sha256/8f/8f35c08665ed4c75ca58caf51de225dfdbeb95ca5a66057adeebfa14c408d6cd` |
| `tests.test_bundle` and `verifier.bundle` | `sha256:39755ebfc0216fd6a10e24c59a29fab33c8fa539f920730e4e0da29fa9ab51af` | 20480 | `.nl2repo/artifacts/private/sha256/39/39755ebfc0216fd6a10e24c59a29fab33c8fa539f920730e4e0da29fa9ab51af` |

## Offline checks

Commands were run from the repository root with no network authorization:

```text
python3 - <<'PY' ... read reports/instruction-revalidation-queue-20260905.json ...
PY
exit 0
result: queue source digest is sha256:53860cf39e8c438fc52b41ec2345a07d43273a417e8e6610ecf6c3234469d042

uv run nl2repo task validate-source catalog/sources/httpx
exit 0
result: source_digest=sha256:53860cf39e8c438fc52b41ec2345a07d43273a417e8e6610ecf6c3234469d042,
status=oracle-passed, task_id=httpx, version=0.2.0

python3 - <<'PY' ... resolve each private digest under
.nl2repo/artifacts ...
PY
exit 0
result: oracle_bundle FOUND None; lock_artifact FOUND None; test_bundle FOUND None;
all declared private refs are missing
```

The Harbor CLI was inspected before this stop: `uv run --frozen --project
harbor-runner harbor --version` exited 0 and reported `0.21.0`. No compile,
Oracle, control, or generated projection command was run after the missing CAS
check.

## Local recovery search

The integration repository was searched by filename and exact digest only; no
network access or package-registry lookup was used:

```text
timeout 25 find .nl2repo/artifacts -type f \( -name '*httpx*' -o -name '*de3d266d324ff365adfecfff4728ef8eae5c6d5df266eb28684c59a117083f66*' -o -name '*8f35c08665ed4c75ca58caf51de225dfdbeb95ca5a66057adeebfa14c408d6cd*' -o -name '*39755ebfc0216fd6a10e24c59a29fab33c8fa539f920730e4e0da29fa9ab51af*' \) -print
exit 0; result: no matches

timeout 25 find <repository-local-handoff-root> -type f \( -name '*httpx*' -o -name '*de3d266d324ff365adfecfff4728ef8eae5c6d5df266eb28684c59a117083f66*' -o -name '*8f35c08665ed4c75ca58caf51de225dfdbeb95ca5a66057adeebfa14c408d6cd*' -o -name '*39755ebfc0216fd6a10e24c59a29fab33c8fa539f920730e4e0da29fa9ab51af*' \) -print
exit 0; result: no matches

timeout 25 find <repository-local-worktree-root> -type f \( -name '*httpx*' -o -name '*de3d266d324ff365adfecfff4728ef8eae5c6d5df266eb28684c59a117083f66*' -o -name '*8f35c08665ed4c75ca58caf51de225dfdbeb95ca5a66057adeebfa14c408d6cd*' -o -name '*39755ebfc0216fd6a10e24c59a29fab33c8fa539f920730e4e0da29fa9ab51af*' \) -print
exit 124; result: bounded by timeout; output contained unrelated httpx documentation/tool files and no exact digest match
```

The search did not prove an installable payload, so no replacement bundle was
constructed.

## Next step

The parent integrator must recover each exact hash- and size-matching artifact
from an approved local frozen bundle, historical handoff, or local CAS backup,
register it in the shared CAS, and then rerun source validation, a double
compile, and the complete Oracle/control matrix against the current source
digest. A differently formatted archive, cache directory, or network download
must not be substituted.
