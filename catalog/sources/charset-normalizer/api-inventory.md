# API inventory

Frozen revision `e239bdc5cc1eb1f0db08d4046ad531f805dbea71` exposes the top-level detection API from `charset_normalizer.api`, compatibility `detect` from `charset_normalizer.legacy`, `CharsetMatch`/`CharsetMatches`/`CliDetectionResult` from `charset_normalizer.models`, Unicode and codec helpers from `charset_normalizer.utils`, and the `normalizer` CLI from `charset_normalizer.cli`.

The scored contract covers byte detection and BOM handling, codec isolation/exclusion, file and stream entry points, binary classification, legacy result shape, ordered match containers, match metadata/output, codec declaration helpers, Unicode classification, version exports, and deterministic CLI paths. Native Cython modules, language frequency internals, logging timestamps, large-payload performance, and external repository operations are outside the deterministic adapter boundary.
