# Build `cachetools`

Create a complete, installable Python project named `cachetools` from an empty
workspace. The project is a small, dependency-free library of bounded mutable
mappings and memoizing decorators. It must reproduce the public behavior below
without relying on a preinstalled `cachetools` package or on network access at
runtime.

## Project Description

The package provides cache implementations based on FIFO, LFU, LRU, random
replacement, and time-aware eviction policies. It also provides decorators for
memoizing ordinary functions and instance methods, plus key-building helpers
and `functools.lru_cache`-style convenience decorators.

The distribution and import package are both named `cachetools`. The version
exposed as `cachetools.__version__` must be `"7.1.7"`.

## Supports

- Support CPython 3.10 and newer Python 3.x versions.
- Use a `src/cachetools/` package layout and provide a `pyproject.toml` that
  supports editable and regular installation with `pip install .`.
- Declare no third-party runtime dependencies. Build and test tools may be
  development-only dependencies.
- Include `cachetools/py.typed` and type-information files for the public
  package modules. The stubs must describe the public generic mapping,
  decorator, and key-function surfaces without changing runtime behavior.
- Keep the package usable offline after installation. The library itself must
  not make network, subprocess, filesystem, or environment-service calls.
- Re-export the nine top-level names listed in the Public API section from
  `cachetools`; also make the `cachetools.func` and `cachetools.keys` modules
  importable directly.
- A short README should explain installation and show ordinary cache and
  decorator usage. Documentation and examples must not become runtime
  dependencies.

## Public API

The following names and import paths are supported. Signatures shown here are
part of the contract; positional and keyword arguments not listed should not
be invented.

### Top-level `cachetools` module

```python
class Cache(maxsize, getsizeof=None)
class FIFOCache(maxsize, getsizeof=None)
class LFUCache(maxsize, getsizeof=None)
class LRUCache(maxsize, getsizeof=None)
class RRCache(maxsize, choice=random.choice, getsizeof=None)
class TTLCache(maxsize, ttl, timer=time.monotonic, getsizeof=None)
class TLRUCache(maxsize, ttu, timer=time.monotonic, getsizeof=None)

def cached(cache, key=cachetools.keys.hashkey,
           lock=None, condition=None, info=False)

def cachedmethod(cache, key=cachetools.keys.methodkey,
                 lock=None, condition=None, info=False)
```

`Cache` and all seven concrete cache classes are mutable mappings. They should
preserve normal mapping behavior for arbitrary hashable keys and values, and
support Python's generic subscription syntax for type checking where the
interpreter provides it.

### `cachetools.func`

```python
def fifo_cache(maxsize=128, typed=False)
def lfu_cache(maxsize=128, typed=False)
def lru_cache(maxsize=128, typed=False)
def rr_cache(maxsize=128, choice=random.choice, typed=False)
def ttl_cache(maxsize=128, ttl=600, timer=time.monotonic, typed=False)
```

Each function is usable either as `decorator = lru_cache(...)` followed by
`@decorator`, or directly as `@lru_cache` when the first argument is a user
function. The returned wrapper is callable and exposes `cache_info`,
`cache_clear`, and `cache_parameters`.

### `cachetools.keys`

```python
def hashkey(*args, **kwargs)
def methodkey(self, *args, **kwargs)
def typedkey(*args, **kwargs)
def typedmethodkey(self, *args, **kwargs)
```

These functions return hashable tuple-like cache keys when their participating
arguments are hashable.

## API Usage Guide

### Common cache mapping behavior

All cache classes derive from `collections.abc.MutableMapping` and expose:

- `maxsize` (read-only): the configured maximum aggregate value size;
- `currsize` (read-only): the aggregate size currently stored;
- `getsizeof(value)`: a static sizing function whose default result is `1`;
- the normal mapping operations (`__getitem__`, `__setitem__`,
  `__delitem__`, `__contains__`, iteration, `len`, `get`, `pop`,
  `setdefault`, `update`, and `clear`); and
- `popitem()`, which returns a `(key, value)` pair selected by the cache
  policy and raises `KeyError` when the cache is empty.

The optional `getsizeof` constructor argument is a callable receiving a value
and returning its size. A value's size is measured when it is inserted or
replaced; mutating a value later does not automatically recompute its size.
Reject negative sizes with `ValueError`. If a value is larger than `maxsize`,
raise `ValueError` and do not retain that value. When an insertion would make
the cache exceed `maxsize`, repeatedly call the policy's `popitem()` until the
new value fits. A zero-sized cache cannot retain a positive-sized value; the
convenience decorators catch that storage rejection and still return the
computed result. An unbounded numeric size such as `math.inf` is supported.

