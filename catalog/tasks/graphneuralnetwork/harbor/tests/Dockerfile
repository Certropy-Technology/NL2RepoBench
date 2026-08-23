FROM ghcr.io/multimodal-art-projection/nl2repobench/graphneuralnetwork@sha256:6388582535fd9c56af5a69eef057a136c3ec4ae54ae26156b6db843286d62152

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN python - <<'PY'
from pathlib import Path
import site

site_packages = Path(site.getsitepackages()[0])
(site_packages / "sitecustomize.py").write_text(
    "import networkx as _nx\n"
    "if not hasattr(_nx, 'from_scipy_sparse_matrix') and hasattr(_nx, 'from_scipy_sparse_array'):\n"
    "    _nx.from_scipy_sparse_matrix = _nx.from_scipy_sparse_array\n",
    encoding="utf-8",
)
PY
RUN mkdir -p /tests/fixture && cp -a /workspace/tests /tests/fixture/tests

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
