# `pytorch-grad-cam` Static Conversion Audit

**Status: blocked.** This directory is an audit record only. No Harbor bundle,
hidden test bytes, source archive, or dataset entry is included.

## Frozen evidence

- Legacy denominator: `178`; protected paths: `tests`, `examples`.
- Verifier image: `ghcr.io/multimodal-art-projection/nl2repobench/pytorch-grad-cam@sha256:d706241fe9aecd394b172aa6ddd361c466d43678e8ee04063844152b25c410e6` (`linux/amd64`).
- Upstream: `jacobgil/pytorch-grad-cam`, commit
  `781dbc0d16ffa95b6d18b96b7b829840a82d93d1`, MIT license, source archive
  SHA-256 `ea3fc94c1e32e972dd4b3c45609fa511798e93e552acff512714225901c89024`.
- Static AST expansion of the exact retained image tests is 178 cases: 176
  parametrized model cases plus one case each in the other two test modules.
- The required public asset `examples/both.png` is present in the upstream
  source (`90,226` bytes, SHA-256
  `8d30785a513e22a2f574c839c7e1751db943d0b5399347e7bb37736f6c5a95c2`) but
  is absent from the final image `/workspace`; it exists only in a deleted
  temporary `/pytorch-grad-cam` source layer.

## Publication blockers

1. The legacy post-processor removes protected `examples/` before constructing
   the candidate workspace, while all three frozen tests open
   `examples/both.png`. Adding that PNG to a Harbor task would be an
   owner-unapproved public source overlay and would change the candidate
   boundary.
2. The image installs unpinned packages from the mutable/private index
   `https://bytedpypi.byted.org/simple`; no hash-locked offline dependency
   closure or package artifact is recorded. The upstream requirements include
   unpinned NumPy, Pillow, Torch/Torchvision, ttach, tqdm, OpenCV, matplotlib,
   and scikit-learn, with additional unpinned pytest tooling.
3. No fresh collection/JUnit, Oracle, empty/stub/forgery/offline controls, or
   separate candidate subprocess boundary has been established.

Keep this task blocked until an immutable approved asset contract, an offline
dependency closure, and the required verifier/runtime gates are available.
