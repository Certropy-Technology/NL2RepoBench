FROM ghcr.io/multimodal-art-projection/nl2repobench/pythonprojecttemplate@sha256:a5623b41263e82ee18f602b1cb5b2d511720dfcfd8c8db26d07ebbef97eb8f71

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture && cp -a /workspace/tests /tests/fixture/tests

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
