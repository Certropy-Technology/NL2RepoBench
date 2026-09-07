## Project Description

Build an installable Python distribution named **SALib** whose import package is
`SALib` and whose console command is `salib`. SALib is a scientific-computing
library for global sensitivity analysis: users describe uncertain model inputs,
generate a method-compatible experimental design, evaluate their own model, and
convert the resulting outputs into sensitivity indices. The package is intended
for scientists, engineers, and Python developers who need both a functional API
and a chainable `ProblemSpec` workflow.

The implementation must provide the public sampling, analysis, utility, result,
test-function, and command-line interfaces specified below. Inputs and outputs
are in-memory NumPy arrays unless a CLI operation explicitly reads or writes a
text file. A problem definition is a mapping with at least:

```python
{
    "num_vars": 3,
    "names": ["x1", "x2", "x3"],
    "bounds": [[-3.14159, 3.14159]] * 3,
}
```

`num_vars`, `names`, and `bounds` must agree. Optional `groups` assigns one group
label per variable, optional `dists` assigns one supported distribution per
variable, and optional `outputs` names model outputs. Uniform bounds are the
default. Samplers return rows in the exact design order required by their paired
analyzers; analyzers preserve parameter or group order from the problem
definition.

In scope are local sampling, numerical sensitivity analysis, result conversion,
basic plotting, model evaluation through Python callables, local multiprocessing,
bundled deterministic benchmark functions, parameter-file parsing, and the
`salib sample` / `salib analyze` command families. Out of scope are a graphical
application, remote data acquisition, automatic execution of arbitrary external
models, persistence beyond explicitly requested text files, and runtime network
access. Distributed evaluation is optional because it requires the separately
installed `pathos` extra; the core package must remain fully usable without a
cluster or external service.

## Supports

- **Runtime:** Python 3.10 or newer. The authoring environment records CPython
  3.13 on Linux/amd64; do not depend on CPython-private behavior.
- **Package manager:** `pip`. The project must install with
  `python -m pip install .` from the workspace root and expose package metadata
  through `pyproject.toml`.
- **Build backend:** a standards-compliant PEP 517 backend. Build requirements
  must be declared in `pyproject.toml` and must not be downloaded at runtime.
- **Runtime dependencies:** `numpy>=2.0`, `scipy>=1.9.3`,
  `matplotlib>=3.5`, `pandas>=2.0`, and `multiprocess`. Distributed evaluation
  may use the optional extra `pathos>=0.3.2`.
- **Network:** no component may contact GitHub, PyPI, DNS, or any external
  service while installing, importing, sampling, analyzing, plotting, or using
  the CLI. All numerical work is local.
- **Entry points:** `from SALib import ProblemSpec` and the executable
  `salib = SALib.scripts.salib:main` are required.

### Project Directory Layout

Create at least the following public structure. Private helpers may be added,
but the import paths shown here must exist.

```text
workspace/
├── pyproject.toml
└── src/
    └── SALib/
        ├── __init__.py                 # exports ProblemSpec
        ├── util/
        │   ├── __init__.py             # read_param_file, handle_seed, scale_samples
        │   ├── problem.py              # ProblemSpec
        │   └── results.py              # ResultDict
        ├── sample/
        │   ├── sobol.py
        │   ├── saltelli.py
        │   ├── latin.py
        │   ├── fast_sampler.py
        │   ├── finite_diff.py
        │   ├── ff.py
        │   └── morris/
        │       ├── __init__.py
        │       └── morris.py
        ├── analyze/
        │   ├── sobol.py
        │   ├── morris.py
        │   ├── fast.py
        │   ├── delta.py
        │   ├── dgsm.py
        │   ├── pawn.py
        │   ├── discrepancy.py
        │   ├── ff.py
        │   └── hdmr.py
        ├── test_functions/
        │   ├── Ishigami.py
        │   ├── Sobol_G.py
        │   ├── linear_model_1.py
        │   ├── linear_model_2.py
        │   ├── lake_problem.py
        │   └── oakley2004.py
        └── scripts/
            └── salib.py
```

### Harness Setup

The evaluation harness starts from the submitted workspace, installs the local
distribution into an environment where the declared scientific dependencies
are already available, imports public objects in fresh Python processes, and
invokes the `salib` executable in subprocesses. It may use temporary parameter,
sample, and output files. The implementation must not assume the repository is
the current directory after installation, must not write into its installed
package directory, and must not rely on editable-install behavior. This is a
public repository-generation specification, not permission to access tests or
reference assets.

## API Usage Guide

### Problem definitions

