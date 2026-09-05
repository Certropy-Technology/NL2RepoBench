# Fonttools instruction-migration revalidation blocker

- Task: `fonttools`
- Revalidation date: `2026-09-05`
- Expected and validated current catalog source digest: `sha256:4fd2c0687dfcd23765652337a92adbb40ed8e7ac1dc9e747ff0d1d6020e3b1b1`
- Frozen upstream revision: `e7e00f1b16aef6ede850206df3c100ccde27b2d3`
- Frozen source archive digest: `sha256:2c7719e06724e5f34b4677eb4e7a5cb17a9cdee1225f829b2881b097d61d666c`
- Lifecycle and historical `production-evidence.json`: unchanged.

## Completed checks

`validate-source`, instruction quality, full-root network lint, TOML/JSON parsing, shell syntax, and `git diff --check` passed. Full-root network lint scanned 480 sources, with zero errors and zero fonttools findings. All three declared private artifacts were present in the parent CAS with matching size and SHA-256. See the JSON summaries in this directory.

Two production compiles using the locked Python toolchain and private CAS exited 0 and were byte-identical. Both produced 58 files, raw manifest digest `sha256:3251979b68e4c1accf023677081d60603654a7dd36e058aa580c8e84a6b76743`, and canonical manifest digest `sha256:924a947ef56828ee50aac66583fd38d8d00072c0ac056ffabc8e7b8295c245a6`.

## NoNetwork blocker

The immutable Oracle bundle is present and hash-verified, but its only member, `solve.sh`, initializes a Git repository, adds `https://github.com/fonttools/fonttools`, and executes `git fetch` for the frozen revision before generating and checking the source archive. This violates the revalidation contract forbidding runtime GitHub, codeload, registry, DNS, and external-service access for Oracle and controls. Oracle and controls were therefore not run, and no new reward or test result is claimed.

## Remediation

Register a replacement private Oracle payload containing the frozen source locally, or replace the Oracle script with a source-local immutable payload while preserving revision and archive-digest checks. Recompile twice against that replacement and run the complete Harbor 0.21.0 Oracle, empty, stub, forgery, and offline matrix. Persist durable receipt summaries before any future production-evidence update. Do not grant GitHub authorization, reuse historical run paths, change the denominator, or change lifecycle solely for this blocker.
