# Build `simple-parsing`

## Project Description

Create a complete, installable Python package named `simple-parsing` from an
empty workspace.  The library adds typed dataclass support to Python's
standard `argparse`: a user defines configuration dataclasses, registers them
with a parser (or uses the convenience functions), and receives populated
instances rather than an unstructured `argparse.Namespace`.

The package also provides reusable dataclass field helpers, nested and
conflicting argument-group handling, subgroup/subparser selection, generated
help text, and serialization of configuration dataclasses.  It must preserve
the ordinary `argparse` behavior for arguments that are added directly to the
parser.

The public package is imported as `simple_parsing`.  Preserve the import paths
and re-exports described below; callers should not have to import private
implementation modules to use the documented functionality.

## Supports

- Python 3.9 and newer.
- An installable project with a root `pyproject.toml`, a package directory
  `simple_parsing/`, and package version `0.1.9`.
- Runtime dependencies declared by the upstream project: `docstring-parser`
  compatible with `~=0.15` and `typing-extensions>=4.5.0`.
- Optional `yaml` support through `pyyaml>=6.0.2` and optional `toml` support
  through `tomli>=2.2.1` and `tomli-w>=1.0.0`.  JSON, pickle, and standard
  library TOML reading on Python versions that provide `tomllib` must not
  require unrelated runtime packages.
- A package that can be installed with `pip install .` or an equivalent
  standards-compliant installer without network access after its declared
  dependencies have been provisioned.
- The package's top-level public names:

  `ArgumentGenerationMode`, `ArgumentParser`, `choice`, `config_for`,
  `ConflictResolution`, `DashVariant`, `field`, `flag`, `helpers`,
  `InconsistentArgumentError`, `list_field`, `main`, `mutable_field`,
  `NestedMode`, `parse_known_args`, `parse`, `ParsingError`, `Partial`,
  `replace`, `replace_subgroups`, `Serializable`, `SimpleHelpFormatter`,
  `subgroups`, `subparsers`, `utils`, and `wrappers`.

- The upstream package layout and import compatibility for the helper modules
  used by the public API, including `simple_parsing.helpers`,
  `simple_parsing.helpers.fields`, `simple_parsing.helpers.hparams`,
  `simple_parsing.helpers.serialization`, `simple_parsing.parsing`,
  `simple_parsing.docstring`, and `simple_parsing.wrappers.field_wrapper`.

## API Usage Guide

### Parser modes and enums

The following enums control how dataclass fields become command-line options:

- `ConflictResolution.NONE` rejects collisions, `EXPLICIT` uses the full
  destination path, `ALWAYS_MERGE` consumes one option with values for all
  repeated instances, and `AUTO` (the default) adds the shortest prefixes that
  distinguish colliding fields.
- `ArgumentGenerationMode.FLAT` removes nesting from option names when it is
  unambiguous, `NESTED` always reflects the dataclass path, and `BOTH` exposes
  both forms.
- `NestedMode.DEFAULT` keeps the complete destination path for nested options;
  `NestedMode.WITHOUT_ROOT` removes the first root component when the
  convenience API is parsing one root dataclass.
- `DashVariant.AUTO`/`UNDERSCORE` use underscore spellings,
  `UNDERSCORE_AND_DASH` accepts both underscore and dash spellings, and
  `DASH` prefers dash spellings.  The exact option aliases must refer to the
  same destination.

The enum members and their import paths must be available from the same places
as in the upstream package.  `ParsingError` is raised for parsing failures and
also behaves as a `SystemExit`-compatible command-line error.

### `ArgumentParser`

Expose `simple_parsing.ArgumentParser`, a subclass-compatible extension of
`argparse.ArgumentParser`, with this constructor contract:

```python
ArgumentParser(
    *args,
    parents=(),
    add_help=True,
    conflict_resolution=ConflictResolution.AUTO,
    add_option_string_dash_variants=DashVariant.AUTO,
    argument_generation_mode=ArgumentGenerationMode.FLAT,
    nested_mode=NestedMode.DEFAULT,
    formatter_class=SimpleHelpFormatter,
    add_config_path_arg=None,
    config_path=None,
    add_dest_to_option_strings=None,
    **kwargs,
)
```

It must retain normal `argparse` methods such as `add_argument`,
`parse_args`, `parse_intermixed_args`, `add_mutually_exclusive_group`,
`add_subparsers`, `set_defaults`, `format_help`, and `print_help`.

Implement:

```python
add_arguments(
    dataclass,
    dest,
    *,
    prefix="",
    default=None,
    dataclass_wrapper_class=DataclassWrapper,
)
```

`dataclass` may be a dataclass type or an instance.  Registering it creates an
argument group and stores the constructed dataclass under `dest` in the parsed
namespace.  An instance supplies defaults; passing a separate `default` at the
same time is invalid.  A non-dataclass input raises a clear `ValueError`.
Nested dataclasses are traversed recursively, inheritance is honored, and
fields with `init=False` or `simple_parsing.field(cmd=False)` do not become
command-line options.

