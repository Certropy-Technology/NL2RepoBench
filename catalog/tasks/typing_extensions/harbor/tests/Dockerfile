FROM ghcr.io/multimodal-art-projection/nl2repobench/typing_extensions@sha256:43d768b2998bf39f873319f2ac1ba13f42490e3c16013f497175fea5a736814c

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname src/test_typing_extensions.py) && cp -a /workspace/src/test_typing_extensions.py /tests/fixture/src/test_typing_extensions.py


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
