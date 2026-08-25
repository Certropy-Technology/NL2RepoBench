# Parse Production Authoring Audit

The authoritative descriptor is `task.toml`. This task freezes upstream commit
`8059e320eccf40d750843006dd2ef25197bbff74`, its direct unprefixed git archive,
a hash-locked setuptools build closure, a private subprocess verifier, and a
private local Oracle archive. No wheel files are vendored.

## Source and license provenance

- Upstream: `https://github.com/r1chardj0n3s/parse`
- Resolved commit: `8059e320eccf40d750843006dd2ef25197bbff74`
- Tree: `d32727361f385b82b19f60f261f0887043b3254b`
- Commit timestamp: `2026-08-01T14:49:10+09:00`
- Submodules: none
- `git archive --format=tar` size: 133120 bytes
- Archive SHA-256: `eb48010aafcc5a9699285f59fbe5abce50bacba1e6da175072163a7ed3c38176`
- Frozen `LICENSE` size: 1085 bytes
- Frozen `LICENSE` SHA-256: `2cc9942fe3f52a669c1fbb4e0bae9a27300d56564a382e954845c3256c4cabe2`
- Upstream `pyproject.toml` declares MIT and `setuptools>=61.2`; the task pins
  setuptools and wheel exactly for candidate builds.

## Verifier boundary and denominator

The 96-leaf `custom-json-v1` suite covers only behavior stated in
`instruction.md`: exact parse, ranged search, ordered non-overlapping findall,
reusable Parser/compile behavior, Result access, and fixed width/precision and
primitive type conversion. Root-owned `run.py` contains expected observations.
It launches a generic `probe.py` as UID 10001; only that subprocess imports the
candidate from `/tmp/candidate-site`. Candidate code is never imported by the
trusted verifier process. Every request and response is bounded JSON, each
probe has a timeout, and the fixed leaf IDs are independent of candidate
collection behavior.

The prior legacy runtime also declared 96 tests. Production authoring retains
that fixed denominator; no test is removed to improve Oracle or control scores.
The original upstream fixture files are retained byte-for-byte inside the
private verifier bundle for traceability. The executable 96-leaf adapter is
deliberately bounded to behavior promised by the public specification; the
retained files are not directly imported by trusted grading.

## Network and artifact policy

Both runtime phases declare no network. Dependency packages are fetched only
during Docker build from a hash-locked requirements artifact. The Oracle uses a
digest-checked local source tar from its private bundle and performs no source
fetch. Verifier and Oracle bytes are content-addressed private artifacts and
are not embedded in this public source directory.

`production-evidence.json` records the final Oracle, empty, stub, forgery, and
offline receipts after Harbor execution. Reviews and pilots are intentionally
outside this authoring task.
