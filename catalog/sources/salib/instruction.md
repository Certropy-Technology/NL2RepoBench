## Project Description

Build an installable Python package named `SALib` (imported as `SALib`) for
global sensitivity analysis of deterministic model outputs. The intended users
are scientists and engineers who describe a bounded model-input space, produce
an output for each sampled input row, and then quantify which inputs influence
that output. The package boundary is numerical analysis: it accepts a problem
description and numeric arrays and returns samples or sensitivity statistics.
It is not a web service, a data store, a plotting application, or a replacement
for the user's model function.

The implementation must expose the public sampler and analyzer modules under
`SALib.sample` and `SALib.analyze`. Samplers turn a problem dictionary and a
sample count into a two-dimensional numeric array. The caller evaluates its
model outside the library and passes the resulting one-dimensional output array
to an analyzer. An analyzer returns a mapping of named sensitivity measures to
numeric arrays (and, where applicable, confidence intervals or other
diagnostic arrays). Preserve input variable order and return stable key names.

This source record is currently blocked as a production benchmark task. The
scientific dependency closure, frozen numerical environment, deterministic
denominator, and separate verifier adapter have not been established. The
implementation requested here must nevertheless be a normal package that can
be installed offline when its declared environment is available; do not hide
missing dependencies behind network downloads or silently substitute unrelated
algorithms.

## Supports

- Runtime: Python 3.10 or newer. The authoring environment records Python 3.13
  on Linux/amd64; the package must not depend on CPython-private behavior.
- Package manager: `pip`. Provide install metadata in `pyproject.toml` and make
  the project installable with `python -m pip install .` when dependencies are
  available. Do not add standard-library modules such as `math`, `json`, or
  `statistics` as pip dependencies.
- Runtime dependencies declared by the pinned project metadata are
  `numpy>=2.0`, `scipy>=1.9.3`, `pandas>=2.0`, `matplotlib>=3.5`, and
  `multiprocess`. Distributed execution may use the optional
  `pathos>=0.3.2` extra. Keep dependency names and supported version ranges
  consistent with the project metadata; do not invent a lock file or claim
  that an offline wheel cache exists.
- Run-time network policy is no-network. The candidate, its tests, and any
  verifier must not access GitHub, PyPI, DNS, a package mirror, or another
  external service. Dependency installation belongs to an offline preparation
  step and must fail clearly if the required packages are unavailable.
- The generated project should have this public layout (additional package
  internals are allowed only when they are needed by these entry points):

  ```text
  workspace/
  ├── pyproject.toml
  ├── README.md
  ├── src/
  │   └── SALib/
  │   ├── __init__.py
  │   ├── util/
  │   │   ├── __init__.py
  │   │   ├── problem.py
  │   │   └── results.py
  │   ├── analyze/
  │   │   ├── __init__.py
  │   │   ├── sobol.py
  │   │   ├── morris.py
  │   │   ├── fast.py
  │   │   ├── delta.py
  │   │   ├── dgsm.py
  │   │   ├── pawn.py
  │   │   ├── discrepancy.py
  │   │   ├── ff.py
  │   │   └── hdmr.py
  │   ├── sample/
  │   │   ├── __init__.py
  │   │   ├── saltelli.py
  │   │   ├── sobol.py
  │   │   ├── morris.py
  │   │   ├── fast_sampler.py
  │   │   ├── finite_diff.py
  │   │   ├── ff.py
  │   │   └── latin.py
  │   └── test_functions/
  │       ├── __init__.py
  │       ├── Ishigami.py
  │       ├── Sobol_G.py
  │       ├── lake_problem.py
  │       ├── linear_model_1.py
  │       ├── linear_model_2.py
  │       └── oakley2004.py
  │   └── scripts/
  │       └── salib.py
  └── README.md
  ```

- The package must import without performing network access or starting a
  process. The console entry point `salib = SALib.scripts.salib:main` is
  required and must return a nonzero exit status for malformed input rather
  than printing a fabricated result.
- The harness supplies an empty workspace and performs installation before
  importing the candidate. Do not assume the repository checkout, an editable
  install, current working directory, or a pre-existing output directory.

## API Usage Guide

