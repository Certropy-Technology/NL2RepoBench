FROM ghcr.io/multimodal-art-projection/nl2repobench/structlog@sha256:ad5c6ff2b6ddd2a7f463b9e31dcd8c201e6f17092eb9c28cd77a4c62421d9d1b

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests
RUN python -m pip install --no-cache-dir colorama

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