A cache miss from `cache[key]` raises `KeyError` unless a subclass overrides
`__missing__(key)`. The `__missing__` hook is used only for subscription misses;
`get`, `pop`, and `setdefault` must retain their ordinary mapping behavior and
must not unexpectedly invoke that hook. `Cache.clear()` empties both stored
values and size bookkeeping in constant time. Subclasses may override
`popitem`, `__getitem__`, `__setitem__`, or `__delitem__` to maintain policy
state, and users may subclass `Cache` to observe evictions.

The base `Cache` policy discards arbitrary entries. The concrete policies are:

- **`FIFOCache`** evicts entries in insertion order. Replacing an existing key
  acts as a reinsertion and moves that key to the newest position. Reads do not
  change its position.
- **`LFUCache`** counts successful retrievals and evicts entries with the
  lowest use count first. Equal-frequency ties are intentionally unspecified;
  callers must not require a particular tie victim.
- **`LRUCache`** marks successful reads and replacements as recent and evicts
  the least recently used entry first.
- **`RRCache`** stores a `choice` callable. On eviction it passes a non-empty
  sequence of current keys to that callable and removes the returned key. The
  default is `random.choice`; a caller may provide a deterministic choice for
  reproducible behavior. The read-only `choice` property returns the callable.

All cache classes are not thread-safe by themselves. Shared access must be
synchronized by the caller or by a memoizing decorator.

### Time-aware caches

`TTLCache(maxsize, ttl, timer=time.monotonic, getsizeof=None)` combines LRU
behavior with one expiration deadline per entry. On insertion, the deadline is
`timer() + ttl`. The supplied timer may return any values that support the
needed addition and later comparisons; it does not have to return seconds or a
number. The read-only `timer` property exposes the configured timer wrapper,
which is callable and can be used as a context manager to observe one frozen
time value during a compound operation. The read-only `ttl` property returns
the configured TTL.

Expired entries are inaccessible and are removed lazily. `expire(time=None)`
removes all entries expired by the supplied time (or by the current timer value
when omitted) and returns an iterable of `(key, value)` pairs in expiration
order. Ordinary mutating operations and size/iteration operations may perform
this cleanup. If no expired entry is available when space is needed, eviction
falls back to LRU order. An entry whose deadline is exactly the observed time
is expired.

`TLRUCache(maxsize, ttu, timer=time.monotonic, getsizeof=None)` has the same
mapping and lazy-expiration behavior, but computes each deadline by calling
`ttu(key, value, now)` at insertion, where `now` is the current timer value.
The read-only `ttu` property returns that callable. Deadlines must be
comparable with later timer values. An insertion whose computed deadline is
already expired removes an existing value for that key rather than retaining
an expired value. When no expired entry is available, this cache also evicts
by LRU order.

For deterministic tests of either time-aware class, provide a controllable
timer object and pass explicit values to `expire`; do not depend on wall-clock
sleep or the default monotonic clock.

### `cached`: memoizing ordinary functions

`cached` is a decorator factory. `cache` may be any mutable mapping, including a
plain `dict`, a `Cache` instance, or `None`. If it is `None`, calls are not
retained but the wrapper remains callable and exposes the same cache metadata
shape where applicable. `key` receives exactly the positional and keyword
arguments passed to the wrapped function and must return a hashable cache key.
The default is `cachetools.keys.hashkey`.

On a cache miss, call the wrapped function once and store its result. Do not
store a call that raises an exception. If storing into a bounded cache raises
`ValueError` because the result is too large, return the result normally but do
not let that storage error replace the function result. Cache hits return the
stored object without calling the wrapped function.

The wrapper must preserve normal introspection metadata, including
`__wrapped__`, name, and docstring. It provides these attributes:

- `cache`: the supplied mapping or `None`;
- `cache_key`: the supplied key function;
- `cache_lock`: the supplied lock, or the condition when no separate lock was
  supplied, otherwise `None`;
- `cache_condition`: the supplied condition, otherwise `None`; and
- `cache_clear()`, which empties the cache and resets statistics when enabled.

When `info=True`, also provide `cache_info()`, returning a tuple-like record
with fields `hits`, `misses`, `maxsize`, and `currsize`. Hits and misses count
calls by cache key; `cache_clear()` resets both counters. For a `Cache` instance,
`maxsize` and `currsize` come from that cache. For a generic mapping,
`maxsize` is `None` and `currsize` is its length. For an uncached `None`, both
are `0`. With `info=False`, no callable statistics method is required.

If `lock` is supplied, guard cache access with its context-manager protocol but
call the wrapped function outside the lock so unrelated calls can proceed. If
`condition` is supplied, it must provide the condition-variable operations
needed by the contract (`wait_for`, `notify_all`, and context management when
it is also used as the lock). Calls with the same key must not execute the
wrapped function concurrently when a condition is supplied; waiting callers
receive the cached result after the first call completes. Exceptions must wake
waiters and clear the pending state. A condition without a separate lock also
serves as the cache lock.

