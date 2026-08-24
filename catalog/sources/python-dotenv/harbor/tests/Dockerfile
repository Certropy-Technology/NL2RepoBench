FROM ghcr.io/multimodal-art-projection/nl2repobench/python-dotenv@sha256:f604ad8f1f95679d3d78463ca6c23be1a4ca92f6a55769c2f5d60f4031dae0a0

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
