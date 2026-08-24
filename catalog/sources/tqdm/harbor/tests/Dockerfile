FROM ghcr.io/multimodal-art-projection/nl2repobench/tqdm@sha256:75c3dba71f588b7022445fcefc59ba03163a8161ca5e4ba9dcc556a8f5403fa9

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
