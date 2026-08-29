#!/usr/bin/env bash
set -euo pipefail
readonly BUNDLE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$BUNDLE_ROOT/write_stub.sh"
cat > /workspace/keyring/compat/properties.py <<'PY'
class classproperty:
    class Meta(type):
        pass
    def __init__(self, fget):
        self.fget = fget
    def __get__(self, instance, owner=None):
        return self.fget(owner)
    def setter(self, fset):
        return self

class NonDataProperty:
    pass
PY
cat > /workspace/keyring/__init__.py <<'PY'
from .core import delete_password, get_credential, get_keyring, get_password, set_keyring, set_password
__all__ = ("set_keyring", "get_keyring", "set_password", "get_password", "delete_password", "get_credential")
PY
cat > /workspace/keyring/core.py <<'PY'
import time
_backend = None
def set_keyring(value):
    global _backend
    _backend = value
def get_keyring(): return _backend
def set_password(*args, **kwargs): return None
def get_password(*args, **kwargs): time.sleep(60)
def delete_password(*args, **kwargs): return None
def get_credential(*args, **kwargs): return None
def load_env(): return None
def load_config(): return None
def disable(): raise NotImplementedError
def recommended(item): return False
PY
