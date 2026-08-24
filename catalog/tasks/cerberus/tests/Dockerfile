FROM ghcr.io/multimodal-art-projection/nl2repobench/cerberus@sha256:b097a72dfc814cc9cd26a418a4a413e2ea6bafafbef6e567413976ed70fba946

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
RUN mkdir -p /tests/fixture/$(dirname cerberus/tests) && cp -a /workspace/cerberus/tests /tests/fixture/cerberus/tests
RUN mkdir -p /tests/fixture/$(dirname cerberus/benchmarks/test_overall_performance_1.py) && cp -a /workspace/cerberus/benchmarks/test_overall_performance_1.py /tests/fixture/cerberus/benchmarks/test_overall_performance_1.py
RUN mkdir -p /tests/fixture/$(dirname cerberus/benchmarks/test_overall_performance_2.py) && cp -a /workspace/cerberus/benchmarks/test_overall_performance_2.py /tests/fixture/cerberus/benchmarks/test_overall_performance_2.py


COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
