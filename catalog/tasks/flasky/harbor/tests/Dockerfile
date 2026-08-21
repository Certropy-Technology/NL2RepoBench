FROM --platform=linux/amd64 ghcr.io/multimodal-art-projection/nl2repobench/flasky@sha256:dd7c1ab35038eb22f5637d7fb8d210d2a6bf080d65ca72c89b4ac31af3e0c342

ENV PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN python -c "import sys; assert sys.version_info[:3] == (3, 9, 23)" && \
    python -c "from importlib.metadata import version; assert version('pytest') == '8.4.1'; assert version('Flask') == '0.12.2'; assert version('Flask-SQLAlchemy') == '2.5.1'; assert version('SQLAlchemy') == '1.4.46'"

RUN printf '%s  %s\n' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/workspace/tests/__init__.py' \
      'd45d5ffc8e05844cf2cdefc3c44710f79bdce461b1a474db879599173c1f07e8' '/workspace/tests/test_api.py' \
      'f0c1ff49a91f2e677e421793fa0df86515e1905c56b65442183a5148cc8e7c1c' '/workspace/tests/test_basics.py' \
      '421fcbba7a1b8148f4cabf030298d3c2b9a4b5b1b18ad54463848d478bc383b3' '/workspace/tests/test_client.py' \
      '95be8206326b64e524bb6216e291ba7dc597e64b4d99a70478633f0f5d0cdd28' '/workspace/tests/test_selenium.py' \
      '7c0ead17f8b367e15be40b3cb9088c7d1fa196f870a4db572a4a31c2528ec76c' '/workspace/tests/test_user_model.py' \
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
