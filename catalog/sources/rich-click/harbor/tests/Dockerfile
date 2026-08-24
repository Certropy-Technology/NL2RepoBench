FROM ghcr.io/multimodal-art-projection/nl2repobench/rich-click@sha256:8f091fb134fce469a442c928a3a8494510e3ff68c7e88b2c1378aff8c813d241

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests
RUN python -m pip install --no-cache-dir 'setuptools>=45' click rich

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