Every sampler and analyzer accepts the same problem mapping. `names` is an
ordered sequence of unique strings, `bounds` has one entry per name, and
`num_vars == len(names) == len(bounds)`. A simple bound is `[lower, upper]` with
`lower < upper`. Distribution-specific bound records may contain additional
parameters when the matching `dists` entry requires them. If `groups` is
present, it has one label per variable. Invalid lengths, non-finite bounds, or
unsupported distribution descriptions are errors and must not be silently
reordered.

Ordinary example:

```python
problem = {
    "num_vars": 2,
    "names": ["rate", "capacity"],
    "bounds": [[0.0, 1.0], [10.0, 20.0]],
}
```

Edge example: a zero-variable problem is not a valid sampling or analysis
problem. A mismatch such as two names and one bound must fail during validation
rather than returning an empty or partially initialized design.

### `SALib.ProblemSpec`

**Import and shape**

```python
from SALib import ProblemSpec

ProblemSpec(*args, **kwargs)
```

`ProblemSpec` is a `dict` subclass initialized from a problem mapping. It keeps
three mutable workflow attributes: `samples` (a two-dimensional NumPy array),
`results` (a one- or two-dimensional NumPy array), and `analysis` (a
`ResultDict`, a mapping of output names to results, or `None`). Construction
validates and normalizes the problem without changing the declared parameter
order. If `outputs` is absent, generic output names are created when results are
known.

Core callable methods are:

```python
sp.sample(func, *args, **kwargs) -> ProblemSpec
sp.set_samples(samples: numpy.ndarray) -> ProblemSpec
sp.evaluate(func, *args, **kwargs) -> ProblemSpec
sp.evaluate_parallel(func, *args, nprocs=None, **kwargs) -> ProblemSpec
sp.set_results(results: numpy.ndarray) -> ProblemSpec
sp.analyze(func, *args, **kwargs) -> ProblemSpec
sp.analyze_parallel(func, *args, nprocs=None, **kwargs) -> ProblemSpec
sp.to_df()
sp.plot(**kwargs)
sp.heatmap(metric=None, index=None, title=None, ax=None)
```

`sample` calls `func(problem, *args, **kwargs)`, stores its two-dimensional
array, clears stale results and analysis, and returns `self`. `evaluate` calls
`func(sp.samples, *args, **kwargs)`, stores its array result, clears stale
analysis, and returns `self`. `analyze` supplies the problem, the required
sample matrix when the analyzer accepts `X`, and the selected output vector;
it stores the returned result and returns `self`. Parallel variants preserve
input/output row order and cap worker use to useful work or available CPUs.
`set_samples` and `set_results` provide already computed arrays and return
`self`; their first dimension must be compatible. Missing samples before
evaluation, missing results before analysis, or incompatible row counts are
errors.

Sampler and analyzer modules are also exposed as chainable dynamic methods,
for example `sample_sobol`, `sample_latin`, `sample_morris`, `analyze_sobol`,
and `analyze_morris`. Their arguments and behavior are identical to the module
functions below except that the stored problem/samples/results are supplied by
the object. Chaining must therefore be deterministic whenever the underlying
call uses the same integer seed.

`to_df()` returns pandas DataFrame objects in the analyzer-specific shape;
multi-output analysis is converted per output. `plot()` returns Matplotlib axes
for result bar charts. `heatmap()` returns the supplied or newly created axes and
filters by output `metric` and sensitivity `index` when provided. Plotting does
not call `show()` and must work with a non-interactive backend. Unknown metric or
index names, analysis before results, and non-array callable returns are invalid.

Ordinary example:

```python
from SALib import ProblemSpec
from SALib.test_functions import Ishigami

sp = ProblemSpec({
    "names": ["x1", "x2", "x3"],
    "bounds": [[-3.14159, 3.14159]] * 3,
    "outputs": ["Y"],
})
sp.sample_sobol(128, seed=7).evaluate(Ishigami.evaluate).analyze_sobol(seed=7)
assert sp.samples.shape[1] == 3
```

Edge example: `ProblemSpec(problem).evaluate(Ishigami.evaluate)` must fail
because no samples have been set. Replacing samples with a new matrix must
invalidate previously stored results and analysis.

### `SALib.util.ResultDict`

```python
from SALib.util.results import ResultDict

ResultDict(*args, **kwargs)
result.to_df()
result.plot(ax=None)
```

`ResultDict` is a dictionary holding named NumPy result arrays and parameter
names. An analyzer may attach a method-specific `to_df`; it returns either one
DataFrame or an ordered tuple of DataFrames (for example total-, first-, then
second-order Sobol results). `plot` returns Matplotlib axes and uses parameter
order from `names`. Neither operation mutates numerical entries. Missing fields
needed by the selected conversion may raise `KeyError`; empty results must
produce an empty conversion or an explicit validation error, never fabricated
indices.

