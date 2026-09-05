# go-go instruction revalidation blocker

- The expected migrated catalog digest `sha256:1ed106ac7934fe89a1048c429708f97a6cdfb8513533e18d4390f98cb58eff16` passed `uv run nl2repo task validate-source catalog/sources/go-go`.
- Oracle, module-bundle, and verifier CAS objects were present and passed exact size and SHA-256 checks.
- Two production compiles with `toolchain.go.lock.toml`, Harbor `0.21.0`, `--allow-private`, and no `--allow-incomplete` passed and were byte-identical: 68 files, raw manifest `sha256:44dd03e4f58e45ebbbd9b2524a2c0c5bc9816e98959e61cb2dd477f8e628600b`, canonical manifest `sha256:7137166c5f1cede1c41e97d9f75142fe3f51286951984e4808b78a6b36f23dc2`.
- The Oracle bundle contains only `solve.sh`; it fetches the pinned revision from `github.com` at runtime and then checks the source archive digest.
- Local recovery searched the task's authoring handoffs, archives, sessions, supervisor outputs, task solution trees, and private CAS. No source archive matching the frozen revision and declared `sha256:b3c92e9e75f682b5543bf069e4c2fc8fce0eda7067639185bd92e686cc648507` was found.
- Oracle and all controls were therefore not started. No grading, reward, collection, or network receipt is claimed.
- Lifecycle, historical `production-evidence.json`, denominator, and generated projection were left unchanged.

Remediation: supply a trusted offline source payload whose bytes match the frozen revision and archive digest, register it in parent-owned private CAS, update the Oracle artifact reference, recompile twice, and rerun the complete Oracle/control matrix.
