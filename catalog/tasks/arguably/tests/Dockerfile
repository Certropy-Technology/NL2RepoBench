FROM ghcr.io/multimodal-art-projection/nl2repobench/arguably@sha256:93563ba710a490978afdb11275583ac8357492bd41821a28d8b5fb9eccb84751

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname test) && cp -a /workspace/test /tests/fixture/test


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
