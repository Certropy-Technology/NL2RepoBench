# Revalidation blocker: Oracle source is not locally recoverable

The queue entry and pre-mutation `validate-source` both identify source digest
`sha256:3373bd50f0a3ec7dcd439ab45313871631dd24d49d3b1d8761232b572b02988c`.
All four declared private artifacts were found in the parent CAS with exact
size and SHA-256 matches. The two production compiles with
`toolchain.node.lock.toml` also passed and were byte-identical by relative
path (73 files); their current compile manifest is recorded in
`compile-summary.json`.

The Oracle bundle is not executable under the current NoNetwork contract. Its
only entrypoint runs `git init`, adds the upstream GitHub remote, and executes
`git fetch --depth=1 origin 3ee1e62d926ac0a5cf631815734d8e06a9381d72`. The
bundle contains no `source.tar` or package payload. Bounded searches of the
current generated task, retained final Harbor workspace, local CAS, local
archives, historical projections, and the local Git object database found no
archive matching the frozen source digest
`sha256:52b0b045635fe457322cea36d04dcaa0b4944d4ac21d07448bb44f93dc3e8101`.
The retained workspace files are generated `index.js`, `index.d.ts`, and
metadata, not a proof of the required Git archive bytes.

Accordingly, no Oracle, control, lifecycle, or historical production-evidence
claim was changed. Parent remediation is to recover the exact frozen archive
from a trusted local source and independently construct/register a replacement
Oracle bundle, then recompile and run the complete matrix under NoNetwork.
