# Project Description

Create an installable Python project named `keyring`. It provides a process-wide facade for storing and retrieving passwords through selectable backend objects. The project includes credential value objects, backend discovery and chaining, configuration files and environment selection, a command-line interface, plugin entry points, and a `urllib` password-manager adapter.

The benchmark environment is headless and offline. It has no usable desktop credential service, D-Bus session, KWallet, macOS Keychain, or Windows Credential Manager. Implement the backend abstraction and platform modules, but do not replace an unavailable system keyring with a hidden process-global password dictionary. Deterministic tests use external in-memory backend subclasses through the public backend interface.

# Supports

- Support Python 3.10 and newer. Verification uses CPython 3.12.
- Provide an installable distribution named `keyring`, with package version `25.7.1.dev8+g7603e7cad`.
- A flat `keyring/` package or a `src/keyring/` layout is acceptable. `python -m pip install . --no-deps --no-build-isolation` must succeed with the preinstalled build closure.
- Provide the console script `keyring = keyring.cli:main` and make `python -m keyring` invoke the same CLI.
- Include `keyring/py.typed` as package data. Keep `keyring/backend_complete.bash` and `keyring/backend_complete.zsh` in the source tree for completion development; the frozen distribution does not install those two shell-source files.
- Include an MIT `LICENSE` file in the project root. The frozen source uses `coherent.licensed`; a local license file prevents that build hook from attempting a network lookup during offline candidate installation.
- Runtime dependencies already installed in the image are `SecretStorage`, `jeepney`, `jaraco.classes`, `jaraco.context`, and `jaraco.functools`. Do not download dependencies at runtime.
- Keep platform integrations import-safe on unsupported platforms. The modules `keyring.backends.SecretService`, `keyring.backends.kwallet`, `keyring.backends.libsecret`, `keyring.backends.Windows`, and `keyring.backends.macOS` must exist. Their backend priority may raise `RuntimeError` when the required platform or service is unavailable.
- Declare the built-in `keyring.backends` entry points named `Windows`, `macOS`, `libsecret`, `SecretService`, `KWallet`, and `chainer`, plus the `devpi_client` entry point named `keyring`.

`keyring.__all__` must contain, in this order:

```python
(
    "set_keyring",
    "get_keyring",
    "set_password",
    "get_password",
    "delete_password",
    "get_credential",
)
```

# API Usage Guide

## Process-wide facade

The following functions are re-exported by `keyring` from `keyring.core`:

### `set_keyring(keyring: KeyringBackend) -> None`

Set the process-wide backend instance. Reject any object that is not an instance of `KeyringBackend` with `TypeError("The keyring must be an instance of KeyringBackend")`.

### `get_keyring() -> KeyringBackend`

Return the current backend. If none has been selected, initialize backend discovery once for the current process and return the selected backend.

### `set_password(service_name: str, username: str, password: str) -> None`

Delegate to the current backend's `set_password` method without changing the values.

### `get_password(service_name: str, username: str) -> str | None`

Delegate to the current backend. Return the stored password or `None` when the backend has no matching entry.

### `delete_password(service_name: str, username: str) -> None`

Delegate deletion to the current backend. Backend-specific deletion errors propagate.

### `get_credential(service_name: str, username: str | None) -> Credential | None`

Delegate to the current backend. Callers must use both fields from the returned credential because a backend may resolve a username when the input is `None`.

## Backend base contract

Import these APIs from `keyring.backend`.

### `class KeyringBackend`

Every concrete backend supplies a class-level numeric `priority`, implements `get_password(service, username)` and `set_password(service, username, password)`, and may override deletion and credential lookup.

- `priority` is readable on both the class and instance. Higher values win discovery. Access may raise `RuntimeError` for an unusable backend.
- `viable` is a class-level boolean view of whether reading `priority` succeeds.
- `get_viable_backends()` iterates registered, non-abstract backend classes whose priorities are readable.
- `name` is a printable class-level name derived from the final module component and class name.
- `str(instance)` has the form `<fully.qualified.Class> (priority: <number>)`, using general numeric formatting.
- Concrete subclasses register automatically when their class is created.
- Calls to concrete `set_password` implementations validate the username first. An empty username is still accepted but emits `DeprecationWarning`.
- The inherited `delete_password` raises `PasswordDeleteError("reason")`.
- The inherited `get_credential(service, username)` returns `None` for `username is None`; otherwise it calls `get_password` and wraps a non-`None` password in `SimpleCredential`.
- `set_properties_from_env()` maps every `KEYRING_PROPERTY_<NAME>=value` variable to a lowercase instance attribute. For example, `KEYRING_PROPERTY_FOO_BAR` sets `foo_bar`.
- `with_properties(**kwargs) -> KeyringBackend` returns a shallow copy with the supplied attributes and does not mutate the original.

