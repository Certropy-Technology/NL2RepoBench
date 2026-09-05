# go-fx instruction revalidation blocker

The migrated catalog digest was validated as
`sha256:00be8bb906f8e6e4217d596f29891f0f142fcd8a83de5cce8ccb30fde3efcf5d`.
The three declared private artifacts are present and size/SHA-256 verified. Two
production compiles with `toolchain.go.lock.toml` and `--allow-private` were
byte-identical across 138 files, with canonical manifest digest
`sha256:789432e1c31f465a76d046053de5d3b06fab79ab1c0adb780f93f72f9d117cc2`.

The Oracle bundle contains `solve.sh` and the dependency module bundle, but no
source archive. Its script performs a runtime `git fetch` from `github.com` for
revision `4f31cd3a0c5d66f1b4290a2719bab14a5cee8ebe` and then checks the expected
source archive digest. Runtime source-host access is forbidden by this task's
NoNetwork policy.

Local recovery was attempted against the current private CAS, the historical
go-fx authoring worktree, historical go-fx generated projections, and local
authoring/CAS bundles containing `source.tar`. Sixty-one embedded archive
candidates were inspected; none matched the frozen source archive digest
`sha256:efe539dae8dab090b45e4224eaae1e476e61fc3ec4156212087d67dd39f5297c`.
No replacement bundle was created because no trusted hash-equivalent payload
was found. No network authorization was used.

Oracle and controls were not run. The source, lifecycle, historical production
evidence, denominator, and generated projection were left unchanged. Parent
remediation: provide a local source archive whose bytes match the frozen source
revision and digest, register a replacement Oracle artifact, recompile twice,
then run the full NoNetwork Oracle/control matrix and bind fresh receipts.