The following APIs are the public numerical surface. Use the module paths
exactly as shown. All `problem` dictionaries contain at least `num_vars`,
`names`, and `bounds`; optional `groups`, `dists`, and `outputs` have one entry
per relevant variable or output. `names` is an ordered list of unique strings
and `bounds` is an ordered list of numeric distribution parameters, normally
`[lower, upper]`. `X` is a finite two-dimensional NumPy array with one column
per variable; `Y` is a finite one-dimensional NumPy array with one value per row
of `X`. Reject incompatible dimensions, invalid bounds, unsupported
distributions, non-finite values, and non-positive sample counts with a clear
exception rather than returning a partial result.

An ordinary problem is:

```python
problem = {
    "num_vars": 2,
    "names": ["rate", "capacity"],
    "bounds": [[0.0, 1.0], [10.0, 20.0]],
}
```

The three structural fields must agree. `groups`, when present, has one group
label per parameter; `outputs`, when present, names model-output columns. An
empty problem is not a valid sampling or analysis problem. A mismatch such as
two names and one bound must fail during validation, not return a partial array.

### `SALib.sample.saltelli.sample`

```python
SALib.sample.saltelli.sample(problem, N, calc_second_order=True,
                             skip_values=None)
```

`problem` is a valid problem dictionary and `N` is a positive integer base
sample count. The optional boolean controls whether second-order Sobol columns
are included. For `D` variables, the return shape is `(N * (2*D + 2), D)` with
second-order terms and `(N * (D + 2), D)` otherwise. `skip_values=None` chooses
a power-of-two offset at least as large as `N`; an explicit non-power-of-two or
too-small offset may emit a `UserWarning`. Rows are generated in the exact
construction order consumed by Sobol analysis. This deprecated compatibility
function has no filesystem or network side effect and does not evaluate a model.

```python
from SALib.sample import saltelli
X = saltelli.sample({"num_vars": 2, "names": ["a", "b"],
                     "bounds": [[0, 1], [0, 1]]}, 64)
```

For an empty or zero-dimensional problem, or for `N<=0`, raise `ValueError`;
do not return an unlabelled array. In normal use `calc_second_order=False`
removes the second-order portion while preserving the first-order row order.

### `SALib.sample.sobol.sample`

```python
SALib.sample.sobol.sample(problem, N, *, calc_second_order=True,
                          scramble=True, skip_values=0, seed=None)
```

`N` is a positive integer base size; `scramble` is boolean, `skip_values` is a
non-negative integer, and `seed` is `None`, an integer, or a NumPy
`Generator`. The return has shape `(N * (2*D + 2), D)` with second-order terms
and `(N * (D + 2), D)` without them; columns follow `problem["names"]`. With a
fixed integer seed, the same problem and options produce the same values and
shape. `scramble=False` removes LMS+shift scrambling, while `skip_values`
skips initial sequence points. The function has no filesystem or network side
effects.

```python
from SALib.sample import sobol
X = sobol.sample({"num_vars": 1, "names": ["temperature"],
                  "bounds": [[250, 350]]}, 16, seed=7)
```

Reject negative `skip_values`, malformed bounds, and a zero-variable problem.
An empty `Y` array is not a valid sampler input; sampling an empty model is an
error, not a special result.

### `SALib.sample.morris.sample`

```python
SALib.sample.morris.sample(problem, N, num_levels=4,
                           optimal_trajectories=None,
                           local_optimization=True, seed=None)
```

`N` is the number of trajectories and `num_levels` is an even positive grid
level count. `optimal_trajectories` is either `None` or an integer from 2
through `N`; `local_optimization` selects the faster local trajectory-selection
strategy (the default). Without groups each trajectory has `D+1` rows; with
`G` groups it has `G+1` rows. The returned matrix has `D` columns, is
trajectory-major, and is compatible with Morris analysis. `seed` controls the
randomized construction. It does not call the model or modify the problem
mapping.

```python
from SALib.sample import morris
X = morris.sample({"num_vars": 2, "names": ["x", "y"],
                   "bounds": [[0, 1], [10, 20]]}, 8, seed=3)
```

Reject `N <= 0`, invalid levels, and an empty problem with `ValueError` (or the
specific input-validation exception used consistently by the package). A
fixed seed is the determinism contract; an unspecified seed may vary between
runs.

### `SALib.sample.fast_sampler.sample`

```python
SALib.sample.fast_sampler.sample(problem, N, M=4, seed=None)
```

