# pytest authoring audit

- Mode: `author-one`; assigned immutable revision `51e9a9f148cd2509a31e3fa0d2b1b3204c2b0dd7`.
- Upstream: `https://github.com/pytest-dev/pytest`; commit tree `7e6a2cca4c3d790892bfc315061df219cd464965`.
- Source archive: `sha256:74c9fa75d3899c423d551d5cc673e470680a6b34e1a45cec99125c67e458c7da`.
- License: root `LICENSE`, SPDX `MIT`, SHA-256 `ca836a5f9ecca3b2f350230faa20a48fb8b145653b5568d784862df864706b9b`.
- Upstream has 80 Python source files and a large `testing/` tree. The production contract is deliberately bounded to deterministic local behavior that can cross the child JSON boundary.
- The verifier never imports candidate code in the trusted process and never accepts candidate-written JUnit, grading, or reward files.
- The candidate process has no egress and receives no hidden paths or private test bytes.
