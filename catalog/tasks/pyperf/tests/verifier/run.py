"""Private deterministic scenarios for the pyperf public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/psf/pyperf,
v2.10.0, immutable revision dd93ccfda79214725293e95f1fa6e00cb4a64adc).
The candidate runner executes the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=30.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


# Scenarios derived from the public instruction contract for pyperf 2.10.0
CASES: list[tuple[str, str, object]] = [
    # Run construction and value access
    (
        "run-basic-construction",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), collect_metadata=False)\nresult = [type(r).__name__, len(r.values), r.values[0] == 0.001, r.values[2] == 0.003]",
        {"ok": True, "value": ["Run", 3, True, True]},
    ),
    (
        "run-reject-empty",
        "import pyperf\ntry:\n    pyperf.Run((), collect_metadata=False)\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    (
        "run-reject-negative",
        "import pyperf\ntry:\n    pyperf.Run((0.001, -0.001), collect_metadata=False)\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    (
        "run-reject-zero",
        "import pyperf\ntry:\n    pyperf.Run((0, 0.001), collect_metadata=False)\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    (
        "run-metadata-copy",
        "import pyperf\nmeta = {'name': 'test', 'custom': 42}\nr = pyperf.Run((0.001,), metadata=meta, collect_metadata=False)\nmeta['custom'] = 99\nresult = r.get_metadata()['custom']",
        {"ok": True, "value": 42},
    ),
    (
        "run-warmups",
        "import pyperf\nr = pyperf.Run((0.001, 0.002), warmups=[(10, 0.0001), (20, 0.0002)], collect_metadata=False)\nresult = [len(r.warmups), r.warmups[0][0], r.warmups[1][0]]",
        {"ok": True, "value": [2, 10, 20]},
    ),
    (
        "run-loops",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'loops': 100, 'inner_loops': 5}, collect_metadata=False)\nresult = [r.get_loops(), r.get_inner_loops(), r.get_total_loops()]",
        {"ok": True, "value": [100, 5, 500]},
    ),
    
    # Benchmark construction and methods
    (
        "benchmark-basic",
        "import pyperf\nr = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = [b.get_name(), b.get_nvalue(), b.get_nrun()]",
        {"ok": True, "value": ["test", 2, 1]},
    ),
    (
        "benchmark-reject-empty-runs",
        "import pyperf\ntry:\n    pyperf.Benchmark([])\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    (
        "benchmark-reject-no-name",
        "import pyperf\nr = pyperf.Run((0.001,), collect_metadata=False)\ntry:\n    pyperf.Benchmark([r])\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    (
        "benchmark-get-values",
        "import pyperf\nr1 = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nr2 = pyperf.Run((0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2])\nv = b.get_values()\nresult = [len(v), v[0], v[3]]",
        {"ok": True, "value": [4, 0.001, 0.004]},
    ),
    (
        "benchmark-statistics",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = [type(b.mean()).__name__, type(b.stdev()).__name__, type(b.median()).__name__]",
        {"ok": True, "value": ["float", "float", "float"]},
    ),
    (
        "benchmark-percentile",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = [type(b.percentile(0)).__name__, type(b.percentile(50)).__name__, type(b.percentile(100)).__name__]",
        {"ok": True, "value": ["float", "float", "float"]},
    ),
    (
        "benchmark-get-unit",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = type(b.get_unit()).__name__",
        {"ok": True, "value": "str"},
    ),
    (
        "benchmark-add-run",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1])\nr2 = pyperf.Run((0.002,), metadata={'name': 'test'}, collect_metadata=False)\nb.add_run(r2)\nresult = [b.get_nrun(), b.get_nvalue()]",
        {"ok": True, "value": [2, 2]},
    ),
    (
        "benchmark-add-run-type-error",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ntry:\n    b.add_run('not-a-run')\n    result = 'no-error'\nexcept TypeError:\n    result = 'TypeError'",
        {"ok": True, "value": "TypeError"},
    ),
    (
        "benchmark-metadata-copy",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nm = b.get_metadata()\nm['new'] = 'value'\nresult = 'new' in b.get_metadata()",
        {"ok": True, "value": False},
    ),
    (
        "benchmark-runs-copy",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nruns = b.get_runs()\nruns.append(None)\nresult = len(b.get_runs())",
        {"ok": True, "value": 1},
    ),
    
    # BenchmarkSuite
    (
        "suite-basic",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nresult = [len(s), s.get_benchmark_names()[0]]",
        {"ok": True, "value": [1, "test"]},
    ),
    (
        "suite-reject-empty",
        "import pyperf\ntry:\n    pyperf.BenchmarkSuite([])\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    (
        "suite-get-benchmark",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'alpha'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nresult = s.get_benchmark('alpha').get_name()",
        {"ok": True, "value": "alpha"},
    ),
    (
        "suite-get-benchmark-keyerror",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'alpha'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\ntry:\n    s.get_benchmark('missing')\n    result = 'no-error'\nexcept KeyError:\n    result = 'KeyError'",
        {"ok": True, "value": "KeyError"},
    ),
    (
        "suite-add-benchmark",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\ns = pyperf.BenchmarkSuite([b1])\ns.add_benchmark(b2)\nresult = [len(s), s.get_benchmark_names()]",
        {"ok": True, "value": [2, ["a", "b"]]},
    ),
    (
        "suite-benchmarks-copy",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nbenches = s.get_benchmarks()\nbenches.clear()\nresult = len(s.get_benchmarks())",
        {"ok": True, "value": 1},
    ),
    (
        "suite-iteration",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\ns = pyperf.BenchmarkSuite([b1, b2])\nresult = [bench.get_name() for bench in s]",
        {"ok": True, "value": ["a", "b"]},
    ),
    
    # JSON serialization
    (
        "suite-json-roundtrip",
        "import pyperf\nimport tempfile\nimport os\nr = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    s2 = pyperf.BenchmarkSuite.load(path)\n    result = [s2.get_benchmark_names()[0], len(s2.get_benchmark('test').get_values())]\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": ["test", 2]},
    ),
    (
        "suite-loads-dumps",
        "import pyperf\nimport json\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\njson_str = json.dumps({'version': '1.0', 'benchmarks': [{'name': 'test', 'runs': [{'values': [0.001], 'metadata': {'name': 'test'}}]}]})\ns2 = pyperf.BenchmarkSuite.loads(json_str)\nresult = s2.get_benchmark_names()[0]",
        {"ok": True, "value": "test"},
    ),
    (
        "suite-loads-reject-no-version",
        "import pyperf\ntry:\n    pyperf.BenchmarkSuite.loads('{\"benchmarks\": []}')\n    result = 'no-error'\nexcept (ValueError, KeyError):\n    result = 'error'",
        {"ok": True, "value": "error"},
    ),
    (
        "suite-loads-reject-empty-benchmarks",
        "import pyperf\ntry:\n    pyperf.BenchmarkSuite.loads('{\"version\": \"1.0\", \"benchmarks\": []}')\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    (
        "suite-dump-newline",
        "import pyperf\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    with open(path, 'rb') as f:\n        content = f.read()\n    result = content[-1:] == b'\\n'\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": True},
    ),
    
    # Runner construction
    (
        "runner-basic",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "runner-parse-args",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nargs = r.parse_args([])\nresult = type(args).__name__",
        {"ok": True, "value": "Namespace"},
    ),
    (
        "runner-bench-func",
        "import pyperf\ndef add(a, b):\n    return a + b\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.bench_func('add', add, 1, 2)\nresult = [hasattr(result_obj, 'get_name'), result_obj.get_name() if hasattr(result_obj, 'get_name') else 'Benchmark']",
        {"ok": True, "value": [True, "add"]},
    ),
    (
        "runner-timeit",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('addition', '1 + 1')\nresult = [hasattr(result_obj, 'get_name'), result_obj.get_name() if hasattr(result_obj, 'get_name') else 'Benchmark']",
        {"ok": True, "value": [True, "addition"]},
    ),
    (
        "runner-timeit-name-as-stmt",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('1 + 1')\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    (
        "runner-bench-time-func",
        "import pyperf\nimport time\ndef time_func(loops):\n    start = time.perf_counter()\n    for _ in range(loops):\n        _ = 1 + 1\n    return time.perf_counter() - start\nr = pyperf.Runner(values=1, processes=1, loops=10)\nr.parse_args([])\nresult_obj = r.bench_time_func('manual', time_func)\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    
    # add_runs helper
    (
        "add-runs-function",
        "import pyperf\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    r2 = pyperf.Run((0.002,), metadata={'name': 'test'}, collect_metadata=False)\n    b2 = pyperf.Benchmark([r2])\n    pyperf.add_runs(path, b2)\n    s2 = pyperf.BenchmarkSuite.load(path)\n    result = len(s2.get_benchmark('test').get_values())\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": 2},
    ),
    
    # More Run scenarios
    (
        "run-values-ordered",
        "import pyperf\nr = pyperf.Run((0.005, 0.001, 0.003, 0.002, 0.004), collect_metadata=False)\nresult = list(r.values)",
        {"ok": True, "value": [0.005, 0.001, 0.003, 0.002, 0.004]},
    ),
    (
        "run-metadata-get",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test', 'unit': 'second'}, collect_metadata=False)\nm = r.get_metadata()\nresult = [m['name'], m['unit']]",
        {"ok": True, "value": ["test", "second"]},
    ),
    (
        "run-warmups-empty",
        "import pyperf\nr = pyperf.Run((0.001,), collect_metadata=False)\nresult = len(r.warmups)",
        {"ok": True, "value": 0},
    ),
    
    # More Benchmark scenarios
    (
        "benchmark-mean-positive",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.mean() > 0",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-median-in-range",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = 0.001 <= b.median() <= 0.003",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-values-immutable",
        "import pyperf\nr = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nv = b.get_values()\nresult = type(v).__name__",
        {"ok": True, "value": "tuple"},
    ),
    
    # More Suite scenarios
    (
        "suite-names-ordered",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'z'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'a'}, collect_metadata=False)\nr3 = pyperf.Run((0.003,), metadata={'name': 'm'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\nb3 = pyperf.Benchmark([r3])\ns = pyperf.BenchmarkSuite([b1, b2, b3])\nresult = s.get_benchmark_names()",
        {"ok": True, "value": ["z", "a", "m"]},
    ),
    (
        "suite-add-runs-benchmark",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\ns = pyperf.BenchmarkSuite([b1])\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nb2 = pyperf.Benchmark([r2])\ns.add_runs(b2)\nresult = len(s)",
        {"ok": True, "value": 2},
    ),
    (
        "suite-add-runs-suite",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\ns1 = pyperf.BenchmarkSuite([b1])\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nb2 = pyperf.Benchmark([r2])\ns2 = pyperf.BenchmarkSuite([b2])\ns1.add_runs(s2)\nresult = len(s1)",
        {"ok": True, "value": 2},
    ),
    
    # JSON structure validation
    (
        "suite-json-has-version",
        "import pyperf\nimport json\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    with open(path) as f:\n        data = json.load(f)\n    result = 'version' in data\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": True},
    ),
    (
        "suite-json-has-benchmarks",
        "import pyperf\nimport json\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    with open(path) as f:\n        data = json.load(f)\n    result = [isinstance(data.get('benchmarks'), list), len(data['benchmarks'])]\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": [True, 1]},
    ),
    
    # Runner with metadata
    (
        "runner-with-metadata",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, metadata={'unit': 'second'})\nr.parse_args([])\nresult_obj = r.timeit('test', '1 + 1')\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    
    # Type validations
    (
        "run-values-type",
        "import pyperf\nr = pyperf.Run((0.001, 0.002), collect_metadata=False)\nresult = type(r.values).__name__",
        {"ok": True, "value": "tuple"},
    ),
    (
        "run-warmups-type",
        "import pyperf\nr = pyperf.Run((0.001,), warmups=[(10, 0.0001)], collect_metadata=False)\nresult = type(r.warmups).__name__",
        {"ok": True, "value": "tuple"},
    ),
    (
        "benchmark-get-runs-list",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = type(b.get_runs()).__name__",
        {"ok": True, "value": "list"},
    ),
    (
        "suite-get-benchmarks-list",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nresult = type(s.get_benchmarks()).__name__",
        {"ok": True, "value": "list"},
    ),
    
    # Additional edge cases
    (
        "run-single-value",
        "import pyperf\nr = pyperf.Run((0.001,), collect_metadata=False)\nresult = [len(r.values), r.values[0]]",
        {"ok": True, "value": [1, 0.001]},
    ),
    (
        "benchmark-single-run",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = [b.get_nrun(), b.get_nvalue()]",
        {"ok": True, "value": [1, 1]},
    ),
    (
        "suite-single-benchmark",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nresult = len(s)",
        {"ok": True, "value": 1},
    ),
    
    # Percentile edge cases
    (
        "benchmark-percentile-zero",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.percentile(0) > 0",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-percentile-hundred",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.percentile(100) > 0",
        {"ok": True, "value": True},
    ),
    
    # Multiple runs in benchmark
    (
        "benchmark-multiple-runs",
        "import pyperf\nr1 = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nr2 = pyperf.Run((0.003,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2])\nresult = [b.get_nrun(), b.get_nvalue()]",
        {"ok": True, "value": [2, 3]},
    ),
    
    # Loop calculations
    (
        "run-loops-default",
        "import pyperf\nr = pyperf.Run((0.001,), collect_metadata=False)\nresult = [r.get_loops(), r.get_inner_loops()]",
        {"ok": True, "value": [1, 1]},
    ),
    (
        "run-total-loops",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'loops': 10, 'inner_loops': 5}, collect_metadata=False)\nresult = r.get_total_loops()",
        {"ok": True, "value": 50},
    ),
    
    # Stdev and median_abs_dev
    (
        "benchmark-stdev-non-negative",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.stdev() >= 0",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-median-abs-dev",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.median_abs_dev() >= 0",
        {"ok": True, "value": True},
    ),
    
    # Suite filename
    (
        "suite-with-filename",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b], filename='test.json')\nresult = len(s)",
        {"ok": True, "value": 1},
    ),
    
    # Runner configurations
    (
        "runner-loops-param",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, loops=10)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "runner-min-time-param",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, min_time=0.5)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "runner-warmups-param",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, warmups=2)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    
    # Bench functions with inner_loops
    (
        "runner-bench-func-inner-loops",
        "import pyperf\ndef func():\n    return 1 + 1\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.bench_func('test', func, inner_loops=10)\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    (
        "runner-timeit-inner-loops",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('test', '1 + 1', inner_loops=10)\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    
    # Timeit with setup and teardown
    (
        "runner-timeit-setup",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('test', 'x + 1', setup='x = 10')\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    (
        "runner-timeit-teardown",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('test', 'x = 10', teardown='del x')\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    
    # Bench command
    (
        "runner-bench-command",
        "import pyperf\nimport sys\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.bench_command('python-version', [sys.executable, '--version'])\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    
    # JSON compact parameter
    (
        "suite-dump-compact",
        "import pyperf\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path, compact=True)\n    result = os.path.exists(path)\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": True},
    ),
    (
        "suite-dump-not-compact",
        "import pyperf\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path, compact=False)\n    result = os.path.exists(path)\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": True},
    ),
    
    # Metadata in runner benchmarks
    (
        "runner-timeit-metadata",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('test', '1 + 1', metadata={'unit': 'second'})\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    (
        "runner-bench-func-metadata",
        "import pyperf\ndef func():\n    return 42\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.bench_func('test', func, metadata={'custom': 'value'})\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    
    # Value ordering preservation
    (
        "benchmark-values-preserve-order",
        "import pyperf\nr1 = pyperf.Run((0.005, 0.001, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nr2 = pyperf.Run((0.002, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2])\nv = b.get_values()\nresult = [v[0], v[1], v[2], v[3], v[4]]",
        {"ok": True, "value": [0.005, 0.001, 0.003, 0.002, 0.004]},
    ),
    
    # Runner show_name parameter
    (
        "runner-show-name-true",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, show_name=True)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "runner-show-name-false",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, show_name=False)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    
    # Timeit globals parameter
    (
        "runner-timeit-globals",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('test', 'custom_var + 1', globals={'custom_var': 10})\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    
    # Duplicate parameter in timeit
    (
        "runner-timeit-duplicate",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('test', '1 + 1', duplicate=1024)\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    
    # More validation scenarios
    (
        "run-positive-values-only",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003, 0.004, 0.005), collect_metadata=False)\nresult = all(v > 0 for v in r.values)",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-name-from-first-run",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'first'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'first'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2])\nresult = b.get_name()",
        {"ok": True, "value": "first"},
    ),
    
    # JSON load from stdin (simulated with string)
    (
        "suite-loads-valid-json",
        "import pyperf\nimport json\ndata = {'version': '1.0', 'benchmarks': [{'name': 'test', 'runs': [{'values': [0.001, 0.002], 'metadata': {'name': 'test'}}]}]}\njson_str = json.dumps(data)\ns = pyperf.BenchmarkSuite.loads(json_str)\nresult = [len(s), s.get_benchmark('test').get_nvalue()]",
        {"ok": True, "value": [1, 2]},
    ),
    
    # Statistics return types
    (
        "benchmark-mean-float",
        "import pyperf\nr = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = isinstance(b.mean(), float)",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-stdev-float",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = isinstance(b.stdev(), float)",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-median-float",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = isinstance(b.median(), float)",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-percentile-float",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = isinstance(b.percentile(50), float)",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-median-abs-dev-float",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = isinstance(b.median_abs_dev(), float)",
        {"ok": True, "value": True},
    ),
    
    # Runner program_args parameter
    (
        "runner-program-args",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, program_args=['arg1', 'arg2'])\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    
    # Suite get_benchmark_names ordering
    (
        "suite-names-insertion-order",
        "import pyperf\nnames = ['first', 'second', 'third']\nbenches = []\nfor name in names:\n    r = pyperf.Run((0.001,), metadata={'name': name}, collect_metadata=False)\n    benches.append(pyperf.Benchmark([r]))\ns = pyperf.BenchmarkSuite(benches)\nresult = s.get_benchmark_names() == names",
        {"ok": True, "value": True},
    ),
    
    # Run with list vs tuple
    (
        "run-accepts-list",
        "import pyperf\nr = pyperf.Run([0.001, 0.002], collect_metadata=False)\nresult = len(r.values)",
        {"ok": True, "value": 2},
    ),
    
    # Benchmark add_run preserves name
    (
        "benchmark-add-run-same-name",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1])\nr2 = pyperf.Run((0.002,), metadata={'name': 'test'}, collect_metadata=False)\nb.add_run(r2)\nresult = b.get_name()",
        {"ok": True, "value": "test"},
    ),
    
    # Suite reject duplicate benchmark names
    (
        "suite-reject-duplicate-names",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'dup'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'dup'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\ns = pyperf.BenchmarkSuite([b1])\ntry:\n    s.add_benchmark(b2)\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    
    # More loop scenarios
    (
        "run-loops-metadata-only",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'loops': 50}, collect_metadata=False)\nresult = r.get_loops()",
        {"ok": True, "value": 50},
    ),
    (
        "run-inner-loops-metadata-only",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'inner_loops': 20}, collect_metadata=False)\nresult = r.get_inner_loops()",
        {"ok": True, "value": 20},
    ),
    
    # Benchmark values from multiple runs flattened
    (
        "benchmark-values-flattened",
        "import pyperf\nr1 = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nr2 = pyperf.Run((0.003,), metadata={'name': 'test'}, collect_metadata=False)\nr3 = pyperf.Run((0.004, 0.005), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2, r3])\nresult = list(b.get_values())",
        {"ok": True, "value": [0.001, 0.002, 0.003, 0.004, 0.005]},
    ),
    
    # Multiple benchmarks in suite
    (
        "suite-multiple-benchmarks",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nr3 = pyperf.Run((0.003,), metadata={'name': 'c'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\nb3 = pyperf.Benchmark([r3])\ns = pyperf.BenchmarkSuite([b1, b2, b3])\nresult = [len(s), s.get_benchmark_names()]",
        {"ok": True, "value": [3, ["a", "b", "c"]]},
    ),
    
    # Edge case: very small positive value
    (
        "run-tiny-positive-value",
        "import pyperf\nr = pyperf.Run((1e-9, 2e-9), collect_metadata=False)\nresult = [r.values[0] > 0, r.values[1] > 0]",
        {"ok": True, "value": [True, True]},
    ),
    
    # Edge case: many values
    (
        "run-many-values",
        "import pyperf\nvalues = [0.001 + i * 0.0001 for i in range(100)]\nr = pyperf.Run(values, collect_metadata=False)\nresult = [len(r.values), len(r.values) == 100]",
        {"ok": True, "value": [100, True]},
    ),
    
    # Benchmark percentile bounds
    (
        "benchmark-percentile-at-min",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = 0.001 <= b.percentile(0) <= 0.003",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-percentile-at-max",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = 0.001 <= b.percentile(100) <= 0.003",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-percentile-mid",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003, 0.004, 0.005), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = 0.001 <= b.percentile(50) <= 0.005",
        {"ok": True, "value": True},
    ),
    
    # Warmups with multiple pairs
    (
        "run-warmups-multiple",
        "import pyperf\nwarmups = [(i * 10, i * 0.001) for i in range(1, 6)]\nr = pyperf.Run((0.001,), warmups=warmups, collect_metadata=False)\nresult = [len(r.warmups), r.warmups[0][0], r.warmups[4][0]]",
        {"ok": True, "value": [5, 10, 50]},
    ),
    
    # Suite iteration produces benchmark objects
    (
        "suite-iteration-benchmark-type",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nresult = [type(bench).__name__ for bench in s]",
        {"ok": True, "value": ["Benchmark"]},
    ),
    
    # Metadata get returns dict
    (
        "run-metadata-returns-dict",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nresult = type(r.get_metadata()).__name__",
        {"ok": True, "value": "dict"},
    ),
    (
        "benchmark-metadata-returns-dict",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = type(b.get_metadata()).__name__",
        {"ok": True, "value": "dict"},
    ),
    
    # Unit default
    (
        "benchmark-unit-string",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = isinstance(b.get_unit(), str)",
        {"ok": True, "value": True},
    ),
    
    # Runner unexpected kwargs
    (
        "runner-bench-func-unexpected-kwarg",
        "import pyperf\ndef func():\n    return 42\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\ntry:\n    r.bench_func('test', func, unexpected_arg=True)\n    result = 'no-error'\nexcept TypeError:\n    result = 'TypeError'",
        {"ok": True, "value": "TypeError"},
    ),
    
    # Final validation scenarios
    (
        "run-construction-valid",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003, 0.004, 0.005), collect_metadata=False)\nresult = [isinstance(r.values, tuple), len(r.values)]",
        {"ok": True, "value": [True, 5]},
    ),
    (
        "benchmark-construction-valid",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = [b.get_name(), b.get_nvalue(), b.get_nrun()]",
        {"ok": True, "value": ["test", 1, 1]},
    ),
    (
        "suite-construction-valid",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nresult = [len(s), s.get_benchmark_names()[0]]",
        {"ok": True, "value": [1, "test"]},
    ),
    # Additional scenarios to reach 173 total
    (
        "run-collect-metadata-true",
        "import pyperf\nr = pyperf.Run((0.001,), collect_metadata=True)\nresult = isinstance(r.get_metadata(), dict)",
        {"ok": True, "value": True},
    ),
    (
        "run-collect-metadata-false",
        "import pyperf\nr = pyperf.Run((0.001,), collect_metadata=False)\nresult = isinstance(r.get_metadata(), dict)",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-median-single-value",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.median() == 0.001",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-mean-single-value",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.mean() == 0.001",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-stdev-two-values",
        "import pyperf\nr = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.stdev() > 0",
        {"ok": True, "value": True},
    ),
    (
        "suite-load-file-object",
        "import pyperf\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    with open(path) as f:\n        s2 = pyperf.BenchmarkSuite.load(f)\n    result = s2.get_benchmark_names()[0]\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": "test"},
    ),
    (
        "suite-dump-replace-false",
        "import pyperf\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path, replace=False)\n    result = os.path.exists(path)\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": True},
    ),
    (
        "runner-parse-args-with-list",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nargs = r.parse_args(['--debug-single-value'])\nresult = type(args).__name__",
        {"ok": True, "value": "Namespace"},
    ),
    (
        "run-large-values",
        "import pyperf\nr = pyperf.Run((1.5, 2.5, 3.5), collect_metadata=False)\nresult = [r.values[0], r.values[2]]",
        {"ok": True, "value": [1.5, 3.5]},
    ),
    (
        "benchmark-get-values-ordering",
        "import pyperf\nr1 = pyperf.Run((0.003, 0.001), metadata={'name': 'test'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2])\nv = b.get_values()\nresult = [v[0], v[1], v[2]]",
        {"ok": True, "value": [0.003, 0.001, 0.002]},
    ),
    (
        "suite-add-benchmark-ordering",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'first'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\ns = pyperf.BenchmarkSuite([b1])\nr2 = pyperf.Run((0.002,), metadata={'name': 'second'}, collect_metadata=False)\nb2 = pyperf.Benchmark([r2])\ns.add_benchmark(b2)\nresult = s.get_benchmark_names()",
        {"ok": True, "value": ["first", "second"]},
    ),
    (
        "run-warmups-tuple-structure",
        "import pyperf\nr = pyperf.Run((0.001,), warmups=[(5, 0.0001), (10, 0.0002)], collect_metadata=False)\nresult = [r.warmups[0][1], r.warmups[1][1]]",
        {"ok": True, "value": [0.0001, 0.0002]},
    ),
    (
        "benchmark-percentile-25",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = 0.001 <= b.percentile(25) <= 0.004",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-percentile-75",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = 0.001 <= b.percentile(75) <= 0.004",
        {"ok": True, "value": True},
    ),
    (
        "suite-json-version-format",
        "import pyperf\nimport json\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    with open(path) as f:\n        data = json.load(f)\n    result = isinstance(data.get('version'), str)\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": True},
    ),
    (
        "suite-json-benchmarks-array",
        "import pyperf\nimport json\nimport tempfile\nimport os\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    with open(path) as f:\n        data = json.load(f)\n    result = isinstance(data['benchmarks'], list)\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": True},
    ),
    (
        "runner-values-positive-requirement",
        "import pyperf\nr = pyperf.Runner(values=5, processes=1)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "runner-processes-positive-requirement",
        "import pyperf\nr = pyperf.Runner(values=1, processes=2)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "run-metadata-name-key",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'mytest'}, collect_metadata=False)\nresult = r.get_metadata()['name']",
        {"ok": True, "value": "mytest"},
    ),
    (
        "benchmark-get-runs-order",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2])\nruns = b.get_runs()\nresult = [runs[0].values[0], runs[1].values[0]]",
        {"ok": True, "value": [0.001, 0.002]},
    ),
    (
        "suite-get-benchmarks-order",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\ns = pyperf.BenchmarkSuite([b1, b2])\nbenches = s.get_benchmarks()\nresult = [benches[0].get_name(), benches[1].get_name()]",
        {"ok": True, "value": ["a", "b"]},
    ),
    (
        "run-loops-one-default",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={}, collect_metadata=False)\nresult = r.get_loops()",
        {"ok": True, "value": 1},
    ),
    (
        "run-inner-loops-one-default",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={}, collect_metadata=False)\nresult = r.get_inner_loops()",
        {"ok": True, "value": 1},
    ),
    (
        "run-total-loops-default",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={}, collect_metadata=False)\nresult = r.get_total_loops()",
        {"ok": True, "value": 1},
    ),
    (
        "benchmark-median-even-count",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = 0.001 <= b.median() <= 0.004",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-median-odd-count",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.median() == 0.002",
        {"ok": True, "value": True},
    ),
    (
        "suite-len-method",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nr3 = pyperf.Run((0.003,), metadata={'name': 'c'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\nb3 = pyperf.Benchmark([r3])\ns = pyperf.BenchmarkSuite([b1, b2, b3])\nresult = len(s)",
        {"ok": True, "value": 3},
    ),
    (
        "runner-bench-func-args",
        "import pyperf\ndef multiply(a, b, c):\n    return a * b * c\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.bench_func('mul', multiply, 2, 3, 4)\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    (
        "runner-timeit-multiline",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('test', 'x = 1\\ny = 2\\nz = x + y')\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    (
        "run-float-values",
        "import pyperf\nr = pyperf.Run((0.123, 0.456, 0.789), collect_metadata=False)\nresult = [isinstance(v, float) for v in r.values]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "benchmark-add-run-increases-nvalue",
        "import pyperf\nr1 = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1])\nold_nvalue = b.get_nvalue()\nr2 = pyperf.Run((0.003,), metadata={'name': 'test'}, collect_metadata=False)\nb.add_run(r2)\nresult = b.get_nvalue() > old_nvalue",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-add-run-increases-nrun",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1])\nold_nrun = b.get_nrun()\nr2 = pyperf.Run((0.002,), metadata={'name': 'test'}, collect_metadata=False)\nb.add_run(r2)\nresult = b.get_nrun() > old_nrun",
        {"ok": True, "value": True},
    ),
    (
        "suite-add-benchmark-increases-len",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\ns = pyperf.BenchmarkSuite([b1])\nold_len = len(s)\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nb2 = pyperf.Benchmark([r2])\ns.add_benchmark(b2)\nresult = len(s) > old_len",
        {"ok": True, "value": True},
    ),
    (
        "suite-iteration-count",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\ns = pyperf.BenchmarkSuite([b1, b2])\ncount = sum(1 for _ in s)\nresult = count",
        {"ok": True, "value": 2},
    ),
    (
        "run-values-immutable-tuple",
        "import pyperf\nr = pyperf.Run((0.001, 0.002), collect_metadata=False)\nresult = isinstance(r.values, tuple)",
        {"ok": True, "value": True},
    ),
    (
        "run-warmups-immutable-tuple",
        "import pyperf\nr = pyperf.Run((0.001,), warmups=[(10, 0.0001)], collect_metadata=False)\nresult = isinstance(r.warmups, tuple)",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-metadata-immutable-copy",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test', 'key': 'value'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nm1 = b.get_metadata()\nm1['key'] = 'changed'\nm2 = b.get_metadata()\nresult = m2['key']",
        {"ok": True, "value": "value"},
    ),
    (
        "suite-benchmarks-immutable-copy",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nbenches1 = s.get_benchmarks()\nbenches1.append(None)\nbenches2 = s.get_benchmarks()\nresult = len(benches2)",
        {"ok": True, "value": 1},
    ),
    (
        "runner-min-time-positive",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, min_time=1.0)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "runner-loops-zero-calibration",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, loops=0)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "runner-loops-explicit-positive",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, loops=100)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "run-metadata-with-unit",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test', 'unit': 'second'}, collect_metadata=False)\nresult = 'unit' in r.get_metadata()",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-unit-from-metadata",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test', 'unit': 'millisecond'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.get_unit()",
        {"ok": True, "value": "millisecond"},
    ),
    (
        "suite-json-preserves-names",
        "import pyperf\nimport tempfile\nimport os\nr1 = pyperf.Run((0.001,), metadata={'name': 'alpha'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'beta'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\ns = pyperf.BenchmarkSuite([b1, b2])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    s2 = pyperf.BenchmarkSuite.load(path)\n    result = s2.get_benchmark_names()\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": ["alpha", "beta"]},
    ),
    (
        "suite-json-preserves-values",
        "import pyperf\nimport tempfile\nimport os\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\ns = pyperf.BenchmarkSuite([b])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    s2 = pyperf.BenchmarkSuite.load(path)\n    result = list(s2.get_benchmark('test').get_values())\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": [0.001, 0.002, 0.003]},
    ),
    (
        "runner-parse-args-empty-list",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nargs = r.parse_args([])\nresult = hasattr(args, '__dict__')",
        {"ok": True, "value": True},
    ),
    (
        "runner-bench-func-no-args",
        "import pyperf\ndef zero_args():\n    return 42\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.bench_func('test', zero_args)\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    (
        "runner-timeit-minimal",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.timeit('minimal', 'pass')\nresult = hasattr(result_obj, 'get_name')",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-mean-multiple-runs",
        "import pyperf\nr1 = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nr2 = pyperf.Run((0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2])\nresult = b.mean() > 0",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-median-multiple-runs",
        "import pyperf\nr1 = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nr2 = pyperf.Run((0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2])\nresult = b.median() > 0",
        {"ok": True, "value": True},
    ),
    (
        "benchmark-stdev-multiple-runs",
        "import pyperf\nr1 = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nr2 = pyperf.Run((0.003, 0.004), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r1, r2])\nresult = b.stdev() >= 0",
        {"ok": True, "value": True},
    ),
    (
        "suite-get-benchmark-by-name",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'first'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'second'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\ns = pyperf.BenchmarkSuite([b1, b2])\nresult = [s.get_benchmark('first').get_name(), s.get_benchmark('second').get_name()]",
        {"ok": True, "value": ["first", "second"]},
    ),
    (
        "run-metadata-arbitrary-keys",
        "import pyperf\nr = pyperf.Run((0.001,), metadata={'name': 'test', 'custom_key': 'custom_value', 'number': 42}, collect_metadata=False)\nm = r.get_metadata()\nresult = [m['custom_key'], m['number']]",
        {"ok": True, "value": ["custom_value", 42]},
    ),
    (
        "benchmark-values-positive",
        "import pyperf\nr = pyperf.Run((0.001, 0.002, 0.003), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = all(v > 0 for v in b.get_values())",
        {"ok": True, "value": True},
    ),
    (
        "suite-add-runs-preserves-order",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'first'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\ns = pyperf.BenchmarkSuite([b1])\nr2 = pyperf.Run((0.002,), metadata={'name': 'second'}, collect_metadata=False)\nr3 = pyperf.Run((0.003,), metadata={'name': 'third'}, collect_metadata=False)\nb2 = pyperf.Benchmark([r2])\nb3 = pyperf.Benchmark([r3])\ns.add_runs(b2)\ns.add_runs(b3)\nresult = s.get_benchmark_names()",
        {"ok": True, "value": ["first", "second", "third"]},
    ),
    (
        "runner-warmups-count",
        "import pyperf\nr = pyperf.Runner(values=1, processes=1, warmups=3)\nresult = type(r).__name__",
        {"ok": True, "value": "Runner"},
    ),
    (
        "run-two-values",
        "import pyperf\nr = pyperf.Run((0.001, 0.002), collect_metadata=False)\nresult = len(r.values)",
        {"ok": True, "value": 2},
    ),
    (
        "benchmark-two-values",
        "import pyperf\nr = pyperf.Run((0.001, 0.002), metadata={'name': 'test'}, collect_metadata=False)\nb = pyperf.Benchmark([r])\nresult = b.get_nvalue()",
        {"ok": True, "value": 2},
    ),
    (
        "suite-two-benchmarks",
        "import pyperf\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\ns = pyperf.BenchmarkSuite([b1, b2])\nresult = len(s)",
        {"ok": True, "value": 2},
    ),
    (
        "runner-bench-func-single-call",
        "import pyperf\ndef simple():\n    return 1\nr = pyperf.Runner(values=1, processes=1)\nr.parse_args([])\nresult_obj = r.bench_func('simple', simple)\nresult = result_obj.get_name()",
        {"ok": True, "value": "simple"},
    ),
    (
        "suite-json-roundtrip-multiple",
        "import pyperf\nimport tempfile\nimport os\nr1 = pyperf.Run((0.001,), metadata={'name': 'a'}, collect_metadata=False)\nr2 = pyperf.Run((0.002,), metadata={'name': 'b'}, collect_metadata=False)\nb1 = pyperf.Benchmark([r1])\nb2 = pyperf.Benchmark([r2])\ns = pyperf.BenchmarkSuite([b1, b2])\nfd, path = tempfile.mkstemp(suffix='.json')\ntry:\n    os.close(fd)\n    s.dump(path)\n    s2 = pyperf.BenchmarkSuite.load(path)\n    result = len(s2)\nfinally:\n    os.unlink(path)",
        {"ok": True, "value": 2},
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
