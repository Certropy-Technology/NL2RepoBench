FROM ghcr.io/multimodal-art-projection/nl2repobench/retrying@sha256:1302235420db9d34955c42273ebaf23df8bbee31ceeaf3c336347f54b64146fe

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname test_retrying.py) \
    && cp -a /workspace/test_retrying.py /tests/fixture/test_retrying.py

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
