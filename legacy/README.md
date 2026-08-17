# Legacy Runner Environment

The root `uv.lock` belongs only to the modern metadata/authoring core. The
historical `main.py` and Docker wrapper use this isolated uv project so their
dependencies cannot change the core lock or CI environment.

```bash
uv sync --project legacy --frozen
uv run --project legacy python main.py
```

OpenHands itself runs in the pinned container images configured by the legacy
runner. This project therefore locks only the host-side Python dependency used
by `docker_self/`. The legacy environment is for historical reproduction and
parity checks; new benchmark execution will move to Harbor.
