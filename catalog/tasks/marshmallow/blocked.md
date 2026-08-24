# Marshmallow Authoring Audit and Blocker

Status: **oracle-passed remediation; historical blocker retained below**. The
current task has a private JSON scenario verifier, offline dependency/Oracle
bundles, generic compiled `33/33` Oracle and empty/stub/forgery controls. The
broader in-process upstream suite below remains historical context only.

## Candidate and Source Freeze

- Upstream: `https://github.com/marshmallow-code/marshmallow`
- Revision requested and resolved in a detached checkout:
  `c7b559a1fa3aba57ca6dba0ab336841c5038a782`
- Commit tree: `09ef226dec750308a6d2e8819487432a61b43aa4`
- Commit time: `2026-08-08T10:26:10-04:00` (author and committer)
- Commit subject: `Bump version and update changelog`
- Submodules: none
- Unprefixed `git archive --format=tar HEAD` SHA-256:
  `c531024b6b6cf15be06fd2205f9304265524a3b1958e3e6c09793bc9b9f35728`
- `LICENSE`: 1,064 bytes, 19 lines, newline terminated; SHA-256
  `906b5d9051e426144cb173ad911667b8ebd05a9c584c2c26c135b32a3ed12001`.
  The file is the MIT License and the project metadata declares `MIT`.
- The detached source checkout was clean after all audit commands.

The source reports version `4.3.1`, distribution and import name
`marshmallow`, `requires-python = ">=3.10"`, and a `flit_core>=3.12,<4`
PEP 517 build backend. A local source sanity build produced
`marshmallow-4.3.1-py3-none-any.whl` (49,219 bytes, SHA-256
`3a0897fff27578fd5d051c858de53b72180e68a856807e4e301f6d04d52dea97`). This
wheel is a temporary validation artifact and is not stored in the catalog.

The package contains 14 Python files under `src/marshmallow`, 5,052 physical
lines, 4,157 nonblank lines, and 3,937 nonblank/non-comment lines. The source
is a medium-sized library rather than a single serializer function. Its
implementation includes schema metaclass binding, field composition,
validation/error aggregation, class registration, context variables, date/time
conversion, and JSON rendering.

## API and Serialization Inventory

The root package explicitly exports 14 names from `marshmallow.__all__`:
`EXCLUDE`, `INCLUDE`, `RAISE`, `Schema`, `SchemaOpts`, `ValidationError`,
`fields`, `missing`, `post_dump`, `post_load`, `pre_dump`, `pre_load`,
`validates`, and `validates_schema` (`src/marshmallow/__init__.py:1-28`).

The `marshmallow.fields` module has 37 `__all__` names, including aliases
`Str`, `Int`, `Bool`, and `URL`, and field classes for `Raw`, `Nested`,
`Pluck`, `List`, `Tuple`, `String`, `UUID`, `Integer`, `Float`, `Decimal`,
`Boolean`, `DateTime`, `NaiveDateTime`, `AwareDateTime`, `Time`, `Date`,
`TimeDelta`, `Mapping`, `Dict`, `Url`, `Email`, `IP`/`IPv4`/`IPv6`, IP
interface fields, `Enum`, `Method`, `Function`, and `Constant`. The
`marshmallow.validate` module provides callable validator classes `And`,
`URL`, `Email`, `Range`, `Length`, `Equal`, `Regexp`, `Predicate`, `NoneOf`,
`OneOf`, `ContainsOnly`, and `ContainsNoneOf`, plus the `Validator` base.

The principal schema contract is:

- `Schema(*, only=None, exclude=(), many=None, load_only=(), dump_only=(),
  partial=None, unknown=None)` constructs a bound schema from declared field
  instances.
- `Schema.dump(obj, *, many=None)` returns native Python data; `Schema.dumps`
  applies the configured render module and returns encoded text/bytes.
- `Schema.load(data, *, many=None, partial=None, unknown=None)` returns
  deserialized native or domain values; `Schema.loads` decodes through the
  configured render module first.
