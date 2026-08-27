# Authoring Provenance

- Frozen upstream: `https://github.com/dateutil/dateutil`
- Revision: `48bd1af97e71baf8e96fce5b663d589caac8f147`
- Static source inventory: `.nl2repo/authoring-work/python-discovery-20260826-r1/python-dateutil/api-inventory.json`
- Git archive source digest: `sha256:9c849ab5171036e43f8cbe8bed72ca6d6a0551a2bb83876158168381c1770d39`
- Scanner content digest: `sha256:9c96a78d11cc4afb04cfce47779d99a25375e19b8d5647451bae07320108c2f0`
- Upstream baseline: `TZ=UTC pytest -q tests`, three independent runs, each `2031 passed, 47 skipped, 17 xfailed`.
- The original baseline first failed under pytest 9.1 because this revision treats a generator passed to `parametrize` as an error. The final environment pins pytest 8.4.2 for baseline evidence; the private verifier uses a subprocess JSON contract and does not depend on pytest collection.