`N` is a positive sample count and `M` is the positive number of Fourier
harmonics. Return an `(N*D, D)` NumPy array with one column per problem
variable. The order of columns and rows is deterministic for identical inputs
and a fixed seed; the function has no persistent side effects. `N` must be
large enough for the selected harmonics or validation must fail rather than
aliasing frequencies.

```python
from SALib.sample import fast_sampler
X = fast_sampler.sample({"num_vars": 2, "names": ["u", "v"],
                         "bounds": [[-1, 1], [0, 4]]}, 32, M=4, seed=11)
```

Reject a non-positive `M`, a non-positive `N`, or bounds that cannot be mapped
to the sampler domain. No rows should be returned for invalid input.

### `SALib.sample.finite_diff.sample`

```python
SALib.sample.finite_diff.sample(problem, N, delta=0.01, seed=None,
                                skip_values=1024) -> numpy.ndarray
```

Generate the derivative-based global sensitivity design. For each of `N`
quasi-random base points, return the base row followed by one finite-difference
perturbation per variable, giving shape `(N*(D+1), D)`. `delta` is a positive
percentage step and `skip_values` is a non-negative Sobol offset. `seed` has
the standard `None`/integer/Generator forms. Rows are scaled to the problem
bounds and remain in base/perturbation block order for `analyze.dgsm`.

```python
from SALib.sample import finite_diff
X = finite_diff.sample(problem, 32, delta=0.01, seed=8)
```

For two variables this has shape `(96, 2)`. Reject `N<=0`, `delta<=0`,
negative skips, malformed bounds, or incompatible dimensions; do not evaluate a
model or write a file.

### `SALib.sample.ff.sample`

```python
SALib.sample.ff.sample(problem, seed=None) -> numpy.ndarray
```

Generate a two-level fractional-factorial design. If `D` is not a power of two,
pad the problem to the next power of two using uniquely named dummy variables
and matching bounds. The matrix has the padded column count and contrast order
expected by `SALib.analyze.ff.analyze`; original columns retain their order.
The effective design is deterministic for the same problem. A three-variable
problem therefore has four columns; a four-variable problem has no dummy
column. Empty or inconsistent problems are invalid.

### `SALib.sample.latin.sample`

```python
SALib.sample.latin.sample(problem, N, seed=None)
```

`problem` supplies the ordered bounded variables and `N` is a positive number
of rows. Return a two-dimensional NumPy array of shape `(N, num_vars)`, scaled
to each variable's bounds. A fixed seed makes the row values reproducible;
columns remain in problem order. The call does not evaluate a model or write
files.

```python
from SALib.sample import latin
X = latin.sample({"num_vars": 2, "names": ["left", "right"],
                  "bounds": [[0, 1], [100, 200]]}, 10, seed=5)
```

Reject `N <= 0`, missing bounds, and inconsistent name/bound counts. An empty
problem has no valid Latin-hypercube representation and should raise an input
error.

### `SALib.analyze.sobol.analyze`

```python
SALib.analyze.sobol.analyze(problem, Y, calc_second_order=True,
                            num_resamples=100, conf_level=0.95,
                            print_to_console=False, parallel=False,
                            n_processors=None, keep_resamples=False,
                            seed=None)
```

`Y` is a one-dimensional numeric output array compatible with the selected
Sobol sampling design. `num_resamples` is positive, `conf_level` is between
zero and one, and the boolean/processor options control reporting and optional
parallel calculation. Return a dictionary containing the standard Sobol
first-order (`S1`), total-order (`ST`), and confidence-interval arrays; when
second-order analysis is enabled it also contains the second-order array and
its interval. Array positions follow `problem["names"]`, and repeated calls
with a fixed seed and identical inputs are reproducible. Console printing is
disabled by default and must not replace the returned mapping.

```python
from SALib.analyze import sobol
stats = sobol.analyze(problem, model_outputs, seed=9)
```

Reject output arrays with incompatible length, non-finite values, invalid
confidence levels, or an empty problem. Do not silently truncate `Y`.

### `SALib.analyze.morris.analyze`

```python
SALib.analyze.morris.analyze(problem, X, Y, num_resamples=100,
                             conf_level=0.95, print_to_console=False,
                             num_levels=4, seed=None, grid_jump=2,
                             optimal_trajectories=None,
                             local_optimization=False)
```

