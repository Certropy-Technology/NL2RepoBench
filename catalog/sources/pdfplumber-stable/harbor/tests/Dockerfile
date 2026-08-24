FROM ghcr.io/multimodal-art-projection/nl2repobench/pdfplumber-stable@sha256:5f1afa11a502918e9624cdc26b849d7c9351ec5ec0cd171c6118a8465e382f30

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