- `Schema.validate(data, *, many=None, partial=None, unknown=None)` returns
  validation messages rather than raising for ordinary validation failures.
- `Schema.from_dict(fields, *, name="GeneratedSchema")` creates an unregistered
  schema class from field instances.
- `pre_load`, `post_load`, `pre_dump`, `post_dump`, `validates`, and
  `validates_schema` decorate instance methods. Hook ordering within one hook
  category is not guaranteed by the upstream documentation.

Important input/output shapes and state are not JSON-only:

- `Field` accepts validators, pre-load/post-load callables, defaults, metadata,
  and error-message overrides. `Function` accepts Python callables and
  `Method` resolves named schema methods (`src/marshmallow/fields.py:2002-2107`).
- `Nested` accepts a schema instance, schema class, registered class name,
  field dictionary, or a callable returning a schema/dictionary. It caches a
  nested schema and deep-copies/binds fields (`src/marshmallow/fields.py:480-625`).
- `List` and `Tuple` accept field classes or instances and recursively
  deserialize/serialize their values. Lists also accept generators and other
  iterables; tuples preserve tuple output (`src/marshmallow/fields.py:732-891`).
- `Enum`, `UUID`, `Decimal`, `DateTime`, `Time`, `Date`, `TimeDelta`, IP, and
  interface fields consume or produce `enum.Enum`, `uuid.UUID`,
  `decimal.Decimal`, `datetime`/`date`/`time`, `timedelta`, and `ipaddress`
  objects. `dump` returns these fields' native serialized forms, while
  `load` returns the domain objects.
- `ValidationError` carries `messages`, `field_name`, raw `data`, and
  `valid_data`; nested/collection errors use dictionaries keyed by fields or
  indexes. This is richer than a scalar exception string.
- `Schema.Meta.render_module` must provide `dumps` and `loads`; the default is
  stdlib `json`, while the tests use `simplejson` and a custom `mockjson`
  module (`src/marshmallow/schema.py:581-789`, `tests/base.py:190-222`).
- Schema class construction mutates the process-wide class registry, nested
  fields cache schema instances, and `experimental.context.Context` stores a
  context-local value using `contextvars` (`src/marshmallow/schema.py:89-190`,
  `src/marshmallow/experimental/context.py:44-73`).

## Tests and Collection

The pinned checkout tracks 19 Python files under `tests/`. Four files are
under `tests/mypy_test_cases/` and are excluded by the upstream pytest setting
`norecursedirs = ".git .ropeproject .tox docs env venv tests/mypy_test_cases"`
(`pyproject.toml:153-154`). The collected suite has 12 test modules and 652
static `test_*` definitions; parametrization expands the final collection to
1,188 unique test nodes:

```text
tests/test_context.py          12
tests/test_decorators.py       44
tests/test_deserialization.py 393
tests/test_error_store.py      31
tests/test_exceptions.py         7
tests/test_fields.py           108
tests/test_options.py           10
tests/test_registry.py           10
tests/test_schema.py            203
tests/test_serialization.py     129
tests/test_utils.py             20
tests/test_validate.py          221
                                ---
                                1188
```

The direct frozen-source baseline used CPython 3.14.6, pytest 9.1.1, and
simplejson 4.1.1 with `PYTHONPATH=src` and `-p no:cacheprovider`:

| Run | Collected | Passed | Failed | Errors | Skipped | Wall time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline-1 | 1,188 | 1,188 | 0 | 0 | 0 | 3.43 s |
| baseline-2 | 1,188 | 1,188 | 0 | 0 | 0 | 3.33 s |
| baseline-3 | 1,188 | 1,188 | 0 | 0 | 0 | 3.38 s |

These are direct source baselines only. They are not Harbor Oracle runs and
do not establish a verifier `valid` result or a publishable reward.

Collection requires the test dependency `simplejson` even though it is not a
runtime dependency: `tests/conftest.py` imports `tests.base`, and
`tests/base.py:10` imports `simplejson` at module import time. A clean
collection attempt with pytest 9.1.1 but without simplejson failed with exit
code 4 and `ModuleNotFoundError: No module named 'simplejson'` before any test
node was collected.

