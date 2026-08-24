# fastjsonschema Remediation Evidence

Status: `oracle-passed`; the generic private-bundle Oracle passed. Empty, stub,
forgery, timeout, and offline controls remain pending. This directory is the
only repository write root for this lane.

## Frozen Source

- Upstream: `https://github.com/horejsek/python-fastjsonschema`
- Revision: `b88fa37cd46bb81e8d9dce91a7e1bc4debedd3a2`
- Tree: `d5ffcff4278232a8097f3cb7feffc6b5f75b3db1`
- Version: `2.22.2`; license `BSD-3-Clause`.
- Source archive SHA-256: `c6d2c4ec7d81009b52c35430082ab13a29a32a92e323e64ffff1d6f304ca717d`.

The materialized `JSON-Schema-Test-Suite` submodule is revision `9fc880bfb6d8ccd093bc82431f17d13681ffae8e`, tree `66c7b275cfafa940e7dcd2213582778757241017`, archive SHA-256 `5b4c6e96e60a52ed2b3c65f785471546383b9b8c7ddae48d1765e7aa39f3fb49`. Only archive and per-file hashes are public under `provenance/`; raw source/test bytes are held by the private verifier bundle referenced in `task.toml`.

## Tests and Closure

The selected upstream-compatible slice contains 2,891 JSON cases across drafts 04, 06, 07, and supported 2019-09 files. Seven task-local scenarios cover defaults, required errors, static references, generated source, and one named callback recipe, for a frozen denominator of 2,898. The no-network verifier installs only local hash-locked wheels: pytest 8.3.5, iniconfig 2.3.0, packaging 26.3, and pluggy 1.6.0.

## Separate Boundary and Risks

Trusted custom verification never imports the candidate. `candidate_rpc.py` runs as UID 10001, accepts bounded JSONL, imports candidate code only in that child, and returns normalized JSON. Remote handlers are an exact URI allowlist; arbitrary URI fetches and arbitrary callback transport are rejected. Generated code is compiled and executed in the child. Generic compiled Oracle evidence is `.nl2repo/runs/oracle/fastjsonschema-custom-compiled-v11/2026-08-24__08-28-35/fastjsonschema__bsjTpPM/verifier/grading.json` with `2898/2898` and reward `1.0`. No model run is claimed by this authoring lane.