### `get_all_keyring() -> list[KeyringBackend]`

Load `keyring.backends` entry points, then instantiate viable backend classes that accept a no-argument constructor. A plugin entry point is loaded; if the loaded object is callable, call it once to let it register a backend. Log and ignore plugin initialization failures so one bad plugin does not prevent discovery.

### `class Crypter` and `class NullCrypter(Crypter)`

`Crypter` defines abstract `encrypt(value)` and `decrypt(value)` methods. `NullCrypter` returns the exact input object unchanged from both methods.

### `class SchemeSelectable`

`_query(service: str, username: str | None = None, **base) -> dict[str, str]` maps service and username keys according to `scheme` and merges `base` fields. The default scheme uses `service` and `username`; `scheme = "KeePassXC"` uses `Title` and `UserName`. Omit the username key when the argument is `None`.

## Built-in deterministic backends

### `keyring.backends.null.Keyring`

Its priority is `-1`. `get_password`, `set_password`, and `delete_password` all return `None` and do not persist values.

### `keyring.backends.fail.Keyring`

Its priority is `0`. Password get, set, and delete operations raise `NoKeyringError`. The message says that no recommended backend was available and directs the caller to install a recommended backend or `keyrings.alt`.

### `keyring.backends.chainer.ChainerBackend`

`backends` contains non-chainer backends that pass the active discovery limit and have priority greater than zero, sorted by descending priority. Its priority is `10` when at least two backends can be chained; otherwise it is one less than the fail backend priority.

- `get_password` returns the first non-`None` result.
- `get_credential` returns the first non-`None` credential.
- `set_password` and `delete_password` try backends in order, stopping at the first normal return. They skip a backend only when that operation raises `NotImplementedError`.

## Backend selection and configuration

Import these functions from `keyring.core`.

### `recommended(backend) -> bool`

Return whether `backend.priority >= 1`.

### `init_backend(limit: Callable[[KeyringBackend], bool] | None = None) -> None`

Select and install a backend. Selection precedence is: `PYTHON_KEYRING_BACKEND`, then the configuration file, then the highest-priority discovered backend that passes `limit`. If nothing qualifies, use `keyring.backends.fail.Keyring`.

### `load_keyring(keyring_name: str) -> KeyringBackend`

Load a fully qualified backend class, read its priority to prove viability, instantiate it without arguments, and return it.

### `load_env() -> KeyringBackend | None`

Load the fully qualified class named by `PYTHON_KEYRING_BACKEND`, or return `None` when the variable is absent. Import, attribute, and viability errors propagate.

### `load_config() -> KeyringBackend | None`

Read UTF-8 INI configuration from the platform config root's `keyringrc.cfg`. Return `None` for a missing file, an empty file, or a file with no `[backend]` section. The `[backend]` section may contain:

```ini
[backend]
default-keyring=keyring.backends.null.Keyring
keyring-path=~/optional/backend/path
```

Expand and prepend `keyring-path` to `sys.path`, then load `default-keyring`. A missing option logs a warning and returns `None`.

### `disable() -> None`

Create the platform configuration directory and write `keyringrc.cfg` containing exactly a `[backend]` section whose `default-keyring` is `keyring.backends.null.Keyring`. Refuse to overwrite an existing file by raising `RuntimeError` whose message starts with `Refusing to overwrite`.

## Credential objects

Import these APIs from `keyring.credentials`.

### `class Credential`

An abstract base class with abstract read-only `username: str` and `password: str` properties. `_vars()` returns `{"username": username, "password": password}`.

### `SimpleCredential(username: str, password: str)`

Expose the two constructor values through read-only properties and the inherited `_vars()` mapping.

