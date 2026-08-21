FROM ghcr.io/multimodal-art-projection/nl2repobench/sortedcontainers@sha256:6958cd0d6a2c6cf84e84f3638633a3fc70c9f9392fddfa9f6385a6d6de91517a

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
