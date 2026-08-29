# has-ansi Provenance

## Frozen source

- Upstream: `https://github.com/chalk/has-ansi`
- Revision: `8ad46b5ecc1f66de8e526c506d72fbe3e092ef20`
- Commit subject: `6.0.2`
- Commit tree: `66f06167c2ed0a20f2a4d50258e925522fecec0d`
- Source archive: `.nl2repo/authoring-work/node-author-wave2-20260828/has-ansi/provenance/source.tar`
- Archive SHA-256: `bf0286a0fb4a59faf5ca08ba2a1b52221154248db05b6f4f5b9a483db97b4d2b`
- Archive size: `20480` bytes
- Tracked source files: `index.js`, `index.d.ts`, `index.test-d.ts`, `license`,
  `package.json`, `readme.md`, and `test.js`, plus repository metadata.

## License and metadata

The frozen `package.json` declares MIT and the frozen `license` file contains
the standard MIT grant. The license SHA-256 is
`5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
The package metadata SHA-256 is
`a3ce4f70caea920b94da8d7b30e61d6c0b612423c507afd2456da2dc61d89fc5`.

The package is ESM (`type = module`), exports a default JavaScript entry and a
TypeScript declaration entry, and has one runtime dependency: `ansi-regex`.
The upstream development command is `xo && ava && tsd`; its two AVA leaves and
one type assertion are used as baseline evidence, while the production slice
below adds deterministic public edge cases.

## Production adaptation

The upstream package has a single synchronous pure function. The production
adapter therefore sends one JSON request and one JSON response per UTF-8 JSONL
line to a fresh candidate child. The trusted verifier never imports candidate
code. It checks the default export, package metadata, type declaration, and
ANSI detection behavior across 24 stable leaf cases. No TTY, clock, process
environment, browser, or external service is part of the scored behavior.