The suite exercises substantially more than plain JSON values:

- `tests/base.py` defines custom `User` and `Blog` objects, several enum
  classes, timezone-aware and naive date/time values, UUIDs, a custom field,
  named methods, `fields.Function` callbacks, and a `simplejson` render module.
- `tests/test_context.py` uses `Context` scopes and lambdas that read the
  current context, including nested schemas and an intentionally unpicklable
  object.
- `tests/test_decorators.py` defines schema classes with pre/post processors
  and schema/field validators. These methods receive `many`, `partial`,
  `unknown`, and optionally original data as keyword arguments.
- `tests/test_deserialization.py` passes `datetime`, `Decimal`, UUID, enum,
  IP address, and byte values; it patches `datetime.datetime` with custom
  subclasses; and it passes validation callback lambdas.
- `tests/test_serialization.py` serializes custom objects, generators, sets,
  named tuples, tuples, and values generated from the current time.
- `tests/test_registry.py` checks process-local registration and class-name
  resolution, including duplicate-name behavior.

No network, socket, HTTP, subprocess, or external service integration was
found in the collected source/tests. The examples and documentation are not
part of the collected suite. The package has no project console entry point or
library CLI; only example scripts and an `orderedset.py` module guard contain
`__main__` blocks.

## Dependencies and Optional Integrations

Runtime metadata declares only these conditional dependencies:

```text
backports-datetime-fromisoformat; python_version < "3.11"
typing-extensions; python_version < "3.11"
```

The upstream `uv.lock` resolves them as backports-datetime-fromisoformat
2.0.3 and typing-extensions 4.16.0. The test group declares unbounded
`pytest` and `simplejson`; the pinned lock currently resolves pytest 9.1.1 and
simplejson 4.1.1. The dev groups additionally include mypy,
types-simplejson, pre-commit, tox, tox-uv, and documentation/lint packages.
The lock has URLs and hashes for registry artifacts, but the repository has no
task-authorized wheelhouse or content-addressed offline dependency bundle.
The lock file alone is not evidence that a final no-network image can build
the flit backend and collect the tests.

The main optional integration is the render-module protocol: callers can
replace stdlib JSON with `simplejson` or any object implementing compatible
`dumps`/`loads` methods. The test suite uses both `simplejson` and a local
`mockjson`, so an adapter or public instruction must preserve this behavior or
explicitly narrow the contract under a new reviewed task version. Python
less-than-3.11 builds additionally need the backport package, and timezone
tests require an environment with the `America/Chicago` IANA zoneinfo data.

## Determinism and Boundary Risks

The three source baselines had identical collection and pass/fail results, but
the behavior contract is not wholly byte-deterministic without environment
controls:

- `tests/test_schema.py` calls `random.seed(1)`, but fixtures and tests also
  use `datetime.now()`, `uuid.uuid1()`, and `uuid.uuid4()`; assertions mostly
  check shape/type or round-trip properties rather than exact generated values.
- `fields.List` accepts sets and preserves their iteration order. The upstream
  tests check membership for a set, not a canonical order.
- `Schema._deserialize` computes unknown-field errors using
  `set(data) - fields` (`src/marshmallow/schema.py:695`). A direct probe with
  the same input under `PYTHONHASHSEED=1,2,3,4,5,12345` produced different
  insertion orders for the `ValidationError.messages` dictionary. A verifier
  comparing serialized error bytes must pin `PYTHONHASHSEED` or normalize
  mapping order.
- Field declaration order is intentionally preserved by normal schema output,
  but class registry state and nested-schema caches are process-local mutable
  state. A fresh process for every API call cannot represent a schema built in
  one call and used in another.

The current production Python candidate boundary is
`nl2repobench.verification.candidate_client.call`. It JSON-encodes one
`module`/`attribute` call with JSON-compatible `args` and `kwargs`, starts a
fresh UID-10001 child, imports the candidate only there, and requires a single
JSON-encoded result line. The runner also exposes module/console execution,
but marshmallow has no console entry point or task adapter. Candidate calls
have bounded request/output sizes and per-call process limits; these limits do
not add object handles or persistent sessions.