Ordinary example: `sobol.analyze(...).to_df()` yields first/total-order tables
and, when enabled, a second-order table. Edge example: `ResultDict().plot()` may
reject the object because there are no plottable metrics, but must not open a
GUI or write a file.

### `SALib.util.read_param_file`

```python
from SALib.util import read_param_file

read_param_file(filename, delimiter=None) -> dict
```

Read a text parameter file with one non-empty record per variable. Columns are
name, lower bound, upper bound, optional group, and optional distribution. With
`delimiter=None`, whitespace separates columns; a supplied delimiter is used
literally. Return a problem dictionary containing ordered `names`, `bounds`,
`num_vars`, `groups`, and `dists`; `dists` is `None` when no non-uniform
distribution is specified. Numeric fields become numbers, not strings. Reading
has no side effect beyond opening the file. Missing files raise the normal file
error; malformed records or inconsistent optional columns are validation
errors.

Ordinary example file and call:

```text
x1 -3.14 3.14
x2 -3.14 3.14
```

```python
problem = read_param_file("params.txt")
```

Edge example: an empty file cannot describe a valid sensitivity problem and
must not be converted into a valid zero-variable problem.

### `SALib.util.handle_seed`

```python
from SALib.util import handle_seed

handle_seed(seed) -> numpy.random.Generator
```

Accept `None`, an integer or integer sequence, a NumPy `SeedSequence`,
`BitGenerator`, or existing `Generator`. Return a `Generator`; reuse a supplied
generator rather than replacing its state. Equal integer seeds create equal
initial streams. `None` requests a fresh nondeterministic stream. Unsupported
objects follow NumPy's seed-validation errors. The function changes only the
state of a passed generator when that generator is subsequently consumed.

Ordinary example: `handle_seed(9).random(3)` is repeatable across two fresh
calls. Edge example: passing an existing generator returns a generator tied to
that existing stream, so repeated use advances state rather than restarting it.

### `SALib.util.scale_samples`

```python
from SALib.util import scale_samples

scale_samples(params: numpy.ndarray, problem: dict) -> numpy.ndarray
```

Scale a two-dimensional unit-hypercube sample according to each problem bound
and optional distribution. Preserve row and column order and return an array of
the same shape. For compatibility, mark the problem as scaled using its
`sample_scaled` entry. Uniform `[0, 1]` bounds leave values unchanged. Invalid
column counts, unsupported distributions, or invalid distribution parameters
are errors. The function may transform `params` in place and mutates the problem
only by recording scaling state; callers that need the original array should
pass a copy.

Ordinary example: scaling `[[0.0], [0.5], [1.0]]` against `[[10, 20]]` produces
the lower bound, midpoint, and upper bound in that order. Edge example: an
`(N, 0)` array with a nonempty problem is a shape error.

### `SALib.sample.sobol.sample`

```python
from SALib.sample import sobol

sobol.sample(problem, N, *, calc_second_order=True, scramble=True,
             skip_values=0, seed=None) -> numpy.ndarray
```

Generate a Saltelli-extended Sobol design within the problem bounds. `N` is a
positive integer base sample size and `D` is the number of variables. The shape
is `(N * (2 * D + 2), D)` with second-order terms and `(N * (D + 2), D)`
without them. `scramble` controls sequence scrambling; `skip_values` is a
non-negative number of initial Sobol points to skip. `seed` accepts `None`, an
integer, or a NumPy `Generator` and controls scrambled sampling. Equal fresh
seeds and arguments return equal arrays. Output rows must remain in the design
order expected by `SALib.analyze.sobol.analyze`. Non-positive `N`, negative
skips, or malformed problems are invalid; non-power-of-two choices may produce
a warning because balance properties are weaker.

Ordinary example: a two-variable problem with `N=8` and
`calc_second_order=False` returns shape `(32, 2)`. Edge example:
`sobol.sample(problem, 1, scramble=False, skip_values=0)` is valid and
deterministic, while `N=0` is not a useful design and must fail validation.

### `SALib.sample.saltelli.sample`

```python
from SALib.sample import saltelli

saltelli.sample(problem, N, calc_second_order=True, skip_values=None)
    -> numpy.ndarray
```

