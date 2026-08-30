# Authoring Audit

This lane freezes virtualenv 21.7.5 at commit
`2a645aece0241e6dc02bf3d67acd88aa0770b601` and uses a 36-leaf private
`custom-json-v1` verifier. The verifier copies the candidate into a private
installation target, invokes each scenario through an unprivileged child, and
owns collection, JUnit, grading, and reward output.

The source revision and raw archive were checked before authoring. The Oracle
script fetches only the frozen revision, asserts the commit and archive hash,
then replaces the Git checkout with the exact archive contents so workspace
limits do not include Git history. Hatch-VCS receives a build-only pretend
version because archive contents have no `.git` metadata.

The production image is Debian CPython 3.12.14 with locked digest
`sha256:356b0d18f9385f4bdcc673af60e1e64c9d1504952e4ec36ee32044c722a6bc4e`.
Candidate build dependencies are installed only during image build from the
private hash lock. Agent and verifier execution use no network; source-host
access is limited to the trusted Oracle invocation.

Observed local gates: source validation passed, the separate verifier image
built, Oracle passed 36/36 with reward 1.0, stub/forgery/call-hang collected
36/36 with reward 0.0, empty/install-hang were bounded install exceptions,
workspace-invalid was rejected, and all recorded public-network probes were
false. No Harbor Agent Run was started.
