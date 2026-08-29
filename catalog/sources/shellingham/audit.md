# shellingham authoring audit

## Frozen source

- Upstream: `https://github.com/sarugaku/shellingham`
- Revision: `926401c4543b84f9f579932d30fb52a104639398`
- Git tree: `77409035ad67ab9aca0d5e4563b7aaf6be96cbcb`
- License: ISC, from the frozen `LICENSE` file
- Raw `git archive --format=tar` digest: `sha256:b936de13a28f170163f749e81556a65834f630af7e7f08914749c5c64fff728b`
- The source contract and Oracle both use the raw `git archive --format=tar` bytes: `sha256:b936de13a28f170163f749e81556a65834f630af7e7f08914749c5c64fff728b`.
- A prefixed archive was also measured during the probe (`sha256:809a70eeb69cea0c806f988509ac114e97c72b8d8dfb76b6bccfd417db68ac5e`) but is not used as authority because its bytes differ.

The source contains seven runtime modules and one upstream test file. It is pure
Python and has no runtime dependency. Its build metadata uses setuptools and
wheel, which are installed only during image construction from the private hash
lock.

## Verifier scope

The production verifier has 24 fixed custom-json-v1 leaves. It calls candidate
code only in a UID-isolated child process, with controlled process records and
filesystem fixtures. The contract covers public metadata and exception identity,
POSIX shell classification, bounded parent traversal, `/proc` parsing, and the
`ps` fallback. The current machine's process tree is never used as a score input.

The Windows ctypes implementation and real host process discovery are outside
the Linux deterministic adaptation. They are recorded as exclusions rather than
silently treated as tested behavior.

## Network and artifact policy

Agent and verifier phases use `no-network`; the agent has no static allowed hosts.
The Oracle-only solve script fetches the exact revision, asserts the resolved
commit, creates a raw git archive, verifies its SHA-256, and extracts it into
`/workspace`. Private verifier and dependency lock bytes are content-addressed
under the task-local artifact store and are not included in the agent image.
