FROM --platform=linux/amd64 ghcr.io/multimodal-art-projection/nl2repobench/autojump@sha256:85f4553300641c5771c1853dcf827857a7cde366f391383ba682d809f826a4e5

ENV PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN python -c "import platform, sys; assert platform.machine() == 'x86_64'; assert sys.version_info[:2] == (3, 13)"
RUN python -c "from importlib.metadata import version; assert version('pytest') == '8.4.1'; assert version('mock') == '5.2.0'"

RUN printf '%s  %s\n' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/workspace/tests/__init__.py' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/workspace/tests/integration/__init__.py' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/workspace/tests/unit/__init__.py' \
      '5f550d554877d587e8941307723db6eb70e7c434c28270a3f2987f6151a9022c' '/workspace/tests/unit/autojump_match_test.py' \
      '094a924a8aaf56c7cf24b77a1cf69ba50d4ddb495b39e484813abbf2922b927b' '/workspace/tests/unit/autojump_utils_test.py' \
    | sha256sum -c -

RUN mkdir -p /tests/fixture && \
    cp -a /workspace/tests /tests/fixture/tests && \
    chmod -R a-w /tests/fixture/tests

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true && \
    chmod 0555 /tests/test.sh && \
    chmod 0444 /tests/grade.py

WORKDIR /tests
