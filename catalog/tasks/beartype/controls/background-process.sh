#!/usr/bin/env bash
set -euo pipefail

# Background-process control for beartype task.
# This control creates a package that spawns background processes.

echo "[control:background-process] Starting background-process control"

WORKSPACE="/workspace"

mkdir -p "${WORKSPACE}/beartype/door"
mkdir -p "${WORKSPACE}/beartype/vale"
mkdir -p "${WORKSPACE}/beartype/roar"
mkdir -p "${WORKSPACE}/beartype/typing"

cat > "${WORKSPACE}/pyproject.toml" << 'EOF'
[build-system]
requires = ["hatchling>=1.14.0"]
build-backend = "hatchling.build"

[project]
name = "beartype"
version = "0.22.9"
description = "Background process implementation"
requires-python = ">=3.10"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["beartype"]
EOF

# Create package that spawns background processes
cat > "${WORKSPACE}/beartype/__init__.py" << 'EOF'
"""Background process implementation."""
import subprocess
import sys

__version__ = "0.22.9"
__version_info__ = (0, 22, 9)

# Spawn background process on import
try:
    subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(3600)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
except Exception:
    pass

class BeartypeConf:
    def __init__(self, **kwargs):
        pass

class BeartypeStrategy:
    pass

class BeartypeViolationVerbosity:
    pass

class BeartypeDecorPlace:
    pass

class FrozenDict(dict):
    pass

def beartype(func=None, *, conf=None):
    def _wrap(f):
        def _stub(*args, **kwargs):
            raise NotImplementedError("stub")
        return _stub
    if func is None:
        return _wrap
    return _wrap(func)

__all__ = [
    'beartype', 'BeartypeConf', 'BeartypeStrategy',
    'BeartypeViolationVerbosity', 'BeartypeDecorPlace',
    'FrozenDict', '__version__', '__version_info__',
]
EOF

touch "${WORKSPACE}/beartype/py.typed"

cat > "${WORKSPACE}/beartype/door/__init__.py" << 'EOF'
"""Background process door module."""

class TypeHint:
    def __init__(self, hint):
        self.hint = hint
    @property
    def args(self):
        return ()
    def is_bearable(self, obj, conf=None):
        raise NotImplementedError("background")
    def die_if_unbearable(self, obj, conf=None, exception_prefix=""):
        raise NotImplementedError("background")
    def is_subhint(self, other):
        raise NotImplementedError("background")
    def is_superhint(self, other):
        raise NotImplementedError("background")

def is_bearable(obj, hint, conf=None):
    raise NotImplementedError("background")

def die_if_unbearable(obj, hint, conf=None, exception_prefix=""):
    raise NotImplementedError("background")

def is_subhint(subhint, superhint):
    raise NotImplementedError("background")

UnionTypeHint = LiteralTypeHint = AnnotatedTypeHint = TypeHint
AnyTypeHint = ClassTypeHint = NewTypeTypeHint = TypeHint
TypeVarTypeHint = CallableTypeHint = GenericTypeHint = TypeHint
SubscriptedTypeHint = TupleFixedTypeHint = TupleVariableTypeHint = TypeHint

__all__ = [
    'TypeHint', 'UnionTypeHint', 'LiteralTypeHint', 'AnnotatedTypeHint',
    'AnyTypeHint', 'ClassTypeHint', 'NewTypeTypeHint', 'TypeVarTypeHint',
    'CallableTypeHint', 'GenericTypeHint', 'SubscriptedTypeHint',
    'TupleFixedTypeHint', 'TupleVariableTypeHint',
    'is_bearable', 'die_if_unbearable', 'is_subhint',
]
EOF

cat > "${WORKSPACE}/beartype/vale/__init__.py" << 'EOF'
"""Background process vale module."""

class Is:
    def __class_getitem__(cls, item):
        raise NotImplementedError("background")

class IsAttr:
    def __class_getitem__(cls, item):
        raise NotImplementedError("background")

class IsEqual:
    def __class_getitem__(cls, item):
        raise NotImplementedError("background")

class IsInstance:
    def __class_getitem__(cls, item):
        raise NotImplementedError("background")

class IsSubclass:
    def __class_getitem__(cls, item):
        raise NotImplementedError("background")

__all__ = ['Is', 'IsAttr', 'IsEqual', 'IsInstance', 'IsSubclass']
EOF

cat > "${WORKSPACE}/beartype/roar/__init__.py" << 'EOF'
"""Background process roar module."""

class BeartypeException(Exception):
    pass

class BeartypeCaveException(BeartypeException):
    pass

class BeartypeConfException(BeartypeException):
    pass

class BeartypeDoorException(BeartypeException):
    pass

class BeartypeDecorException(BeartypeException):
    pass

class BeartypeCallException(BeartypeException):
    pass

class BeartypeCallHintViolation(BeartypeCallException):
    pass

class BeartypeCallHintParamViolation(BeartypeCallHintViolation):
    pass

class BeartypeCallHintReturnViolation(BeartypeCallHintViolation):
    pass

class BeartypeDoorHintViolation(BeartypeDoorException):
    pass

class BeartypeWarning(UserWarning):
    pass

class BeartypeDecorHintWarning(BeartypeWarning):
    pass

class BeartypeDoorWarning(BeartypeWarning):
    pass

__all__ = [
    'BeartypeException', 'BeartypeCaveException', 'BeartypeConfException',
    'BeartypeDoorException', 'BeartypeDecorException', 'BeartypeCallException',
    'BeartypeCallHintViolation', 'BeartypeCallHintParamViolation',
    'BeartypeCallHintReturnViolation', 'BeartypeDoorHintViolation',
    'BeartypeWarning', 'BeartypeDecorHintWarning', 'BeartypeDoorWarning',
]
EOF

cat > "${WORKSPACE}/beartype/typing/__init__.py" << 'EOF'
"""Background process typing module."""
from typing import *

__all__ = [
    'Any', 'Annotated', 'Callable', 'Literal', 'Optional', 'TypeVar',
    'TypedDict', 'Union', 'cast', 'get_args', 'get_origin',
    'get_type_hints', 'no_type_check', 'overload',
]
EOF

echo "[control:background-process] Background process package created"
echo "[control:background-process] Expected: verifier cleans up spawned processes"
echo "[control:background-process] Background-process control completed"