Provide the deprecated Saltelli sampler for compatibility. It returns the same
second-order-dependent row counts as the Sobol sampler and preserves the row
layout required by Sobol analysis. `skip_values=None` chooses a power-of-two
skip at least as large as `N` (and at least the implementation's documented
minimum); an explicit skip should be a power of two and at least `N` or a
`UserWarning` may be emitted. This API does not accept a seed. Invalid problems,
non-positive `N`, or negative skips fail rather than returning a partial matrix.

Ordinary example: `saltelli.sample(problem, 16, False)` produces
`16 * (D + 2)` rows. Edge example: an explicit non-power-of-two skip is accepted
only with its compatibility warning; callers should prefer `sobol.sample`.

### `SALib.sample.latin.sample`

```python
from SALib.sample import latin

latin.sample(problem, N, seed=None) -> numpy.ndarray
```

Generate an `(N, D)` Latin-hypercube design scaled to the declared bounds.
Every variable contributes one value from each of `N` equal-probability strata;
row order may be randomized, but equal fresh seeds reproduce it. Grouped
variables use their group relationship consistently. `N` must be positive.
Sampling does not mutate user arrays or write files.

Ordinary example: `latin.sample(problem, 20, seed=2)` returns 20 rows and D
columns within bounds. Edge example: `N=1` returns one in-bounds row;
`N=0` or inconsistent groups are invalid.

### `SALib.sample.morris.sample`

```python
from SALib.sample import morris

morris.sample(problem, N, num_levels=4, optimal_trajectories=None,
              local_optimization=True, seed=None) -> numpy.ndarray
```

Generate `N` Morris trajectories, or select `optimal_trajectories` trajectories
from that pool. `num_levels` is an even integer grid size. Without groups, each
trajectory has `D + 1` rows; with `G` groups it has `G + 1` rows. The return has
`D` columns and contains either `N` trajectories or the selected optimum count.
`optimal_trajectories`, when supplied, is an integer from 2 through `N`.
`local_optimization=False` requests the more expensive brute-force selection.
The seed contract matches other stochastic samplers. Result ordering is
trajectory-major and must be retained for Morris analysis. Invalid grid levels,
selection counts, group lengths, or problem dimensions fail validation.

Ordinary example: a three-variable ungrouped problem, `N=4`, and no trajectory
selection returns `(16, 3)`. Edge example: requesting five optimal trajectories
from four generated trajectories is invalid.

### `SALib.sample.fast_sampler.sample`

```python
from SALib.sample import fast_sampler

fast_sampler.sample(problem, N, M=4, seed=None) -> numpy.ndarray
```

Generate the extended FAST design with shape `(N * D, D)`. `M` is the positive
number of harmonics used by both sampler and analyzer. The sample size must be
large enough for the selected `M`; otherwise raise a validation error rather
than aliasing frequencies. Equal fresh seeds reproduce phase choices and row
order. Output is paired with `SALib.analyze.fast.analyze` using the same `M`.

Ordinary example: `fast_sampler.sample(problem, 65, M=4, seed=3)` returns
`65 * D` rows. Edge example: a very small `N` that cannot support `M=4` is
invalid even though an array of that shape could be allocated.

### `SALib.sample.finite_diff.sample`

```python
from SALib.sample import finite_diff

finite_diff.sample(problem, N, delta=0.01, seed=None, skip_values=1024)
    -> numpy.ndarray
```

Generate a base quasi-random point followed by one finite-difference perturbation
per variable, producing `(N * (D + 1), D)` rows. `delta` is a positive
percentage step and `skip_values` is a non-negative Sobol-sequence offset.
Results are scaled to bounds and ordered in base/perturbation blocks required by
DGSM analysis. The seed accepts the standard seed forms. Invalid delta, skip,
or dimensions fail validation.

Ordinary example: two variables and `N=10` produce `(30, 2)`. Edge example:
`delta=0` cannot measure derivatives and is invalid.

### `SALib.sample.ff.sample`

```python
from SALib.sample import ff

ff.sample(problem, seed=None) -> numpy.ndarray
```

Generate a two-level fractional-factorial design. If `D` is not a power of two,
pad the problem to the next power of two with uniquely named dummy variables and
matching bounds; the returned matrix has that padded column count. The design
order must be compatible with `SALib.analyze.ff.analyze`. The seed parameter is
accepted for API consistency; repeated calls with the same effective problem
produce the same contrast design. Invalid or zero-variable problems fail.

Ordinary example: a three-variable problem is padded to four columns and the
added dummy factor remains visible in the problem and analysis. Edge example:
a four-variable problem needs no dummy column and retains all original names in
their original order.

### `SALib.analyze.sobol.analyze`

