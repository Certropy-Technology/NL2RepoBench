# Commons Imaging Provenance

- upstream URL: `https://github.com/apache/commons-imaging`
- immutable revision: `99ac2f89ff2ce84a21b198cc06785a020e856156`
- frozen source archive: `.nl2repo/authoring-inputs/java-maven-wave1/java-commons-imaging/source.tar`
- source archive SHA-256: `a89b7e7a4b9066e98dea66e8e8e73c128d542979b2a254382564495343eb58c5`
- license: Apache-2.0, from upstream `LICENSE.txt` and `NOTICE.txt`
- runtime: Temurin JDK `21.0.12+8`, Maven `3.9.11`, Linux `amd64`
- network: authoring source was pre-frozen; all candidate, verifier, Oracle, and control runs are `no-network`
- bounded contract: `org.apache.commons.imaging.PixelDensity`
- contract leaf count: `10`
- dependency closure: empty runtime Maven repository, private refs are shared with the validated Java empty closure
- private verifier digest: task-local staging; parent CAS registration pending
- private Oracle digest: task-local staging; parent CAS registration pending

The task-local staging handoff was compiled with `javac --release 21` and the
shell scripts passed `bash -n`. The source validator also passed. The staged
empty closure is built from `maven-lock-v1.json` with zero artifacts and an
empty `maven-repository`; it is not a placeholder for an unresolved upstream
test dependency.

The worker handoff intentionally does not write shared CAS or formal artifact
references. See `.nl2repo/authoring-work/java-commons-imaging/staging-refs.json`
for the parent registration manifest.

The full upstream project contains image codecs, resources, tests, and build
plugins. They are not owned by this task. Only the self-contained PixelDensity
public API is exposed through the verifier contract.
