FROM ghcr.io/multimodal-art-projection/nl2repobench/parse@sha256:b62739aff75c836823bf0140ae6db4d329beb74cf79cdb170ed5adb85966ee18

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
