FROM ghcr.io/multimodal-art-projection/nl2repobench/humanize@sha256:18407d80e95c1a277a5e6fb66c1174b7f2b3699ec10125adc7d6e180f2f6a626

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests/test_filesize.py) && cp -a /workspace/tests/test_filesize.py /tests/fixture/tests/test_filesize.py
RUN mkdir -p /tests/fixture/$(dirname tests/test_i18n.py) && cp -a /workspace/tests/test_i18n.py /tests/fixture/tests/test_i18n.py
RUN mkdir -p /tests/fixture/$(dirname tests/test_lists.py) && cp -a /workspace/tests/test_lists.py /tests/fixture/tests/test_lists.py
RUN mkdir -p /tests/fixture/$(dirname tests/test_number.py) && cp -a /workspace/tests/test_number.py /tests/fixture/tests/test_number.py
RUN mkdir -p /tests/fixture/$(dirname tests/test_time.py) && cp -a /workspace/tests/test_time.py /tests/fixture/tests/test_time.py


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
