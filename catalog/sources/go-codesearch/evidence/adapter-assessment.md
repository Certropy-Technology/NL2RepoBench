# Separate-verifier assessment

The repository is not limited to deterministic scalar library calls. `index`
reads and writes on-disk index files, `cindex` walks arbitrary filesystem
trees and optionally ZIP files, `csearch` opens indexed source files, and
`csweb` serves an HTTP endpoint and reads external paths. The index reader uses
platform-specific mmap implementations, including unsafe Windows code. A
bounded child-side adapter could cover a deliberately narrow package subset,
but that scope is not yet approved and the previous patch's private verifier,
Oracle, and module artifacts are unavailable.

This is a verifier blocker. No Oracle, controls, reward, or generated runtime
is claimed.
