# normalize-url revalidation blocker

- Task: `normalize-url` version `2.0.0`
- Queue/source digest: `sha256:b2415b8b7315ba2df244fc9cad8ad2de80ca598cfffa36c8b2b037951d15ae88`
- Frozen revision: `863d275c21d6411a7494b8f728a515633bc01d84`
- Frozen source archive digest: `sha256:6c7fd8315e3feae64c76202281560a3b4a27f807d736371c783d921049ab5cfe`
- Classification: `artifact/verifier` blocker for this revalidation pass.

`validate-source` passed before mutation. All four declared private CAS artifacts
were found and matched their declared sizes and SHA-256 values; details are in
`artifact-check.json`. The generated task Oracle bundle was inspected offline and
contains only `solve.sh`, with no embedded source archive. That script executes a
runtime `git fetch` from `github.com` for the frozen revision and therefore cannot
run under the task's required NoNetwork policy. The exact source archive was not
present in the generated bundle, so no replacement payload was assumed.

No compile, Harbor Oracle, or controls were run, and no historical receipt was
reused. Lifecycle, `task.toml`, generated projection, and
`production-evidence.json` are unchanged. All paths in this evidence use
placeholders; no local worktree or run path is persisted.

## Next step

Recover and independently verify an exact source archive for the frozen revision
and digest, then have the parent register a NoNetwork-safe Oracle bundle in the
private CAS. Compile twice and run fresh Oracle plus all supported controls against
the resulting manifest. Do not add host authorization or change the denominator.
