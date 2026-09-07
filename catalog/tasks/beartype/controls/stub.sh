#!/usr/bin/env bash
set -euo pipefail

# Stub control for beartype task.
# This control creates a minimal installable beartype package with correct
# structure but stub implementations that should fail most tests.

echo "[control:stub] Starting stub control"

WORKSPACE="/workspace"

# Create package structure
mkdir -p "${WORKSPACE}/beartype/door"
mkdir -p "${WORKSPACE}/beartype/vale"
mkdir -p "${WORKSPACE}/beartype/roar"
mkdir -p "${WORKSPACE}/beartype/typing"

# Create pyproject.toml
cat > "${WORKSPACE}/pyproject.toml" << 'EOF'
[build-system]
requires = ["hatchling>=1.14.0"]
build-backend = "hatchling.build"

[project]
name = "beartype"
version = "0.22.9"
description = "Stub implementation"
requires-python = ">=3.10"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["beartype"]
EOF

# Create beartype/__init__.py with stub decorator
cat > "${WORKSPACE}/beartype/__init__.py" << 'EOF'
"""Stub beartype implementation."""

__version__ = "0.22.9"
__version_info__ = (0, 22, 9)

class BeartypeConf:
    """Stub configuration."""
    def __init__(self, **kwargs):
        pass

class BeartypeStrategy:
    """Stub strategy enum."""
    pass

class BeartypeViolationVerbosity:
    """Stub verbosity enum."""
    pass

class BeartypeDecorPlace:
    """Stub place enum."""
    pass

class FrozenDict(dict):
    """Stub frozen dict."""
    pass

def beartype(func=None, *, conf=None):
    """Stub decorator that does nothing."""
    if func is None:
        return lambda f: f
    return func

__all__ = [
    'beartype',
    'BeartypeConf',
    'BeartypeStrategy',
    'BeartypeViolationVerbosity',
    'BeartypeDecorPlace',
    'FrozenDict',
    '__version__',
    '__version_info__',
]
EOF

# Create beartype/py.typed
touch "${WORKSPACE}/beartype/py.typed"

# Create beartype/door/__init__.py
cat > "${WORKSPACE}/beartype/door/__init__.py" << 'EOF'
"""Stub door module."""

class TypeHint:
    """Stub TypeHint class."""
    def __init__(self, hint):
        self.hint = hint
    
    @property
    def args(self):
        return ()
    
    def is_bearable(self, obj, conf=None):
        raise NotImplementedError("stub")
    
    def die_if_unbearable(self, obj, conf=None, exception_prefix=""):
        raise NotImplementedError("stub")
    
    def is_subhint(self, other):
        raise NotImplementedError("stub")
    
    def is_superhint(self, other):
        raise NotImplementedError("stub")

def is_bearable(obj, hint, conf=None):
    """Stub is_bearable."""
    raise NotImplementedError("stub")

def die_if_unbearable(obj, hint, conf=None, exception_prefix=""):
    """Stub die_if_unbearable."""
    raise NotImplementedError("stub")

def is_subhint(subhint, superhint):
    """Stub is_subhint."""
    raise NotImplementedError("stub")

UnionTypeHint = TypeHint
LiteralTypeHint = TypeHint
AnnotatedTypeHint = TypeHint
AnyTypeHint = TypeHint
ClassTypeHint = TypeHint
NewTypeTypeHint = TypeHint
TypeVarTypeHint = TypeHint
CallableTypeHint = TypeHint
GenericTypeHint = TypeHint
SubscriptedTypeHint = TypeHint
TupleFixedTypeHint = TypeHint
TupleVariableTypeHint = TypeHint

__all__ = [
    'TypeHint', 'UnionTypeHint', 'LiteralTypeHint', 'AnnotatedTypeHint',
    'AnyTypeHint', 'ClassTypeHint', 'NewTypeTypeHint', 'TypeVarTypeHint',
    'CallableTypeHint', 'GenericTypeHint', 'SubscriptedTypeHint',
    'TupleFixedTypeHint', 'TupleVariableTypeHint',
    'is_bearable', 'die_if_unbearable', 'is_subhint',
]
EOF

# Create beartype/vale/__init__.py
cat > "${WORKSPACE}/beartype/vale/__init__.py" << 'EOF'
"""Stub vale module."""

class Is:
    """Stub Is validator."""
    def __class_getitem__(cls, item):
        raise NotImplementedError("stub")

class IsAttr:
    """Stub IsAttr validator."""
    def __class_getitem__(cls, item):
        raise NotImplementedError("stub")

class IsEqual:
    """Stub IsEqual validator."""
    def __class_getitem__(cls, item):
        raise NotImplementedError("stub")

class IsInstance:
    """Stub IsInstance validator."""
    def __class_getitem__(cls, item):
        raise NotImplementedError("stub")

class IsSubclass:
    """Stub IsSubclass validator."""
    def __class_getitem__(cls, item):
        raise NotImplementedError("stub")

__all__ = ['Is', 'IsAttr', 'IsEqual', 'IsInstance', 'IsSubclass']
EOF

# Create beartype/roar/__init__.py
cat > "${WORKSPACE}/beartype/roar/__init__.py" << 'EOF'
"""Stub roar module."""

class BeartypeException(Exception):
    """Stub base exception."""
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

# Create beartype/typing/__init__.py
cat > "${WORKSPACE}/beartype/typing/__init__.py" << 'EOF'
"""Stub typing compatibility module."""
from typing import *

__all__ = [
    'Any', 'Annotated', 'Callable', 'Literal', 'Optional', 'TypeVar',
    'TypedDict', 'Union', 'cast', 'get_args', 'get_origin',
    'get_type_hints', 'no_type_check', 'overload',
]
EOF

echo "[control:stub] Stub package structure created"
echo "[control:stub] Expected: low score (<=0.20) with frozen denominator collected"
echo "[control:stub] Stub control completed"