```python
from SALib.analyze import sobol

sobol.analyze(problem, Y, calc_second_order=True, num_resamples=100,
              conf_level=0.95, print_to_console=False, parallel=False,
              n_processors=None, keep_resamples=False, seed=None) -> ResultDict
```

Analyze outputs from the matching Sobol/Saltelli design. `Y` is a finite
one-dimensional array whose length exactly matches the sampler formula. Return
`names`, `S1`, `S1_conf`, `ST`, and `ST_conf`, each first-order array following
problem order. With second order enabled, also return square `S2` and `S2_conf`
arrays indexed by parameter pairs. `num_resamples` is positive and
`0 < conf_level < 1`. `parallel=True` may use `n_processors`, but must return the
same key/shape/order contract as serial execution. `keep_resamples` retains
bootstrap resample arrays in the result. `seed` controls confidence resampling;
an equal nonzero integer seed reproduces confidence values. Constant `Y`, NaNs,
wrong design lengths, and incompatible `calc_second_order` settings must be
handled explicitly through documented warnings/NaNs or validation errors, not
misinterpreted as a different design. `print_to_console=True` prints tabular
results and does not change the return value.

Ordinary example: analyze `Ishigami.evaluate(sobol.sample(problem, 128,
seed=1))` with `seed=1`. Edge example: a `Y` vector generated with
`calc_second_order=False` must be analyzed with the same flag.

### `SALib.analyze.morris.analyze`

```python
from SALib.analyze import morris

morris.analyze(problem, X, Y, num_resamples=100, conf_level=0.95,
               scaled=False, print_to_console=False, num_levels=4,
               seed=None) -> ResultDict
```

Analyze a complete Morris trajectory design. `X` is the exact sample matrix
passed to the model and `Y` has one finite result per row. Return ordered
`names`, `mu`, `mu_star`, `sigma`, and `mu_star_conf`, one value per variable or
group. `num_levels` must equal the sampling value. `scaled=True` scales effects
using observed standard deviations and therefore requires the actual evaluated
`X`. The seed controls bootstrap confidence resampling. Invalid trajectory
lengths, confidence levels, or inconsistent `X`/`Y` rows are errors.

Ordinary example: pass `morris.sample(problem, 10, seed=4)` and corresponding
model outputs with `num_levels=4`. Edge example: a constant output may yield
zero or undefined spread statistics but must preserve the result shape.

### `SALib.analyze.fast.analyze`

```python
from SALib.analyze import fast

fast.analyze(problem, Y, M=4, num_resamples=100, conf_level=0.95,
             print_to_console=False, seed=None) -> ResultDict
```

Analyze an extended FAST output vector. Its length must be `N * D` for an
integer `N` that supports the same positive `M` used for sampling. Return
ordered `S1`, `ST`, `S1_conf`, and `ST_conf` arrays of length `D`. Bootstrap
confidence estimates are reproducible with an equal nonzero integer seed and
are indicative rather than exact inferential guarantees. Printing is optional
and does not replace the returned result. Wrong lengths or incompatible `M`
values are errors.

Ordinary example: analyze outputs from `fast_sampler.sample(problem, 65, M=4,
seed=2)` with `M=4`. Edge example: changing the analyzer to `M=5` is invalid
for results generated with `M=4`.

### `SALib.analyze.delta.analyze`

```python
from SALib.analyze import delta

delta.analyze(problem, X, Y, num_resamples=100, conf_level=0.95,
              print_to_console=False, seed=None, y_resamples=None,
              method="all", bootstrap_savedf=None, bins_specs={}) -> ResultDict
```

Perform moment-independent analysis on any compatible `(N, D)` input matrix and
length-`N` output vector. `method` is `"all"`, `"delta"`, or `"sobol"`.
Return `names`, notes, the requested delta configurations and corresponding
confidence arrays, and/or `S1` and `S1_conf`; each per-variable result follows
problem order. `num_resamples` and optional `y_resamples` are positive,
`0 < conf_level < 1`, and `bins_specs` may map a parameter name to a bin count or
ordered bin boundaries. `bootstrap_savedf`, when supplied, is the only option
that writes a diagnostic bootstrap table. Equal nonzero seeds reproduce
resampling. Invalid methods, unknown parameter names, unusable bins, too-small
classes, and row mismatches produce analysis errors or warnings rather than
silently dropping variables.

Ordinary example: Latin-sample a problem, evaluate it, and call
`delta.analyze(problem, X, Y, method="all", seed=5)`. Edge example: an empty
`bins_specs` uses defaults; a bin specification outside the variable range must
be rejected or explicitly replaced with a warning-backed default.

### `SALib.analyze.dgsm.analyze`

