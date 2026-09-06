# Revalidation blocker

Task `idna` remains at its existing `controls-passed` lifecycle state. This
revalidation does not replace the prior production evidence because the current
Oracle payload is not usable under the required NoNetwork policy.

## Frozen input

- Queue source digest: `sha256:77f31395c0968d86e6470daa7f444772b7dbb868ab135e5058997b7cc7c100c5`
- Validated source digest: `sha256:77f31395c0968d86e6470daa7f444772b7dbb868ab135e5058997b7cc7c100c5`
- Frozen upstream revision: `e2073db14d28d1c3299649dd0c2dd4205b43ebfd`
- Frozen source archive: `sha256:9f05c7eabad5785cddefcb84a85230194b42dccb20b349027135854db25161f8`
- Existing runtime solution has no source archive and is not modified by this worker.

## Artifact checks

The dependency lock, verifier bundle, and Oracle bundle are present in the
parent private CAS and their declared sizes and SHA-256 values match. The
bounded details are in
`artifact-check.json`. The Oracle archive contains only `solve.sh`; it does not
contain a source payload.

## Blocker

`solve.sh` performs `git clone --no-checkout https://github.com/kjd/idna` at
runtime, then creates the frozen archive. This violates the revalidation
NoNetwork contract, which forbids source-host, DNS, registry, and external
service authorization for Agent, candidate, verifier, Oracle, and controls.
The complete inspection is in `oracle-inspection.json`.

## Local recovery attempts

The worker searched the current generated runtime, task-local source/evidence,
the retained authoring claim and exact historical work paths, retained handoff
and patch indexes, local uv package caches, and local uv Git caches. The uv
cache has idna 3.19 installed wheel trees, but no immutable Git revision proof
or exact frozen archive. No replacement bundle was created. Details and the
next unblock action are in `local-recovery-search.json`.

## Commands and results

- `uv run nl2repo task validate-source catalog/sources/idna`: exit `0`; the
  result is bound to the queue digest in `artifact-check.json`.
- `sha256sum` over all three declared private artifacts: exit `0`; all values
  match `artifact-check.json`.
- `tar -tvf` over the verifier and Oracle bundles: exit `0`; the Oracle
  inventory is bound in `oracle-inspection.json`.
- Bounded local recovery searches: exit `0` where results were obtained;
  broad historical-tree probes that exceeded their bounded timeout were not
  treated as recovery evidence. The narrowed searches are recorded in
  `local-recovery-search.json`.

## Next unblock action

Recover the exact source archive from a trusted retained source, or reproduce
it from a local Git object store that proves the frozen revision and archive
digest. Then the parent must register an offline Oracle bundle, update the
private artifact binding, compile twice, and rerun Oracle plus the complete
supported control matrix. No compile, Harbor run, replacement registration,
projection update, or receipt reuse is claimed by this revalidation.
