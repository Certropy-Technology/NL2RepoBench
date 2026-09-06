# go-semver instruction revalidation blocker

- task: `go-semver`
- source digest: `sha256:8b969f84d5d34827a61c7e4c73af2e48ab0b2564a2b4a678e4b8b689bcdb9dd3`
- frozen revision: `dd2b995c61c39ddd668b23ac919b04d607be35ab`
- required upstream archive: `sha256:883b1aa28b1a3920344950359343bdc2e43b5a70d854fb0850913b2c548325e2`
- required archive size: not declared in `task.toml`; the digest is authoritative.

## Checks

The queue expected source digest `sha256:8b969f84d5d34827a61c7e4c73af2e48ab0b2564a2b4a678e4b8b689bcdb9dd3`. The command
`uv run nl2repo task validate-source catalog/sources/go-semver` exited `0` and reported that exact digest before this evidence was added.

All declared private CAS objects were present and verified by SHA-256 and size:

- module bundle: `sha256:b9bf47e58cb4c81a841b26fb23ad73768d9e6624b1f3bdb93eac1dd1bdb583a0`, 425 bytes;
- Oracle bundle: `sha256:a4a2abf6822ef3199138ea0350982fb1312d00f6db5666dfd7c3e9e68d0acd46`, 734 bytes;
- verifier bundle: `sha256:0e76e0c9566953dbd22af1360cb26e40c01c98317e15fceb77e64a5cda605d97`, 1763 bytes.

The Oracle bundle contains only `solve.sh`. Its source acquisition step uses GitHub at runtime, which is prohibited for this revalidation. The retained local search hashed 4,225 indexed `source.tar` candidates and 5,596 broader archive candidates; neither search found the required archive digest. The local Go module cache contains revision metadata for the frozen commit but no matching source zip or extracted directory. A broad filesystem scan was bounded at 300 seconds (exit `124`) and replaced with the completed indexed scans.

The source compiled twice with `toolchain.go.lock.toml`, `--allow-private`, and the parent CAS artifact root. Both runs exited `0` and produced byte-identical manifests of 12,731 bytes with SHA-256 `sha256:c0cf8c9fff4e8377bd957dd46e6e8b0a4a1376e5823ba5753926c9790a7d7c6c`. No generated projection was changed.

## Classification and next step

This is an `artifact`/`infrastructure` blocker, not a model result. Harbor Oracle, controls, and fresh NoNetwork receipts were not run because no exact local Oracle source payload is available and network authorization is forbidden. Prior `production-evidence.json` remains untouched because its receipts predate the instruction migration and are not valid revalidation evidence.

Next step: parent should recover or register a source archive whose bytes hash exactly to `sha256:883b1aa28b1a3920344950359343bdc2e43b5a70d854fb0850913b2c548325e2`, then update the private CAS binding, recompile, and run the complete Oracle/control matrix under NoNetwork.
