# fastjsonschema Remediation Evidence

Status: `awaiting-agent-run`; release `0.3.1` rebuilt all private references in
its task-local content-addressed artifact store and compiled a production bundle.
The independent Agent Run loop owns any Harbor `run` invocation. This directory
is the only public catalog write root for this lane.

## Frozen Source

- Upstream: `https://github.com/horejsek/python-fastjsonschema`
- Revision: `b88fa37cd46bb81e8d9dce91a7e1bc4debedd3a2`
- Tree: `d5ffcff4278232a8097f3cb7feffc6b5f75b3db1`
- Version: `2.22.2`; license `BSD-3-Clause`.
- Source archive SHA-256: `c6d2c4ec7d81009b52c35430082ab13a29a32a92e323e64ffff1d6f304ca717d`.

The materialized `JSON-Schema-Test-Suite` submodule is revision `9fc880bfb6d8ccd093bc82431f17d13681ffae8e`, tree `66c7b275cfafa940e7dcd2213582778757241017`, archive SHA-256 `5b4c6e96e60a52ed2b3c65f785471546383b9b8c7ddae48d1765e7aa39f3fb49`. Only archive and per-file hashes are public under `provenance/`; raw source/test bytes are held by the private verifier bundle referenced in `task.toml`.

## Tests and Closure

The selected upstream-compatible slice contains 2,891 JSON cases across drafts 04, 06, 07, and supported 2019-09 files. Eight task-local scenarios cover defaults, required errors, static references, generated source, one named callback recipe, and the package-root API surface, for a frozen denominator of 2,899. The no-network verifier installs the candidate's hash-locked build dependency closure during Docker build: pytest 8.3.5, iniconfig 2.3.0, packaging 26.3, and pluggy 1.6.0. The task does not vendor a wheelhouse.

## Separate Boundary and Risks

Trusted custom verification never imports the candidate. `candidate_rpc.py` runs as UID 10001, accepts bounded JSONL, imports candidate code only in that child, and returns normalized JSON. Remote handlers are an exact URI allowlist; arbitrary URI fetches and arbitrary callback transport are rejected. Generated code is compiled and executed in the child. A candidate timeout or child exit terminates further child interaction and records every remaining frozen leaf as failed, so a malicious hang remains bounded without changing the denominator.

The 860,160-byte verifier archive is `sha256:03355c1dca9c063d8e5b55be9dbeeb0dfdbac6d1f734f71dc91235c64fa70608`. The 10,240-byte Oracle archive is `sha256:21ac1473fd0093f61613e6d6f545beacc845c6fd779d692cc4d338a01bab7afd`. Its `solve.sh` fetches only the declared revision, checks the resolved commit, then verifies the declared source archive SHA-256 before materializing `/workspace`. Both are private artifacts under `.nl2repo/artifacts/` and are not public catalog inputs.

The isolated source baseline used Python 3.12.11 with pytest 8.3.5. Three runs using `pytest -q -c /dev/null` produced `4457 passed, 449 xfailed, 936 xpassed` from 5,842 collected tests in 50.57 s, 48.34 s, and 49.06 s. The repository-level pytest coverage configuration was disabled for this source probe because it targets this benchmark repository rather than the frozen upstream package. No Harbor Agent Run or model run is claimed by this authoring lane.
