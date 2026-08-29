# Build `jsonschema-specifications`

Create a complete, installable Python project named `jsonschema-specifications`
from an empty workspace.  It packages the official JSON Schema metaschemas and
vocabularies as a `referencing` registry.  The import package is
`jsonschema_specifications`.

## Project Description

The package provides a module-level `REGISTRY` containing the JSON Schema
metaschemas for drafts 3, 4, 6, 7, 2019-09, and 2020-12, together with the
vocabulary metaschemas for the two newer drafts.  Each registry key is the
canonical URI of one resource and each value is a JSON-compatible mapping.
The registry is crawled so nested resources can be looked up through the
`referencing` library.

This is a data package and registry factory, not a validator, HTTP client, or
general-purpose schema loader.  Runtime behavior must be deterministic and
must not use the network, subprocesses, current time, or user-specific files.

## Supports

- Support CPython 3.10 and newer Python 3.x versions; the evaluation runtime is
  CPython 3.12 on Linux.
- Provide an installable distribution named `jsonschema-specifications` and an
  import package named `jsonschema_specifications`.
- Declare the runtime dependency `referencing>=0.31.0`.  Build tools and test
  tools are not runtime dependencies.
- Include all JSON files and extensionless vocabulary files under
  `jsonschema_specifications/schemas/` as package data.  Installation must
  preserve their contents and nested directory structure.
- Provide normal PEP 517 packaging metadata.  A static version is acceptable
  for a locally generated implementation; behavior must not depend on VCS
  metadata.

## API Usage Guide

### `jsonschema_specifications.REGISTRY`

`from jsonschema_specifications import REGISTRY` is the only required public
entry point.  It is a `referencing.Registry` (or compatible schema registry)
with exactly these 20 canonical resource keys:

```text
http://json-schema.org/draft-03/schema
http://json-schema.org/draft-04/schema
http://json-schema.org/draft-06/schema
http://json-schema.org/draft-07/schema
https://json-schema.org/draft/2019-09/schema
https://json-schema.org/draft/2019-09/meta/applicator
https://json-schema.org/draft/2019-09/meta/content
https://json-schema.org/draft/2019-09/meta/core
https://json-schema.org/draft/2019-09/meta/format
https://json-schema.org/draft/2019-09/meta/meta-data
https://json-schema.org/draft/2019-09/meta/validation
https://json-schema.org/draft/2020-12/schema
https://json-schema.org/draft/2020-12/meta/applicator
https://json-schema.org/draft/2020-12/meta/content
https://json-schema.org/draft/2020-12/meta/core
https://json-schema.org/draft/2020-12/meta/format-annotation
https://json-schema.org/draft/2020-12/meta/format-assertion
https://json-schema.org/draft/2020-12/meta/meta-data
https://json-schema.org/draft/2020-12/meta/unevaluated
https://json-schema.org/draft/2020-12/meta/validation
```

Registry keys are deterministic and the registry is already crawled.  Calling
`REGISTRY.crawl()` again returns an equal registry.  Use
`REGISTRY.contents(uri)` to retrieve a resource mapping.  A trailing `#` is a
normal empty fragment and should resolve through `referencing` as equivalent
to the corresponding key without it.

Every resource mapping has an identifier matching its registry URI, except
that the four legacy draft identifiers include a trailing `#` in their `$id`
or `id` value.  The draft-06 and draft-07 resources have the title
`Core schema meta-schema`; the 2020-12 schema has the title
`Core and Validation specifications meta-schema`.  Vocabulary resources have
the title `... vocabulary meta-schema` appropriate to their vocabulary.

The 2020-12 schema contains `$schema` equal to its own canonical schema URI.
The registry values must be mappings, not serialized JSON strings, and lookup
must not mutate the stored mappings.

### Package data and dotfiles

The package scans the two-level schema layout at runtime using package-resource
APIs.  It ignores directories and files whose names begin with `.` while
loading resources, so an incidental `.DS_Store` file must not break registry
construction.  This behavior is an implementation boundary for package data;
do not hard-code absolute filesystem paths.

## Implementation Notes

- Use `importlib.resources` or an equivalent package-resource mechanism so the
  installed distribution works from a normal wheel, not only from a checkout.
- Build each resource with `referencing.Resource.from_contents`, add resources
  to an immutable registry, and crawl the final registry before exporting it.
- Keep `REGISTRY` stable after import.  Do not expose private helpers as part
  of `__all__`; `jsonschema_specifications.__all__` must be exactly
  `['REGISTRY']`.
- Package data files are part of the public behavior.  Do not replace them with
  an abbreviated synthetic fixture or fetch them from the network.
- The hidden verifier invokes the public entry point through an isolated child
  process.  Do not copy tests, verifier code, or reference source into the
  generated workspace.
