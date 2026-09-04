# Adapter assessment

The public package is not a simple scalar or JSON library. Its primary API
contract is `interface{}` plus reflection: callers supply arbitrary slices,
maps, structs, pointers, functions, predicates, reducers, join callbacks, and
`reflect.Value` values. `Chain` and `LazyChain` retain mutable state across a
sequence of operations; `Set` mutates nested values by a string path and has
distinct panic/error behavior.

The current Go lane requires a separate verifier and a bounded child-side
protocol. JSON can represent only a restricted value subset and cannot carry a
Go callback closure, preserve dynamic type identity, model pointer aliasing,
or reproduce arbitrary reflection and mutation semantics. A faithful adapter
would be a new task-specific language and object runtime rather than a bridge
to the frozen public API. No such adapter is approved or present.

The dependency probe also demonstrates that the complete offline closure is
not available: `github.com/stretchr/testify@v1.4.0` cannot be looked up with
`GOPROXY=off` and an empty `GOMODCACHE`.

Conclusion: blocked under the current production contract; do not generate a
Harbor projection or fabricate Oracle/controls evidence.
