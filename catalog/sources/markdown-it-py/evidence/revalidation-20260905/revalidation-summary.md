# markdown-it-py revalidation

- Classification: fully revalidated in a fresh NoNetwork run.
- Queue/source instruction digest: `sha256:6e845c73d38a99145aff9c8e824d8d497c7307bd7206fac2164801f4433d85c3`.
- Frozen source archive: revision `bff75edcd7e6ce68f417803361d6e9f1223ad373`, digest `sha256:16144aa1aa730efe92e175a3677d0546f571049f612a20452f47136dead1f88c`.
- Oracle bundle: `sha256:df88ef6ebcffe7c8121fbbc2a23faf908f79481b30fdfda04eeb093988ce644f`, containing the exact `source.tar`; no runtime source fetch and no host authorization.
- Two production compiles were byte-identical. Canonical manifest: `sha256:6740a8dc9d6c7d496e7679e26647f2102d06f45fe752c69bece03bd6835e712a`.
- Fresh Oracle: valid, `24/24`, reward `1.0`; network probes were false.
- Fresh controls: `stub` collected `24`, passed `0`, reward `0.0`; `forgery` and `install-hang` completed as valid installation-failure controls with reward `0.0`; all network probes were false.
- All runs used Harbor `0.21.0`, Python `3.12.11`, and NoNetwork. Run artifacts remain in ignored roots represented by `<ignored-run-root>` and `<ignored-control-root>`; no receipts are claimed from prior runs.

The lifecycle, task metadata, generated projection, shared CAS, and production
evidence were not modified by this retry.
