FROM --platform=linux/amd64 ghcr.io/multimodal-art-projection/nl2repobench/pss@sha256:38e0fcf6fb1a74781d6d57c524c750be9e56f0173193733c4a23cf6e8c8d1459

ENV PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN python -c "import platform, sys; assert platform.machine() == 'x86_64'; assert sys.version_info[:3] == (3, 10, 11)"
RUN python -c "from importlib.metadata import version; assert version('pytest') == '8.4.1'; assert version('colorama') == '0.4.6'"

# The base image is the immutable holder of the hidden fixture. The manifest
# is generated inside the image so no hidden test bytes enter this task tree.
RUN mkdir -p /tests/fixture && \
    cp -a /workspace/test /tests/fixture/test && \
    (cd /tests/fixture/test && find . -type f -print0 | sort -z | xargs -0 sha256sum) \
      > /tests/fixture/test.sha256 && \
    printf '%s  %s\n' \
      'a96a99bebf5625c230bf8032a144f24cbaad3ca423a302a441fe5abf7520c321' \
      '/tests/fixture/test.sha256' | sha256sum -c - && \
    chmod -R a-w /tests/fixture/test && \
    chmod 0444 /tests/fixture/test.sha256

RUN python -c "import site; open('/opt/sitepkg', 'w', encoding='utf-8').write(site.getsitepackages()[0])" && \
    useradd --uid 10001 --create-home candidate 2>/dev/null || true

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN chmod 0555 /tests/test.sh && chmod 0444 /tests/grade.py

WORKDIR /tests
