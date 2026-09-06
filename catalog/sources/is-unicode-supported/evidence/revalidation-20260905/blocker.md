# is-unicode-supported instruction revalidation blocker

- Task: `is-unicode-supported` `2.1.0`
- Queue instruction digest: `sha256:f5e57567a989f3bdd624acbe85f9731b971cf14bc236cb3e183ff34425e429ee`
- Frozen revision: `e0373335038856c63034c8eef6ac43ee3827a601`
- Frozen source archive digest: `sha256:f15b5aac5c7f5e331c91310d01ac6c73efb36686bd9ae87c47847dbf6978bc38`
- Failure class: `artifact`
- Network access: forbidden and not used

## Checks

The queue digest was read before any task-local change. `uv run nl2repo task
validate-source catalog/sources/is-unicode-supported` exited `0` and reported the
same queue digest. All four private CAS objects declared by `task.toml` were
present and matched their declared sizes and SHA-256 values:

- dependency closure `sha256:35899cb523c2a7a07e0639c5df87900c354a16eb0a9f53ddb74808ee18411fdd`, 10240 bytes;
- command plan `sha256:005ffae244839bfaceab5ce2c04af99127726c472e30db90c1af6243617c7f82`, 10240 bytes;
- test bundle `sha256:1b49cf389301637da257db381c87879340d19af8eeca5946b334bc8185322da3`, 10240 bytes;
- Oracle bundle `sha256:d010d8d5808855f7cb599615abb9cf4f8ae483eb25a1d0167bef1a4c4d693105`, 10240 bytes.

The Oracle bundle contains only `solve.sh`. Its source acquisition runs
`git fetch` from `https://github.com/sindresorhus/is-unicode-supported`, which is
prohibited by the task's NoNetwork policy. The checked-in generated runtime,
task-local evidence, retained authoring worktrees, handoffs, archives, runs,
local npm/git caches, and exact source archive candidates were searched. No
local bytes matched the frozen archive digest, so no replacement bundle was
constructed or proposed.

## Compile evidence

The source was compiled twice with `toolchain.node.lock.toml`, the parent CAS,
`--allow-private`, and no `--allow-incomplete`. Both compiles exited `0`,
produced 74-file bundles with canonical manifest digest
`sha256:9c7f5fe442ad1eb200296ce3215aac76a327878f55abdad2d410fa70eddc1922`,
and were byte-identical. This compile evidence does not qualify the task for
Harbor execution because the Oracle source payload is unresolved under
NoNetwork.

## Durable evidence

- `recovery-search.json` records exact artifact checks and bounded local searches.
- `compile-a-summary.json` and `compile-b-summary.json` record both compile receipts.
- `revalidation-commands.log` is the source-local command log for this blocker.

The existing `task.toml` and `production-evidence.json` were preserved. No
Oracle, control, generated projection, or Harbor run was performed after the
Oracle network-fetch issue was identified.

## Next step

The parent integrator must recover an exact source archive whose bytes hash to
`sha256:f15b5aac5c7f5e331c91310d01ac6c73efb36686bd9ae87c47847dbf6978bc38`,
register a reviewed replacement Oracle bundle in the shared CAS, then rerun
the double compile and complete NoNetwork Oracle/control matrix against the
new final manifest. A package registry tarball, alternate archive format, or
network authorization is not an acceptable substitute.
