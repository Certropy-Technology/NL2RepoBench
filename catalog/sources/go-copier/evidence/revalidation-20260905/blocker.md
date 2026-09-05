# Revalidation blocker

The current 517-byte Oracle bundle contains only `solve.sh`. Its script performs a
runtime `git clone` from `github.com/jinzhu/copier`, which is forbidden for the
NoNetwork Oracle and controls.

The three declared private CAS objects were independently verified by size and
SHA-256. Local recovery searched the task CAS, the go-copier archive receipt and
authoring state, the supervisor compile area, and historical Go worktrees. The
only source-like bytes found were a vendored `github.com/jinzhu/copier v0.4.0`
snapshot from go-yq. The frozen source is revision
`c6b47b092d9840406d0abc347e68a28a7b812643`, pseudo-version
`v0.4.1-0.20260314121710-c6b47b092d98`, and archive digest
`sha256:11b05c7a410dc39fd2cbcfb0f6cb307c1a694d3c33fff7a422109921f704cf18`.
The v0.4.0 material cannot be used as a replacement without an exact archive
digest match, so no replacement bundle was created and no source host was
authorized.

Two fresh production compiles completed successfully and were byte-identical.
The source lifecycle, historical production evidence, denominator, and generated
projection remain unchanged. Parent may resolve this blocker by registering a
private Oracle payload containing the exact frozen source archive and a solve
script that verifies its revision and archive digest before copying the source.
