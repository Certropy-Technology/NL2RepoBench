# `jsonlines` production authoring record

Status: `controls-passed`. Review, pilot, dataset integration, commit, and push
are outside this lane.

The task freezes upstream commit
`43d1a30b9634f8b715b6af3f2473927caa1e704d`. Its unprefixed 71,680-byte
`git archive` has SHA-256
`fd839af51a766d70dccb95db84e6bcf741f55b01ed756b817be4838f202407a6`.
The root BSD-3-Clause `LICENSE.rst` has SHA-256
`bca354e6392b2421ffb1f1e234545c515433b9291362c1bb9fd100922b90eb42`.
The tree has no submodules.

The bounded 30-leaf contract covers top-level exports; text and binary Reader
decoding; JSON values; BOM and RFC 7464 prefixes; EOF, empty, malformed UTF-8,
malformed JSON, null and typed-read errors; iteration and skipping; custom
loads; Error fields and inheritance; text, binary, compact, sorted, custom and
flushing Writer behavior; lifecycle semantics; and read/write/append/exclusive
file modes. Trusted expected values remain in the separate verifier. Only an
unprivileged, resource-limited child imports candidate code and returns JSON
observations.

The raw 558-byte requirements lock pins `attrs==25.4.0`,
`setuptools==80.10.2`, and `wheel==0.45.1` with package-index hashes. Docker
build installs it with `--require-hashes`; no wheel or wheelhouse is vendored.
Agent and verifier runtime phases are no-network. The Oracle bundle contains
only `solve.sh` and the digest-verified local source archive and performs no
fetch.

The first two Oracle attempts are retained under task-specific run roots as
failed remediation evidence: one used the wrong upload path, and one omitted
the preinstalled dependency site from the isolated child. Neither changed the
contract or weakened isolation. The final Harbor 0.21.0 Oracle passed 30/30 at
reward 1.0. Empty scored 0, and the installable stub and forgery controls each
scored 1/30. All four final network receipts report
`public_network_available=false`. Exact paths and hashes are in
`production-evidence.json`.
