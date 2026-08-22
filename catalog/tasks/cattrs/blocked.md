# `cattrs` static authoring audit and blocker

Status: **blocked**. This directory contains public, task-local authoring
provenance and validation evidence only. It contains no upstream test bytes,
private test bundle, private command plan, dependency wheelhouse, Dockerfile,
Harbor verifier, Oracle solution, secret, generated reward, or shared catalog
index update. The exact public revision was inspected in disposable checkouts
under `/tmp`; those checkouts are not task artifacts.

## Candidate identity and source freeze

The candidate was read from `reports/python-package-candidates.v1.md` and its
JSON companion:

- distribution/import package: `cattrs` (with a legacy `cattr` compatibility
  namespace);
- upstream: `https://github.com/python-attrs/cattrs`;
- requested revision:
  `f2e42f3c69dabd48dd1a5b8fb1aad9c1d39c339a`;
- commit subject: `Improve TypedDict key quoting`;
- author time: `2026-08-04T23:14:34+02:00`;
- commit time: `2026-08-09T22:01:30+02:00`;
- commit tree: `e49e94f623db7edafff0c4887f08e99241af0f49`;
- submodules: none;
- detached checkout: clean before and after the audit.

The unprefixed Git archive was generated three times from a full-history
checkout. All runs produced 1,576,960 bytes and the same SHA-256:

```text
fa31f0fd7b0764cd9f142e70988113e2b2852790144b7cb81064614170c5e470
```

The discovery report labels this candidate `hard`, estimates 5,980 source
SLOC, 150 public API symbols, 70 test files, 436 static test definitions, and
three runtime dependencies. Those values are retained as discovery/ranking
metadata, not treated as a frozen denominator. A transparent local inventory
found 36 modern `cattrs` modules and 14 `cattr` compatibility modules (50
tracked Python files); the modern package has 6,892 physical, 5,722 nonblank,
and 5,418 noncomment lines. The report does not specify its SLOC counting
method, so the local count is recorded rather than silently substituted.

This revision is not the PyPI 26.1.0 release used as discovery metadata. In a
full-history checkout:

```text
git describe --tags --always --long HEAD
v26.1.0-41-gf2e42f3
```

A temporary wheel build from the exact commit produced
`cattrs-26.1.1.dev41-py3-none-any.whl` (74,618 bytes,
SHA-256 `b63542e19188414649359a0ca3017e9f192413959b8e0903746a842ccd865d50`).
The public `cattrs-26.1.0.tar.gz` is 495,672 bytes with SHA-256
`fa239e0f0ec0715ba34852ce813986dfed1e12117e209b816ab87401271cdd40`; 12
runtime source files differ between that release sdist and the requested
post-release commit. Therefore a final task must use the exact commit/archive
lock and must not use the PyPI release as a source substitute.

## License and archive evidence

`LICENSE` at the requested commit is the standard MIT License:

- bytes: 1,074;
- Git blob: `340022c335c359953f29e61e4beb8049ea038d7c`;
- file SHA-256:
  `f5fb9d1ede37a88ca47f420c499dca0f4a05bc993e12c77d23520aad291c01bf`.

The commit-specific raw GitHub bytes have the same length and SHA-256. The
GitHub license endpoint reports `MIT License`, SPDX ID `MIT`, key `mit`, and
path `LICENSE`. The source text, project metadata (`license = {text = "MIT"}`),
and public license endpoint agree. This is acceptable license evidence; the
remaining blockers are source/version, environment, verifier, and artifact
boundaries rather than licensing.

## Complete Python package/API inventory

The audit covered every tracked `.py` file under both installable namespaces,
not only root `__all__` entries. An AST inventory and a runtime
`inspect.signature` inventory were generated outside the repository after
installing all public optional backends. The runtime inventory covered 50
importable modules, 108 modern `__all__` slots (84 unique names), 53 legacy
`cattr.__all__` slots (36 unique names), 137 locally defined public classes or
functions in the modern namespace, and public methods of all exported
classes. The normalized inventory JSON is outside the task tree and has SHA-256
`4646c3a6c282ce2e27543d98c6538d96973ec8da42b6ef61874356f0b0244f8d`.

