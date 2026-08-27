# Source and Contract Provenance

## Freeze

- Upstream: `https://github.com/EndlessCheng/codeforces-go`
- Revision: `4996b3d7733aabafe25ba045bbc87f794d963ac4`
- Archive SHA-256: `4430dd7dc9bdddc82768874bc08ecfe694234af0367f7422c612e78ddd566563`
- License: MIT (`LICENSE`, copyright notice for 2019 Sigma ndless)
- Source component: `copypasta/bitset.go`, package `copypasta`

The full upstream `copypasta` package does not compile at the frozen revision:
`go test ./copypasta` fails because unrelated `copypasta/bits.go` references an
unimported `binary` identifier. This task copies only the exported,
standard-library-only `Bitset` component, which is independently compilable.
The adaptation does not weaken that component's contract or claim that the full
upstream package test suite passes.

## API Inventory

The source file exports `NewBitset`, `Bitset`, and the methods documented in
`instruction.md`. Its receiver is the slice type itself, so all mutating
operations have value receivers but modify shared storage. The implementation
uses `uint` machine words and `math/bits`; the task fixes Linux/amd64 so word
width is 64.

Out of scope: the unexported string matching helper in the same source file,
all other `copypasta` helpers, contest programs, and external module
dependencies declared by the repository root.

## Hidden Contract Mapping

| Contract group | Public specification | Source behavior |
| --- | --- | --- |
| Point mutation | `Has`, `Set`, `Reset`, `Flip` | Direct word-bit operations |
| Search and summaries | `Index*`, `Next*`, `LastIndex1`, counts, string, indexes | `math/bits` scans and word-order traversal |
| Half-open ranges | `SetRange`, `ResetRange`, `FlipRange`, `ResetFrom` | Boundary masks and whole-word loops |
| Word shifts and arithmetic | `Lsh`, `Rsh`, `Add`, `Sub` | Fixed-storage shifts, carry, and borrow semantics |
| Relations | `Or`, `And`, `Xor`, `Equals`, `HasSubset` | Equal-length wordwise mutation/comparison |
| Transport bounds | Bridge input rules | Task-specific deterministic safety adapter, not an upstream API claim |

The private contract exercises every specified group through the public bridge.
It does not inspect private fields, import candidate code in the trusted
verifier, or require behavior not stated in `instruction.md`.
