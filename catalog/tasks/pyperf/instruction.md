# Project Description

Create a complete installable Python package named `pyperf` from an empty workspace.

The project is a benchmarking library and result-file toolkit.

It lets a caller register callable or statement benchmarks.

It runs repeated measurements through worker processes.

It exposes benchmark values and summary statistics.

It serializes benchmark suites as JSON.

It provides a command-line interface for creating, inspecting, and transforming files.

The implementation must be a normal Python distribution, not a collection of snippets.

The package must import as `pyperf` after installation.

The command-line entry point must be available as `pyperf`.

The module form `python -m pyperf` must invoke the same command-line interface.

The implementation must not depend on network access at runtime.

Do not include upstream tests, private test fixtures, or source-control metadata in the package.

## Natural Language Instruction

Implement the public behavior of pyperf version 2.10.0 described in this specification.

Start from an empty `workspace/` directory and create all packaging metadata and source files.

Provide the `pyperf` import package and its public root exports.

Provide a `Runner` that accepts benchmark configuration and registers benchmark operations.

Support callable benchmarks with `Runner.bench_func`.

Support loop-aware timing callbacks with `Runner.bench_time_func`.

Support statement benchmarks with `Runner.timeit`.

Support asynchronous callable registration with `Runner.bench_async_func`.

Support external command registration with `Runner.bench_command`.

Provide immutable-style run records and benchmark aggregation objects.

Provide JSON loading, dumping, and round-trip behavior for benchmark suites.

Provide the `pyperf` and `python -m pyperf` command entry points.

Keep public values ordered and make repeated serialization structurally stable.

Use explicit exceptions for invalid values, malformed records, duplicate names, and bad options.

Do not promise exact timing magnitudes: timing depends on the host and is intentionally not tested.

Do not hard-code host CPU counts, CPU model strings, process scheduling, or wall-clock durations.

The package should use `psutil` only for the documented optional system metadata operations.

## Supports / Environment Configuration

Use Python 3.12 on a Debian 12 compatible Linux environment.

The upstream package declares Python `>=3.9` and runtime dependency `psutil>=5.9.0`.

Declare the package name `pyperf` and version `2.10.0` in packaging metadata.

Use a standard setuptools build backend and an installable wheel or editable package.

The console script entry point is `pyperf = pyperf.__main__:main`.

The module entry point is `pyperf.__main__:main`.

Runtime tests run without network access.

Do not download source code, dependencies, benchmark data, or metadata during execution.

All dependencies required by the test image are installed during image construction.

The candidate implementation must work when invoked from a clean working directory.

Environment variables and host metadata may affect displayed metadata, but not JSON shape.

Timing values are positive numeric samples and may differ between runs.

The test harness may use small process and value counts to keep tests bounded.

