FROM ghcr.io/multimodal-art-projection/nl2repobench/graphneuralnetwork@sha256:6388582535fd9c56af5a69eef057a136c3ec4ae54ae26156b6db843286d62152

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture && cp -a /workspace/tests /tests/fixture/tests

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
