FROM ghcr.io/multimodal-art-projection/nl2repobench/gitingest@sha256:bbd145dbf70464c96b4f085af13911b53e599ab79ca46e5c9c9a25a159a093a2

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests
RUN python -m pip install --no-cache-dir gitpython loguru strenum eval-type-backport

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
