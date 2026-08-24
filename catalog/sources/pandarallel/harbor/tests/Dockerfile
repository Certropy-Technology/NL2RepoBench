FROM --platform=linux/amd64 ghcr.io/multimodal-art-projection/nl2repobench/pandarallel@sha256:f25336a4bdcab50fb33ef2cb008c10634915e98e7dcbe167750a5190fc46ed38

ENV PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN python -c "import sys; assert sys.version_info[:3] == (3, 10, 18)" && \
    python -c "from importlib.metadata import version; assert version('pytest') == '8.4.1'; assert version('pandas') == '2.3.2'; assert version('numpy') == '2.2.6'; assert version('psutil') == '7.0.0'; assert version('dill') == '0.4.0'; assert version('pyarrow') == '21.0.0'"

RUN test "$(find /workspace/tests -type f | wc -l)" -eq 1 && \
    test "$(stat -c '%a' /workspace/tests/test_pandarallel.py)" = 755 && \
    test "$(stat -c '%a' /workspace/setup.py)" = 755 && \
    printf '%s  %s\n' \
      '94c75928f37417101654b14bd9598951e82c462fb0120b040c804229aaacbbe5' '/workspace/tests/test_pandarallel.py' \
      '843ac26c38a41abae578250bc0f9419194b320a0f67327d941037a4268f6cfe7' '/workspace/setup.py' \
    | sha256sum -c -

RUN python -c "import site; open('/opt/sitepkg', 'w', encoding='utf-8').write(site.getsitepackages()[0])" && \
    mkdir -p /tests/fixture && \
    cp -a /workspace/tests /tests/fixture/tests && \
    chmod -R a-w /tests/fixture/tests

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true && \
    chmod 0555 /tests/test.sh && \
    chmod 0444 /tests/grade.py

WORKDIR /tests