```python
from SALib.analyze import dgsm

dgsm.analyze(problem, X, Y, num_resamples=100, conf_level=0.95,
             print_to_console=False, seed=None) -> ResultDict
```

Analyze the block layout returned by `finite_diff.sample`. Return ordered
`names`, `vi`, `vi_std`, `dgsm`, and `dgsm_conf` arrays of length `D`. `X` and
`Y` must preserve each base row followed by its D perturbations. Confidence
resampling follows the seed contract. Zero perturbations, incompatible row
counts, non-finite values, or invalid confidence settings are errors or produce
explicit undefined numerical entries; they must not be silently reordered.

Ordinary example: `X = finite_diff.sample(problem, 32, seed=8)` followed by
`dgsm.analyze(problem, X, model(X), seed=8)`. Edge example: deleting one output
breaks the block structure and must fail.

### `SALib.analyze.pawn.analyze`

```python
from SALib.analyze import pawn

pawn.analyze(problem, X, Y, S=10, print_to_console=False, seed=None)
    -> ResultDict
```

Perform PAWN moment-independent analysis for any matching input/output rows.
`S` is a positive number of conditioning intervals. Return one ordered value per
variable for the minimum, mean, median, maximum, coefficient of variation, and
standard deviation of conditional-distribution distances, plus `names`. NaN
observations are ignored where a valid statistic remains. Grouped factors are
analyzed individually and combined by group in declared group order. The seed
controls deterministic tie/resampling behavior. Too few finite observations,
non-positive `S`, and row mismatches are invalid.

Ordinary example: analyze a seeded Latin design with `S=10`. Edge example: a
column containing only NaNs cannot produce a valid factor statistic and must be
reported as undefined rather than assigned zero importance.

### `SALib.analyze.discrepancy.analyze`

```python
from SALib.analyze import discrepancy

discrepancy.analyze(problem, X, Y, method="WD", print_to_console=False,
                    seed=None) -> ResultDict
```

Calculate discrepancy-based indices from any matching `(N, D)` design and
length-`N` output. `method` is one of `"WD"`, `"CD"`, `"MD"`, or
`"L2-star"`, matching SciPy QMC discrepancy names. Return per-variable indices
and names in problem order. `seed` is accepted for analyzer API compatibility;
the calculation itself is deterministic for equal arrays. Invalid methods,
non-finite data that SciPy cannot process, or mismatched rows fail explicitly.

Ordinary example: call with a Latin design and `method="WD"`. Edge example: an
unknown lowercase method such as `"wd"` is not silently substituted for the
documented uppercase name.

### `SALib.analyze.ff.analyze`

```python
from SALib.analyze import ff

ff.analyze(problem, X, Y, second_order=False, print_to_console=False,
           seed=None) -> ResultDict
```

Analyze the exact contrast design produced by `SALib.sample.ff.sample`. Return
`names` and main effects `ME`; when `second_order=True`, also return interaction
names and effects `IE`. Dummy factors added by the sampler remain represented so
users can compare them with real effects. Ordering follows the padded problem.
The result's `to_df()` returns a main-effect DataFrame and either an interaction
DataFrame or `None`. Seed is accepted for API consistency. Wrong design shape or
incompatible problem mutation is invalid.

Ordinary example: analyze a three-factor problem after the sampler adds a dummy
fourth factor. Edge example: with `second_order=False`, the interaction DataFrame
is `None`, not an invented zero matrix.

### `SALib.analyze.hdmr.analyze`

```python
from SALib.analyze import hdmr

hdmr.analyze(problem, X, Y, maxorder=2, maxiter=100, m=2, K=20,
             R=None, alpha=0.95, lambdax=0.01,
             print_to_console=False, seed=None) -> ResultDict
```

Fit an HDMR surrogate and report sensitivity contributions for an arbitrary
matching input/output data set. Supported domains are `maxorder` 1 through 3,
`maxiter` 1 through 1000, spline intervals `m` 2 through 10, bootstrap count
`K` 1 through 100, `0.5 <= alpha <= 1`, and `0 <= lambdax <= 10`. `R` is the
bootstrap subset size and defaults from the data size. Return the documented
contribution and confidence fields (`Sa`, `Sa_conf`, `Sb`, `Sb_conf`, `STotal`,
`S_conf`, `ST`, `ST_conf`, and selection/emulator coefficient data) while
preserving term order. A seeded bootstrap is repeatable. Printing does not alter
the result. Out-of-range controls, insufficient rows, or inconsistent/non-finite
arrays must fail validation rather than truncate the model.

