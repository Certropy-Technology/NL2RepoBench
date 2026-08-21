FROM --platform=linux/amd64 ghcr.io/multimodal-art-projection/nl2repobench/pyperclip@sha256:a3cac678d154fc68b673495484f834c92daa4aa3db42e0008264a49c3f7d2769

RUN mkdir -p /tests/fixture/tests \
    && cp -a /workspace/tests/test_pyperclip.py /tests/fixture/tests/test_pyperclip.py \
    && test "$(sha256sum /tests/fixture/tests/test_pyperclip.py | cut -d' ' -f1)" = "4e4570c598bece8cc307fa1f52966063b1d23d5e466218720c76a6ddf3437963" \
    && rm -rf /workspace \
    && mkdir -p /workspace

RUN test -z "$(command -v xclip || true)" \
    && test -z "$(command -v xsel || true)" \
    && test -z "$(command -v wl-copy || true)" \
    && test -z "$(command -v wl-paste || true)" \
    && test -z "$(command -v klipper || true)" \
    && test -z "$(command -v qdbus || true)" \
    && test ! -e /dev/clipboard

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py

RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod 0555 /tests/test.sh \
    && chmod 0444 /tests/grade.py /tests/fixture/tests/test_pyperclip.py

ENV DISPLAY="" \
    WAYLAND_DISPLAY="" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

WORKDIR /tests
