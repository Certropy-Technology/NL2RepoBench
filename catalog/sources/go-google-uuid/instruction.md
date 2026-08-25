# Build the serializable Parse API of google/uuid

Create a single Go module with module path `github.com/google/uuid` and a
public `UUID` type plus `Parse(value string) (UUID, error)`. Parse canonical
UUID text and return a value whose `String()` method emits lowercase canonical
form. The module must be pure Go, single-module, offline-buildable, and must
not use `replace`, cgo, plugins, workspaces, or external services.