Ordinary example: use `maxorder=2, K=10, seed=6` on a sufficiently large Latin
design. Edge example: `maxorder=4` is outside the public domain and must fail.

### Bundled test functions

These functions are public, vectorized model examples. They accept rows as
observations, preserve row order, return NumPy arrays, do not write files, and
raise normal NumPy shape/broadcasting errors for incompatible inputs.

#### `SALib.test_functions.Ishigami.evaluate`

```python
from SALib.test_functions import Ishigami

Ishigami.evaluate(X: numpy.ndarray, A: float = 7.0,
                  B: float = 0.1) -> numpy.ndarray
```

`X` has shape `(N, 3)` and the result has shape `(N,)`. It evaluates the
standard three-variable Ishigami-Homma function using columns in order. Results
are deterministic. Ordinary example: two input rows produce two outputs. Edge
example: an empty `(0, 3)` array returns an empty vector; fewer than three
columns is invalid.

#### `SALib.test_functions.Sobol_G`

```python
from SALib.test_functions import Sobol_G

Sobol_G.evaluate(values, a=None, delta=None, alpha=None) -> numpy.ndarray
Sobol_G.sensitivity_index(a, alpha=None) -> numpy.ndarray
Sobol_G.total_sensitivity_index(a, alpha=None) -> numpy.ndarray
```

`evaluate` accepts `(N, D)` values and optional length-`D` parameter vectors;
omitting `delta` and `alpha` selects the original G-function. It returns one
deterministic value per row. The index helpers return one analytical index per
factor in input order. Ordinary example: supply `a=np.array([0, 1, 4])` for a
three-column design. Edge example: parameter vectors whose lengths differ from
`D` are invalid; an empty `(0, D)` design returns an empty evaluation vector.

#### Linear models

```python
from SALib.test_functions import linear_model_1, linear_model_2

linear_model_1.evaluate(values) -> numpy.ndarray
linear_model_2.evaluate(values) -> numpy.ndarray
```

Both require `(N, 5)` arrays and return `(N,)` deterministic outputs.
`linear_model_1` gives equal weight to all five columns; `linear_model_2` uses
descending weights from the first through fifth column. Ordinary example: an
all-zero row returns zero. Edge example: an empty `(0, 5)` input returns an
empty vector, while the wrong number of columns is invalid.

#### Lake problem functions

```python
from SALib.test_functions import lake_problem

lake_problem.evaluate(values: numpy.ndarray, nvars: int = 100,
                      seed=101) -> numpy.ndarray
lake_problem.evaluate_lake(values: numpy.ndarray, seed=101) -> numpy.ndarray
lake_problem.lake_problem(X, a=0.1, q=2.0, b=0.42, eps=0.02)
```

`evaluate` consumes rows ordered as `a, q, b, mean, stdev, delta, alpha` and
returns four objectives per row: maximum phosphorus, utility, inertia, and
reliability. `evaluate_lake` consumes rows ordered as `a, q, b, mean, stdev` and
returns phosphorus trajectories. `lake_problem` evaluates one deterministic
state update for scalar or broadcast-compatible array inputs. Equal seeds
reproduce stochastic inflows. `nvars` must be positive; incompatible columns or
broadcast shapes are invalid. Ordinary example: calling `evaluate` twice with
the same values and seed yields equal arrays. Edge example: `nvars=0` is invalid.

#### `SALib.test_functions.oakley2004.evaluate`

```python
from SALib.test_functions import oakley2004

oakley2004.evaluate(X: numpy.ndarray, A: numpy.ndarray,
                    M: numpy.ndarray) -> numpy.ndarray
```

Evaluate the Oakley-O'Hagan benchmark for a two-dimensional observation matrix
and coefficient arrays of compatible documented dimensions. Return one
deterministic output per observation without mutating inputs. Ordinary example:
`X.shape[0]` equals the result length. Edge example: incompatible coefficient
dimensions raise a NumPy shape error; an empty but dimensionally valid `X`
returns an empty vector.

### `salib` command-line interface

The installed executable has two command families:

```text
salib sample METHOD [OPTIONS]
salib analyze METHOD [OPTIONS]
```

Supported sampling method names include `sobol`, `saltelli`, `latin`, `morris`,
`fast_sampler`, `finite_diff`, and `ff`. Supported analysis names include
`sobol`, `morris`, `fast`, `delta`, `dgsm`, `pawn`, `discrepancy`, `ff`, and
`hdmr`. `salib -h`, `salib sample -h`, `salib analyze -h`, and
`salib <action> METHOD -h` print the relevant help. Unknown actions, methods,
or flags are argparse errors with a nonzero exit; no action prints top-level
help rather than running work.