Do not require a terminal, isolated CPUs, elevated privileges, or a specific processor.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── setup.cfg                         # optional compatibility metadata
├── pyperf/
│   ├── __init__.py
│   ├── __main__.py
│   ├── _bench.py
│   ├── _runner.py
│   ├── _timeit.py
│   ├── _timeit_cli.py
│   ├── _metadata.py
│   ├── _formatter.py
│   ├── _utils.py
│   └── ...                           # supporting public behavior modules
└── README.rst                        # concise package documentation
```

`pyperf/__init__.py` must expose the documented root imports.

`pyperf/__main__.py` must contain the console/module command dispatcher.

The underscored files above are implementation modules; their internal helpers are not public.

Do not add a second differently named package or a competing console entry point.

## API Usage Guide

### Root package: `pyperf`

Import path: `pyperf.Run`.

Signature: `Run(values, warmups=None, metadata=None, collect_metadata=True)`.

`values` is a non-empty iterable of positive numeric measurement values.

`warmups` is optional and contains `(loops, value)` pairs with integer loop counts.

`metadata` is an optional mapping of JSON-compatible benchmark metadata.

`collect_metadata=True` permits collection of environment metadata before applying overrides.

The returned run exposes a tuple-like ordered `values` property.

It exposes a tuple-like `warmups` property, empty when no warmups were supplied.

`get_metadata()` returns a dictionary copy of metadata.

`get_loops()`, `get_inner_loops()`, and `get_total_loops()` return loop counts.

Invalid, non-positive, or empty measurement input raises `ValueError`.

Invalid warmup pairs raise `ValueError`.

Example: `pyperf.Run((0.001, 0.002), collect_metadata=False)` retains two values in order.

Boundary: `pyperf.Run((), collect_metadata=False)` must be rejected rather than creating an empty run.

### Root package: benchmark records

Import path: `pyperf.Benchmark`.

Signature: `Benchmark(runs)` where `runs` is a non-empty sequence of `Run` objects.

The first run must contain a benchmark name in its metadata.

`get_name()` returns that benchmark name.

`get_values()` returns one ordered tuple containing values from all non-calibration runs.

`get_nvalue()` returns the number of values returned by `get_values()`.

`get_nrun()` returns the number of runs in the benchmark.

`get_runs()` returns a list copy of the run records.

`get_metadata()` returns common metadata shared by the runs.

`mean()`, `stdev()`, `median()`, and `median_abs_dev()` return numeric summaries.

`percentile(p)` accepts a number in the inclusive range 0 through 100.

`get_unit()` returns the benchmark unit, defaulting to the package timing unit when absent.

`add_run(run)` appends a compatible `Run` and invalidates derived summaries.

A non-`Run` passed to `add_run` raises `TypeError`.

Incompatible checked metadata raises `ValueError`.

Example: constructing a `Run` with `metadata={"name": "sort"}` permits `Benchmark((run,))`.

Boundary: `Benchmark(())` and a first run without a name must both raise `ValueError`.

### Root package: benchmark suites

Import path: `pyperf.BenchmarkSuite`.

Signature: `BenchmarkSuite(benchmarks, filename=None)`.

`benchmarks` is a non-empty sequence of `Benchmark` objects.

`get_benchmark_names()` returns names in suite insertion order.

`get_benchmarks()` returns a list copy.

`get_benchmark(name)` returns the matching benchmark or raises `KeyError`.

`add_benchmark(benchmark)` rejects duplicate benchmark objects and duplicate names.

`add_runs(result)` accepts a `Benchmark` or another `BenchmarkSuite`.

`__len__()` reports the number of benchmarks and iteration preserves insertion order.

`BenchmarkSuite.loads(string)` parses a supported JSON string.

`BenchmarkSuite.load(file)` accepts a filename, `-` for standard input, or a text file object.

`dump(file, compact=True, replace=False)` writes a JSON suite and terminates it with a newline.

The JSON root includes a supported `version` and a `benchmarks` array.

A benchmark JSON record preserves its name, values, and applicable metadata.

Unsupported versions, malformed JSON, empty suites, and duplicate benchmark names raise errors.

Example: `suite.dump("result.json")` followed by `BenchmarkSuite.load("result.json")` preserves names and values.

Boundary: loading JSON without a supported `version` or without benchmarks must fail clearly.

### Root package helper

Import path: `pyperf.add_runs`.

Signature: `add_runs(filename, result)`.

`filename` identifies an existing benchmark JSON file.

`result` is a compatible `Benchmark` or benchmark result to merge into that file.

The helper updates the file while preserving compatible suite structure.

It must reject incompatible result types and incompatible metadata.

### Root package: `Runner`

Import path: `pyperf.Runner`.

Signature: `Runner(values=None, processes=None, loops=0, min_time=0.1, metadata=None, show_name=True, program_args=None, add_cmdline_args=None, _argparser=None, warmups=1)`.

`values` controls values collected per process; a positive configured value is required.

`processes` controls worker process count and must be positive when supplied.

`loops` is zero for automatic calibration or a non-negative explicit count.

`min_time` is the positive minimum target duration used by calibration.

`metadata` supplies metadata added to produced runs.

`show_name` controls presentation of the benchmark name.

The runner adds command-line options for process count, values, warmups, loops, output, and display.

Only one `Runner` instance of a given runner class may be created in one process.

`parse_args(args=None)` parses and stores runner options, returning the parsed namespace.

### Runner callable methods

Import path: `pyperf.Runner.bench_func`.

Signature: `bench_func(name, func, *args, **kwargs)`.

It benchmarks calling `func(*args)` and returns a `Benchmark`-compatible result in manager mode.

`name` is a unique non-empty benchmark name for that runner.

Keyword options include documented `inner_loops` and `metadata`.

Unexpected keyword arguments raise `TypeError`.

Import path: `pyperf.Runner.bench_time_func`.

Signature: `bench_time_func(name, time_func, *args, **kwargs)`.

`time_func` receives a loop count followed by `*args` and returns elapsed numeric time.

The method records values while preserving the benchmark name and supplied metadata.

Import path: `pyperf.Runner.bench_async_func`.

Signature: `bench_async_func(name, func, *args, **kwargs)`.

`func(*args)` is awaited in the benchmark worker.

The optional `loop_factory`, `inner_loops`, and `metadata` settings are passed through.

Import path: `pyperf.Runner.timeit`.

Signature: `timeit(name, stmt=None, setup="pass", teardown="pass", inner_loops=None, duplicate=None, metadata=None, globals=None)`.

`stmt` is benchmark code; when omitted, the name is used as the statement.

`setup` and `teardown` are code snippets used around the statement.

The result has the same benchmark value and JSON shape guarantees as callable benchmarks.

Import path: `pyperf.Runner.bench_command`.

Signature: `bench_command(name, command)`.

`command` is a command argument sequence for an external process benchmark.

The command method preserves the benchmark name and reports subprocess failures as errors.

Do not make timing values exact or host-dependent values part of the public contract.

## Command-Line Usage

`pyperf show file.json` displays one or more benchmark files.

`pyperf hist file.json` displays a histogram without changing the file.

`pyperf stats file.json` displays statistics for the selected benchmarks.

`pyperf metadata file.json` displays metadata.

`pyperf check file.json` checks benchmark stability.

`pyperf dump file.json` displays stored runs.

`pyperf timeit 'expression'` runs a quick statement benchmark.

`pyperf collect_metadata` collects environment metadata and can write JSON with `-o`.

`pyperf convert input.json --stdout` writes a transformed suite to standard output.

A valid command exits with status 0.

A missing file, malformed JSON, unsupported option, or invalid benchmark input exits non-zero.

Output intended as JSON must parse as JSON and use a root object with benchmark data.

Human-readable output may contain timing text, but its exact numeric formatting is not contractual.

## Implementation Notes

Keep benchmark values in insertion order; do not sort values unless an API explicitly requests it.

Preserve benchmark names and compatible metadata during merges and JSON round trips.

Use copies when returning metadata, run lists, benchmark lists, or other mutable containers.

Reject negative and zero measurement values according to the documented `Run` contract.

Keep JSON serialization deterministic in key ordering and structural shape.

Do not expose private helper names as root exports merely because they appear in source modules.

Worker processes may be used internally, but tests must still work with small process counts.

Do not require CPU affinity, elevated scheduling priority, or Linux-specific files for core APIs.

Metadata collection should degrade gracefully when optional host information is unavailable.

The command-line layer and library layer must agree on the same JSON format.

The implementation may report warnings for unstable measurements without changing valid values.

Do not write secrets, absolute host paths, or verifier reports into benchmark output.

## Examples and Error Handling

Normal example: create a named `Run`, wrap it in a `Benchmark`, and inspect `get_values()`.

```python
import pyperf
run = pyperf.Run((0.001, 0.002), metadata={"name": "demo"}, collect_metadata=False)
bench = pyperf.Benchmark((run,))
print(bench.get_values())
```

Normal example: create a suite, dump it to JSON, load it again, and compare names and value shapes.

```python
suite = pyperf.BenchmarkSuite((bench,))
suite.dump("result.json")
loaded = pyperf.BenchmarkSuite.load("result.json")
assert loaded.get_benchmark_names() == ["demo"]
```

Normal example: register `Runner.timeit("addition", "1 + 1")` and write output with `-o result.json`.

```python
runner = pyperf.Runner(values=1, processes=1)
runner.timeit("addition", "1 + 1")
```

Normal example: invoke `python -m pyperf metadata result.json` and inspect successful output.

```text
python -m pyperf metadata result.json
```

Boundary example: reject `Run((0, -1), collect_metadata=False)` with `ValueError`.

Boundary example: reject `BenchmarkSuite.loads("{}")` because it is not a supported suite document.

Boundary example: reject a duplicate benchmark name rather than silently replacing the first one.

Boundary example: reject an invalid percentile outside the inclusive 0–100 range.

Non-bindable behavior: exact nanosecond or second values vary with CPU, OS load, Python build, and scheduler.

Non-bindable behavior: CPU model, CPU count, affinity, process priority, and host metadata vary by environment.

Non-bindable behavior: calibration duration and the number of internal worker retries are implementation/runtime details.

Tests should therefore assert positive numeric values, ordering, types, JSON keys, exit codes, and exceptions.

They must not assert a particular measured magnitude, CPU identity, wall-clock duration, or process schedule.
