# Textual Traceability

The public instruction is intentionally limited to deterministic utility and
value-object behavior. The private verifier maps one-to-one to these public
contracts:

| Leaf IDs | Public contract in `instruction.md` | Boundary check |
| --- | --- | --- |
| `slug-basic`, `slug-unicode`, `slug-empty`, `tcss-id`, `tcss-id-special` | `_slug.slug` and `_slug.slug_for_tcss_id` | JSON string equality |
| `camel-simple`, `camel-acronym` | `case.camel_to_snake` | JSON string equality |
| `cell-ascii`, `cell-combining`, `cell-cjk`, `column-tab` | `_cells.cell_len` and `cell_width_to_column_index` | JSON integer equality |
| `wrap-words`, `wrap-fold` | `_wrap.compute_wrap_offsets` | JSON list equality |
| `clamp-low`, `clamp-high` | `geometry.clamp` | JSON scalar equality |
| `offset-value`, `size-value`, `region-corners`, `region-value` | Geometry value objects and `Region.from_corners` | tuple-like values serialized as lists |
| `color-hex`, `color-red`, `color-hsl` | `Color.parse`, `Color.from_hsl` | six-field color serialized as list |
| `markup-escape` | `markup.escape` | JSON string equality |
| `color-invalid` | `Color.parse` malformed input exception contract | exception type name |

The implementation notes explicitly exclude terminal rendering, snapshots,
event loops, and optional syntax highlighting, so those upstream tests are not
claimed by this task. Packaging and the documented import layout are covered by
the candidate install step before any behavior leaf can execute.
