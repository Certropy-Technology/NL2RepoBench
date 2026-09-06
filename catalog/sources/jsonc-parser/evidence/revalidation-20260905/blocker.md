# jsonc-parser instruction revalidation blocker

## Classification

- Task: `jsonc-parser`
- Queue source digest: `sha256:e366a245047ae686542da07fe1768750a1d1aaa77de14a36cb98403db5e66b5c`
- Immutable upstream archive digest: `sha256:4d9fef513a7d3543b79aa9965ffe967cede24c3b675037e44374123589a2ad9b`
- Failure class: `artifact`
- Status: revalidation blocked; existing lifecycle remains `controls-passed`
- Network policy: `no-network`; no source host, registry, DNS, or external-service authorization was used

The parent CAS does not contain any of the four private artifacts declared by
`catalog/sources/jsonc-parser/task.toml`. The exact digest, expected size, and
artifact role are recorded in
`catalog/sources/jsonc-parser/evidence/revalidation-20260905/local-recovery-search.json`.

## Offline checks

The following checks were run before deciding the blocker:

1. Parsed the queue and confirmed the expected current source digest.
2. Ran `uv run nl2repo task validate-source catalog/sources/jsonc-parser`; it
   passed with source digest `sha256:e366a245047ae686542da07fe1768750a1d1aaa77de14a36cb98403db5e66b5c`.
3. Resolved all four declared references against
   `<integration-root>/.nl2repo/artifacts/private/sha256`;
   all four leaves were absent.
4. Verified the current generated projection's source and distribution archives:
   `source.tar` is 266,240 bytes with SHA-256
   `4d9fef513a7d3543b79aa9965ffe967cede24c3b675037e44374123589a2ad9b`, and
   `distribution.tar` is 112,640 bytes with SHA-256
   `99ecb53a34efa2cc74f71a0907eb732215c16a5741f733183fab715625f44260`.
   These are payload members or projections, not proof of the missing private
   outer bundle bytes.
5. Searched historical task worktrees, authoring handoffs, retained runs,
   worker artifact storage, and bounded local package caches by exact digest and
   expected size. No match was found.

## Why no replacement was constructed

The current projection exposes enough files to describe the task, but it does
not preserve the original private npm cache bundle, command bundle, test bundle,
or Oracle bundle byte streams and their tar metadata. Repacking available files
would produce a new artifact with an unproven digest and would invalidate the
existing private references. No replacement path, outer hash, or inner bundle
binding is therefore proposed.

## Required remediation

The parent must register the exact four CAS objects, or supply replacement
bundles whose outer and inner bytes are independently verified against the
declared contract. After that, the parent must compile twice with the locked
Node toolchain, bind a new final manifest, and run a fresh no-network Oracle,
empty, stub, forgery, and offline matrix. Until then this worker did not run
compile or Harbor and did not alter `task.toml`, lifecycle metadata, generated
runtime, or the prior `production-evidence.json`.
