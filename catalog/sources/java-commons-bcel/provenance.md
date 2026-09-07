# Commons BCEL Provenance

## Frozen Source

- Repository: `https://github.com/apache/commons-bcel`
- Revision: `279ec2300c1d9757061454c200d5e19090bee39e`
- Frozen archive: `.nl2repo/authoring-inputs/java-maven-wave1/java-commons-bcel/source.tar`
- Archive SHA-256: `sha256:273653bda961ef41e1c0203480cf66edd88a0aa92e464fddebc4f9c15ef770e0`
- License: Apache-2.0
- License file SHA-256: `sha256:b1d2870f1a00e4d7f56576e5f0870cba109e041f8af66866cf5b499478e654e7`

The archive and revision were supplied by the parent source-freeze stage. It
was extracted and inspected without network access. The static inventory is
stored in task-local staging and is not public verifier code.

## Bounded Contract

The selected contract covers only the public `ByteSequence` type and its
standard-library stream behavior. It deliberately excludes the upstream
multi-module/test dependency graph. It has eight fixed verifier leaves and no
third-party runtime or verifier dependency.

## Offline Closure

The Maven lock uses an empty artifact list, a fixed Java 21 project, no
repositories, and a private empty Maven store. The offline store manifest was
validated against the current lock using `MavenPackageManager`.

## Integration State

Verifier, Oracle, lock/store/inventory, and all registration metadata are staged
under `.nl2repo/authoring-work/java-commons-bcel/`. Parent integration must
register these bytes in task-scoped CAS, populate formal refs, compile the
production runtime, and run Oracle/controls. No worker-side Oracle or controls
result is claimed.
