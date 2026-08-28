# Build `editables`

Create a complete, installable Python project named `editables` from an empty
workspace. It is a small pure-Python packaging helper that emits the files and
import machinery used by editable wheels. The project must work without a
preinstalled copy of `editables` and without runtime network access.

## Project Description

The library models an editable project rooted at a local directory. A project
can expose a source directory through a `.pth` file, map top-level packages or
modules either with an import hook or with self-replacing modules, and expose a
subpackage by writing a package `__init__.py` that points at a local directory.
The package also provides the import finder used by the import-hook strategy.

The distribution is named `editables`, the import package is `editables`, and
the frozen reference revision reports version `0.6`.

## Supports

- Support CPython 3.12 on Linux using only the Python standard library at
  runtime. The public behavior is limited to filesystem paths, strings,
  importlib objects, and in-process state.
- Provide an installable package layout containing `editables/__init__.py`,
  `editables/redirector.py`, and a `editables/py.typed` marker.
- Declare no third-party runtime dependencies. The build backend may be
  declared in `pyproject.toml`, but it must be usable by the offline agent
  image and must not be fetched during evaluation.
- Normal library operations must not contact a network, invoke a subprocess,
  or require a service. Temporary files and ordinary local directories are
  valid caller-provided inputs.
- Preserve deterministic insertion order for generated files, mappings, and
  path entries. Do not expose the reference source or tests through the
  generated project.

## API Usage Guide

### Root package

`editables.__version__` is the string `"0.6"`. The package exports
`EditableProject`, `EditableException`, `is_valid`, and `normalize`; preserving
the two documented root exports is required and the exception class must be
usable with `except editables.EditableException`.

### Validation and normalization

```python
editables.is_valid(name: str) -> bool
editables.normalize(name: str) -> str
```

`is_valid` accepts a PEP 426-style project name made from letters, digits,
periods, underscores, and hyphens, with an alphanumeric first and last
character. `normalize` lowercases a name and replaces every run of `-`, `_`, or
`.` with one underscore. A valid name such as `my-project` becomes
`my_project`; invalid names are rejected by `EditableProject`.

### `EditableProject`

```python
EditableProject(project_name: str, project_dir: str | os.PathLike)
```

The constructor validates the project name, stores `project_dir` as a
`pathlib.Path`, defaults `map_method` to `"import_hook"`, and derives both
`pth_name` and `bootstrap_name` as `_editable_impl_<normalized>.pth` and
`_editable_impl_<normalized>`. It starts with empty `redirections`,
`path_entries`, and `subpackages` collections.

The `map_method` property accepts only `"import_hook"` and `"self_replace"`.
Any other assignment raises `ValueError`; `use_hook()` returns whether the
current method is `"import_hook"`.

```python
project.make_absolute(path: str | os.PathLike) -> pathlib.Path
```

Resolve a path relative to `project_dir`. The returned path is absolute and
normalized according to `Path.resolve()`.

```python
project.map(name: str, target: str | os.PathLike) -> None
```

Map a top-level module or package. A directory target maps to its
`__init__.py`; a file target maps directly. Missing or non-file targets raise
`EditableException`. With `map_method == "import_hook"`, dotted names are
rejected because the finder only handles top-level imports. Successful calls
store an absolute target in insertion order.

```python
project.add_to_path(dirname: str | os.PathLike) -> None
project.add_to_subpackage(package: str, dirname: str | os.PathLike) -> None
```

Append a resolved path entry, or associate a dotted package name with a
resolved directory. Repeated subpackage names replace the previous location
without changing the public return contract.

```python
project.files() -> Iterable[tuple[str, str]]
project.dependencies() -> list[str]
project.pth_file() -> str
project.package_redirection(package: str, location: pathlib.Path) -> tuple[str, str]
project.self_replacer(target: str) -> str
project.bootstrap_file() -> str
```

`files()` yields generated wheel members in this order: the `.pth` file when
its content is nonempty, each subpackage redirection, then either one
`_editable_impl_<normalized>.py` bootstrap file for import hooks or one
self-replacing `<name>.py` file per mapped name for the self-replace strategy.
The `.pth` content has an import line for the bootstrap before path entries.
`dependencies()` returns `['editables']` only when there are mapped names and
the import-hook strategy is active; otherwise it returns an empty list.

`package_redirection` returns the package path ending in `__init__.py` and
content assigning `__path__` to a one-element list containing the string form
of the resolved location. `self_replacer` returns a module body that loads the
target file into the requested module name through
`importlib.util.spec_from_file_location`. `bootstrap_file` installs the
redirecting finder and registers each mapping in insertion order.

### `RedirectingFinder`

`editables.redirector.RedirectingFinder` is a class implementing the
`importlib.abc.MetaPathFinder` protocol. Its class-level `_redirections`
mapping is updated by:

```python
RedirectingFinder.map_module(name: str, path: str) -> None
RedirectingFinder.install() -> None
RedirectingFinder.find_spec(fullname: str, path=None, target=None) -> ModuleSpec | None
RedirectingFinder.invalidate_caches() -> None
```

`install()` adds the finder to `sys.meta_path` at most once. `find_spec` only
handles an unmapped top-level name when `path is None`; dotted names, imports
with a non-`None` package path, and unmapped names return `None`. A mapped name
returns a file-based module spec for its target. `invalidate_caches()` is a
valid no-op compatible with `importlib.invalidate_caches()`.

## Implementation Notes

- Keep the package pure Python and keep the candidate boundary installable
  from its repository root with `pip install --no-deps .`.
- Generated paths must use absolute resolved paths, and generated text must be
  stable for fixed inputs. Preserve mapping and path insertion order.
- Import-hook and self-replace are distinct behaviors. Do not collapse them
  into one implementation if that changes generated filenames, dependencies,
  or import semantics.
- The verifier exercises the public contract in a child process and owns the
  collection and reward reports. Do not write to `/tests`, `/logs`, or trusted
  verifier paths from the candidate package.