The complete modern module set is `cattrs`, `_compat`, `_generics`, `cols`,
`converters`, `disambiguators`, `dispatch`, `enums`, `errors`, `fns`, `gen`,
`gen._consts`, `gen._generics`, `gen._lc`, `gen._shared`, `gen.typeddicts`,
`literals`, `preconf`, `preconf.bson`, `preconf.cbor2`, `preconf.json`,
`preconf.msgpack`, `preconf.msgspec`, `preconf.orjson`, `preconf.pyyaml`,
`preconf.tomlkit`, `preconf.tomllib`, `preconf.ujson`, `strategies`,
`strategies._class_methods`, `strategies._subclasses`, `strategies._unions`,
`subclasses`, `typealiases`, `types`, and `v`. The legacy set is `cattr`,
`cattr.converters`, `cattr.disambiguators`, `cattr.dispatch`, `cattr.errors`,
`cattr.gen`, `cattr.preconf`, and the seven legacy preconf backend modules.

The supported/documented modern surface is listed below. Names in modules
whose names begin with `_` were also inventoried because upstream tests import
them, but they are implementation seams and are not promoted as public task
API without a separate decision.

- `cattrs` root (25 exports):
  `AttributeValidationNote`, `BaseConverter`, `BaseValidationError`,
  `ClassValidationError`, `Converter`, `ForbiddenExtraKeysError`,
  `GenConverter`, `IterableValidationError`, `IterableValidationNote`,
  `SimpleStructureHook`, `StructureHandlerNotFoundError`,
  `UnstructureStrategy`, `get_structure_hook`, `get_unstructure_hook`,
  `global_converter`, `override`, `register_structure_hook`,
  `register_structure_hook_func`, `register_unstructure_hook`,
  `register_unstructure_hook_func`, `structure`,
  `structure_attrs_fromdict`, `structure_attrs_fromtuple`,
  `transform_error`, and `unstructure`.
- `cattrs.converters`: `BaseConverter`, `Converter`, `GenConverter`, and
  `UnstructureStrategy`. The reviewed constructor signatures are:
  `BaseConverter(dict_factory=dict, unstruct_strat=AS_DICT,
  prefer_attrib_converters=False, detailed_validation=True,
  unstructure_fallback_factory=..., structure_fallback_factory=...)` and
  `Converter`/`GenConverter` add `omit_if_default`, `forbid_extra_keys`,
  `type_overrides`, `unstruct_collection_overrides`, and `use_alias`.
  Public methods include `structure`, `unstructure`, both attrs conversion
  directions, hook registration (direct, predicate, and factory forms), hook
  lookup, generated collection/typed-dict/annotated hooks, and `copy`.
- `cattrs.gen`: `override`,
  `make_dict_structure_fn`, `make_dict_structure_fn_from_attrs`,
  `make_dict_unstructure_fn`, `make_dict_unstructure_fn_from_attrs`,
  `make_hetero_tuple_structure_fn`, `make_hetero_tuple_unstructure_fn`,
  `make_iterable_unstructure_fn`, `make_mapping_structure_fn`, and
  `make_mapping_unstructure_fn`. `AttributeOverride` is the attrs-backed
  value object used by `override` and by all generated hook factories.
- `cattrs.gen.typeddicts`: `make_dict_structure_fn` and
  `make_dict_unstructure_fn` for `TypedDict` classes.
- `cattrs.cols`: `defaultdict_structure_factory`,
  `homogenous_tuple_structure_factory`, `is_abstract_set`, `is_any_set`,
  `is_defaultdict`, `is_frozenset`, `is_mapping`, `is_mutable_sequence`,
  `is_namedtuple`, `is_sequence`, `is_set`,
  `iterable_unstructure_factory`, `list_structure_factory`,
  `mapping_structure_factory`, `mapping_unstructure_factory`,
  `namedtuple_dict_structure_factory`,
  `namedtuple_dict_unstructure_factory`, `namedtuple_structure_factory`,
  and `namedtuple_unstructure_factory`.