`X` and `Y` describe the same evaluated trajectories. Return a mapping whose
standard numeric arrays include Morris elementary-effect summaries (`mu`,
`mu_star`, and `sigma`) and associated confidence information, with one entry
per problem variable. Preserve variable order. Fixed seeds make resampling
reproducible; console output is optional and must not be the API result.

```python
from SALib.analyze import morris
stats = morris.analyze(problem, X, Y, num_resamples=50, seed=4)
```

Reject row/column mismatches, invalid levels or confidence values, and empty
input. The analyzer must not mutate `X`, `Y`, or `problem`.

### `SALib.analyze.fast.analyze`

```python
SALib.analyze.fast.analyze(problem, Y, M=4, print_to_console=False)
```

`Y` is the output vector from a compatible FAST sample and `M` is the positive
FAST parameter. Return a mapping of first-order and total-order sensitivity
arrays keyed by the public names documented by the package, in problem order.
The function is pure apart from optional console output and rejects incompatible
lengths, invalid `M`, and empty input.

### `SALib.analyze.delta.analyze`

```python
SALib.analyze.delta.analyze(problem, X, Y, num_resamples=100,
    conf_level=0.95, print_to_console=False, seed=None, y_resamples=None,
    method="all", bootstrap_savedf=None, bins_specs={}) -> ResultDict
```

This moment-independent analysis accepts any compatible `(N,D)` input matrix
and length-`N` output vector. `method` is `"all"`, `"delta"`, or `"sobol"`.
The result contains `names`, `notes`, the requested balanced/step/raw delta
indices and confidence fields, and/or first-order `S1` fields, each in problem
order. `num_resamples` and `y_resamples` (when given) are positive and
`0 < conf_level < 1`. `bins_specs` maps parameter names to an integer number of
bins or ordered bin boundaries; empty specs use defaults. `bootstrap_savedf`,
when supplied, writes a diagnostic bootstrap DataFrame to that caller-selected
path. Equal integer seeds reproduce bootstrap results. Unknown methods, unknown
parameter names, unusable bins, too-small classes, and row mismatches raise an
analysis error or emit the documented warning; they must not silently drop a
variable.

```python
from SALib.analyze import delta
stats = delta.analyze(problem, X, Y, method="all", seed=5)
```

An ordinary Latin design is compatible. A bin specification outside the data
range must be rejected or replaced only with an explicit warning-backed
fallback. `print_to_console=True` prints results without changing the mapping.

### `SALib.analyze.dgsm.analyze`

```python
SALib.analyze.dgsm.analyze(problem, X, Y, num_resamples=100,
    conf_level=0.95, print_to_console=False, seed=None) -> ResultDict
```

Analyze the block layout returned by `finite_diff.sample`. Return ordered
`names`, `vi`, `vi_std`, `dgsm`, and `dgsm_conf` arrays of length `D`. `X` and
`Y` must preserve each base point followed by its D perturbations. Confidence
resampling uses the supplied seed. Zero perturbations, incompatible block
lengths, non-finite data, and invalid confidence levels are validation errors
or explicit undefined numerical results; they must not be silently reordered.

```python
from SALib.analyze import dgsm
stats = dgsm.analyze(problem, X, model_outputs, seed=8)
```

Deleting one output from a valid evaluation breaks the block structure and must
fail before returning a partial result. Console printing is optional.

### `SALib.analyze.pawn.analyze`

```python
SALib.analyze.pawn.analyze(problem, X, Y, S=10,
                           print_to_console=False, seed=None) -> ResultDict
```

Perform PAWN moment-independent analysis on any matching input/output rows. `S`
is a positive number of conditioning intervals. Return `names` plus the
per-variable `minimum`, `mean`, `median`, `maximum`, `CV`, and `stdev` PAWN
statistics in problem order. NaN observations are ignored when a valid statistic
remains. Grouped factors are analyzed individually and combined by group in
declared group order. `seed` controls random tie/resampling behavior. Too few
finite observations, `S<=0`, and row mismatches are invalid. A column containing
only NaNs must be reported undefined, not assigned a fabricated zero.

### `SALib.analyze.rbd_fast.analyze`

```python
SALib.analyze.rbd_fast.analyze(problem, X, Y, M=10,
    num_resamples=100, conf_level=0.95, print_to_console=False,
    seed=None) -> ResultDict
```

