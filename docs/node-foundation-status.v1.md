# Node/npm Foundation Status

The additive Node/npm foundation is development-only in this checkout.

- Host validation used Node `22.23.1` and npm `10.9.8` without contacting a registry.
- `toolchain.node.lock.toml` records the exact runtime and Harbor `0.21.0` schema `1.4`.
- No verified digest-pinned Node `linux/amd64` image is present in the checkout, so the
  image entries intentionally remain unpinned and are marked `development-only`.
- Production Node compilation fails closed until a digest-pinned Node 22 image and a
  locked verifier/grader image are added to a separately reviewed toolchain lock.
- The synthetic task is excluded from every Python dataset and is never used for a
  Python/Node score parity claim.

Docker and Harbor execution are intentionally not part of this foundation change.