Common sampling flags are exactly:

```text
-n, --samples INT       required base sample/trajectory count
-p, --paramfile PATH    required parameter definition file
-o, --output PATH       required sample output file
-s, --seed INT          optional random seed
--delimiter TEXT        output delimiter; default is one space
--precision INT         floating-point output precision; default 8
```

The sampler writes a numeric text matrix to `--output`, one sample per line, in
the same row order as the Python API. Method-specific options correspond to the
callable parameters above and are listed by method help; boolean second-order
selection must produce the same shapes as `calc_second_order` in the Python API.

Common analysis flags are exactly:

```text
-p, --paramfile PATH          required parameter definition file
-Y, --model-output-file PATH  required numeric model-output file
-c, --column INT              zero-based output column; default 0
--delimiter TEXT              input delimiter; default is one space
-s, --seed INT                optional random seed
```

Analysis commands print their result table to standard output. Methods that
require the original sample matrix must also accept their documented
method-specific sample-file argument; method-specific resampling, confidence,
harmonic, level, order, and parallel flags must map without semantic changes to
the corresponding Python function. Files are read using the requested delimiter
and selected output column. Missing files, an out-of-range column, malformed
numbers, or incompatible sample/output lengths produce a nonzero exit and a
diagnostic on standard error; they must not create a successful-looking result.

Ordinary examples:

```bash
salib sample sobol -n 128 -p params.txt -o samples.txt -s 11
salib analyze sobol -p params.txt -Y model_output.txt -c 0 -s 11
```

Edge examples: `salib sample sobol -n 0 ...` must fail, and
`salib analyze sobol -p missing.txt ...` must fail without creating or
overwriting unrelated files. `-h` succeeds without requiring input files.

## Implementation Notes

1. **Sampler/analyzer pairing is part of the contract.** Sobol analysis consumes
   Sobol or Saltelli designs; FAST consumes `fast_sampler`; DGSM consumes
   `finite_diff`; Morris consumes Morris trajectories; fractional factorial
   analysis consumes `ff`. Never infer a different design merely because an
   output length is divisible by several candidate formulas.
2. **Preserve semantic order.** Problem names, groups, sample rows, outputs,
   sensitivity arrays, DataFrame rows, printed tables, and CLI files must use
   stable documented order. Parallel execution may change scheduling but not
   returned order.
3. **Randomness is local and explicit.** Use NumPy generators rather than the
   process-global RNG where the API accepts `seed`. Two fresh calls with equal
   nonzero integer seeds and equal inputs must agree. `seed=None` may vary.
   Passing an existing generator consumes that generator's stream. Do not use
   Python's hash randomization for numerical or display ordering.
4. **Scientific validation precedes calculation.** Validate problem lengths,
   array rank, row counts, method-specific design size, confidence levels, and
   finite numeric requirements. Preserve meaningful NumPy/SciPy warnings for
   mathematically undefined constant-output cases, but do not hide malformed
   layouts behind zero-filled results.
5. **State invalidation is strict.** New samples invalidate old model results and
   analysis. New results invalidate old analysis. Failed operations must not
   leave a `ProblemSpec` claiming that stale downstream state belongs to new
   upstream data.
6. **Resource behavior is bounded.** Multiprocessing pools must be closed and
   joined even when a worker fails. Plot functions return axes and never call a
   blocking display. File handles are closed promptly. The core API performs no
   network access and writes only where a caller explicitly supplies a path.
7. **Result interoperability matters.** Analysis results remain dictionary-like,
   retain NumPy arrays for numerical use, and expose analyzer-appropriate pandas
   conversion. Console printing and plotting are views over the same result, not
   alternate calculations.

Small verifiable examples:

```python
# Shape agreement across a paired design.
X = sobol.sample(problem, 4, calc_second_order=False, seed=1)
assert X.shape == (4 * (problem["num_vars"] + 2), problem["num_vars"])
```

```python
# Seeded sampling is repeatable without sharing mutable global state.
X1 = latin.sample(problem, 8, seed=42)
X2 = latin.sample(problem, 8, seed=42)
assert numpy.array_equal(X1, X2)
```

```python
# Chaining and direct calls describe the same workflow state.
sp = ProblemSpec(problem).set_samples(X)
sp.set_results(Ishigami.evaluate(X))
assert sp.samples.shape[0] == sp.results.shape[0]
```

```python
# CLI text output remains a two-dimensional numeric matrix when reloaded.
# samples = numpy.loadtxt("samples.txt", ndmin=2)
# assert samples.shape[1] == problem["num_vars"]
```