Perform Random Balanced Design FAST on a matching `(N,D)` design and output
vector. `M` is the positive harmonic count. Return an ordered `S1` array of
length `D` plus any method-documented confidence fields. Inputs must remain
finite and aligned by row; `num_resamples` is positive and confidence levels
are in `(0,1)`. The seed controls resampling. Wrong rows, invalid harmonics, or
empty arrays fail explicitly. `print_to_console` only adds a report.

### `SALib.analyze.rsa.analyze`

```python
SALib.analyze.rsa.analyze(problem, X, Y, bins=20,
                           print_to_console=False) -> ResultDict
```

Use regional sensitivity analysis on a matching design and output vector. The
positive `bins` count partitions the output into regions and the returned
mapping retains parameter names and the per-parameter regional measures in
problem order. Equal arrays and options produce equal numerical results; no
random or filesystem behavior is required. Invalid dimensions, non-positive
bins, non-finite values, and empty problems must raise a clear input error.
`print_to_console` does not alter the return value.

### `SALib.util.read_param_file`

```python
SALib.util.read_param_file(filename, delimiter=None) -> dict
```

Read one variable per non-empty text record. Columns are parameter name, lower
bound, upper bound, optional group, and optional distribution. With
`delimiter=None`, whitespace separates columns; a provided delimiter separates
columns literally. Return ordered `names`, `bounds`, `num_vars`, `groups`, and
`dists`; `dists` is `None` when all variables are uniform. Numeric columns are
numbers, not strings. Missing files raise the normal file exception and
malformed rows raise a validation error. An empty file cannot become a valid
zero-variable problem.

```text
x1 -3.14 3.14
x2 -3.14 3.14
```

```python
problem = SALib.util.read_param_file("params.txt")
```

### `SALib.util.handle_seed` and `scale_samples`

```python
SALib.util.handle_seed(seed) -> numpy.random.Generator
SALib.util.scale_samples(params: numpy.ndarray, problem: dict) -> numpy.ndarray
```

`handle_seed` accepts `None`, an integer or integer sequence, a NumPy
`SeedSequence`, `BitGenerator`, or existing `Generator`. Equal integer seeds
create equal initial streams; a supplied generator is reused and therefore
advances when consumed. Unsupported seed objects follow NumPy validation
errors. `scale_samples` transforms a two-dimensional unit-hypercube array to
the problem bounds and optional distributions, preserving shape and order. It
records the compatibility `sample_scaled` marker in `problem`; callers should
pass a copy when they need unscaled inputs. Invalid columns, distributions, or
parameters raise errors. For example, `[[0],[.5],[1]]` against `[[10,20]]`
maps to the lower bound, midpoint, and upper bound; `(N,0)` against a nonempty
problem is invalid.

### `SALib.util.results.ResultDict`

```python
from SALib.util.results import ResultDict
ResultDict(*args, **kwargs)
result.to_df()
result.plot(ax=None)
```

`ResultDict` is dictionary-like storage for named NumPy analysis arrays and
parameter names. Method-specific `to_df()` returns one DataFrame or an ordered
tuple of DataFrames (for example total, first, and optional second-order Sobol
tables). `plot` returns Matplotlib axes and does not call `show()` or write a
file. Conversion and plotting do not mutate numerical entries. Missing fields
may raise `KeyError`; an empty result must not invent indices.

### `SALib.ProblemSpec`

```python
from SALib import ProblemSpec
ProblemSpec(*args, **kwargs)
sp.sample(func, *args, **kwargs) -> ProblemSpec
sp.set_samples(samples) -> ProblemSpec
sp.evaluate(func, *args, **kwargs) -> ProblemSpec
sp.evaluate_parallel(func, *args, nprocs=None, **kwargs) -> ProblemSpec
sp.set_results(results) -> ProblemSpec
sp.analyze(func, *args, **kwargs) -> ProblemSpec
sp.analyze_parallel(func, *args, nprocs=None, **kwargs) -> ProblemSpec
sp.to_df()
sp.plot(**kwargs)
sp.heatmap(metric=None, index=None, title=None, ax=None)
```

