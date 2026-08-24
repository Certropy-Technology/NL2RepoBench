FROM --platform=linux/amd64 ghcr.io/multimodal-art-projection/nl2repobench/coverage_shield@sha256:78b52f4c9cbf18b368a958cb3b933727c0a30b064b1fa33492e887129565f4c9

RUN mkdir -p /tests/fixture \
    && cp -a /workspace/tests /tests/fixture/tests \
    && find /tests/fixture -type d -name __pycache__ -prune -exec rm -rf '{}' + \
    && rm -rf /workspace/tests

COPY fixture-manifest.sha256 /tests/fixture-manifest.sha256
RUN sha256sum --check --strict /tests/fixture-manifest.sha256

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod 0555 /tests/test.sh \
    && chmod 0444 /tests/grade.py /tests/fixture-manifest.sha256 \
    && find /tests/fixture -type d -exec chmod 0555 '{}' + \
    && find /tests/fixture -type f -exec chmod 0444 '{}' +

WORKDIR /tests
