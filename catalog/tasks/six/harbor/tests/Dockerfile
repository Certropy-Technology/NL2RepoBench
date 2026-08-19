FROM ghcr.io/multimodal-art-projection/nl2repobench/six@sha256:403962b64fa09689196c6d29a82bf7a9525a95dbb4459f12cca4a920a056dc91

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname test_six.py) && cp -a /workspace/test_six.py /tests/fixture/test_six.py


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