- `cattrs.disambiguators`: `create_default_dis_func` and
  `is_supported_union`; the legacy alias
  `create_uniq_field_dis_func` is also present and is re-exported by the
  `cattr.disambiguators` compatibility module.
- `cattrs.dispatch`: `FunctionDispatch`, `MultiStrategyDispatch`, and the
  documented hook type aliases (`TargetType`, `UnstructuredValue`,
  `StructuredValue`, `StructureHook`, `UnstructureHook`, and `HookFactory`).
- `cattrs.errors`: `CattrsError`, `StructureHandlerNotFoundError`,
  `BaseValidationError`, `IterableValidationError`,
  `IterableValidationNote`, `ClassValidationError`,
  `AttributeValidationNote`, and `ForbiddenExtraKeysError`. The validation
  classes preserve nested `ExceptionGroup` structure, notes, target class,
  path/index, and extra-field sets.
- `cattrs.fns`, `cattrs.literals`, `cattrs.typealiases`, `cattrs.types`, and
  `cattrs.v`: respectively `identity`/`raise_error`, literal predicates,
  type-alias predicates/factory, `SimpleStructureHook`, and
  `format_exception`/`transform_error`.
- `cattrs.strategies`: `configure_tagged_union`,
  `configure_union_passthrough`, `include_subclasses`, and
  `use_class_methods`.
- `cattrs.preconf`: `validate_datetime`, `wrap`,
  `is_primitive_enum`, and `literals_with_enums_unstructure_factory`.
  Each backend module exposes a `make_converter` factory, a
  `configure_converter` function, and its converter subclass:
  `BsonConverter`, `Cbor2Converter`, `JsonConverter`, `MsgpackConverter`,
  `MsgspecJsonConverter`, `OrjsonConverter`, `PyyamlConverter`,
  `TomlkitConverter`, `TomllibConverter`, and `UjsonConverter`. `bson` also
  contains `Base85Bytes`; the msgspec backend exposes typed dumps/loads hook
  methods.
- The installed `cattr` compatibility namespace was audited separately. Its
  root re-exports `BaseConverter`, `Converter`, `GenConverter`,
  `UnstructureStrategy`, `global_converter`, `override`, `structure`,
  `structure_attrs_fromdict`, `structure_attrs_fromtuple`, and `unstructure`.
  Compatibility modules re-export the old `gen`, `errors`, `dispatch`,
  `disambiguators`, and seven preconfigured converter surfaces. This shim is
  part of the source/package boundary and must not be dropped while claiming
  parity with the frozen revision.

The public contract is substantially broader than the 25 root names: it
covers attrs and dataclass classes, `TypedDict`, named tuples, enums, unions,
generics, `Annotated`, `Literal`, `NewType`, `Final`, sequences, mappings,
sets, deques, `defaultdict`, custom hook factories, generated functions,
validation error trees, and all nine optional serialization backends. The
inventory also recorded signatures for all exported functions/classes and
methods; no module was excluded because it lacked an `__all__` declaration.
The additional public-but-undocumented names found by the same scan (for
example `get_annots`, `generate_mapping`, `subclasses`, and backend-specific
factory helpers) are explicitly marked internal/test-visible rather than
silently omitted from the inventory.

## Dependency closure and the `attrs` relationship

The exact cattrs `pyproject.toml` declares:

```text
requires-python: >=3.10
runtime: attrs>=25.4.0, typing-extensions>=4.14.0,
         exceptiongroup>=1.1.1; python_version < 3.11
build: hatchling, hatch-vcs
```

Optional backend requirements are `pymongo`, `cbor2`, `msgpack`, `msgspec`,
`orjson`, `PyYAML`, `tomlkit`, `tomli`/`tomli-w`, and `ujson`. The test group
adds `hypothesis`, `pytest`, `pytest-typing` (CPython 3.14 only), `mypy`
(CPython 3.14 only), `pytest-benchmark`, `immutables`, `coverage`, and
`pytest-xdist`; lint, docs, and benchmark groups add further packages.

