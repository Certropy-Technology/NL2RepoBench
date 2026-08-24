FROM --platform=linux/amd64 ghcr.io/multimodal-art-projection/nl2repobench/records@sha256:03378b1619c4ddcfebb0f3941e8fd448fe2754cf9489f13594cb0b40551f5a2d

ENV PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN python -c "from importlib.metadata import version; assert version('pytest') == '8.4.1'; assert version('SQLAlchemy') == '2.0.43'; assert version('tablib') == '3.8.0'; assert version('openpyxl') == '3.1.5'; assert version('docopt') == '0.6.2'"
RUN printf '%s  %s\n' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/workspace/tests/__init__.py' \
      'ee39073d4f9fd5e91bf740bf227096abf0d8212a12f9c9000ae398ae4636c93c' '/workspace/tests/conftest.py' \
      '84558af919e0ff2256adfb026cbda8399a86f58a9c1cce51dca074fde3364073' '/workspace/tests/test_105.py' \
      '58d9ba8a6b4358ece2e11b61bb70d8e14ffddbc08e2d1df1163d15ce7bc6396d' '/workspace/tests/test_69.py' \
      'adaf50f977a0d0a7574995e58d75dad3935b99e4e6f696f479bda7b90aae9587' '/workspace/tests/test_records.py' \
      'f830d4b33e36a27ed0930af28259f6f6064cd154489e64cea8fa47f7d8d2f759' '/workspace/tests/test_transactions.py' \
    | sha256sum -c -

RUN python -c "import site; open('/opt/sitepkg', 'w', encoding='utf-8').write(site.getsitepackages()[0])" && \
    mkdir -p /tests/fixture && \
    cp -a /workspace/tests /tests/fixture/tests && \
    chmod -R a-w /tests/fixture/tests

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true \
    && chmod 0555 /tests/test.sh \
    && chmod 0444 /tests/grade.py

WORKDIR /tests