When the same dataclass or field names are registered more than once, apply the
selected `ConflictResolution` policy without changing the resulting dataclass
shapes.  In merge mode a shared option may accept one value or one value per
registered instance; a single value is replicated to every instance, while an
inconsistent number of values raises `InconsistentArgumentError`.

### Convenience parsing functions

Expose:

```python
parse(
    config_class,
    config_path=None,
    args=None,
    default=None,
    dest="config",
    *,
    prefix="",
    add_help=True,
    nested_mode=NestedMode.WITHOUT_ROOT,
    conflict_resolution=ConflictResolution.AUTO,
    add_option_string_dash_variants=DashVariant.AUTO,
    argument_generation_mode=ArgumentGenerationMode.FLAT,
    formatter_class=SimpleHelpFormatter,
    add_config_path_arg=None,
    **kwargs,
)
```

`args` accepts a shell-like string or a sequence of argument strings.  Return
the dataclass instance stored under `dest`; command-line values override
provided and file-derived defaults.  `parse_known_args` has the same parsing
options plus `attempt_to_reorder=False` and returns
`(dataclass_instance, unknown_args)` rather than rejecting leftover arguments.
The convenience API must reject using the same name for `dest` and
`add_config_path_arg`.

### Dataclass field helpers

The helpers are importable from `simple_parsing` and/or
`simple_parsing.helpers.fields` as in the upstream package.

```python
field(
    default=MISSING,
    alias=None,
    cmd=True,
    positional=False,
    *,
    to_dict=True,
    encoding_fn=None,
    decoding_fn=None,
    default_factory=MISSING,
    init=True,
    repr=True,
    hash=None,
    compare=True,
    metadata=None,
    **custom_argparse_args,
)
choice(*choices, default=MISSING, **kwargs)
list_field(*default_items, **kwargs)
dict_field(default_items=(), **kwargs)
set_field(*default_items, **kwargs)
mutable_field(fn, init=True, repr=True, hash=None, compare=True, metadata=None,
              *fn_args, **fn_kwargs)
```

- `field` extends `dataclasses.field`.  `alias` adds option strings, `cmd`
  controls whether an option is generated, `positional` requests a positional
  argument, and extra keyword arguments are passed through to `argparse`.
  `to_dict`, `encoding_fn`, and `decoding_fn` control serialization when the
  containing dataclass is serializable.
- `choice` accepts individual values, an enum type, or a mapping from option
  names to stored values.  The selected mapping value, rather than its key, is
  placed in the dataclass.  A default outside the choices is an error.
- `list_field`, `dict_field`, and `set_field` create independent mutable
  defaults for each dataclass instance.  `mutable_field` creates a
  `default_factory` from a callable and its arguments.

Boolean helpers are:

```python
flag(
    default=MISSING,
    *,
    default_factory=MISSING,
    negative_prefix="--no",
    negative_option=None,
    nargs=None,
    type=str2bool,
    action=BooleanOptionalAction,
    **kwargs,
)
flags(default_factory=MISSING, nargs="*", type=str2bool, **kwargs)
```

A `flag` creates positive and negative forms and is required when it has no
default, otherwise optional.  `negative_option` overrides the generated
negative spelling.  `flags` parses a variable number of boolean values.
Accepted textual boolean values include the common true/false, yes/no, and
t/f forms; invalid values fail through the normal `argparse` error path.

`subgroups(mapping, *args, default=MISSING, default_factory=MISSING,
**kwargs)` creates a field selecting one of several dataclass types, instances,
or supported partial callables.  The selected key is an argument choice and
only the selected subgroup's values are used to construct the result.  The
default must be a
valid key or matching dataclass value; `default` and `default_factory` cannot
both be supplied.  Nested and repeated subgroups are supported.  Anonymous
lambda subgroup factories are not required to be supported and must fail
clearly rather than being invoked merely for type inspection.

`subparsers(subcommands, default=MISSING, **kwargs)` creates an argparse
subparser choice from a mapping of command names to dataclass types.  The
selected command is represented by the corresponding dataclass instance.

### Nested dataclass and argparse semantics

For a dataclass such as `Config(inner: Inner)`, recursively construct `Inner`
and preserve its defaults.  In flat mode, an unambiguous field may be exposed
as `--count`; nested mode exposes the complete path such as
`--config.inner.count`; both mode accepts both forms.  The
`WITHOUT_ROOT` setting removes only the first root component, not the inner
components.  Explicit `prefix` values and automatically selected conflict
prefixes must compose deterministically.

Infer argument conversion from annotations and defaults for at least:

- required and optional scalar values;
- `bool`, `list`, `set`, homogeneous and heterogeneous tuples;
- `Enum`, `Literal`, and supported `Union` values;
- positional fields, aliases, repeated dataclass instances, and custom
  `argparse` actions;