`ProblemSpec` is a dictionary-like problem object with `samples`, `results`,
and `analysis` state. `sample` calls a user sampler with the problem first,
stores its two-dimensional NumPy result, clears stale downstream state, and
returns `self`. `evaluate` calls a model with `samples` as its first argument,
stores its one- or two-dimensional output, clears old analysis, and returns
`self`. `analyze` calls the selected analyzer with the stored problem and
arrays, stores its result, and returns `self`; parallel methods preserve row
order and cap workers to useful work. `set_samples` and `set_results` accept
already computed arrays and return `self`, with compatible first dimensions
required. Missing upstream state, non-array callable results, or incompatible
rows are errors. New samples must invalidate old results and analysis.

Dynamic methods such as `sample_sobol`, `sample_latin`, `sample_morris`,
`sample_fast_sampler`, `analyze_sobol`, and `analyze_morris` forward arguments
to the corresponding module API while supplying stored state. This enables:

```python
sp = ProblemSpec(problem)
sp.sample_sobol(128, seed=7).evaluate(model).analyze_sobol(seed=7)
X, Y, S = sp.samples, sp.results, sp.analysis
```

`to_df()` uses the method-specific pandas conversion. `plot()` returns axes for
result bars and `heatmap()` returns the supplied or newly created axes; neither
opens a blocking GUI. Calling `evaluate` before sampling or `analyze` before
results must fail rather than fabricate empty arrays. Plotting requires an
available analysis and works with a non-interactive backend.

### `SALib.test_functions`

The bundled benchmark functions are vectorized public model functions. They
preserve observation order, return NumPy arrays, and have no filesystem,
process, or network side effects. Normal NumPy shape/broadcast exceptions are
appropriate for incompatible inputs.

```python
from SALib.test_functions import Ishigami, Sobol_G
Ishigami.evaluate(X, A=7.0, B=0.1) -> numpy.ndarray
Sobol_G.evaluate(values, a=None, delta=None, alpha=None) -> numpy.ndarray
Sobol_G.sensitivity_index(a, alpha=None) -> numpy.ndarray
Sobol_G.total_sensitivity_index(a, alpha=None) -> numpy.ndarray
```

Ishigami requires `(N,3)` and returns `(N,)`; an empty `(0,3)` input returns an
empty vector. Sobol G accepts `(N,D)` and optional length-`D` parameter arrays;
the index helpers return one value per factor. Equal inputs and arguments are
deterministic, while incompatible coefficient lengths fail.

```python
from SALib.test_functions import linear_model_1, linear_model_2
linear_model_1.evaluate(values) -> numpy.ndarray
linear_model_2.evaluate(values) -> numpy.ndarray
```

The linear models require `(N,5)` and return `(N,)`. The first uses equal
weights; the second uses descending weights from five to one. All-zero rows
return zero and empty `(0,5)` inputs return empty vectors.

```python
from SALib.test_functions import lake_problem, oakley2004
lake_problem.evaluate(values, nvars=100, seed=101) -> numpy.ndarray
lake_problem.evaluate_lake(values, seed=101) -> numpy.ndarray
lake_problem.lake_problem(X, a=0.1, q=2.0, b=0.42, eps=0.02)
oakley2004.evaluate(X, A, M) -> numpy.ndarray
```

Lake `evaluate` consumes columns ordered `a,q,b,mean,stdev,delta,alpha` and
returns four objectives; `evaluate_lake` consumes `a,q,b,mean,stdev` and
returns phosphorus trajectories. `nvars` must be positive and equal seeds
reproduce stochastic inflows. `oakley2004.evaluate` returns one deterministic
value per compatible observation. Empty dimensionally valid arrays return empty
outputs; incompatible columns or broadcast shapes are errors.

### `salib` CLI

The installed executable provides:

```text
salib sample METHOD [OPTIONS]
salib analyze METHOD [OPTIONS]
```

Sampling methods are `sobol`, `saltelli`, `latin`, `morris`, `fast_sampler`,
`finite_diff`, and `ff`; analysis methods are `sobol`, `morris`, `fast`,
`delta`, `dgsm`, `pawn`, `discrepancy`, `ff`, and `hdmr`. `-h`/`--help` prints
top-level, action, or method help. No action prints top-level help and exits;
unknown actions, methods, and flags are argparse errors with nonzero status.

Common sample invocation and flags:

```text
salib sample METHOD -n INT -p PARAMFILE -o OUTPUT
                         [-s SEED] [--delimiter TEXT] [--precision INT]
```

`-n/--samples`, `-p/--paramfile`, and `-o/--output` are required. `-s/--seed`
defaults to `None`, `--delimiter` defaults to one space, and `--precision`
defaults to 8. The command writes a numeric matrix one row per line in Python
API order. Method-specific options mirror their function arguments.

