FROM ghcr.io/multimodal-art-projection/nl2repobench/python-pathspec@sha256:8e05b4044ed04d3c6a39dd4a468be773baaed5fb06ce8fe6dd861d30198dcb43

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests/test_01_util.py) && cp -a /workspace/tests/test_01_util.py /tests/fixture/tests/test_01_util.py
RUN mkdir -p /tests/fixture/$(dirname tests/test_02_gitwildmatch.py) && cp -a /workspace/tests/test_02_gitwildmatch.py /tests/fixture/tests/test_02_gitwildmatch.py
RUN mkdir -p /tests/fixture/$(dirname tests/test_03_pathspec.py) && cp -a /workspace/tests/test_03_pathspec.py /tests/fixture/tests/test_03_pathspec.py
RUN mkdir -p /tests/fixture/$(dirname tests/test_04_gitignore.py) && cp -a /workspace/tests/test_04_gitignore.py /tests/fixture/tests/test_04_gitignore.py


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
