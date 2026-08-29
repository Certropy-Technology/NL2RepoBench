# Authoring Provenance

- Package: `jiter`, upstream `https://github.com/pydantic/jiter`.
- Frozen revision: `0fc3c06b4555bb814d3c44ba08d715d9d064da3d`.
- `git archive --format=tar` digest: `sha256:093d45e8a53c7d8be9472abbc0e6ff822b9d6987ce17a61bcb75092a11b01693`.
- `LICENSE` digest: `sha256:7c7134b9f7b978c03fca875517cf398db91f19bbb8109b6685e742aa3f57468e`.
- Upstream package metadata identifies MIT licensing and the Python module
  `jiter`; the public stub is `crates/jiter-python/jiter.pyi`.
- The upstream distribution is a Rust/PyO3 extension. This task explicitly
  adapts the JSON-safe public API to a pure-Python implementation so the
  candidate can install and execute under the no-network, bounded verifier.
- The private verifier and Oracle archive are content-addressed artifacts and
  are not copied into the public source tree.
- The private verifier entrypoint explicitly adds its own directory to
  `sys.path` because Harbor launches it with `python -I`; the corrected bundle
  is `sha256:73818aeb5481e0001983de93771711e142cf2c3007e0d44f4e64dbdd6321ae77`.
- Authoring workspace: `.nl2repo/authoring-work/python-author-wave2-20260828/jiter`;
  the upstream checkout is used only to create the digest-checked Oracle
  archive and is not part of the candidate workspace.
