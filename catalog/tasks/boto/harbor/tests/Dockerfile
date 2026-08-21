FROM ghcr.io/multimodal-art-projection/nl2repobench/boto@sha256:6a70abf3ae8807746d708ce0ab1de72e46f7b14e3f91d68c542a112523468c24

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests
RUN python -m pip install --no-cache-dir pytest 'botocore>=1.40.52,<1.41.0' 'jmespath>=0.7.1,<2.0.0' 's3transfer>=0.14.0,<0.15.0'

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
