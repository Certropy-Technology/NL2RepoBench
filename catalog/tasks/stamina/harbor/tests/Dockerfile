FROM ghcr.io/multimodal-art-projection/nl2repobench/stamina@sha256:21cbd1883da2af9c19dbf9ba0d4fe2a3780cc64279fa4e9bc8ae67d19e4122bf

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
