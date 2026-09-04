# Build the cleanhttp Go module

## Project Description

Create the pure-Go module `github.com/hashicorp/go-cleanhttp` at repository
root. It provides independent `net/http` clients and transports, plus a
middleware handler that rejects request paths containing non-printable runes.

## Supports

- Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, and one root `go.mod` whose
  module path is `github.com/hashicorp/go-cleanhttp`.
- Offline builds with `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
  `GOTOOLCHAIN=local`, and `-mod=vendor`. Include `go.sum` and a valid vendor
  directory even though this module has no external dependencies.
- Pure Go only. Do not use cgo, plugins, `unsafe`, generated code, external
  services, or global mutable state to answer bridge requests.
- The evaluator calls a child-side JSON bridge with one request per line. It
  uses bounded strings and integers. Return structured errors for malformed
  or unknown requests and do not write diagnostics to stdout.

## API Usage Guide

Import the package as `github.com/hashicorp/go-cleanhttp`.

```go
func DefaultTransport() *http.Transport
func DefaultPooledTransport() *http.Transport
func DefaultClient() *http.Client
func DefaultPooledClient() *http.Client

type HandlerInput struct {
    ErrStatus int
}

func PrintablePathCheckHandler(next http.Handler, input *HandlerInput) http.Handler
```

`DefaultPooledTransport` returns a fresh transport configured for reusable
clients. Its proxy function is `http.ProxyFromEnvironment`. It uses a
30-second dial timeout and keepalive, 100 maximum idle connections, a
90-second idle-connection timeout, a 10-second TLS handshake timeout, a
one-second `Expect: 100-continue` timeout, HTTP/2 attempts enabled, and
`runtime.GOMAXPROCS(0) + 1` maximum idle connections per host.

`DefaultTransport` returns a separate fresh transport with the same pooled
defaults except that it disables keepalives and sets
`MaxIdleConnsPerHost` to `-1`. Changing a transport returned by either
function must not affect a later call.

`DefaultClient` returns a new `http.Client` whose transport has the
non-pooled settings. `DefaultPooledClient` returns a new client whose
transport has the pooled settings. Neither client shares its transport with a
previous call or with `http.DefaultClient`.

`PrintablePathCheckHandler` returns middleware. It invokes `next` only when
the request is non-nil and `r.URL.Path` consists entirely of Unicode printable
runes. When the path contains a non-printable rune, it writes an error status
and does not invoke `next`. A nil `input`, or an input whose `ErrStatus` is
zero, uses `http.StatusBadRequest`; any other `ErrStatus` is written as-is.
For a nil request the returned handler does not invoke `next` or write a
response.

## Implementation Notes

Use the standard library's `net/http`, `net`, `runtime`, `time`, `strings`,
and `unicode` packages. Preserve the public signatures and package name.
The transport constructors return concrete, mutable `*http.Transport` values,
not `http.DefaultTransport` or a wrapper around it.

The bridge exercises transport fields, client-owned transports, and handler
status/forwarding behavior. It does not make HTTP requests, inspect network
reachability, or depend on environment proxy values. Do not hard-code bridge
fixtures or write verifier-owned reports or rewards from candidate code.
