# `parse5` Traceability

The frozen verifier has 54 unique `node:test` leaves. Every leaf invokes an
installed candidate package as UID 10001 through the one-shot JSON boundary;
trusted test code never imports candidate JavaScript.

| Public contract | Verifier coverage | Leaves |
| --- | --- | ---: |
| ESM package metadata, declarations, package-root exports, documented adapter method names, Parser static shape, namespace/error constants | package inspection and compatibility-export probes | 6 |
| `parse` document defaults, doctype/mode, text/entities, comments, attributes, optional tags, table correction, formatting reconstruction | bounded document tree projections | 9 |
| raw text, RCDATA, scripting flag, SVG/MathML, namespaced attributes, templates, Unicode/null handling | bounded document tree projections | 11 |
| source locations and parse-error callback | location/error projections | 3 |
| `parseFragment` overloads and HTML/select/table/raw-text/SVG contexts | bounded fragment projections | 9 |
| `serialize` canonical document, text/attribute escaping, voids, doctypes, comments, templates | canonical string comparisons | 7 |
| `serializeOuter`, attribute ordering, entity and raw-text round trips, UTF-16 offsets | canonical string and location comparisons | 9 |
| **Total** | fixed collection | **54** |

Reverse traceability is complete for the supported package-root surface:

- `Project Description` and `Supports` map to package inspection and the
  compiler's offline install/package boundary.
- `Default tree representation` maps to document/fragment projections,
  namespace checks, template-content checks, and source locations.
- Each documented root function has direct behavioral leaves.
- Root compatibility exports, the documented `Parser` static entries, and the
  documented adapter method names are checked for existence/kind only,
  matching the explicit low-level exclusion in the instruction.
- Custom tree adapters and direct tokenizer/parser construction are excluded in
  the public instruction and therefore have no hidden behavioral assertions.

The verifier intentionally does not copy the upstream 19,325-leaf suite. That
suite proves the frozen reference revision is healthy; the task verifier uses a
reviewable, fully specified root-API contract suitable for 0-to-1 generation.
