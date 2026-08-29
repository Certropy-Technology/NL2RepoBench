# Espree provenance

- Upstream: `https://github.com/eslint/js`
- Frozen revision: `8173ecfeb7473bff90d1da11b1347082f47e262e`
- Frozen raw git archive (tar, `source/` prefix):
  `sha256:bc2f79fda450ef344b0696f374d492f95fee28b74254abbc1584440fd9739ac4`
- Package: `packages/espree`, version `11.2.0`
- License: BSD-2-Clause; package `LICENSE` SHA-256:
  `sha256:26c95937762a3dc17a3934a0a2773c70259ba4bf28dab713c225e4af8eb9d349`
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64 glibc
- Upstream package source: 5 implementation files; upstream package tests:
  12 files and 135 `it(...)` cases.

The production candidate closure pins `acorn@8.16.0`, `acorn-jsx@5.3.2`, and
`eslint-visitor-keys@5.0.1` with integrity-checked npm cache entries. The
Oracle fetches only the frozen source revision; candidate and verifier phases
are network-isolated. Harbor 0.21.0 production compilation produced 102
manifest entries with zero integrity mismatches. The final Oracle collected
24/24 leaves and received reward 1.0; empty, stub, forgery, and offline
controls all completed with reward 0 and a false public-network probe.
