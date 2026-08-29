# huggingface_hub authoring audit

## Frozen source

- Upstream: `https://github.com/huggingface/huggingface_hub`
- Revision: `c6be77fb44d91f474da963e5ad6fce4801811027`
- Package version at the revision: `1.29.0.dev0`
- License: Apache-2.0; upstream `LICENSE` SHA-256
  `sha256:c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`
- Reproducible unprefixed `git archive --format=tar` SHA-256:
  `sha256:64d379d7374b8afb92dbade7829d328982633d137941ea0aa088d17582e6294d`
- Detached checkout and source probes live under
  `.nl2repo/authoring-work/python-author-wave2-20260828/huggingface-hub/upstream`.

## Inventory and adaptation

The frozen tree contains 183 implementation Python files and 82 Python test
files. Static AST inventory found 1,503 public definitions across 170 modules.
The upstream suite includes live Hub/HTTP, credential, OAuth, CLI, Xet/native,
optional dependency, Windows, and service integration behavior. A direct
collection probe of the selected deterministic modules collected 118 nodes but
failed collection for missing development-only `jedi` and `pytest-mock`.

The production denominator is a newly authored 40-leaf custom-json-v1 contract
for offline local behavior: exports, URL and header construction, validation,
URI parsing, metadata records, commit records, date parsing, object filtering,
cache path naming, API configuration, and filesystem initialization. It does not
copy upstream tests or reference source into public catalog files.

## Environment remediation

The task uses the digest-pinned CPython 3.12.14 slim-bookworm image already used
by production Python lanes. Candidate and verifier dependencies are installed
at build time from a private `--require-hashes` lock. The agent and verifier
are `no-network`; only the private Oracle bundle contains the frozen source.

## Status

Source, verifier, controls, and Oracle bundle are task-local. Harbor Oracle,
Agent, and control jobs are not started here because this lane is prohibited
from starting a Harbor Agent Run. The handoff reports only commands actually
executed in this worktree.
