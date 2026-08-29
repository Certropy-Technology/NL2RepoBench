# API Inventory

The frozen TypeScript source contains 15 modules under `src/`. The root
CommonJS export inventory is:

- `Client`, `FTPContext`, `FTPError`
- `FileInfo`, `FileType`, `parseList`
- `enterPassiveModeIPv4`, `enterPassiveModeIPv6`

The deterministic scored slice additionally reaches the documented module
paths `dist/parseControlResponse`, `dist/transfer`,
`dist/parseListMLSD`, and `dist/StringWriter`. These exports are exercised only
with JSON values and local Node streams. The network client, TLS sockets,
filesystem transfers, callbacks carrying native stream objects, and server
authentication remain outside the scored boundary.

The public behaviors covered by the fixed adapter are:

| Surface | Contract coverage |
| --- | --- |
| `FileInfo`/`FileType` | defaults, enum values, type getters, date alias, permission constants |
| `parseList` | MLSD facts and links, Unix permissions/links, DOS entries, ordering, filtering, errors |
| control response parser | single/multiline grouping, CRLF normalization, incomplete rest, predicates and code bands |
| passive response parser | PASV host/port, EPSV delimiters, malformed responses |
| `StringWriter` | Buffer-only writes, byte bound, UTF-8 chunking, decoding |
| `Client` | closed initial state, timeout, UTF-8/default verbosity, pre-connect close |
