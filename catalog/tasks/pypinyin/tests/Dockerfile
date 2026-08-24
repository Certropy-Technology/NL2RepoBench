FROM ghcr.io/multimodal-art-projection/nl2repobench/pypinyin@sha256:e6d86e2b150ea5ebe79ed78dff2a13f60f1a73cfe99e827ba100ce4da37d8f3e

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
