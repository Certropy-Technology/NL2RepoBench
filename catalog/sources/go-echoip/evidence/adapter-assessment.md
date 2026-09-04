# Separate-verifier adapter assessment

Status: blocked.

The service contract crosses boundaries that are not represented by the
current reviewed Go bridge: MaxMind country/city/ASN database bytes, request
remote addresses and trusted proxy headers, reverse DNS, TCP port reachability,
HTML templates and static assets, HTTP routing, and optional pprof handlers.
The public CLI also depends on filesystem paths for databases and templates.
A deterministic child-side adapter would need bounded fixture formats and
local DNS/TCP/HTTP doubles; none is currently approved for this revision.

The pure helper APIs `iputil.ToDecimal` and `useragent.Parse` are insufficient
to represent the package's advertised service behavior. No verifier or
Oracle is fabricated.
