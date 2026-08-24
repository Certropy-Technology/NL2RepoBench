FROM ghcr.io/multimodal-art-projection/nl2repobench/boltons@sha256:770deb94e716b3a1592900ab389ac628f7b2a41d360e55bdb633bbff4c948e52

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
