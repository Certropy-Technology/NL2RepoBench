# `ip-address` instruction-migration revalidation recovery

## Frozen input check

Before any source change, `nl2repo task validate-source` returned catalog source
digest
`sha256:fa27ead6260eab4025afeb8fcf134d1bb3110a1e3d11b22404f4ee104bcacafb`,
which exactly matches the instruction-revalidation queue. This catalog digest is
distinct from the frozen upstream Git archive digest
`sha256:5003fe0f3466d3c7b6a494d5aae4df4ca87d165fbede1e50b87fceaaa7f4977d`.

All four private artifacts declared by `task.toml` exist in the parent CAS and
match both their declared byte sizes and SHA-256 digests. The current Oracle
artifact is not eligible for this revalidation because its `solve.sh` executes
`git clone` against GitHub before copying an already embedded
`oracle-package/` into the workspace.

## Bounded local recovery

The current Oracle bundle and generated runtime were inspected first. They
contain the same complete `ip-address` 10.5.0 package, including declarations,
compiled CommonJS modules, source maps with embedded TypeScript source content,
the frozen MIT license, and package metadata. The embedded license hash matches
the task's source-freeze evidence. The recorded authoring source archive path no
longer exists, and no matching task-specific archive was found in retained
handoffs or authoring state. A historical npm cache candidate was version
10.7.0 and was rejected rather than substituted for the frozen 10.5.0 bytes.

An ignored replacement Oracle bundle was built solely from the existing
hash-verified Oracle payload. It preserves all 31 `oracle-package/` files
byte-for-byte. Its new offline `solve.sh` checks the frozen revision and source
archive declarations, verifies a SHA-256 manifest covering every embedded
package file, and then copies the package into the workspace. It contains no
URL, Git, registry, DNS, or external-service operation. Two deterministic
repack attempts were byte-identical, and the offline solve smoke test passed.

Replacement proposal:

- local handoff path: `.nl2repo/ip-address-recovery/oracle-bundle.tar`
- outer digest: `sha256:2c366383f5c693af884cb4000354c0c9519883b640621289bd084aeb59f4bcfe`
- outer size: `307200` bytes
- `solve.sh`: `sha256:8cb86f899aa49ba4ab99e880630842a309d6bef1a9b3f9e2d239c853061d38ba`
- freeze declaration: `sha256:96cc9eb24cd173e9dff40f50b497424e313b6ce1a6abf942fda43d5336db4af6`
- 31-file package hash manifest: `sha256:4558abaf641a47be88f675fe28286147a6257f52abe18771154d97bd7e50c074`

The proposed parent-owned binding is:

```toml
[oracle_bundle]
digest = "sha256:2c366383f5c693af884cb4000354c0c9519883b640621289bd084aeb59f4bcfe"
size_bytes = 307200
media_type = "application/vnd.nl2repobench.oracle+tar"
uri = "artifact://private/sha256:2c366383f5c693af884cb4000354c0c9519883b640621289bd084aeb59f4bcfe"
visibility = "private"
```

## Disposition

The worker did not mutate shared CAS or `task.toml`. Compile and Harbor were
not run because doing so with the current binding would retain the forbidden
runtime GitHub fetch, while compiling against an unregistered digest would not
be reproducible. The lifecycle and prior production evidence remain unchanged;
the old receipts are not claimed as current after the instruction migration.

The parent must verify and register the replacement, update the Oracle artifact
binding, recompute the catalog source digest, compile twice with
`toolchain.node.lock.toml`, and run a fresh NoNetwork Oracle and full supported
control matrix against the resulting final manifest.
