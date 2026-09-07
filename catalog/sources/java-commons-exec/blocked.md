# Superseded Authoring Blocker

The previous missing-CAS blocker is superseded by the current task-local
handoff. The bounded `CommandLine` and `StringUtils` contract now has a
standard-library-only verifier, a positive frozen denominator of 10, an empty
Maven closure, and a task-local Oracle bundle.

The task remains `inventoried` and `awaiting-integrator`: the parent must
register the staged private bytes in `.nl2repo/artifacts`, write the formal
artifact references, compile `catalog/tasks/java-commons-exec`, and run the
Oracle and controls matrix. No production-valid or gate-passed result is
claimed in this worker handoff.

## Task-Local Handoff

All paths below are relative to `.nl2repo/authoring-work/java-commons-exec/`:

```text
source-freeze.json
java-inventory.json
dependency-inputs/maven-lock-v1.json
dependency-inputs/lock.tar
dependency-inputs/offline-store.tar
dependency-inputs/inventory.json
verifier.tar
oracle.tar
staging-refs.json
```

The empty closure is intentional: the selected verifier and bounded source
slice import only JDK classes. The source revision, license bytes, inventory,
contract, archive sizes, and SHA-256 values are recorded in the corresponding
freeze and staging manifests.
