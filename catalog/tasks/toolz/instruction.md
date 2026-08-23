# Build `toolz`

Create a complete, installable pure-Python project named `toolz` from an empty
workspace. It is a functional utility library for iterables, dictionaries,
and higher-order functions. The project must also provide the `toolz.curried`,
`toolz.sandbox`, and `tlz` import packages described below.

This document is the public behavior contract. Implement the observable API,
data-model behavior, error behavior, laziness, and import layout; do not copy
the upstream source or tests. The project must work without network access at
runtime and must not depend on a preinstalled copy of `toolz` or `cytoolz`.

## Project Description

`toolz` supplies small composable helpers for sequence processing, mapping
transforms, function composition, memoization, currying, and simple data
processing recipes. The library is organized into three main functional
areas:

- `toolz.itertoolz` contains lazy or sequence-oriented iterator operations.
- `toolz.functoolz` contains function wrappers, composition, currying, and
  callable introspection helpers.
- `toolz.dicttoolz` contains non-mutating dictionary transforms and nested
  update/access helpers.

`toolz.recipes` contains `countby` and `partitionby`. The
`toolz.curried` namespace exposes the same operations as curry-enabled
callables. `toolz.sandbox` exposes the small experimental `EqualityHashKey`,
`unzip`, and `fold` helpers. `tlz` is a compatibility namespace that can
prefer an installed `cytoolz` implementation but must fall back to the pure
Python `toolz` implementation.

## Supports

- Support Python 3.9 and newer Python 3.x versions in the supported source
  range. The implementation must remain pure Python and should not require a
  specific non-CPython runtime.
- Provide the root packages `toolz/` and `tlz/` with these subpackages:
  `toolz.curried`, `toolz.sandbox`, `toolz.sandbox.tests`, and `toolz.tests`.
  The package layout must support both editable and regular installation.
- Provide a standards-compliant `pyproject.toml` for distribution `toolz`,
  with `Requires-Python >=3.9`, BSD-3-Clause license metadata, and version
  `1.1.0`. `toolz.__version__` must be a string equal to the installed
  distribution version.
- Declare no third-party runtime dependencies. `cytoolz` is optional and must
  not be required to import or use `toolz` or the pure-Python `tlz` fallback.
  Build and test tools are not runtime dependencies.
- Normal library operations must not contact a network, invoke a service, or
  require files outside the installed package and caller-owned inputs.
- Preserve lazy behavior where an API returns an iterator. A caller may
  consume such results once, or materialize them with `list` or `tuple`.
  Do not silently turn every iterator operation into an eager list.
- Preserve ordinary Python callable, iterator, mapping, exception, equality,
  hashing, pickling, and introspection behavior where the API below exposes
  those protocols.

## API Usage Guide

### Package and re-exports

The following imports must work after installation:

```python
import toolz
import toolz.compatibility
import toolz.dicttoolz
import toolz.functoolz
import toolz.itertoolz
import toolz.recipes
import toolz.curried
import toolz.curried.exceptions
import toolz.curried.operator
import toolz.sandbox
import toolz.sandbox.core
import toolz.sandbox.parallel
import tlz
```

The root `toolz` namespace re-exports the names in the `__all__` declarations
of `itertoolz`, `functoolz`, `dicttoolz`, and `recipes`. It additionally exposes
`partial`, `reduce`, the built-in `sorted`, `map`, and `filter`, and the alias
`comp` for `compose`. The module attributes `curried` and `sandbox` refer to
their corresponding subpackages. Accessing `toolz.__version__` must return
`"1.1.0"` after installation.

### Iterator operations

Implement these signatures in `toolz.itertoolz`:

```text
remove(predicate, seq)
accumulate(binop, seq, initial=no_default)
groupby(key, seq)
merge_sorted(*seqs, **kwargs)
interleave(seqs)
unique(seq, key=None)
isiterable(x)
isdistinct(seq)
take(n, seq)
drop(n, seq)
take_nth(n, seq)
first(seq)
second(seq)
nth(n, seq)
last(seq)
get(ind, seq, default=no_default)
concat(seqs)
concatv(*seqs)
mapcat(func, seqs)
cons(el, seq)
interpose(el, seq)
frequencies(seq)
reduceby(key, binop, seq, init=no_default)
iterate(func, x)
sliding_window(n, seq)
partition(n, seq, pad=no_pad)
partition_all(n, seq)
count(seq)
pluck(ind, seqs, default=no_default)
join(leftkey, leftseq, rightkey, rightseq,
     left_default=no_default, right_default=no_default)
tail(n, seq)
diff(*seqs, **kwargs)
topk(k, seq, key=None)
peek(seq)
peekn(n, seq)
random_sample(prob, seq, random_state=None)
```

The operations have these observable rules:

- `remove`, `take`, `drop`, `take_nth`, `concat`, `concatv`, `mapcat`,
  `cons`, `interpose`, `iterate`, `sliding_window`, `partition`,
  `partition_all`, `pluck`, `join`, `diff`, `peek`, `peekn`, and
  `random_sample` return lazy iterators where their normal use is iterative.
