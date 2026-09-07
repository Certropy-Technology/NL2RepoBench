# Commons Exec Provenance

- upstream: `https://github.com/apache/commons-exec`
- revision: `72e67549226fbf7a93b04241c6a64f3dd61a8388`
- frozen input: `.nl2repo/authoring-inputs/java-maven-wave1/java-commons-exec/source.tar`
- frozen archive SHA-256: `sha256:ab9cc9498250b470b22531751e120f7db9598737e21d70be5bd38aed7be59ba8`
- license: `Apache-2.0`
- `LICENSE.txt` SHA-256: `sha256:b1d2870f1a00e4d7f56576e5f0870cba109e041f8af66866cf5b499478e654e7`
- `NOTICE.txt` SHA-256: `sha256:ac502939768f44417889f0f7bf0f096b8a2fa859524f635035c621623871651d`
- source inventory digest: `sha256:55bcf233eb7df8ca398c3011c56e2cc7966047e9c423c25392e2400736dc648a`

The discovery record supplies the immutable revision. The staged archive is a
source tar and intentionally does not contain a `.git` directory; archive and
license bytes are therefore recorded explicitly rather than claiming a local
Git checkout assertion.

## Current bounded contract

The public contract is limited to `org.apache.commons.exec.CommandLine` and
`org.apache.commons.exec.util.StringUtils`: quote-aware command parsing and
construction, argument rendering, separator normalization, splitting/joining,
and map-based substitution. Process execution, environment discovery,
watchdogs, native launchers, and upstream test-only dependencies are excluded.

The separate verifier has 10 fixed leaves and compiles with
`javac --release 21` using only the JDK. The Maven closure is intentionally
empty and is represented by the task-local lock/store/inventory artifacts.

Task-local registration manifest:
`.nl2repo/authoring-work/java-commons-exec/staging-refs.json`.
Parent integration must register these bytes in the private CAS before adding
formal refs to `task.toml` or generating a runtime.

## Authoring commands

```text
sha256sum .nl2repo/authoring-inputs/java-maven-wave1/java-commons-exec/source.tar
tar -xf .../source.tar (task-local staging only)
uv run python -c 'from nl2repobench.authoring.inventory import scan_java_source'
javac --release 21 -d /tmp/java-exec-harness-compile <bounded source and harness files>
bash -n catalog/sources/java-commons-exec/harbor/{solution/solve.sh,tests/test.sh,controls/*.sh}
uv run nl2repo task validate-source catalog/sources/java-commons-exec
git diff --check
```

The archive verification exited 0 with digest
`sha256:ab9cc9498250b470b22531751e120f7db9598737e21d70be5bd38aed7be59ba8`.
The bounded source and separate harness compilation exited 0. No network was
used during this remediation pass. No Oracle, controls, generated runtime, or
production gate result is claimed until parent integration registers the
staged private bytes.