This generic contract cannot preserve the frozen assertions:

1. A JSON request cannot carry a `Field`/`Schema` instance, `datetime`,
   `Decimal`, UUID, enum, IP address, custom object, generator, or Python
   callback. A direct call returning a `Schema`, `Field`, or `ValidationError`
   also cannot be emitted because the child serializes the result with
   `json.dumps`.
2. `fields.Function`, decorator hooks, `validates`, `validates_schema`, and
   `Nested(lambda: ...)` require callable code and class definitions inside
   the same candidate process as the schema.
3. Class-registry registration, nested-schema caching, and `Context` scopes
   require state across operations. The generic client starts a new process
   for each `call`, so splitting construction, load/dump, and error inspection
   changes semantics.
4. The upstream tests inspect rich `ValidationError` fields and valid data,
   use custom render modules, patch modules, and compare domain object types;
   flattening these into independent JSON calls would be a new test contract.

Preserving this behavior requires an approved task-specific child adapter that
accepts declarative JSON scenarios, constructs all schemas/fields/callbacks
inside the untrusted child, and returns normalized observations to trusted
tests. No such adapter or approved narrowed assertion contract exists in this
task. Directly running the upstream tests in trusted pytest would violate the
separate-verifier policy.

## Publication Blockers and Reopen Requirements

The following required artifacts are intentionally absent from this task-local
directory:

- private test bundle and its digest/visibility metadata;
- allowlisted verifier command-plan artifact;
- hash-locked offline build/test wheelhouse, including flit_core, pytest,
  simplejson, and the conditional runtime dependencies for the selected
  Python version;
- immutable final environment/image lock and structured final-image
  collection record;
- Oracle solution bundle and Oracle/control results;
- reviewed candidate subprocess adapter for object, callback, and stateful
  schema behavior.

Keep this candidate **blocked**. Reopen only after the dependency closure and
final environment are provisioned, the private tests and command plan are
resolved through the approved artifact store, and either a task-specific
trusted adapter preserves the frozen assertions or the task is deliberately
rescoped to a new JSON-safe behavior contract. Then collect in the final
verifier environment, run three independent valid Oracle trials, and run the
empty/stub/forgery/offline controls before review or publication.

## Commands and Scope Controls

Commands run without Docker, Harbor, Oracle, negative controls, or shared
catalog/dataset edits:

```text
GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none --no-checkout \
  https://github.com/marshmallow-code/marshmallow /tmp/nl2repo-marshmallow-source
git -C /tmp/nl2repo-marshmallow-source checkout --detach \
  c7b559a1fa3aba57ca6dba0ab336841c5038a782
git -C /tmp/nl2repo-marshmallow-source show -s --format='%H%n%T%n%aI%n%cI%n%s' HEAD
git -C /tmp/nl2repo-marshmallow-source archive --format=tar HEAD | sha256sum
sha256sum /tmp/nl2repo-marshmallow-source/LICENSE \
  /tmp/nl2repo-marshmallow-source/pyproject.toml \
  /tmp/nl2repo-marshmallow-source/uv.lock
uv build --wheel --out-dir /tmp/marshmallow-dist
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  uv run --no-project --with pytest==9.1.1 --with simplejson==4.1.1 \
  python -m pytest --collect-only -q -p no:cacheprovider
for run in 1 2 3; do
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
    uv run --no-project --with pytest==9.1.1 --with simplejson==4.1.1 \
    python -m pytest -p no:cacheprovider -q --junitxml=/tmp/marshmallow-baseline-${run}.xml
done
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  uv run --no-project --with pytest==9.1.1 \
  python -m pytest --collect-only -q -p no:cacheprovider
```

The last command is the intentional missing-`simplejson` check and exits 4
with the conftest import error described above. Temporary source, wheel, JUnit,
and collection artifacts were kept outside the worktree. Only this
task-local `blocked.md` was added; no private bytes or secrets were written.
