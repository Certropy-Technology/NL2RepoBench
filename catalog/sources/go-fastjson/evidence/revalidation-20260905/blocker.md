# go-fastjson instruction revalidation blocker

- The expected catalog digest `sha256:229bc88eb28614fa8d3e1789df847fe2ac00e21b6201d89138793b1294117738` was validated.
- All three declared private CAS objects were present and verified by exact size and SHA-256.
- Two production compiles with `toolchain.go.lock.toml`, Harbor `0.21.0`, `--allow-private`, and no `--allow-incomplete` passed and were byte-identical: 74 files, raw manifest `sha256:64f92f61694b574f3c7d67a055f3fbe84a5563398bf3d0049e25ba7ce508ed2e`, canonical manifest `sha256:961ac919eb25155ef14958e9677989982352f5514b1099dd8899cb5c59663d33`.
- The current Oracle bundle contains no source archive. Its `solve.sh` performs `git fetch` from `github.com`, then creates the source archive at runtime.
- A bounded offline exact-digest search covered the current bundle, task-local evidence, historical authoring state, private CAS metadata/payload names, tracked objects, and local authoring archives. No bytes matching the frozen source revision and archive digest were found, so no replacement private bundle was created.
- Oracle, empty, stub, forgery, and offline Harbor runs were not started. No grading, reward, collection, or run receipt is claimed.
- Lifecycle, historical `production-evidence.json`, denominator, and generated projection were left unchanged.

Remediation: provide a trusted private source archive whose bytes match revision `d652a1b1909d3520389b2c287ca3cf3aa3791451` and archive digest `sha256:e7d863c47fbe692c97f5148a75dcda72695fca9dc672642dcdb4a22da28861a2`; replace the runtime fetch, recompile twice, and rerun Oracle plus the complete controls matrix under NoNetwork.