- `accumulate` yields the first source item or `initial`, then each accumulated
  result. An empty source without `initial` yields no items.
- `groupby` accepts either a callable or an index/key accepted by `getter` and
  returns a mapping from key to a list of source items in encounter order.
  `frequencies` returns counts, and `count` returns the number of items.
- `merge_sorted` merges already sorted inputs lazily. Its optional `key`
  keyword controls comparisons. `unique` retains the first item for each
  item or key. `isiterable` reports whether `iter(x)` succeeds and
  `isdistinct` checks whether all values are distinct.
- `take`, `drop`, `take_nth`, `first`, `second`, `nth`, `last`, and `tail`
  implement ordinary zero-based sequence/iterator access. Out-of-range access
  follows normal iterator/indexing exceptions unless a documented default is
  supplied.
- `get` accepts a scalar index/key or a sequence of indexes/keys. With a
  sequence of indexes it returns a tuple of selected values. Missing values
  return `default`; when `no_default=True` is requested by the supported
  signature, the original `KeyError` or `IndexError` is raised.
- `concat` concatenates a sequence of sequences, while `concatv` accepts the
  sequences as separate arguments. `mapcat` maps a callable and concatenates
  each result. `interleave` cycles through input iterables until all are
  exhausted. `cons` yields its element before the source and `interpose`
  places its element between source items.
- `partition(n, seq, pad=...)` yields fixed-size tuples and pads a short final
  group when a pad value is supplied. `partition_all` yields the final short
  group without padding. `sliding_window` yields overlapping tuples.
- `reduceby` groups by a callable or getter and reduces each group. `join`
  performs an inner or defaulted left/right/full join according to the two
  default arguments and yields pairs. `diff` yields rows whose selected values
  differ, with optional `default` padding and `key` comparison.
- `topk` returns a tuple of the largest `k` values, optionally by `key`.
  `peek` returns `(first_item, replayable_iterator)` and `peekn` returns
  `(tuple_of_first_items, replayable_iterator)`; the replayed iterator includes
  all peeked items. `random_sample` samples each item independently, and an
  integer `random_state` must make repeated runs deterministic.
- `getter(index)` returns a callable that retrieves one index/key or a nested
  sequence of indexes/keys. The sentinel `no_default` is a distinct internal
  default marker, and `no_pad` is the distinct default marker for `partition`.

### Dictionary operations

Implement these signatures in `toolz.dicttoolz`:

```text
merge(*dicts, **kwargs)
merge_with(func, *dicts, **kwargs)
valmap(func, d, factory=dict)
keymap(func, d, factory=dict)
itemmap(func, d, factory=dict)
valfilter(predicate, d, factory=dict)
keyfilter(predicate, d, factory=dict)
itemfilter(predicate, d, factory=dict)
assoc(d, key, value, factory=dict)
dissoc(d, *keys, **kwargs)
assoc_in(d, keys, value, factory=dict)
update_in(d, keys, func, default=None, factory=dict)
get_in(keys, coll, default=None, no_default=False)
```

`merge` returns a new mapping and gives later mappings precedence. `merge_with`
collects values for equal keys and applies `func` to each value list. The map
and filter operations construct a new mapping using `factory`; they do not
mutate the input. `assoc` and `dissoc` copy before changing keys. `assoc_in`
and `update_in` copy each nested mapping along the changed path, create missing
levels with `factory`, and leave the original structure unchanged. `get_in`
walks nested mappings/sequences and returns `default` for missing paths unless
`no_default` is true, in which case the underlying lookup exception is raised.
Mapping insertion order and custom mapping factories must be preserved.

### Function operations

Implement these `toolz.functoolz` APIs:

```text
identity(x)
apply(*func_and_args, **kwargs)
thread_first(val, *forms)
thread_last(val, *forms)
memoize(func, cache=None, key=None)
compose(*funcs)
compose_left(*funcs)
pipe(data, *funcs)
complement(func)
juxt(*funcs)
do(func, x)
curry(func, *args, **kwargs)
flip(func, a, b)
excepts(exc, func, handler=return_none)
```

`identity` returns its argument. `apply` calls the first argument with the
remaining positional and keyword arguments and rejects a missing callable.
`compose` applies functions right-to-left, `compose_left` applies them
left-to-right, and `pipe` applies them left-to-right starting with `data`.
With no functions, the composition result is the identity function. `complement`
negates a predicate, `do` runs a side-effect function and returns its input,
and `flip` calls a binary function with its two arguments reversed.

`memoize` caches results using a supplied mapping or a generated mapping. Its
optional `key(args, kwargs)` receives the call arguments and must return a
hashable key. Unhashable memoization arguments raise `TypeError`. The wrapper
preserves the wrapped callable metadata needed by ordinary introspection.

