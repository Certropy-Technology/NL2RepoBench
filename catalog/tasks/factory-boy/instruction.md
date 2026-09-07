# Project Description

Build the pinned `factory_boy` Python distribution from an empty `workspace/`.
Its import package `factory` provides declarative factories, lazy declarations,
strategies, fuzzy values, random-state controls, and helper constructors.

# Natural Language Instruction

Create the installable distribution and every core symbol listed in the local
API inventory and guide below. Preserve declaration order, overrides, nested
factories, traits, post-generation hooks, random reproducibility, and errors.
ORM integrations are outside this contract.

# Supports or Environment Configuration

- Use CPython 3.12 on Linux and the exact package/build closure in `task.toml`.
- Distribution name is `factory_boy`; import package is `factory`, including
  its metadata and typing marker.
- Agent, candidate, verifier, Oracle, and controls run with no network access.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── factory/
    ├── __init__.py
    ├── base.py
    ├── declarations.py
    ├── enums.py
    ├── errors.py
    ├── faker.py
    ├── fuzzy.py
    ├── helpers.py
    ├── random.py
    ├── utils.py
    └── py.typed
```

# API Usage Guide

The existing guide and local inventories are authoritative for factory classes,
declarations, helpers, fuzzy values, random APIs, and utility signatures.

# Implementation Notes

Keep generation deterministic under a fixed random state. Do not add ORM or
database integrations, or import-time network behavior.

# Examples

```python
import factory
class UserFactory(factory.Factory):
    class Meta:
        model = dict
    name = factory.Sequence(lambda n: f"user-{n}")
```

```python
factory.build_batch(UserFactory, 2)
```

# Error Handling and Boundary Conditions

```python
factory.reseed_random(17)
```

```python
factory.use_strategy(factory.STUB_STRATEGY)
```

# Build `factory-boy`

## Project Description

Implement an installable Python distribution named `factory_boy` whose import
package is `factory`. It is a declarative test-fixture factory library. The
task targets the deterministic core API of factory_boy 3.3.4.dev0 at the
pinned upstream revision.

The contract covers the dependency-free core, Faker and fuzzy declarations,
random-state helpers, and utility helpers. ORM integrations are outside this
task because they require external frameworks and databases.

## Supports

- CPython 3.12 or newer on Linux.
- A setuptools build producing the `factory_boy` distribution and importable
  `factory` package, including `factory/py.typed`.
- Faker as the only runtime third-party dependency. The verifier supplies a
  hash-locked Faker and build/test closure; evaluation has no network access.
- Deterministic local execution without network, database, subprocess,
  filesystem fixtures, or wall-clock requirements.

## API Usage Guide

`factory.base.Factory` is the main class. A subclass normally declares
`class Meta: model = Model`. A subclass without a model is abstract and
calling `build()` or `create()` raises `factory.errors.FactoryError`.
`Factory.build(**kwargs)` constructs without persistence; `Factory.create()`
uses the create hook; `Factory.stub()` returns an attribute object.
`build_batch(size, **kwargs)` and `create_batch` preserve order. `DictFactory`
and `ListFactory` provide dictionary/list models.

The package root re-exports `Factory`, `BaseFactory`, `StubFactory`,
`DictFactory`, `ListFactory`, `FactoryError`, `Faker`, declaration classes,
helper functions, strategy constants, and `__version__`.

### Declarations

Import declarations from `factory` or `factory.declarations`:

- `LazyFunction(function)` calls a zero-argument callable for each build.
- `LazyAttribute(function)` calls `function(resolver)` after earlier fields.
- `Sequence(function)` calls `function(counter)` with the factory sequence
  number. `reset_sequence(value=0, force=False)` resets the counter.
- `LazyAttributeSequence(function)` receives the resolver and sequence number.
- `SelfAttribute(name, default=...)` reads a resolved attribute; leading dots
  select a parent container.
- `Iterator(iterable, cycle=True, getter=None)` yields values in order and
  cycles by default. `reset()` restarts it; a non-cycling iterator raises
  `StopIteration` when exhausted.
- `SubFactory(factory_class, **defaults)` builds a nested object. Nested
  overrides use `child__attribute`.
- `Dict(mapping)` and `List(values)` resolve nested declarations and accept
  nested overrides.
- `Transformer(default, transform=callable)` transforms its default;
  `Transformer.Force(value)` bypasses the transform for one call.
- `Maybe(decider, yes_declaration, no_declaration)` selects a declaration.
  `Trait(**declarations)` defines a named parameter set.
- `PostGeneration(function)` calls `function(instance, create, extracted,
  **kwargs)` after a build. `PostGenerationMethodCall(name, *args, **kwargs)`
  calls a method on the generated object.

### Helpers, Faker, fuzzy values, and utilities

`factory.helpers` provides `build`, `build_batch`, `create`, `create_batch`,
`stub`, `stub_batch`, `generate`, `generate_batch`, `simple_generate`,
`simple_generate_batch`, decorator helpers, `make_factory`, and the `debug`
context manager. Helpers use the corresponding factory strategy and preserve
batch order.

`factory.Faker(provider, locale=None, **kwargs)` delegates to Faker during a
build. `factory.fuzzy` provides `FuzzyText`, `FuzzyChoice`, `FuzzyInteger`,
`FuzzyDecimal`, `FuzzyFloat`, `FuzzyDate`, `FuzzyNaiveDateTime`, and
`FuzzyDateTime`; each exposes `fuzz()` and respects its bounds.
`factory.random.reseed_random(seed)` seeds factory and Faker randomness, while
`get_random_state()` and `set_random_state(state)` save and restore it.
`factory.utils.import_object(module_name, attribute_name)` imports a named
attribute and raises `AttributeError` for a missing one.

## Implementation Notes

Keep the public import paths and class relationships compatible with the
package. Declaration resolution is ordered and lazy; overrides and nested
paths must remain available to the build step. Builds must not mutate
declarations shared by a factory class. Optional ORM modules may remain
available only when their external framework is installed; importing the core
package must succeed without those frameworks.
