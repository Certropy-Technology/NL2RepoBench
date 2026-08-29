# Test Traceability

The private 44-leaf `node:test` contract is organized as follows:

- `packaging_and_exports` (4): package name/version, ESM root import, default export, named export.
- `distance_core` (12): empty strings, identity, one edit of each kind, symmetry, common examples, repeated characters, UTF-16 behavior, and longer inputs.
- `distance_cutoff` (8): exact values within a cutoff, truncation above a cutoff, zero cutoff, length-based early cutoff, reversed inputs, empty input, omitted options, and null options.
- `closest_match` (16): nearest candidate, exact match, single candidate, empty list, non-array boundary, first tie, duplicates, cutoff qualification, no qualifying result, empty target, case sensitivity, Unicode, longer candidate lists, zero-cutoff behavior, tied short candidates, and closer-later candidates.
- `immutability_and_unicode` (4): candidate-array immutability, options immutability, Unicode nearest matching, and repeated deterministic calls.

Every leaf maps to the public `API Usage Guide`: default distance behavior and cutoff semantics map to `leven`; nearest, order, duplicate, invalid-list, and cutoff behavior map to `closestMatch`; package leaves map to `Supports` and `Implementation Notes`. No leaf relies on private helper names or an undocumented CLI.