`thread_first` and `thread_last` thread the value through callable forms or
tuple forms. A tuple form inserts the value as the first or last argument.
`juxt` calls each supplied callable with the same arguments and returns a
tuple. `curry` supports decorator use, partial positional/keyword arguments,
additional calls, and callable metadata; once enough arguments are present it
calls the wrapped function. `excepts` catches the specified exception class or
tuple and passes the exception to `handler`, using `return_none` by default.

The module also exposes `instanceproperty`, `InstanceProperty`, `Compose`,
`num_required_args`, `has_varargs`, `has_keywords`, `is_valid_args`,
`is_partial_args`, and `is_arity` for the introspection and serialization
behavior exercised by the package. These helpers must work with ordinary
Python functions, builtins, `functools.partial`, and `curry` instances where
the interpreter exposes enough signature information.

### Recipes and curried namespace

`toolz.recipes.countby(key, seq)` returns a mapping of key results to counts,
and `partitionby(func, seq)` splits the input whenever consecutive key
results change. Both accept a callable or getter-compatible key.

`toolz.curried` must expose the ordinary function namespace plus curry-enabled
versions of `accumulate`, `assoc`, `assoc_in`, `cons`, `countby`, `dissoc`,
`do`, `drop`, `excepts`, `filter`, `get`, `get_in`, `groupby`, `interpose`,
`itemfilter`, `itemmap`, `iterate`, `join`, `keyfilter`, `keymap`, `map`,
`mapcat`, `nth`, `partial`, `partition`, `partition_all`, `partitionby`,
`peekn`, `pluck`, `random_sample`, `reduce`, `reduceby`, `remove`,
`sliding_window`, `sorted`, `tail`, `take`, `take_nth`, `topk`, `unique`,
`update_in`, `valfilter`, and `valmap`. Calling one of these with only an
initial subset of required arguments returns another curry object; completed
calls have the same result as the corresponding `toolz` function. The
namespace also exposes `merge` and `merge_with` from
`toolz.curried.exceptions`, and `toolz.curried.operator` provides curry
wrappers for callable members of Python's `operator` module except the
explicitly ignored unary/getter names.

### Sandbox and compatibility modules

`toolz.sandbox.core.EqualityHashKey(obj, key=None)` wraps an object with
custom equality and hashing based on `key`, and `unzip(seq)` returns the
component iterators for a sequence of tuples. `toolz.sandbox.parallel.fold`
has signature `fold(binop, seq, default=no_default, map=map, chunksize=128,
combine=None)`: it reduces chunks through the supplied map implementation and
combines intermediate results, requiring `chunksize > 1`.

`toolz.compatibility` is a deprecated standard-library compatibility module.
It exposes `map`, `filter`, `range`, `zip`, `reduce`, `zip_longest`,
`iteritems`, `iterkeys`, `itervalues`, `filterfalse`, and the `PY3`, `PY34`,
and `PYPY` flags. Importing or reloading it emits the documented
`DeprecationWarning` while preserving those names.

### `tlz` fallback namespace

Importing `tlz` must install its compatibility loader and make the `tlz`
submodules mirror `toolz` when `cytoolz` is absent. If a compatible `cytoolz`
installation is present, the loader may prefer its implementations while
keeping `toolz.pipe` as the stable pure-Python reference. The project must not
download, vendor, or require `cytoolz` merely to satisfy the `tlz` imports.

## Error, ordering, and determinism contract

- Preserve normal Python exceptions for invalid arity, missing values,
  exhausted iterators, unsupported indexing, invalid factories, and unhashable
  memoization arguments. Do not convert errors into sentinel values unless a
  `default` parameter explicitly requests that behavior.
- Preserve encounter order for grouping, merging, filtering, frequency maps,
  joins, and first-seen uniqueness. Do not sort mappings unless the operation
  explicitly says to do so.
- Do not consume an input iterator more than the operation requires. Lazy
  results must defer work until iteration where the signature describes an
  iterator.
- For random sampling, honor the supplied integer seed or random-state object.
  Tests and examples must not rely on wall-clock timing or uncontrolled random
  state.
- Callable wrappers and curry objects must remain picklable when their wrapped
  callables are picklable, and their module/name/qualname metadata must remain
  coherent enough for normal Python introspection.

## Implementation Notes

- Keep the public module names and re-export identities consistent. In
  particular, root aliases must refer to the same callable objects as their
  defining modules, and curried wrappers must preserve the underlying
  function's result behavior.
- Use only Python's standard library for runtime imports. The optional
  `cytoolz` preference belongs only to the `tlz` compatibility behavior.
- Provide an installable `pyproject.toml` and include both runtime packages,
  their subpackages, `LICENSE.txt`, and the distribution metadata. A source
  checkout without an installed distribution must not be the only way to
  obtain the version string.
- Keep caller-provided mapping factories, callbacks, iterables, and random
  state objects under the caller's control. The library must not serialize,
  mutate, or replace them beyond the operation's documented copy/update
  semantics.
- The complete upstream behavior includes live Python callables, iterators,
  curry state, pickling, and the optional `tlz` loader. Any separate verifier
  must preserve those semantics through an explicitly reviewed child-side
  adapter; a generic JSON call alone is not a substitute for this contract.
