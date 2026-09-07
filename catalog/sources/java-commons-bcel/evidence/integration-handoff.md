# Integration Handoff

Status: `awaiting-integrator`

## Inputs

- Repository: `https://github.com/apache/commons-bcel`
- Revision: `279ec2300c1d9757061454c200d5e19090bee39e`
- Source archive: `.nl2repo/authoring-inputs/java-maven-wave1/java-commons-bcel/source.tar`
- Source archive SHA-256: `sha256:273653bda961ef41e1c0203480cf66edd88a0aa92e464fddebc4f9c15ef770e0`
- Runtime: Temurin `21.0.12+8`, Maven `3.9.11`, Linux `amd64`, glibc
- Toolchain digest: parent lock digest recorded in `staging-refs.json`
- Harbor execution: agent/candidate/verifier/Oracle/controls `no-network`

## Selected Contract

The task verifies the bounded public `org.apache.bcel.util.ByteSequence` API:
constructor, cursor index, signed/unsigned reads, big-endian multi-byte reads,
full reads, and EOF behavior. The verifier has eight fixed leaf IDs and uses
only JDK classes plus the candidate JVM process protocol.

## Task-local Staging

All bytes are under `.nl2repo/authoring-work/java-commons-bcel/`:

- `java-inventory.json`
- `dependency-inputs/maven-lock-v1.json`
- `dependency-inputs/lock-archive.tar`
- `dependency-inputs/offline-store.tar`
- `dependency-inputs/maven-store.manifest.json`
- `dependency-inputs/dependency-inventory.json`
- `harness/`
- `verifier.tar`
- `oracle/solve.sh`
- `oracle.tar`
- `staging-refs.json`

`staging-refs.json` is the parent registration manifest. Each digest, size,
media type, and URI is computed from the corresponding local bytes. The worker
did not write shared `.nl2repo/artifacts`, `catalog/tasks`, or any shared code.

## Required Parent Steps

1. Register lock archive, offline store archive, dependency inventory, verifier
   archive, and Oracle archive in the task-scoped private CAS in the order shown
   by `staging-refs.json`.
2. Recompute and compare every returned digest and size before writing formal
   private refs to `task.toml`.
3. Set `[dependencies].status = "known"` with package manager `maven`, and add
   the three registered dependency refs. Set the verifier contract digest and
   bundle ref, plus `oracle_bundle`.
4. Compile without `--allow-incomplete` using the current Java compiler.
5. Build the separate verifier image and run Maven offline smoke, Oracle once,
   and empty/stub/forgery/hang/install-failure/offline controls.
6. Rotate canonical production evidence only after all receipts bind the new
   generated bundle digest.

No Oracle, controls, reward, or production-valid claim is made by this worker.
