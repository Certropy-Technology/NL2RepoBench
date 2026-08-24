FROM ghcr.io/multimodal-art-projection/nl2repobench/voluptuous@sha256:9d1deaa58ac3e73dc8de4b8d3fdc5c574830637753d71e93ce5b5cdbad0c05fd

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
