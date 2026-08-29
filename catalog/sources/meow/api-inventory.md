# Meow API Inventory

## Public surface

- Root ESM default export: `meow(helpText?, options) -> Result`.
- `Options`: `importMeta`, `flags`, `input`, `commands`, `description`, `help`, `version`, `autoHelp`, `autoVersion`, `pkg`, `argv`, `inferType`, `booleanDefault`, `allowUnknownFlags`, and `helpIndent`.
- `Flag`: `type`, `choices`, `default`, `shortFlag`, `aliases`, `isMultiple`, and `isRequired`.
- `Result`: `input`, optional `command`, `flags`, `unnormalizedFlags`, `pkg`, `help`, `showHelp`, and `showVersion`.

## Frozen behavior groups

1. Package root and ESM export shape.
2. String, boolean, number, negated, default, alias, short, repeated, and camel-case flags.
3. Choices and invalid option validation.
4. Positional input conversion and `inferType`.
5. Commands, pass-through input, and command validation.
6. Description/help normalization, version metadata, and indentation.
7. Package metadata and normalized/unnormalized result fields.

The private contract deliberately excludes callback predicates, process exits, arbitrary non-JSON values, filesystem discovery beyond supplied `pkg`, and TypeScript declaration assertions.
