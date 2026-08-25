# `ftfy` production authoring record

The task is bounded to deterministic public behavior from python-ftfy 6.3.1 at
commit `74dd0452b48286a3770013b3a02755313bd5575e`. The unprefixed
`git archive --format=tar` is 686,080 bytes with SHA-256
`c4bb6cb686c1f1e56cbe50dafcaf575512763acd4d7ebdda4dd3d4da41aad1ec`.
The frozen source declares Apache-2.0, Python >=3.9, Hatchling, and the sole
runtime dependency `wcwidth`.

The production verifier is not the inherited 336-item same-process pytest
projection. It is a bounded custom JSON contract whose candidate-facing
adapter runs as uid 10001 in a fresh isolated Python process and imports only
the installed candidate site. Trusted expected observations stay in the
private parent runner. The slice covers package identity, text and encoding
repair, entities, explanations and plan replay, byte guessing, custom codecs,
incremental decoding, character fixes, badness, formatting, file streaming,
and CLI behavior. Every leaf maps to behavior stated in `instruction.md`.

The candidate build closure is installed from a hash-locked requirements file
during image build. It contains the Hatchling closure and `wcwidth`; there are
no vendored distributions. Runtime agent and verifier network modes remain
`no-network`. The Oracle bundle contains the digest-verified frozen source tar
and does not fetch source at run time.

## Final control outcome

The official Harbor 0.21.0 Oracle passed all 15 frozen leaves with
`valid=true` and reward 1.0. The empty control was the accepted valid model-zero
installation failure, and the forgery control was valid at 0/15. All four
verifier network receipts show `public_network_available=false`.

The stub control is a blocker. Its candidate installation succeeded, but the
trusted custom verifier attempted to parse an empty child report and raised
`JSONDecodeError`. Grading consequently recorded `valid=false`,
`failure_class=verifier`, and `failure_reason=verifier-internal-error`. A
verifier failure cannot satisfy a negative control regardless of its displayed
reward. The lifecycle is therefore `blocked`, not `controls-passed`; review,
pilot, and publication remain out of scope. Exact receipt paths and hashes are
in `production-evidence.json` and `evidence/stub-control.txt`.
