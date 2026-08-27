# Frozen test inventory

The production verifier has 25 unique leaf IDs (`custom-json-v1`):

- 19 positive behavior and repeatability cases across all 9 facade functions;
- 5 negative-contract cases for malformed expressions, wrong types, unknown
  symbols, non-square matrices, and Python-code syntax;
- 1 JSON-serialization safety case.

The frozen upstream baseline evidence contains 1,098 collected cases, 18
skips, and no failures/errors in each of three baseline XML reports. That
upstream collection is evidence about source health only; it is not the task
denominator.
