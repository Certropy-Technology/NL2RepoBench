# p-locate instruction revalidation blocker

- Task: `p-locate`
- Source digest after instruction migration: `sha256:48c3532ceea3ea335638a1875376a184f34ec9f485ccf258795d597cff4dda43`
- Frozen revision: `b9ccdaaa83f8d2f53f8acf8ff3c97b7aa21f655b`
- Frozen archive: `sha256:7c1a4f05591c63b2ef538dfb24df894a3ff3d2de56622a85b7787d54e3e0299b`, 30,720 bytes
- Lifecycle and historical `production-evidence.json` were not modified.

## Validation and artifacts

The queue digest matched and this source passed before mutation:

```text
uv run nl2repo task validate-source catalog/sources/p-locate
exit_code=0; status=controls-passed; source_digest=sha256:48c3532ceea3ea335638a1875376a184f34ec9f485ccf258795d597cff4dda43
```

All four declared private artifacts were found in the trusted local CAS and verified by exact
size and SHA-256. The detailed checks and CAS placeholders are in `artifact-verification.json`.
The dependency, command, test, and Oracle artifact digests are respectively
`sha256:6a0913d75bb8ab3708466dceb83046fa8244cfd279591a09183f991a068ccc9f` (133,120 bytes),
`sha256:10e70a89b271a2cd71d8dbaa6848530c6550ac4d87e65ae87d7332265e5eedd9` (10,240 bytes),
`sha256:6a2b2aedd4529bd2e6dd0f4d1a4cb641b617ee118306fe88e67ce80e851fb424` (30,720 bytes), and
`sha256:4af6763bc0c4901a9f0a4b3d7b5f9f6d0cfe555d4f5e24a9de1e74d67acd9cf9` (10,240 bytes).

## Compile result

The current source compiled twice with the locked Node toolchain and `--allow-private`; both
outputs were byte-identical. Each bundle contains 91 files, manifest file SHA-256
`sha256:19b828ed4877a4d541c9d4a5825f911d2aadabce4ec484eb42765802369463be`, and canonical
manifest digest `sha256:98dfbe98be5e91dc937650a16b89cee03d7127339b83a7345905d186173206c0`.
See `compile-summary.json` for normalized commands and review results.

## Blocker and skipped gates

The exact Oracle artifact contains `solve.sh` that performs a runtime `git fetch` from
`github.com/sindresorhus/p-locate.git` before checking out the frozen revision and verifying
the archive digest. The exact 30,720-byte frozen source archive was not found in bounded scans
of trusted CAS, historical handoffs, generated projections, runs, or local caches. The existing
generated projection also contains no source payload. Running Harbor would therefore require
forbidden runtime source acquisition, so no Oracle or controls were started.

Classification: `artifact-or-verifier`.

Skipped set: Oracle, empty, stub, forgery, install-script, call-hang, and offline controls;
fresh grading, network, reward, and failure sets do not exist. No score or current validity is
claimed. This is not an infrastructure or model result.

## Remediation

Recover or provide the exact frozen source archive bytes, verify revision, size, and SHA-256,
then register a replacement Oracle artifact in the parent CAS. Recompile twice against the
replacement, inspect the final manifest, and run a fresh Harbor 0.21.0 Oracle plus every
supported control under NoNetwork. Require collection `38/38`, Oracle reward at least `0.80`,
real-denominator stub/forgery rewards at most `0.20`, and `public_network_available=false`.
