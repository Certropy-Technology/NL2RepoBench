FROM ghcr.io/multimodal-art-projection/nl2repobench/flask-restful@sha256:79d845aef38ea77517f3d4e6f7b38440d06c717d1cce2c1869bedaabe3856237

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname tests) && cp -a /workspace/tests /tests/fixture/tests
RUN python -m pip install --no-cache-dir pytest 'Flask==1.1.4' 'Werkzeug==1.0.1' 'Jinja2==2.11.3' 'MarkupSafe==2.0.1' 'itsdangerous==1.1.0' 'click==7.1.2' aniso8601 six pytz mock blinker

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
