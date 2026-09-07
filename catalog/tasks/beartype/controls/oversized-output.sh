#!/usr/bin/env bash
set -euo pipefail

# Oversized-output control for beartype task.
# This control creates a package that generates excessive output.

echo "[control:oversized-output] Starting oversized-output control"

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
description = "Oversized output implementation"
requires-python = ">=3.10"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["beartype"]
EOF

# Create package that spews massive output
cat > "${WORKSPACE}/beartype/__init__.py" << 'EOF'
"""Oversized output implementation."""
import sys

__version__ = "0.22.9"
__version_info__ = (0, 22, 9)

# Generate 10MB of output on import
for i in range(100000):
    print("X" * 100, file=sys.stderr)

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
    if func is None:
        return lambda f: f
    return func

__all__ = [
    'beartype', 'BeartypeConf', 'BeartypeStrategy',
    'BeartypeViolationVerbosity', 'BeartypeDecorPlace',
    'FrozenDict', '__version__', '__version_info__',
]
EOF

touch "${WORKSPACE}/beartype/py.typed"

cat > "${WORKSPACE}/beartype/door/__init__.py" << 'EOF'
"""Oversized output door module."""

class TypeHint:
    def __init__(self, hint):
        self.hint = hint
    @property
    def args(self):
        return ()
    def is_bearable(self, obj, conf=None):
        raise NotImplementedError("oversized")
    def die_if_unbearable(self, obj, conf=None, exception_prefix=""):
        raise NotImplementedError("oversized")
    def is_subhint(self, other):
        raise NotImplementedError("oversized")
    def is_superhint(self, other):
        raise NotImplementedError("oversized")

def is_bearable(obj, hint, conf=None):
    raise NotImplementedError("oversized")

def die_if_unbearable(obj, hint, conf=None, exception_prefix=""):
    raise NotImplementedError("oversized")

def is_subhint(subhint, superhint):
    raise NotImplementedError("oversized")

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
"""Oversized output vale module."""

class Is:
    def __class_getitem__(cls, item):
        raise NotImplementedError("oversized")

class IsAttr:
    def __class_getitem__(cls, item):
        raise NotImplementedError("oversized")

class IsEqual:
    def __class_getitem__(cls, item):
        raise NotImplementedError("oversized")

class IsInstance:
    def __class_getitem__(cls, item):
        raise NotImplementedError("oversized")

class IsSubclass:
    def __class_getitem__(cls, item):
        raise NotImplementedError("oversized")

__all__ = ['Is', 'IsAttr', 'IsEqual', 'IsInstance', 'IsSubclass']
EOF

cat > "${WORKSPACE}/beartype/roar/__init__.py" << 'EOF'
"""Oversized output roar module."""

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
"""Oversized output typing module."""
from typing import *

__all__ = [
    'Any', 'Annotated', 'Callable', 'Literal', 'Optional', 'TypeVar',
    'TypedDict', 'Union', 'cast', 'get_args', 'get_origin',
    'get_type_hints', 'no_type_check', 'overload',
]
EOF

echo "[control:oversized-output] Oversized output package created"
echo "[control:oversized-output] Expected: verifier handles large output without crashing"
echo "[control:oversized-output] Oversized-output control completed"
