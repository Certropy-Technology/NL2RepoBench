# echoip: blocked authoring record

## Project Description

`echoip` is a Go HTTP service that reports the request IP and optional MaxMind
country, city, and ASN metadata. It also provides JSON, health, port-probe,
cache-debug, template, reverse-DNS, and command-line-client routes.

## Supports

The frozen revision exposes pure helpers in `iputil` and `useragent`, but a
production task would need to cover the HTTP server and its route behavior.
The service reads MaxMind database files, may perform reverse DNS and TCP
connectivity checks, parses trusted proxy headers, renders templates, and can
enable profiling handlers.

## API Usage Guide

The relevant public Go symbols are `iputil.ToDecimal(net.IP) *big.Int`,
`iputil.LookupAddr(net.IP) (string, error)`,
`iputil.LookupPort(net.IP, uint64) error`, and
`useragent.Parse(string) UserAgent`. The HTTP package additionally exposes
`http.New(geo.Reader, *http.Cache, bool) *http.Server` and
`(*http.Server).Handler() net/http.Handler`, whose behavior depends on a
database implementation and injected lookup callbacks.

## Implementation Notes

This candidate remains blocked. The required Go module closure was not
available in the no-network probe: `github.com/oschwald/geoip2-golang` and
its transitive modules were absent from an empty module cache. A faithful
separate verifier would also need deterministic MaxMind database fixtures,
HTTP request/response assertions, reverse-DNS and port-probe doubles, template
assets, and bounded profiling behavior. No reviewed child-side adapter exists
for those host and network boundaries. The dependency-free helper tests alone
are not a sufficient task contract, so no runtime, Oracle, controls, or reward
is claimed.

## Remediation

Materialize and hash-lock the complete Go module closure, then approve a
typed child-side adapter with deterministic GeoIP fixtures and local doubles
for DNS, TCP port checks, HTTP requests, templates, and profiling. Freeze a
positive public-behavior denominator and rerun source collection, compiler,
Oracle, and all negative controls before changing lifecycle status.

