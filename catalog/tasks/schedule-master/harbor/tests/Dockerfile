FROM --platform=linux/amd64 ghcr.io/multimodal-art-projection/nl2repobench/schedule-master@sha256:903e864b08437cacb1dbf4305f6ecc1443d09c6af7a714e2d81c4c5fee2d6677

ENV TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN printf '%s  %s\n' \
      '05bba4db69922fc2a9722451e668bb0bcc86d9a1b26550864abd7a631c46c66a' \
      '/workspace/test_schedule.py' | sha256sum -c - && \
    python -c "import pytest, pytz; assert pytest.__version__ == '8.4.1'; assert pytz.__version__ == '2025.2'"

RUN python -c "import site; open('/opt/sitepkg', 'w', encoding='utf-8').write(site.getsitepackages()[0])" && \
    mkdir -p /tests/fixture && \
    cp -a /workspace/test_schedule.py /tests/fixture/test_schedule.py

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py

RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod 0555 /tests/test.sh && chmod 0444 /tests/grade.py /tests/fixture/test_schedule.py

WORKDIR /tests