The requested attrs candidate was also checked at its exact revision
`c1dc5dcba16ed827aa6dcad896b41a3afedb4e32`:

```text
git describe --tags --always --long HEAD
25.4.0-125-gc1dc5dc
```

Its repeated unprefixed source archive is 2,150,400 bytes with SHA-256
`b83faf32c14ce76de55803d8d641e1ea557efd184fa4218de08c4888e9699f4b`, and
its MIT `LICENSE` is 1,109 bytes with SHA-256
`882115c95dfc2af1eeb6714f8ec6d5cbcabf667caff8729f42420da63f714e9f`. Its
exact source build produced `attrs-26.1.1.dev70-py3-none-any.whl`
(68,560 bytes, SHA-256
`d3fef6216338715872359d49b7eb2d3759762962b55c9bbb7254121b5ad35b16`).
The cattrs source imports these attrs symbols:

```text
NOTHING, NothingType, Attribute, Factory, Converter, define, evolve, frozen,
has, resolve_types, fields, fields_dict, AttrsInstance
```

All 13 symbols exist in the exact attrs checkout. A representative cattrs
smoke run using the locked registry `attrs==25.4.0` passed 159 tests, while
the full baseline below used the exact attrs source wheel. This gives useful
compatibility evidence but does not create a dependency artifact.

`uv lock --check` passed and the cattrs lock contains 81 package records. Its
base resolution is `attrs==25.4.0`, `typing-extensions==4.14.1`, and
`exceptiongroup==1.3.0`; the exact attrs candidate revision is not represented
as a content-addressed dependency source in that lock. The attrs source itself
also needs `hatchling`, `hatch-vcs`, and `hatch-fancy-pypi-readme>=23.2.0` to
build. Thus the lock is useful resolver evidence, not a final offline
`DependencyBundle` for the two exact source revisions.

All extras were installable in a temporary CPython 3.14 environment, but
PyYAML and PyMongo were built locally during that sync. `orjson`, `ujson`,
`msgspec`, `cbor2`, and other optional paths have platform/Python-specific
wheels or build behavior. No immutable base-image digest, wheelhouse, system
build-tool lock, or authorized private dependency artifact exists in this
lane. Environment and dependency status therefore remain **unknown**.

## Test inventory, collection, and baseline

The source tree has 64 tracked test `.py` files and one typing `.md` file. The
six non-`__init__` benchmark `.py` files under `bench/` account for the
report's 70-file estimate. AST counting gives 418 `test*` definitions in the
test tree and 18 benchmark definitions, matching the report's 436 static
definition estimate when benchmark files are included. Static definitions are
not a test denominator.

The test configuration is interpreter/plugin-sensitive. `tests/conftest.py`
ignores `test_gen_dict_649.py` and the 3.14-only msgspec file below Python
3.14, ignores `*_695.py` below Python 3.12, and ignores `_cpython.py` files on
PyPy; the `pytest-typing` plugin adds the
`tests/test_typing_structure.md` collection on CPython 3.14. The upstream
Justfile runs `pytest ... tests`, not the benchmark directory.

With all public optional backends installed and the exact attrs source wheel,
CPython 3.14.6, pytest 9.0.3, and pytest-typing 26.3.0, this command was run
twice:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  PYTHONPATH=/tmp/cattrs-full/src \
  /tmp/cattrs-venv314/bin/python -m pytest \
  --collect-only -q -p no:cacheprovider tests
