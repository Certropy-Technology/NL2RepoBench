# `python-dotenv` production authoring record

Status: `controls-passed`. Review, pilot, dataset integration, commit, and push
are outside this task.

The task freezes upstream commit
`02b68577f37da2c4f4b9377d7a0ca2b58fdacf20`. Its unprefixed 153,600-byte
`git archive` has SHA-256
`e6ec01e11aa990e59b45e40b3f44b597cef8d107fc270e261974ab15fa40371e`.
The root BSD-3-Clause `LICENSE` has SHA-256
`80619b7049f08c81683ad0e01f08f257a840652dd71ee83146d36658c7d2c2b9`.
The tree has no submodules. Documentation-only symlinks are removed after the
Oracle verifies and extracts the intact archive because the candidate artifact
boundary accepts regular files and directories only; package source and build
inputs are unchanged.

The bounded 33-leaf contract covers public parsing, quoting, comments, invalid
records, interpolation and precedence, key lookup, deterministic parent
discovery, environment loading, set/unset mutation, alternate encoding, the
command-string helper, and module CLI list/get/set/unset/run/version/error
behavior. The trusted process owns expected values and scoring. Only an
unprivileged, resource-limited child imports candidate code and creates
temporary `.env` fixtures; CLI calls are argument-vector subprocesses without
shell evaluation.

The 631-byte requirement lock pins Click 8.4.2, setuptools 80.10.2, and wheel
0.45.1 with package-index hashes. Docker build uses `--require-hashes`; no
wheel or wheelhouse is vendored. Candidate and verifier runtime phases are
no-network. The Oracle bundle contains only `solve.sh` and the local frozen
source archive and performs no fetch.

The final Harbor 0.21.0 Oracle passed 33/33 at reward 1.0. Empty scored 0;
the installable stub and forgery controls each scored 2/33. The workspace
forgery could not modify trusted reward or verifier files. All four final
network receipts report `public_network_available=false`. Exact task-local
receipt paths and hashes are recorded in `production-evidence.json`.
