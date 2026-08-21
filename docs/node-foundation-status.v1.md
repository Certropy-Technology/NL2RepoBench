# Node/npm Foundation Status

The additive Node/npm foundation is development-only in this checkout.

- Host validation used Node `22.23.1` and npm `10.9.8` without contacting a registry.
- `toolchain.node.lock.toml` records the exact runtime and Harbor `0.21.0` schema `1.4`.
- The official Node `linux/amd64` manifest was verified as
  `docker.io/library/node@sha256:8607a9064d4a571140998ae9e52a3b3fcf9cff361d04642d5971e6cd76d39e27`;
  both development image entries use that digest.
- Production Node compilation still fails closed because the private npm dependency
  artifact and production verifier/grader lock have not been reviewed and added.

## Development E2E evidence

- Harbor `0.21.0`, task schema `1.4`, Docker Compose `5.4.0`.
- Three independent Oracle trials: `3/3`, `valid=true`, reward `1.0`, collection `8`.
- Empty `nop` control: reward `0.0`, model failure `candidate-installation-failed`.
- The E2E bundle used `--allow-incomplete`; these results do not establish production
  publication or Python/Node score parity.
- The synthetic task is excluded from every Python dataset and is never used for a
  Python/Node score parity claim.

Docker and Harbor execution are intentionally not part of this foundation change.