Common analysis invocation and flags:

```text
salib analyze METHOD -p PARAMFILE -Y MODEL_OUTPUT_FILE
                          [-c COLUMN] [--delimiter TEXT] [-s SEED]
```

`-p/--paramfile` and `-Y/--model-output-file` are required; `-c/--column` is
zero-based and defaults to 0, `--delimiter` defaults to one space, and `-s`
defaults to `None`. Analysis reads the selected output column and prints a
result table. Missing files, malformed numeric data, out-of-range columns, and
incompatible lengths produce nonzero status and a diagnostic on stderr. Help
does not require input files and invalid commands must not create unrelated
files.

## Implementation Notes

- Keep sampling and analysis separate. A sampler returns numeric input rows; it
  must never call a user model, read a URL, or write a result file. An analyzer
  consumes caller-provided outputs and must validate that the dimensions agree
  with the problem and the sampling design.
- Preserve the ordered correspondence between `names`, `bounds`, columns of
  `X`, and positions in every returned sensitivity array. Return ordinary
  Python dictionaries or the package's documented mapping type with stable
  keys; do not use unordered output to encode variable order.
- Use NumPy/SciPy numeric operations and document floating-point tolerance in
  tests. Do not compare floating-point results by string formatting, and do
  not turn NaN or infinity into a plausible sensitivity score. Seeded paths
  must be reproducible without changing global random state unexpectedly.
- Optional parallel execution must be explicitly controlled, clean up child
  processes, and provide the same result as the serial path within the
  documented numerical tolerance. No multiprocessing setup may be required at
  import time.
- Validate before expensive computation: `num_vars` must agree with names and
  bounds, bounds must contain two finite ordered values, and every input row
  must have the expected number of columns. Raise a descriptive `ValueError`
  or the package's documented input exception; never silently drop rows.
- Keep imports, packaging, and examples usable in a no-network environment.
  Do not download data, use a remote random seed, or rely on a user's current
  directory. Avoid adding a CLI or public re-export unless its behavior is
  fully specified and tested.
- Treat a supplied NumPy `Generator` as caller-owned state: do not reseed it,
  replace it with the process-global legacy RNG, or serialize it into a result.
  Integer seeds should be normalized once at the public boundary. Parallel
  workers may receive independent reproducible streams, but merging their
  outputs must follow original row order and must close all pools on both
  success and exception.
- Keep serialization simple and loss-aware. CLI numeric files should be
  readable by `numpy.loadtxt` with the selected delimiter and precision; names,
  groups, and distribution metadata belong to the parameter file, not to an
  undocumented header embedded in sample rows. DataFrame conversion may add
  labels but must not round or stringify the underlying sensitivity values.
- Public exceptions should identify the invalid contract (for example, a
  Sobol output length inconsistent with `N`, `D`, and `calc_second_order`) and
  should occur before creating output files. Warnings are appropriate for
  documented deprecated APIs or statistically weak designs, not as a way to
  accept malformed arrays. Plotting must remain safe in headless CI by using
  the caller's axes or a non-interactive backend.

Small verifiable examples for the completed package include:

1. A two-variable bounded problem produces a two-column Latin sample, and the
   same integer seed reproduces the same array.
2. A model evaluated row-by-row on a valid sampler output can be passed to an
   analyzer, whose returned arrays have one element per declared variable.
3. Reversing the declared variable order reverses the corresponding input
   columns and named result positions; it must not silently reorder variables.
4. Passing an output vector with one fewer value than the sample rows raises a
   validation exception before a partial sensitivity mapping is returned.

5. A problem with Unicode names such as `"温度"` and `"压力"` retains those
   names in the returned analysis mapping and DataFrame; encoding must not
   change the column order or replace names with numeric positions.
6. Calling `salib analyze ... -c 2` against a one-column output file exits
   nonzero and leaves the requested output directory unchanged. Calling
   `salib --help` succeeds without importing a model or requiring a parameter
   file.

Because the source is blocked, these notes are a public authoring contract and
not a claim that Oracle, controls, a frozen test denominator, or production
dependency artifacts exist. Do not mark the task runnable until those missing
artifacts and the unbound callable/array/dataframe/parallel boundaries have
been independently resolved.
