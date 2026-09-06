# Artifact Path Remediation

The instruction-migration Oracle and controls completed against a deterministic
candidate bundle, but parent projection review rejected that bundle. Its npm
cache index contains an absolute authoring-worktree path in a pacote tarball
cache key. The package bytes and integrity field are frozen, but the cache
metadata would leak the authoring host path into `catalog/tasks`.

The checked-in projection was therefore not replaced. The tracked Oracle and
control summaries remain useful revalidation input, but they do not authorize a
current final manifest. The dependency cache must be normalized to a stable
task-relative key, registered as a new private artifact, and used to compile a
new manifest. Because artifact bytes and the final manifest will change, the
Oracle and complete control matrix must be rerun under NoNetwork.
