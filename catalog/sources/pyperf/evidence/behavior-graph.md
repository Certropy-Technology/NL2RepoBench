# Public behavior graph

| behavior | public surface | observable contract | excluded
|---|---|---|---|
| root imports | `pyperf.Run`, `pyperf.Benchmark`, `pyperf.BenchmarkSuite`, `pyperf.add_runs`, `pyperf.Runner`, `pyperf.format_metadata` | imports and names resolve | internal import order |
| run values | `pyperf.Run(values, warmups=None, metadata=None, collect_metadata=True)` | positive values retain order; invalid/empty input raises | host metadata |
| benchmark aggregation | `pyperf.Benchmark((run,))` | ordered `get_values()` and consistent `get_nvalue()` | measured timings |
| suite JSON | `pyperf.BenchmarkSuite.loads(text)` and `dump(file)` | supported JSON has version/benchmarks and round-trips | host metadata |
| runner | `pyperf.Runner(...).bench_func/timeit/bench_time_func` | result exposes values and JSON output | timing magnitude/scheduling |
| CLI | `pyperf.__main__:main` | valid command exits zero and output shape is stable | CPU and wall time |
