# Build `basic-ftp`

## Project Description

Create an installable CommonJS npm package named `basic-ftp`, version `6.2.0`,
from an empty workspace. It is a promise-oriented FTP/FTPS client for Node.js.
This task scores a deterministic, offline-compatible slice of the public
library: package exports, FTP directory-listing metadata, control-response
parsing, passive-mode response parsing, bounded text collection, and the
initial client configuration. Do not implement a fake network service.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc.
- CommonJS package semantics. `require("basic-ftp")` must load the package root.
- `package.json` must declare `name: "basic-ftp"`, `version: "6.2.0"`,
  `main: "dist/index.js"`, and a `dist/` tree containing the runtime modules.
- Commit an npm v3 `package-lock.json` consistent with the package. The clean
  verifier runs `npm ci --offline --ignore-scripts --no-audit --no-fund` and
  then packs and installs the package without network access.
- Runtime dependencies are not required. Do not use lifecycle hooks, native
  addons, workspaces, loaders, registry configuration, or runtime downloads.
- The scored boundary is JSON and deterministic. FTP servers, sockets, TLS,
  filesystem transfers, current time, and external services are outside the
  scored slice. The implementation may expose those APIs, but hidden checks
  invoke only the documented operations below.

## API Usage Guide

### Root exports and `FileInfo`

`require("basic-ftp")` exports `Client`, `FTPContext`, `FTPError`, `FileInfo`,
`FileType`, `parseList`, `enterPassiveModeIPv4`, and
`enterPassiveModeIPv6`. The package must preserve CommonJS named exports and
the documented import paths under `dist/`.

`new FileInfo(name)` creates a metadata record. `name` is a string. The public
fields start with `type = FileType.Unknown`, `size = 0`,
`rawModifiedAt = ""`, and absent optional fields. `FileType` contains
`Unknown`, `File`, `Directory`, and `SymbolicLink` numeric values. The boolean
getters `isFile`, `isDirectory`, and `isSymbolicLink` reflect `type` exactly.
`date` is a getter/setter alias for `rawModifiedAt`. `FileInfo.UnixPermission`
contains `Read: 4`, `Write: 2`, and `Execute: 1`.

### `parseList(rawList) => FileInfo[]`

Import path: `require("basic-ftp").parseList`.

Parse a deterministic FTP directory listing string. Split CRLF or LF lines,
ignore blank lines and lines beginning with `total`, then select one parser for
the whole list. The supported forms are MLSD, Unix, and DOS.

- MLSD facts use `key=value;` fields followed by one space and the entry name.
  Recognize `size`/`sizd`, `type`, `modify`, `unique`, Unix owner/group and
  `unix.mode` facts case-insensitively. `file`, `dir`, and symbolic-link forms
  set the corresponding `FileType`; `cdir` and `pdir` are omitted. MLSD
  modification timestamps are UTC `Date` values from
  `YYYYMMDDHHMMSS[.sss]`, and `rawModifiedAt` is their ISO string. Resolve
  symbolic links by `unique` when a target entry is present, while omitting a
  target whose name contains `/`.
- Unix listings expose file type, nine-bit permissions as three numeric
  read/write/execute values, hard-link count, owner, group, byte size, raw
  date text, and symbolic-link target. Entries named `.` and `..` are omitted.
- DOS listings expose file/directory type, byte size (directories use zero),
  raw date text, and name. Entries named `.` and `..` are omitted.

The resulting array preserves listing order. An unsupported non-empty format
throws an `Error` explaining that only MLSD, Unix, or DOS listings are
supported. The returned records are ordinary `FileInfo` instances.

### Control responses

Import `parseControlResponse`, `isSingleLine`, `isMultiline`,
`positiveCompletion`, and `positiveIntermediate` from
`basic-ftp/dist/parseControlResponse`.

`parseControlResponse(text: string)` returns `{messages: string[], rest: string}`.
It normalizes CRLF to LF, ignores blank lines, emits complete three-digit
single-line responses, groups multiline responses from `ddd-` through the
matching `ddd` closing line, and returns an incomplete final group as `rest`
with a trailing LF. `isSingleLine` recognizes `ddd` followed by end-of-line or
a space; `isMultiline` recognizes `ddd-`. `positiveCompletion(code)` is true
for 200 through 299, and `positiveIntermediate(code)` is true for 300 through
399, with both bounds exclusive of other codes.

### Passive-mode response parsing

Import `parsePasvResponse` and `parseEpsvResponse` from
`basic-ftp/dist/transfer`.

`parsePasvResponse(message: string)` returns `{host, port}` from a response
such as `227 Entering Passive Mode (192,168,1,100,10,229)`. The host joins
the four address bytes with dots and the port is `p1 * 256 + p2`, using the
low eight bits of each port component. Malformed responses throw an `Error`.

`parseEpsvResponse(message: string)` returns the decimal port from an EPSV
response such as `229 Entering Extended Passive Mode (|||6446|)`. Both `|` and
`!` delimiters are accepted. A missing or non-numeric port throws an `Error`.

### `StringWriter`

Import `StringWriter` from `basic-ftp/dist/StringWriter`.
`new StringWriter(maxByteLength = 1048576)` is a Node `Writable` that accepts
only `Buffer` chunks, counts bytes rather than JavaScript characters, and
rejects a write that would exceed the bound with an `Error`. After the stream
finishes, `getText(encoding)` concatenates all chunks and decodes them using a
Node buffer encoding such as `utf8`, `ascii`, or `latin1`.

### `Client` initial state

`new Client(timeout = 30000, options?)` creates a client without connecting to
anything. `client.closed` is true initially, `client.ftp.timeout` equals the
provided timeout, and the FTP context uses UTF-8 by default with verbose
logging disabled. `client.close()` is idempotent and closes local resources.
Connection, authentication, directory mutation, upload, download, and TLS
handshake behavior are intentionally outside the deterministic contract.

## Implementation Notes

- Build the package from an empty workspace and keep the public module layout
  under `dist/`; do not assume a globally installed copy of `basic-ftp`.
- Preserve CommonJS imports, class instances, Node stream backpressure/error
  behavior, listing order, UTC date conversion, and informative exceptions.
- The hidden verifier calls candidate code in a separate bounded Node process
  through a fixed JSON adapter. It never supplies module names, source code,
  shell commands, sockets, or test files to the candidate.
- The upstream revision also contains network and container integration tests.
  Those tests are not part of this bounded task because they require an FTP
  server; passing them is not necessary for the scored offline slice.
