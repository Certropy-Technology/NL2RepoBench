# Build `basic-ftp`

## Project Description

Create an installable CommonJS npm package named `basic-ftp`, version `6.2.0`,
from an empty workspace. It is a promise-oriented FTP/FTPS client for Node.js.
The deterministic contract covers package exports, FTP listing metadata,
control-response parsing, passive-mode parsing, bounded text collection, and
the initial client state. Network transfers are outside this local contract.

## Natural Language Instruction

Implement `basic-ftp` as a modular package with the public root exports and
`dist/` modules described below. Preserve CommonJS `require` behavior, class
instances, listing order, UTC date conversion, stream errors, and informative
malformed-input errors. Provide four capability groups: metadata records and
listing parsers; control and passive response parsers; a bounded UTF-8 stream
collector; and a local, unconnected client configuration. Do not implement a
fake FTP server or replace local parsing with network access.

## Supports or Environment Configuration

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc.
- The package name is `basic-ftp`; `require("basic-ftp")` loads the root.
- `package.json` declares `name: "basic-ftp"`, `version: "6.2.0"`, and
  `main: "dist/index.js"`. Commit an npm v3 `package-lock.json`.
- Runtime dependencies are empty. `npm ci --offline --ignore-scripts
  --no-audit --no-fund` must work with the preloaded package manager.
- Agent, candidate, verifier, Oracle, controls, and runtime operations use
  `network_mode=no-network`; do not contact FTP servers, DNS, GitHub, npm, or
  any external service. Current time and random data are not API inputs.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── dist/
    ├── index.js
    ├── FileInfo.js
    ├── FTPContext.js
    ├── FTPError.js
    ├── parseList.js
    ├── parseControlResponse.js
    ├── transfer.js
    ├── StringWriter.js
    └── Client.js
```

The root export must expose `Client`, `FTPContext`, `FTPError`, `FileInfo`,
`FileType`, `parseList`, `enterPassiveModeIPv4`, and
`enterPassiveModeIPv6`. The parser and writer modules must be importable from
their corresponding `dist/` paths.

## API Usage Guide

### `FileInfo` and listing data

Import path: `require("basic-ftp")`; in CommonJS code use
`const { FileInfo, FileType } = require("basic-ftp")`.
Node's ESM interop may use `import basicFtp from "basic-ftp"` for the same
CommonJS default export; preserve the named CommonJS exports required above.
`new FileInfo(name)` accepts a string and starts with `type =
FileType.Unknown`, `size = 0`, and `rawModifiedAt = ""`. `FileType` contains
numeric `Unknown`, `File`, `Directory`, and `SymbolicLink` values. The
`isFile`, `isDirectory`, and `isSymbolicLink` getters follow `type`; `date` is
the getter/setter alias for `rawModifiedAt`. `FileInfo.UnixPermission` has
`Read: 4`, `Write: 2`, and `Execute: 1`. Invalid names must fail clearly.

`parseList(rawList) => FileInfo[]` accepts a string containing MLSD, Unix, or
DOS entries. It ignores blank lines, CRLF/LF differences, and lines beginning
with `total`, then uses one parser for the complete list. MLSD recognizes
`size`/`sizd`, `type`, `modify`, `unique`, owner/group, and `unix.mode`; `cdir`
and `pdir` are omitted. Unix entries expose type, permissions, links, owner,
group, size, raw date text, and symbolic-link target. DOS entries expose type,
size, raw date text, and name. Preserve input order, omit `.` and `..`, convert
MLSD UTC timestamps `YYYYMMDDHHMMSS[.sss]` to `Date`, and resolve a symbolic
link target by `unique` only when that target is a local entry. Unsupported
non-empty formats throw `Error`.

```js
const { parseList } = require("basic-ftp");
const entries = parseList("type=file;size=3;modify=20240102112233; note.txt");
console.log(entries[0].name, entries[0].size, entries[0].isFile);
```

### Control and passive response modules

Import `parseControlResponse`, `isSingleLine`, `isMultiline`,
`positiveCompletion`, and `positiveIntermediate` from
`basic-ftp/dist/parseControlResponse`. `parseControlResponse(text) =>
{messages: string[], rest: string}` normalizes CRLF, ignores blank lines,
groups `ddd-` through the matching `ddd` line, and returns an incomplete final
group in `rest` with a trailing LF. The predicates recognize three-digit
response forms; completion is true only for 200-299 and intermediate only for
300-399.

Import `parsePasvResponse(message) => {host, port}` and
`parseEpsvResponse(message) => number` from `basic-ftp/dist/transfer`.
PASV joins four address bytes and computes `p1 * 256 + p2`; EPSV accepts `|`
or `!` delimiters. Missing, malformed, or nonnumeric fields throw `Error`.

```js
const { parsePasvResponse } = require("basic-ftp/dist/transfer");
parsePasvResponse("227 Entering Passive Mode (192,168,1,100,10,229)");
```

### `StringWriter` and `Client`

`new StringWriter(maxByteLength = 1048576)` from
`basic-ftp/dist/StringWriter` is a Node `Writable`. `write(chunk)` accepts a
`Buffer`, counts bytes rather than JavaScript characters, and errors when the
bound would be exceeded. After completion, `getText(encoding) => string`
concatenates chunks and decodes with a Node encoding such as `utf8` or
`latin1`.

`new Client(timeout = 30000, options?)` creates no connection. Initially
`closed` is true, `ftp.timeout` equals `timeout`, UTF-8 is enabled, and verbose
logging is disabled. `close() => void` is idempotent and only closes local
resources. Authentication, sockets, TLS, uploads, downloads, and directory
mutation are not required by this contract.

## Implementation Notes

Keep runtime code under `dist/` and preserve named CommonJS exports. Date
conversion must be UTC and parser output must be deterministic. Do not use
current time, environment-specific paths, global network state, or unordered
iteration when output order is observable. A malformed list or response must
fail rather than silently becoming an empty successful result.

## Examples

```js
const { FileInfo, FileType } = require("basic-ftp");
const info = new FileInfo("docs");
info.type = FileType.Directory;
console.log(info.isDirectory, info.size);
```

```js
const { parseEpsvResponse } = require("basic-ftp/dist/transfer");
console.log(parseEpsvResponse("229 Entering Extended Mode (|||6446|)"));
```

## Error Handling and Boundary Conditions

- An empty listing returns an empty array; a non-empty unknown format throws
  an `Error` instead of inventing entries.
- `parsePasvResponse("227 bad")` and a response with a missing EPSV port throw
  `Error`.
- `StringWriter(2)` must reject a third byte even when the chunk contains one
  multibyte character; limits are byte limits.
- `client.close(); client.close()` remains safe, while operations requiring a
  connection must not initiate an implicit network request.
