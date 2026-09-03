# Figures Provenance

- Upstream: `https://github.com/sindresorhus/figures`
- Frozen revision: `3da3d1713e9a09dbfcfc99eac86af8f4377597b6`
- Source archive digest: `sha256:c1b1db9dd7ff5771b6301e85ade19184e7bf46990b95008240729c39287b3258`
- License: MIT; the checked source license file digest is recorded in the task-local evidence.
- Upstream package metadata: `figures@6.1.0`, ESM, Node `>=18`, runtime dependency `is-unicode-supported`.
- The source archive is fetched only by the trusted Oracle solution, with a run-scoped authorization for `github.com`, and is never placed in the Agent image or public instruction.
- Candidate dependencies are installed from the private npm cache bundle at build time. Candidate and verifier execution use `no-network` mode.

The archive digest was computed with `git archive --format=tar` at the frozen
revision. The Oracle solution repeats the revision assertion and archive digest
check before populating `/workspace`.
