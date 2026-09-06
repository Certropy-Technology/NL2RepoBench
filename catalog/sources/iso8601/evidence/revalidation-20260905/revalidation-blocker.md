# iso8601 instruction revalidation blocker

- Task: `iso8601`, version `0.1.1`
- Queue source digest: `sha256:88a3765b6b36b0c76caab4fa5b502cd39cf73804714ab84db44d13779714f8e3`
- Queue instruction digest: `sha256:1b4d2afd14e3ff3efb078e81cb8cce9b1d61ba642f8374de640ea01b0ad63eaa`
- Frozen upstream revision: `00c9262b9ad141f287b3263be7f2244fa01988c2`
- Frozen source archive: `sha256:6253d109a195cd118c204e64b513b14d8d07e0293c6089bf1dd1167cc2e2a97f`
- Failure class: `artifact-or-verifier`
- Network policy: `no-network`; no source-host, registry, DNS, or external-service authorization was used.

## Validation before changes

`uv run nl2repo task validate-source catalog/sources/iso8601` exited `0` and returned the queue source digest. The instruction SHA-256 matched the queue digest. The task-local source files, inventory, verifier/control scripts, and prior production evidence were read before this evidence was added.

## Artifact checks

The dependency lock, verifier bundle, and Oracle outer bundle were each found in the parent CAS and matched their declared sizes and SHA-256 values. The Oracle bundle contains only `solve.sh`; it does not contain `source.tar`, `oracle-package/`, or another source payload. Its script runs `git fetch` from `https://github.com/micktwomey/pyiso8601` for the pinned revision and then checks the declared archive digest. This cannot run under the required no-egress Oracle policy.

Detailed artifact results are in `artifact-check.json`.

## Local recovery

The bounded recovery search checked the generated runtime, task-local evidence, historical authoring handoffs/archives/retained runs, worker artifacts, Git objects, and local uv cache. No exact byte sequence with the frozen archive SHA-256 was found. The uv cache contains an installed/wheel form of `iso8601` 2.1.0, not the required unprefixed git archive, so it is not an acceptable replacement.

Detailed search results are in `local-recovery-search.json`.

## Revalidation result

No compile or Harbor run was started because the current Oracle requires prohibited runtime source fetch and no exact local source payload is available. No replacement bundle was constructed. The prior `production-evidence.json` and `[lifecycle]` status were preserved because their receipts are stale after instruction migration and no current-manifest receipts can be truthfully claimed.

## Next step

The parent must register a private Oracle bundle containing the exact frozen source archive, replace the runtime-fetching Oracle script, compile twice with the parent CAS and locked toolchain, and run the current-manifest Oracle plus empty, stub, forgery, and offline controls. Only then may current production evidence and the generated projection be replaced.
