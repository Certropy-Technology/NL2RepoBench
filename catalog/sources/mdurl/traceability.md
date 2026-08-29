# mdurl traceability

| Hidden leaf family | Public contract section | Evidence |
| --- | --- | --- |
| `api/*` | Root exports, `URL`, `parse`, `format`, `encode`, `decode` | version/export order, field order, identity, constants, host parsing, whitespace, IPv6, escape toggle, exclusion, and custom protocol behavior |
| `decode/*` | `decode` API Usage Guide | valid UTF-8, incomplete byte, invalid continuation, and surrounding text |
| `encode/*` | `encode` API Usage Guide | default exclusions, controls, Unicode, existing escapes, custom arguments, and surrogate handling |
| `parse/*` | `parse` API Usage Guide | all 88 frozen URL fixture cases, including authority, custom protocols, Unicode, IPv6, and delimiter boundaries |
| `format/*` | `format` API Usage Guide | all 88 frozen URL fixture round trips |

The public specification does not mention hidden filenames, fixture literals,
or implementation helpers. Every scored family is reachable from the documented
API and its expected observable value is independently fixed in the private
verifier bundle.
