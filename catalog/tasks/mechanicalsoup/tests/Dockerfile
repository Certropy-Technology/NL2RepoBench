FROM ghcr.io/multimodal-art-projection/nl2repobench/mechanicalsoup@sha256:54a9ee32015e3b67b09459f08ae752b7bd9f7920a78a2ffc5b2ba772ca8d60d6

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
