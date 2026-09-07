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

The following APIs are the public numerical surface. Use the
module paths exactly as shown. All `problem` dictionaries contain at least
`num_vars`, `names`, and `bounds`; optional `groups`, `dists`, and `outputs`
have one entry per relevant variable or output. `names` is an ordered list of
unique strings and `bounds` is an ordered list of numeric distribution
parameters, normally `[lower, upper]`. `X` is a finite two-dimensional NumPy
array with one column per variable; `Y` is a finite one-dimensional NumPy
array with one value per row of `X`. Reject incompatible dimensions, invalid
bounds, unsupported distributions, non-finite values, and non-positive sample
counts with a clear exception rather than returning a partial result.

### `SALib.sample.saltelli.sample`

```python
SALib.sample.saltelli.sample(problem, N, calc_second_order=True)
```

`problem` is a valid problem dictionary and `N` is a positive integer base
sample count. The optional boolean controls whether second-order Sobol
columns are included. The return value is a NumPy array with shape determined
by the selected order and the number of variables. Rows are generated in a
repeatable construction order for identical inputs and configuration. This
function does not evaluate a model and does not mutate `problem`.

```python
from SALib.sample import saltelli
X = saltelli.sample({"num_vars": 2, "names": ["a", "b"],
                     "bounds": [[0, 1], [0, 1]]}, 64)
```

For an empty or zero-dimensional problem, or for `N=0`, raise `ValueError`;
do not return an unlabelled array. In normal use `calc_second_order=False`
removes the second-order portion while preserving the first-order row order.

### `SALib.sample.sobol.sample`

```python
SALib.sample.sobol.sample(problem, N, calc_second_order=True,
                          scramble=True, skip_values=0, seed=None)
```

`N` is a positive integer base size; `scramble` is boolean, `skip_values` is a
non-negative integer, and `seed` is either `None` or an integer/NumPy random
seed accepted by the implementation. The return value is a two-dimensional
NumPy array whose columns follow `problem["names"]`. With a fixed integer seed,
the same problem and options must produce the same values and shape. The
function has no filesystem or network side effects.

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
                           local_optimization=False, seed=None)
```

`N` is the number of trajectories, `num_levels` is a valid positive grid level
count, `optimal_trajectories` is either `None` or a supported positive
selection count, and `local_optimization` is boolean. `seed` controls the
randomized construction when supplied. Return a two-dimensional NumPy array
of model-input rows in problem-variable order. It does not call the model or
modify the problem mapping.

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

`N` is a positive sample count, `M` is a positive harmonic/interference
parameter supported by the FAST sampler, and `seed` is optional. Return a
two-dimensional NumPy array with one column per problem variable. The order of
columns and rows is deterministic for identical inputs and a fixed seed; the
function has no persistent side effects.

```python
from SALib.sample import fast_sampler
X = fast_sampler.sample({"num_vars": 2, "names": ["u", "v"],
                         "bounds": [[-1, 1], [0, 4]]}, 32, M=4, seed=11)
```

Reject a non-positive `M`, a non-positive `N`, or bounds that cannot be mapped
to the sampler domain. No rows should be returned for invalid input.

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

### `SALib.analyze.delta.analyze`, `SALib.analyze.dgsm.analyze`,
`SALib.analyze.pawn.analyze`, `SALib.analyze.rbd_fast.analyze`, and
`SALib.analyze.rsa.analyze`

These analyzer modules are public package areas, but no task-local API or test
inventory is available for this blocked source. Their exact callable
signatures, required sample design, and complete result-key contracts are
**not confidently bindable** from the available evidence. Implementing agents
must not guess those contracts or expose made-up defaults. If the pinned
package metadata or authoritative public documentation is available in the
offline build input, mirror its documented signatures and add corresponding
examples; otherwise leave these optional analyzers out of the claimed contract
and report them as not confidently bindable.

### `SALib.util` and `ProblemSpec`

The convenience `ProblemSpec` workflow and utility helpers are also **not
confidently bindable** for this blocked task: their exact public methods,
signatures, return shapes, and interaction with pandas/callables require the
missing task-specific inventory. Do not fabricate a `ProblemSpec` class,
utility function, CLI flag, or dataframe behavior. If implemented from
authoritative package metadata, preserve ordinary Python exceptions and return
objects documented by that metadata rather than serializing them to guessed
JSON.

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

Small verifiable examples for the completed package include:

1. A two-variable bounded problem produces a two-column Latin sample, and the
   same integer seed reproduces the same array.
2. A model evaluated row-by-row on a valid sampler output can be passed to an
   analyzer, whose returned arrays have one element per declared variable.
3. Reversing the declared variable order reverses the corresponding input
   columns and named result positions; it must not silently reorder variables.
4. Passing an output vector with one fewer value than the sample rows raises a
   validation exception before a partial sensitivity mapping is returned.

Because the source is blocked, these notes are a public authoring contract and
not a claim that Oracle, controls, a frozen test denominator, or production
dependency artifacts exist. Do not mark the task runnable until those missing
artifacts and the unbound callable/array/dataframe/parallel boundaries have
been independently resolved.
