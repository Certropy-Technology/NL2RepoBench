# `mime` replacement Oracle proposal

## Current finding

The queue source digest is
`sha256:2538fa5b2bbd69faeb9bd87058227df1c1fc9205d9cef1d57b73201fc488f0e7`.
`uv run nl2repo task validate-source catalog/sources/mime` passes. The existing
private Oracle bundle and checked-in generated projection both contain the exact
frozen source archive for revision
`f2d1243892616c0ec1031eb5132d56e43159ecc0`:

- size: `266240` bytes
- SHA-256: `sha256:8f8e826ccafe064ca20139c47422291210c5bf8998fbe32f9ef3d9706d589199`

The existing `solve.sh` nevertheless performs a runtime request to GitHub before
copying this already verified local archive. That is incompatible with the
current mandatory `no-network` policy, so the historical receipts are not current
receipts for this revalidation.

## Proposed replacement

An ignored replacement bundle was constructed at the temporary relative path
`.nl2repo/mime-replacement-oracle/mime-oracle-no-network.tar` (absolute worker
path is available in the handoff, but is intentionally not recorded here). Its
outer bytes are:

- size: `399360` bytes
- SHA-256: `sha256:336fe8c2758d3972bfa04adf472eb87cbab134bf81c948d900fce75808c541e5`

The only semantic change to `solve.sh` is removal of the Node HTTPS reachability
probe and its unused URL/revision variables. The replacement retains the source
archive SHA-256 assertion, copies `oracle-source.tar` to the working location,
clears `/workspace`, and copies the local Oracle package. The source archive and
all Oracle package bytes are unchanged from the exact existing private CAS
bundle. Parent registration and independent diff/provenance review are required;
this proposal does not alter `task.toml`, lifecycle, CAS, generated projection,
or production evidence.

The replacement inner file inventory was checked. In particular:

| file | size | SHA-256 |
| --- | ---: | --- |
| `solve.sh` | 486 | `sha256:fcf616e084ab54caef59852edaa587be48bab140b5dd391562d56d651f96ff3c` |
| `oracle-source.tar` | 266240 | `sha256:8f8e826ccafe064ca20139c47422291210c5bf8998fbe32f9ef3d9706d589199` |
| `oracle-package/package.json` | 507 | `sha256:bc34aaac9224cf13225fc2ac9b6aca0bc9d190e86e17a94ab0d3aaf6afad0001` |
| `oracle-package/dist/src/Mime.js` | 4056 | `sha256:6c2e15ba264cb9722c73f22db9248f5c631f5c0ce15006f7c07880dfdf567e3d` |
| `oracle-package/dist/src/index.js` | 231 | `sha256:f0ee0d51fc31f54a6cb55fdc2c4b88b5feeb0f8b6b2b51e0c9a64fe76b284784` |
| `oracle-package/dist/src/index_lite.js` | 175 | `sha256:bea773ec620e8408ef93aca09b7b88b97790a12215498d5e8c86509a5f7a8d08` |
| `oracle-package/dist/src/mime_cli.js` | 2065 | `sha256:d3e19f02c6d0d302f9a32bef66f56ecef33bc76d3a8226313c51725544526995` |

## Offline smoke

With the pinned Node base image and Docker `--network none`, the replacement:

1. verified the frozen source archive hash;
2. installed the local Oracle package using `npm ci --offline --ignore-scripts
   --no-audit --no-fund`; and
3. successfully checked `getType("txt") === "text/plain"` and
   `getExtension("text/html") === "html"`.

The previous first smoke attempt had a shell quoting typo in the test expression;
it was corrected and the bounded rerun exited `0`. No lifecycle or production
evidence change was made, and the full Harbor Oracle/control matrix remains
pending parent CAS registration.
