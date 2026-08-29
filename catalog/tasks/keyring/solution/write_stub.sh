#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace/keyring/backends /workspace/keyring/compat
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "keyring"
version = "25.7.1.dev8+g7603e7cad"

[project.scripts]
keyring = "keyring.cli:main"
EOF
cat > /workspace/keyring/__init__.py <<'PY'
__all__ = (
    "set_keyring", "get_keyring", "set_password", "get_password",
    "delete_password", "get_credential",
)

def set_keyring(*args, **kwargs): raise NotImplementedError
def get_keyring(*args, **kwargs): raise NotImplementedError
def set_password(*args, **kwargs): raise NotImplementedError
def get_password(*args, **kwargs): raise NotImplementedError
def delete_password(*args, **kwargs): raise NotImplementedError
def get_credential(*args, **kwargs): raise NotImplementedError
PY
cat > /workspace/keyring/backend.py <<'PY'
from importlib import metadata

class KeyringBackend:
    _classes = set()
    viable = True
    priority = 0
    def set_properties_from_env(self): pass

class Crypter: pass

class NullCrypter:
    def encrypt(self, value): return value
    def decrypt(self, value): return value

class SchemeSelectable: pass

def get_all_keyring(): return []
def _load_plugins(): return None
PY
cat > /workspace/keyring/core.py <<'PY'
def set_keyring(*args, **kwargs): raise NotImplementedError
def get_keyring(*args, **kwargs): raise NotImplementedError
def set_password(*args, **kwargs): raise NotImplementedError
def get_password(*args, **kwargs): raise NotImplementedError
def delete_password(*args, **kwargs): raise NotImplementedError
def get_credential(*args, **kwargs): raise NotImplementedError
def load_env(): return None
def load_config(): return None
def disable(): raise NotImplementedError
def recommended(item): return False
PY
cat > /workspace/keyring/credentials.py <<'PY'
class Credential: pass
class SimpleCredential: pass
class AnonymousCredential: pass
class EnvironCredential: pass
PY
cat > /workspace/keyring/errors.py <<'PY'
class KeyringError(Exception): pass
class PasswordSetError(KeyringError): pass
class PasswordDeleteError(KeyringError): pass
class InitError(KeyringError): pass
class KeyringLocked(KeyringError): pass
class NoKeyringError(KeyringError, RuntimeError): pass
class ExceptionRaisedContext: pass
class ExceptionInfo: pass
PY
cat > /workspace/keyring/cli.py <<'PY'
class CommandLineTool: pass
def main(argv=None): raise NotImplementedError
PY
cat > /workspace/keyring/http.py <<'PY'
class PasswordMgr: pass
PY
cat > /workspace/keyring/backends/__init__.py <<'PY'
PY
cat > /workspace/keyring/backends/null.py <<'PY'
class Keyring:
    priority = -1
    def get_password(self, *args, **kwargs): return None
    set_password = delete_password = get_password
PY
cat > /workspace/keyring/backends/fail.py <<'PY'
class Keyring:
    priority = 0
PY
cat > /workspace/keyring/backends/chainer.py <<'PY'
class ChainerBackend: pass
PY
cat > /workspace/keyring/compat/__init__.py <<'PY'
PY
cat > /workspace/keyring/compat/properties.py <<'PY'
class NonDataProperty: pass
class classproperty: pass
PY
