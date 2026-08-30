# `urllib3` Authoring Audit

## Frozen source

- Upstream: `https://github.com/urllib3/urllib3`
- Revision: `85a8a9cfad3398bc504d088233d0a11af219a82a`
- Exact `git archive --format=tar HEAD` SHA-256:
  `sha256:3a5d7d03213b00b8e8f18be2df77b38bc55829380ffe91302c0cca6821e186c0`
- License: MIT, `LICENSE.txt` SHA-256
  `sha256:130e3a64d5fdd5d096a752694634a7d9df284469de86e5732100268041e3d686`
- The frozen tree has 176 tracked files, 35 Python source modules, about 12,197
  source lines, and no submodules or native extension.

## Behavior boundary

The upstream suite collected 2,627 tests with the declared Python 3.12.14
environment. A network-isolated run reached 2,252 passed, 326 skipped, and 46
TLS/proxy integration failures. The failures are limited to dummy-server,
certificate, pyOpenSSL, and HTTP/2 transport cases whose external/native
behavior is outside this task. The scored contract is 32 deterministic JSON
leaves for local URL, header, multipart, retry, timeout, response, exception,
and export behavior.

## Packaging remediation

This revision uses `hatch-vcs`/`setuptools-scm` and generates
`src/urllib3/_version.py`. A candidate workspace does not contain `.git`, and
the generated file must be written into a writable build source. The task
therefore pins the exact SCM build closure and injects
`SETUPTOOLS_SCM_PRETEND_VERSION_FOR_URLLIB3=2.7.1.dev42` into the verifier.
The verifier first copies the Harbor workspace to its writable staging tree;
the existing bounded candidate installer then runs `pip install --target` with
no dependencies and no runtime network access.

## Security boundary

The private verifier bundle uses `custom-json-v1` and calls the candidate only
through the UID-10001 `candidate_client`. Hidden expectations remain in the
root-owned verifier process. Agent and verifier policies are `no-network` with
empty static host lists. The Oracle bundle contains only the digest-verified
source archive, a fixed generated version file, and `solve.sh`.
