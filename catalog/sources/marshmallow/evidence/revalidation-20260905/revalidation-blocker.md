# Marshmallow instruction revalidation blocker

## Frozen input

- Task: `marshmallow` version `0.2.0`
- Queue source digest: `sha256:6b8a6087f0d7c1c5999a96beb03c35b3e4dac0be15bfa1da3a95b78d0b10f0e1`
- Upstream revision: `c7b559a1fa3aba57ca6dba0ab336841c5038a782`
- Frozen source archive digest: `sha256:c531024b6b6cf15be06fd2205f9304265524a3b1958e3e6c09793bc9b9f35728`
- Runtime and verifier policy: Python 3.12.14, Harbor 0.21.0, `no-network`.

`uv run nl2repo task validate-source catalog/sources/marshmallow` passed before
this evidence was added.

## Recovery performed

The three private refs declared by `catalog/sources/marshmallow/task.toml` were
checked by exact CAS path, size, and SHA-256. None is present locally:

- dependency lock: `sha256:bc408863839162492d8a79745b9b43d824f7f3f02624578d1a01a2ef200085fe`, 381 bytes;
- verifier bundle: `sha256:92658c9384b100fe31012387e6f6a30723e060409b98a924d612a7509ee896c2`, 30,720 bytes;
- Oracle bundle: `sha256:aa7501c75af112c83d666772e5e63b25d1b7c8b7bef06ce0fd615ac580180e1b`, 1,454,080 bytes.

The checked-in projection contains `catalog/tasks/marshmallow/solution/source.tar`,
but its bytes are 1,443,840 bytes with digest
`sha256:a5cb26f6b0028ddbcf39d6cf2733aa1889ec4e1eb853600e1080aa747034ee17`, not
the frozen archive digest. Its inventory also contains generated `__pycache__`
entries. Copies found in bounded local historical worktree searches were the same
projection payload and did not establish the frozen archive or missing private
bundles.

## Blocker and remediation

The available Oracle cannot be inspected or run because its declared private
bundle is absent. The projection payload cannot be substituted: it is not an
exact source-archive match, and runtime source fetch is forbidden by the task
network policy. No lifecycle, `task.toml`, or historical production evidence was
changed. No generated projection was changed.

Parent remediation is to recover exact source/archive bytes and all three private
CAS objects from a trusted local source, verify every size and SHA-256, then
compile twice with the locked toolchain and rerun a complete fresh Oracle,
empty, stub, forgery, and offline matrix against the new final manifest.
