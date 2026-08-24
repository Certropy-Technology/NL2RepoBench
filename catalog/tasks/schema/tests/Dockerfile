FROM ghcr.io/multimodal-art-projection/nl2repobench/schema@sha256:39cc925630f3643f539c608e89942a01a8d9c208f2d358fa9d36aee9b49017a3

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname test_schema.py) && cp -a /workspace/test_schema.py /tests/fixture/test_schema.py


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
