FROM ghcr.io/multimodal-art-projection/nl2repobench/autopep8@sha256:dbecf8fbccb83e9071ba33e16d127c2b0797c6f31372b9cbf40104b8ac9a66fe

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname test) && cp -a /workspace/test /tests/fixture/test


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
