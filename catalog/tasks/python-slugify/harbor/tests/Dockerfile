FROM ghcr.io/multimodal-art-projection/nl2repobench/python-slugify@sha256:a5124fec018d540e2201a687ee16d5748be5ac9c38981cb7a9e746b0dc76a83c

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname test.py) && cp -a /workspace/test.py /tests/fixture/test.py


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