```

Both runs exited zero with no collection errors and collected **1,002**
items. The normalized node-id list was byte-identical in both runs and has
SHA-256 `cb0b2e2f30963de10d1c089e2fea871a825f1aba7693ea33b3a3e10d98aa9e66`.
The all-extras collection is the only collection observation in this audit
that is complete for the CPython 3.14 test set; it is not yet a frozen
benchmark denominator because no final image or private test artifact exists.

The same all-extras collection on CPython 3.12.11 and 3.13.14 collected
**988** items and emitted an `Unknown config option: typing_checkers` warning
because the 3.14-only typing plugin is not installed under those lock
markers. The 14-node difference is seven Markdown typing checks, one
`test_msgspec_314_cpython.py` item, and six `test_gen_dict_649.py` items. This
proves that `requires-python >=3.10` is not sufficient to determine a stable
frozen total.

A collection with the test group but without optional extras collected 928
items and failed with four collection errors (`msgspec`, `yaml`, and `bson`
were absent). Optional backend policy must therefore be explicit; missing
extras cannot be silently treated as skipped tests.

For an additional source-only baseline, the full CPython 3.14 all-extras suite
was run twice with JUnit output:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
  PYTHONPATH=/tmp/cattrs-full/src \
  /tmp/cattrs-venv314/bin/python -m pytest -q -p no:cacheprovider \
  --junitxml=/tmp/cattrs-baseline-N.xml tests
```

Each run exited zero in about 4 minutes 50 seconds and reported **987
passed, 15 xfailed**, with no ordinary failures or errors. The JUnit suite
reported `tests=1002`, `failures=0`, `errors=0`, `skipped=15`. The normalized
(class, node, status) JUnit records were identical across runs and have
SHA-256 `a2041bec0accd4cef9c2aba1b66ff3b64693caa045e0942668354ddf019391fb`.
The 15 expected failures are represented as JUnit skips; the eventual metric
must state whether xfail is excluded, counted as non-passed, or handled by a
separate expected-status contract. This baseline is not an Oracle reward and
does not satisfy the three-run publication gate.

## Serialization and callable boundary

The upstream package cannot be represented faithfully by the generic
JSON-only `candidate_client` contract used by a separate verifier:

- `structure` receives a live target class/type object and arbitrary Python
  values; `unstructure` returns values that may be sets, tuples, bytes,
  `Path`, enums, datetimes, custom mappings, attrs instances, dataclasses,
  named tuples, or backend-specific objects.
- Hook registration accepts live functions, predicates, factories, bound
  methods, `functools.partial` objects, and callbacks that close over classes
  or converter state. `override` stores structuring and unstructuring
  callables in an attrs object.
- `Converter` and `MultiStrategyDispatch` are mutable, stateful registries
  with per-instance caches. `global_converter`, `copy`, `deepcopy`, recursive
  generation, and hook replacement require state to survive across calls.
- The generated-hook factories execute generated Python source with
  `compile`/`eval` and optionally populate the process-global `linecache`.
  Generated function identity, source names, and cache state are observable
  in tests.
- Preconfigured JSON, Msgpack, BSON, CBOR2, Msgspec, orjson, ujson, YAML,
  TOML, and tomllib converters accept backend-specific keyword arguments and
  return `str`, `bytes`, native date/time values, ObjectIds, or other objects.
- Validation uses nested PEP 654 `ExceptionGroup` instances with notes,
  target types, field/index paths, and set-valued extra-field errors; tests
  also exercise pickling of these objects.
- The test suite dynamically defines attrs classes, dataclasses, TypedDicts,
  named tuples, enums, recursive/self/generic types, and callable hooks inside
  the trusted pytest process. It directly imports candidate modules and
  private compatibility helpers.

Directly importing the candidate from trusted pytest would violate the
separate-verifier rule. A production task needs a cattrs-specific child-side
scenario adapter that can declaratively define classes/types, register a
finite callback vocabulary inside the untrusted child, invoke stateful
converter sessions, invoke each selected backend, and return normalized
JSON-safe values and exception trees. Hidden expected values and callback
assertions must remain in a private verifier bundle. No such adapter or
private command/test artifact is present here.

## Determinism and environment sensitivity

The two collection runs and two full source baselines were stable under the
same CPython 3.14.6, dependency versions, `PYTHONHASHSEED=0`, and plugin set.
That does not imply byte determinism across environments:

- The default converter preserves ordinary sets as sets. A direct probe over
  `PYTHONHASHSEED=0,1,2,3,12345` produced different set iteration/repr order.
  The JSON preconfigured converter turns the same set into a list, so its
  serialized array order also changed with the hash seed.
