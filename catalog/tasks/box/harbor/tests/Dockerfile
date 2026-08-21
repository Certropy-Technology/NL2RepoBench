FROM ghcr.io/multimodal-art-projection/nl2repobench/box@sha256:216814b130e1822af7721203bc14c3aa0bcc100a643659db6d29ec07f9b3bd3f

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname test) && cp -a /workspace/test /tests/fixture/test


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
