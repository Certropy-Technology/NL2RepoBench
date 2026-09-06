# icecream Revalidation Remediation

## Result

Revalidation stopped before compilation and Harbor execution because all three
declared private artifacts are absent from the parent CAS. Existing lifecycle
and production evidence were preserved unchanged. The queue's expected current
catalog source digest is `sha256:cf0471bf57fbb397f15f0a8d098a8650287be52fde4e7b5dea4f6ab130f6314a`,
with instruction digest
`sha256:821d621fc95cff82572e976926e52cf9e979908c7edd623bb842535ec9be4214`.
The frozen upstream source archive digest remains
`sha256:cf563c74849444da66c3e3914346d1f89086da3565980876f037f542daf5367c`.

## Missing Artifacts

| Artifact | Declared digest | Declared size | Exact CAS path | Result |
| --- | --- | ---: | --- | --- |
| Oracle bundle | `sha256:3bbbcb3e3079b77cae19296ef383718a5def8cb616b4556700e5da2d5aab844b` | 71680 bytes | `.nl2repo/artifacts/private/sha256/3b/3bbbcb3e3079b77cae19296ef383718a5def8cb616b4556700e5da2d5aab844b` | missing |
| Dependency lock | `sha256:ad6e28a9c7cc27fb297dde6940deb37fd89e76c6e0615e460ef7c788835eab24` | 1380 bytes | `.nl2repo/artifacts/private/sha256/ad/ad6e28a9c7cc27fb297dde6940deb37fd89e76c6e0615e460ef7c788835eab24` | missing |
| Verifier bundle | `sha256:08fa6c3fd95f8037ce3d90614e68ae372746cae482f43046819222a356419e35` | 20480 bytes | `.nl2repo/artifacts/private/sha256/08/08fa6c3fd95f8037ce3d90614e68ae372746cae482f43046819222a356419e35` | missing |

The CAS check used the exact digest-derived paths and returned no file for each
artifact; therefore no size or SHA-256 could be computed for absent bytes.

## Offline Recovery Attempts

All attempts were local and used no network, registry, DNS, GitHub, codeload,
or external service:

| Command | Exit/result |
| --- | --- |
| `for spec in '3bbbcb3e3079b77cae19296ef383718a5def8cb616b4556700e5da2d5aab844b 71680' 'ad6e28a9c7cc27fb297dde6940deb37fd89e76c6e0615e460ef7c788835eab24 1380' '08fa6c3fd95f8037ce3d90614e68ae372746cae482f43046819222a356419e35 20480'; do set -- $spec; p=.nl2repo/artifacts/private/sha256/${1:0:2}/$1; if [ -f "$p" ]; then stat -c%s "$p"; else echo MISSING "$p"; fi; done` | exit 0; each exact CAS check reported `MISSING` |
| `timeout 30s rg -l --hidden -g '!*.log' -g '!*.patch' '3bbbcb3e3079b77cae19296ef383718a5def8cb616b4556700e5da2d5aab844b|ad6e28a9c7cc27fb297dde6940deb37fd89e76c6e0615e460ef7c788835eab24|08fa6c3fd95f8037ce3d90614e68ae372746cae482f43046819222a356419e35|cf563c74849444da66c3e3914346d1f89086da3565980876f037f542daf5367c' .nl2repo ~/.pi/agent/sessions/--data-NL2RepoBench--/subagent-artifacts catalog/sources/icecream` | exit 0; only textual references in source metadata and session records, no payload bytes |
| `timeout 30s find .nl2repo ~/.cache ~/.local/share -type f \( -name '*.tar' -o -name '*.tar.gz' -o -name '*.tgz' -o -name '*.zip' -o -name '*.lock.txt' \) -iname '*icecream*'` | exit 0; no matching archive, package, or lock file was returned |
| `find catalog/sources/icecream -type f -print` | exit 0; only public source metadata, instruction, and stub/forgery controls are present; no private payload |
| `uv run nl2repo task validate-source catalog/sources/icecream` | exit 0; source digest `sha256:cf0471bf57fbb397f15f0a8d098a8650287be52fde4e7b5dea4f6ab130f6314a` |

The timed-out searches are retained as infrastructure-limited attempts, not as
proof that an exact replacement payload exists. No archive or lock bytes were
accepted or constructed.

## Next Step

Parent should recover exact bytes from a trusted local handoff or CAS backup,
verify each declared digest and size, and register them in the parent CAS. Then
recompile twice with the locked toolchain and rerun the complete NoNetwork
Oracle/control matrix against the new final manifest. Do not authorize a source
host, lower the denominator, or reuse the historical receipts. Until all three
private artifacts are restored and hash-verified, this task remains pending
revalidation and no Harbor result is claimed.