### `AnonymousCredential(password: str)`

Expose `password`. Accessing `username` raises `ValueError("Anonymous credential has no username")`. `_vars()` returns only `{"password": password}`.

### `EnvironCredential(user_env_var: str, pwd_env_var: str)`

Read values lazily from the named environment variables. Missing or empty values raise `ValueError("Missing environment variable:<NAME>")`. Instances compare equal when their two variable-name attributes are equal.

## Errors and compatibility context

`KeyringError` is the base for `PasswordSetError`, `PasswordDeleteError`, `InitError`, `KeyringLocked`, and `NoKeyringError`. `NoKeyringError` is also a `RuntimeError`.

`ExceptionRaisedContext(ExpectedException=Exception)` is a deprecated exception-suppressing context manager. Construction emits `DeprecationWarning`. The entered `ExceptionInfo` is truthy when an exception occurred and exposes `type` and `value`; only matching exception types are suppressed. It must not retain the traceback object.

## Descriptor compatibility

Import these APIs from `keyring.compat.properties`.

### `NonDataProperty(fget)`

Act like a property that implements only `__get__`. Reading through an instance calls `fget`; assigning the same name on an instance overrides the descriptor. Reading through the class returns the descriptor itself.

### `classproperty`

Provide class-level property access and an optional `.setter`. With `metaclass=classproperty.Meta`, assignment through either the class or an instance invokes the setter and stores no instance attribute. Assigning to a classproperty with no setter raises `AttributeError("can't set attribute")`. Plain functions are treated as class methods; wrapped `classmethod` and `staticmethod` values are also supported.

## Command-line interface

`keyring.cli.main(argv=None)` accepts these global options:

- `-p/--keyring-path PATH`
- `-b/--keyring-backend FULLY.QUALIFIED.CLASS`
- `--list-backends`
- `--disable`
- `--mode password|creds` (default `password`)
- `--output plain|json` (default `plain`)
- optional shell completion via `--print-completion bash|zsh|tcsh`

Operations are `get`, `set`, `del`, and `diagnose`.

- `get SERVICE USERNAME` in password mode prints only the password. Missing data exits with status 1.
- `--mode creds get SERVICE [USERNAME]` uses `get_credential` and prints username then password in plain mode. JSON mode prints the credential's `_vars()` mapping.
- `set SERVICE USERNAME` reads a password from all of standard input when stdin is not a TTY; remove exactly one trailing newline. On a TTY, use `getpass.getpass`.
- `del SERVICE USERNAME` delegates deletion.
- `diagnose` prints the config path and data root.
- Missing required service or username arguments produce an argparse error with status 2.
- When the optional `shtab` package is absent, `--print-completion` prints `Install keyring[completion] for completion support.` to stderr and exits with status 1.

`CommandLineTool.strip_last_newline(value: str) -> str` removes one final `\n` only. An empty string and strings without a final newline are unchanged.

## `urllib` password manager

`keyring.http.PasswordMgr` provides:

- `get_username(realm, authuri) -> str`: return `getpass.getuser()`.
- `add_password(realm, authuri, password) -> None`: store under `(realm, current_user)`.
- `find_user_password(realm, authuri) -> tuple[str, str]`: return the stored password; when absent, prompt with context containing `<user>@<realm>` and the URI, store the entered password, then return it.
- `clear_password(realm, authuri) -> None`: delete the current user's password for the realm.

# Implementation Notes

- Keep current-backend state in `keyring.core`; top-level facade functions must all observe the same selected object.
- Backend registration and class-level properties are observable. A backend's `priority` must not become an ordinary per-instance property.
- Do not initialize or contact a platform credential service during `import keyring`.
- Keep optional platform imports inside backend modules or viability checks so unsupported hosts can still import the top-level package and CLI.
- Build metadata must include the console script, backend plugin entry points, completion resources, and typing marker.
- The verifier supplies deterministic backend subclasses. It does not ask the library to persist fixture passwords globally.
- Candidate calls execute in isolated child processes with JSON-serializable responses. Platform-native objects and callbacks are not passed across this boundary.
- Live Secret Service, KWallet, libsecret, Windows Credential Manager, macOS Keychain, interactive TTY behavior, and multiprocessing discovery are outside this task version's frozen denominator.
