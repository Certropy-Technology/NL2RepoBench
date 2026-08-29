# Traceability

The public instruction is the source of the candidate contract. The private
`node:test` bundle is collected as 32 deterministic leaves through the
subprocess client in `harbor/tests/private/test_client.mjs`.

| Contract area | Covered behavior | Evidence surface |
| --- | --- | --- |
| Packaging | name/version, ESM mode, root export, declaration file, offline v3 lock | private packaging leaf; `tests/command-plan.json` |
| Name inventories | modifier, foreground, background, underline and combined color order | private inventory leaves |
| ANSI style pairs | modifiers, base colors, bright aliases, close codes and non-enumerable groups | private style/group leaves |
| Conversion builders | basic, 256-color, truecolor and underline escape sequences | private builder leaves |
| Color conversion | grayscale boundaries, RGB cube, hexadecimal parsing and ANSI-16 reduction | private conversion leaves |
| Isolation | candidate calls run in a UID-separated child with bounded CPU/process/file/output limits | `tests/private/test_client.mjs`; verifier runtime |

The Oracle source is kept only in the private artifact bundle. The candidate
receives the instruction and an empty workspace; it does not receive the
Oracle package or private test bytes.
