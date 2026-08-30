# Authoring Audit

- Source acquisition resolved the claimed full revision and verified its tree,
  tag, absence of submodules, archive byte count, and SHA-256 digest.
- The missing generated license file and detached-tree SCM version are handled
  explicitly: Oracle verifies the original archive, restores it, writes the
  canonical MIT text locally, and verifier builds set the exact version through
  `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_ZIPP=4.1.0`.
- Build dependencies are exact-pinned and hash-locked for online Docker build
  installation. No wheelhouse or package-under-test bytes are vendored.
- Agent and verifier execution are no-network. `agent_allowed_hosts` is empty;
  only an Oracle run may receive the exact `github.com` source-host override.
- The separate verifier owns all reports and invokes candidate behavior only in
  an unprivileged bounded subprocess.
- No Harbor model Agent Run is part of this lane.