- `ForbiddenExtraKeysError` stores extra fields in a set. The `repr` of the
  enclosing `ClassValidationError` changed field order across hash seeds even
  though the semantic set was equal.
- Generated hook source and `linecache` entries are process-local and depend
  on generation order. A fresh child process is needed for clean state; raw
  function filenames or linecache sizes should not be compared across calls.
- Hypothesis data generation, Python typing behavior, attrs behavior, and
  optional serializer output vary with Python version and dependency versions.
  The 988-versus-1,002 collection totals demonstrate one concrete version
  effect. The suite's expected failures are also status-sensitive.
- Mapping/attribute declaration order is intentionally meaningful, while set
  order is not. A verifier comparing serialized bytes must either pin the
  interpreter/hash seed and every backend or canonicalize unordered values,
  exception sets, and backend-specific representations.

Static scans found no network, socket, subprocess, or external-service calls
in the candidate library or its public tests. They did find dynamic
`eval`/`compile`, `linecache`, global mutable dispatch state, optional native
serialization modules, and several set-based algorithms. These are isolation
and reproducibility concerns even in an offline task.

## Decision and reopen conditions

Keep `cattrs` **blocked** and do not publish or run Oracle in this lane. The
blocking findings are:

1. The requested commit is a post-release development snapshot (`26.1.1.dev41`)
   whose behavior differs from PyPI 26.1.0; source and version locks must be
   explicit.
2. The exact attrs candidate revision is a post-25.4.0 development snapshot
   (`26.1.1.dev70`), while the cattrs lock resolves registry attrs 25.4.0. A
   final dependency bundle must choose and attest the exact closure rather than
   infer it from a lockfile.
3. No immutable verifier image, platform/Python lock, system build-tool lock,
   content-addressed wheelhouse, or private dependency artifact is available.
4. Collection changes with Python version and pytest plugin availability, and
   the 15 xfail statuses need an approved metric policy.
5. The upstream behavior crosses live class, callable, stateful registry,
   generated-code, exception-group, and binary serialization boundaries that
   the generic separate-verifier JSON contract cannot carry. No reviewed
   child-side adapter exists.
6. No private hidden-test bundle, allowlisted command artifact, Oracle bundle,
   or control records are authorized here.

Reopen only after the exact cattrs and attrs source revisions are materialized
through the authorized private artifact resolver, a final image and complete
build/runtime/test/optional dependency closure are frozen, one exact
interpreter/plugin/test set is selected with a structured collection record,
xfail/skipped semantics are written into the metric contract, and a reviewed
child-side adapter preserves the callable/stateful/serialization behavior.
Oracle and empty/stub/forgery/offline controls belong to that later stage.

## Commands and evidence summary

The principal public-source commands completed without modifying this task or
shared repository state were:

```text
GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none \
  https://github.com/python-attrs/cattrs.git /tmp/cattrs-full
git -C /tmp/cattrs-full checkout --detach f2e42f3c69dabd48dd1a5b8fb1aad9c1d39c339a
git -C /tmp/cattrs-full archive --format=tar HEAD | sha256sum   # repeated x3
uv lock --check
git -C /tmp/cattrs-full describe --tags --always --long HEAD
uv build --wheel --out-dir /tmp/cattrs-full-dist --no-sources
uv sync --locked --no-dev --group test --all-extras --no-install-project ...
python -m pytest --collect-only -q -p no:cacheprovider tests
python -m pytest -q -p no:cacheprovider --junitxml=/tmp/cattrs-baseline-N.xml tests
```

The dependency-closure probe separately checked out attrs at
`c1dc5dcba16ed827aa6dcad896b41a3afedb4e32`, built its temporary wheel, verified
all 13 attrs symbols imported by cattrs, and ran a 159-test cattrs smoke set
against registry `attrs==25.4.0`. No hidden test bytes, private fixtures,
Docker build, Harbor run, Oracle execution, shared index, or secret was used.
