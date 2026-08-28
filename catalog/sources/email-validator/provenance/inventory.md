# Source And Test Inventory

- Upstream: `https://github.com/JoshData/python-email-validator`
- Frozen revision: `b73d010bb3db70547199f39fd85d2286a7f6f476`
- Commit: `Fix 'original' field having an un-escaped local part`
- Commit time: `2026-06-25T09:15:51-04:00`
- License: Unlicense; `LICENSE` SHA-256 `672179752e109134a3fb2bdd0780b29fdb7a03974f0f586a13aead5129562d4c`
- Reproducible unprefixed `git archive --format=tar HEAD` SHA-256: `6645b1719e7183f35d0ec20900e67391d0a3c2d570f442957203d64758609801`
- Implementation surface: 9 package Python modules plus package metadata and CLI.
- Upstream tests: `test_main.py`, `test_syntax.py`, `test_deliverability.py`, and deterministic mocked DNS data. Baseline probe: 317 passed, exit code 0, Python 3.12.11 with `dnspython==2.8.0`, `idna==3.15`, and `pytest==9.0.3`.
- Risk flags: DNS and Unicode/IDNA behavior. DNS is adapted to deterministic resolver scenarios in a separate subprocess verifier; no live DNS is required.

The production denominator is a fixed 30-leaf JSON-safe contract subset, not the full upstream count. It covers packaging/exports, syntax normalization, option gates, result compatibility methods, IDNA and Unicode, domain literals, deterministic deliverability branches, caching resolver configuration, and the CLI boundary.
