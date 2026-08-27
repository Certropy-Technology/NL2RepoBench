# Build `mime`

## Project Description

Create an installable npm package named `mime`, version `4.1.0`, from an empty
workspace. It provides deterministic MIME type and file-extension lookup for
the standard and vendor MIME databases, plus a small command-line interface.

The task is repository generation. Reproduce the specified public behavior
with your own package files; do not copy the pinned upstream source or tests.

## Supports

- Node.js `24.19.0` and npm `11.17.0` on `linux/amd64`.
- ESM semantics: `package.json` must contain `"type": "module"`.
- The package root must be importable as `mime` and expose a default `Mime`
  instance plus the named `Mime` class export.
- The `mime/lite` subpath must expose the same default instance/class shape,
  using the standard type database without vendor-only types.
- Export `mime/types/standard.js`, `mime/types/other.js`, and
  `mime/package.json` as documented package subpaths.
- Expose the `mime` executable from `bin/cli.js`. It must support extension to
  type lookup, reverse type to extension lookup, `--version`, `--name`, and
  `--help`.
- Include a v3 `package-lock.json` that agrees with `package.json`. The
  runtime package must have no runtime dependency and must install with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Runtime behavior must not need a network service, native addon, custom
  loader, registry configuration, or lifecycle script. Build tooling and
  development-only dependencies are outside the scored runtime package.

## API Usage Guide

### Default `mime` instance

Import the default export from `mime` or `mime/lite`.

#### `mime.getType(pathOrExtension)`

Return the lowercase MIME type string for a recognized extension. Accept bare
extensions and file paths using either `/` or `\\` separators. A leading dot
is allowed, and the final extension is matched case-insensitively. Return
`null` when the value is not a string, has no detectable extension, or is not
recognized.

Examples include `getType('txt') === 'text/plain'`,
`getType('.config.json') === 'application/json'`,
`getType('dir\\text.txt') === 'text/plain'`, and
`getType('file.bogus') === null`.

#### `mime.getExtension(type)`

Return the default lowercase extension for a recognized MIME type, or `null`
for non-strings and unknown values. Matching is case-insensitive, surrounding
whitespace is ignored, and semicolon-separated header parameters such as
`charset=UTF-8` are ignored.

Examples include `getExtension('text/html') === 'html'`,
`getExtension(' text/HTML; charset=UTF-8 ') === 'html'`, and
`getExtension('application/x-bogus') === null`.

#### `mime.getAllExtensions(type)`

Return a `Set` containing every extension associated with a recognized MIME
type. Return `null` for a non-string or unknown type. The set must not contain
the leading `*` marker used internally for extensions that are not eligible
as the default extension.

The built-in database must include at least these mappings:

```text
html -> text/html       js -> text/javascript
json -> application/json txt -> text/plain
xml -> application/xml  wasm -> application/wasm
jpeg/jpg/jpe -> image/jpeg
```

### `Mime` class

Import the named `Mime` export from `mime` or `mime/lite`. Constructing
`new Mime(typeMap, ...)` defines each supplied object in order, where each key
is a MIME type and each value is an array of extensions. The first extension
is the default returned by `getExtension`.

#### `mime.define(typeMap, force = false)`

Return the same mutable instance. Extension matching is case-insensitive. If
an extension is already mapped to a different type, throw unless `force` is
`true`; with `force`, the new type replaces the extension mapping. Starred
extensions such as `*abc` are included in `getAllExtensions` and can be a
default extension, but they must not replace the extension-to-type mapping.

The built-in default instances are immutable: calling `define` on one must
throw. Custom instances remain mutable.

### CLI

The executable writes one result followed by a newline. For example:

```bash
mime mpeg                 # video/mpeg
mime -r video/mpeg        # mpeg
mime --version            # 4.1.0
mime --name               # mime
mime --help               # usage text
```

For an unknown lookup, exit nonzero. Reverse lookup uses the last argument;
the ordinary lookup uses the first positional argument.

## Implementation Notes

Keep the package ESM-compatible and make all documented subpath imports work
after installation. Preserve deterministic ordering and lowercase output.
Do not require the verifier's private tests, adapter, reward files, source
checkout, or any network access in the candidate repository.

The scored contract is the bounded behavior above, not complete parity with
every entry in the upstream MIME database or every upstream development tool.