- `default_factory`, `InitVar`, postponed/forward annotations, and inherited
  dataclass fields.

Do not mutate a caller's dataclass instance merely by registering it.  Preserve
dataclass field declaration order in generated groups and help text.  Help text
uses field comments, field docstrings, and class docstrings where available,
and includes defaults through `SimpleHelpFormatter` while retaining
`argparse`'s error behavior.

### Configuration files

`config_path` and `add_config_path_arg` load defaults from supported file
extensions and merge them with explicit defaults.  JSON and pickle use the
standard library.  YAML requires PyYAML; TOML writing requires `tomli-w`, and
TOML reading uses `tomllib` where available or `tomli` otherwise.  Explicit
command-line values take precedence over file values.  A list of config paths
is applied in order, with later values overriding earlier defaults.

### Serialization API

Expose the serialization helpers from `simple_parsing.helpers.serialization`:

```python
to_dict(dc, dict_factory=dict, recurse=True, save_dc_types=False)
from_dict(cls, d, drop_extra_fields=None)
load(cls, path, drop_extra_fields=None, load_fn=None)
save(obj, path, format=None, save_dc_types=False, **kwargs)
dumps(dc, dump_fn=json.dumps)
loads(cls, s, drop_extra_fields=None, load_fn=json.loads)
```

Also expose the JSON/YAML convenience variants (`load_json`, `load_yaml`,
`save_json`, `save_yaml`, `dumps_json`, `dumps_yaml`, `loads_json`, and
`loads_yaml`) and the classes `Serializable`, `SerializableMixin`,
`FrozenSerializable`, `YamlSerializable`, and `SimpleJsonEncoder` through the
same helper-module paths as the upstream package.  Keep
`SimpleSerializable` importable from
`simple_parsing.helpers.serialization.serializable`.  `Serializable` remains
available through the historical `simple_parsing.helpers` and top-level
re-exports.

Compatibility exports `dump`, `dump_json`, `dump_yaml`, and
`JsonSerializable` must remain importable from their upstream helper-module
paths. They are compatibility seams, not permission to add arbitrary keyword
arguments to `dumps`.

A serializable dataclass must round-trip nested dataclasses, lists, tuples,
sets, enums, paths, optional values, and registered custom encoders/decoders.
The `.json`, `.yaml`/`.yml`, `.pkl`, `.npy`, `.pth`, and `.toml` extensions map
to the corresponding format.  Unknown extensions raise a clear
`RuntimeError`; unavailable optional format packages raise an import error at
use time rather than breaking basic JSON use.  `drop_extra_fields` controls
whether unknown mapping keys are discarded or used for registered subclass
decoding.

### Replacement, partials, and hyperparameters

- `replace(obj, changes_dict=None, **changes)` returns a dataclass value with
  recursive changes while leaving the original value unchanged.
- `replace_subgroups(obj, selections=None)` switches subgroup selections and
  reconstructs the selected dataclass values.
- `config_for(cls_or_callable, ignore_args=(), frozen=True, **defaults)` and
  `Partial` support reusable partially configured dataclass factories.
- `simple_parsing.helpers.hparams` exposes `hparam`, `uniform`,
  `log_uniform`/`loguniform`, `categorical`, `HyperParameters`, `Point`,
  `LogUniformPrior`, and `UniformPrior`.  The related
  `simple_parsing.helpers.hparams.priors` module exposes `Prior`,
  `NormalPrior`, and `CategoricalPrior` as well.  Hyperparameter fields
  preserve their declared defaults, bounds, categorical values, optional
  shapes, and seeded sampling behavior.

### Docstring and utility compatibility

Keep the documented helper imports working, including
`simple_parsing.docstring.get_attribute_docstring`,
`AttributeDocString`, `simple_parsing.utils.str2bool`, and the wrapper enums.
Utility functions may remain implementation details unless they are re-exported
or imported by the documented helper modules, but do not remove compatibility
aliases used by the package.

## Implementation Notes

- Keep the package importable on Python 3.9; use `typing-extensions` for
  typing features unavailable in the minimum interpreter.
- Preserve normal `argparse` option parsing, error messages, and namespace
  conventions.  The generated dataclass object is stored at the requested
  destination while unrelated manually added arguments remain on the same
  namespace.
- Keep all behavior local and deterministic.  Do not require network access,
  hardware, environment-specific paths, or a service account.  Preserve
  insertion order for dataclass fields, choices, mappings, and generated
  serialization output.
- Avoid importing optional YAML, TOML, NumPy, or PyTorch functionality until a
  caller requests the corresponding feature.  Basic import, argparse parsing,
  JSON serialization, and core dataclass helpers must work without those
  optional packages.
- Include packaging metadata, the MIT license text, and a useful README with
  installation and ordinary examples.  Do not copy implementation source or
  upstream test assertions into the public specification.