### `cachedmethod`: memoizing instance methods

`cachedmethod` has the same result, metadata, locking, condition, statistics,
exception, and oversized-result rules as `cached`, but `cache`, `lock`, and
`condition` arguments are callables that receive the method's `self` and return
the per-instance mapping or synchronization object. The key function is called
as `key(self, *args, **kwargs)`.

The default `methodkey` ignores `self`, so equal method arguments may share a
cache across instances when the cache callable returns a shared mapping. A
custom key function can include the instance when that is required.

The decorator is a descriptor. Bound wrappers expose `cache`, `cache_key`,
`cache_lock`, `cache_condition`, `cache_clear`, and (with `info=True`)
per-instance `cache_info` properties. Preserve the wrapped method's name,
docstring, and `__wrapped__` behavior. Instances used with the statistics path
must have a mutable `__dict__` so a bound wrapper and its counters can be
stored. Slot-only or immutable-`__dict__` instances must raise `TypeError` on
that unsupported path; the non-statistics compatibility path may emit a
`DeprecationWarning` where the public API permits it.

Using `cachedmethod` around a `classmethod` is a deprecated compatibility path:
keep it working for the supported Python range and emit `DeprecationWarning`
with normal warning semantics. Do not require classmethod support for new
instance-method designs.

### `cachetools.func` decorators

Each convenience decorator uses a thread-safe internal condition and returns a
wrapper with `cache_info`, `cache_clear`, and `cache_parameters`.

- `fifo_cache`, `lfu_cache`, `lru_cache`, and `rr_cache` select the matching
  cache policy. Their default `maxsize` is `128`.
- `ttl_cache` uses an LRU cache with a default `maxsize` of `128`, `ttl` of
  `600`, and `time.monotonic` timer.
- `maxsize=None` disables the bound and permits unbounded retention.
- `maxsize=0` executes calls but retains no values.
- `typed=False` uses ordinary key equality, so arguments such as `1` and
  `1.0` may share a result. `typed=True` includes argument types in the key.
- Passing a callable as the first argument applies the decorator directly to
  that user function with default settings.
- `cache_parameters()` returns a new dictionary containing exactly the
  effective `maxsize` and `typed` settings; mutating that dictionary must not
  change the wrapper.
- `cache_info()` follows the same four fields and reset behavior as `cached`.
  The convenience wrappers are thread-safe by default, but the wrapped
  function itself may run concurrently for distinct keys.

For `rr_cache`, honor the supplied `choice` callable. For `ttl_cache`, honor
custom `ttl` and `timer` values, including non-numeric timer domains such as
`datetime` plus `timedelta`.

### `cachetools.keys` functions

`hashkey(*args, **kwargs)` returns a tuple-like key containing positional
arguments and a distinct separator before keyword pairs. Keyword pairs are
ordered deterministically by keyword name. Positional and keyword forms must
not collide accidentally. All participating values must be hashable; allow the
normal `TypeError` from hashing an unhashable value.

`methodkey(self, *args, **kwargs)` has the same layout but drops its first
argument, normally an instance. `typedkey` adds the concrete type of every
argument (including keyword values) so values of different types produce
different keys. `typedmethodkey` does the same while dropping the first
argument. The returned tuple-like keys must support tuple concatenation and
pickling without changing equality or hash behavior.

## Implementation Notes

- Use deterministic ordering where the API promises it: keyword ordering in key
  functions, FIFO/LRU order, and expiration order. Do not invent a tie-breaker
  for LFU equal-frequency victims or pretend random replacement is deterministic.
- Inject timers, `ttu`, `choice`, sizing functions, locks, and conditions through
  the public arguments rather than relying on hidden global state.
- Do not expose private helper classes or implementation modules as additional
  required public API. The supported public names are the 18 names listed in
  `cachetools.__all__`, `cachetools.func.__all__`, and `cachetools.keys.__all__`.
- Keep exception types and lazy-expiration behavior observable through the
  public mapping and decorator interfaces. Do not swallow user-function
  exceptions or synchronization failures.
- The finished repository must install and import without the verifier tests
  being present in the workspace. Tests and test fixtures must remain separate
  from the candidate implementation.

Example:

```python
from cachetools import LRUCache, cached

cache = LRUCache(maxsize=2)
cache["a"] = 10
cache["b"] = 20
_ = cache["a"]
cache["c"] = 30       # "b" is the least recently used entry

@cached(LRUCache(maxsize=64), info=True)
def square(value):
    return value * value

assert square(4) == 16
assert square(4) == 16
assert square.cache_info().hits == 1
```
