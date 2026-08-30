# tiktoken source freeze

- Upstream: `https://github.com/openai/tiktoken`
- Revision: `4e71bbe0c078468e00fefbf94b39849389f346e5`
- Release: `0.14.0` (`Release 0.14.0 (#597)`)
- License: MIT; `LICENSE` SHA-256 `sha256:418cb499b436128d653d79941333a5437b7be2ea9213dcc2f04d15d5d2c51d86`
- Git archive (tar, prefix `tiktoken/`) SHA-256: `sha256:80736cfc1a7cf9c87e530f3cf4cc7b536a3261208ded244138872b130b9f41d7`
- Checkout: `.nl2repo/authoring-work/tiktoken/source`
- Freeze command: `git clone --no-tags https://github.com/openai/tiktoken ... && git fetch --no-tags --depth=1 origin 4e71bbe0c078468e00fefbf94b39849389f346e5 && git checkout --detach 4e71bbe0c078468e00fefbf94b39849389f346e5`

The source build was probed with CPython 3.12.11, setuptools-rust, Rust 1.97.1,
and the upstream six-file vocabulary cache. The selected public upstream suite
passed 33 tests with `TIKTOKEN_MAX_EXAMPLES=25`. Because upstream constructors
download 8.1 MiB of remote vocabulary at first use and the model run must be
strictly offline, the scored task uses the bounded custom-json adaptation
described in `instruction.md`.
