FROM ghcr.io/multimodal-art-projection/nl2repobench/emoji@sha256:4b7b1ef33001317d8ebc54a7467e2ad1688d7a6d3ac0672911de770098037d0b

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests
RUN mkdir -p /tests/fixture/$(dirname utils/testutils.py) && cp -a /workspace/utils/testutils.py /tests/fixture/utils/testutils.py


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
