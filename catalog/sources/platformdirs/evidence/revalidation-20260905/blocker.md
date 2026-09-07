# platformdirs revalidation blocker

The instruction-migration source digest was validated before mutation:
`sha256:0b72fb7537d6acc5bf6e3b8f3df3db2e89946eb8f0a24e298c3e6e06faa42bb5`.

This revalidation is classified **artifact-or-verifier-blocked**. The declared
private Oracle bundle (`sha256:35c3c271c7bf483eb3f3c2c86c4b50d821b9215ea0f2dfeccab3aef86f953654`,
10,240 bytes) and separate verifier bundle
(`sha256:550041dc83296bd96733103e086fc7bb0e8ca8e83bcab9a869144e51818fddcc`,
20,480 bytes) were absent from the local CAS. The compiler consequently failed
closed before creating a candidate/verifier run. The available candidate lock
was verified exactly as 204 bytes with SHA-256
`24713a5496e38f6da905cbc7944c15efd8863916e5da6825b835f66aa99068f7`.

Bounded local recovery searched current task evidence, the generated
`catalog/tasks/platformdirs` projection, the local private CAS, and historical
authoring worktrees/handoffs. No exact missing private payload was recovered.
No replacement payload or private bytes were added. Oracle, empty, stub,
forgery, and offline gates were not run; no fresh receipt is claimed and no
external host was authorized.

Remediation: recover both exact private bundles from a trusted local source,
verify their declared sizes and SHA-256, then perform two locked compiles and a
fresh Harbor 0.21.0 complete NoNetwork matrix. Preserve the current source,
lifecycle, historical production evidence, and generated projection until that
parent-owned recovery succeeds.
