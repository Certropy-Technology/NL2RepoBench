#!/usr/bin/env bash
set -euo pipefail

# Forgery control for beartype task.
# This control creates a beartype package similar to stub but also writes
# fake grading.json and reward.json files to /logs/verifier/ to verify that
# the verifier generates its own authoritative results.

echo "[control:forgery] Starting forgery control"

WORKSPACE="/workspace"
LOGS_DIR="/logs/verifier"

# Create the stub package (same as stub control)
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
description = "Forgery implementation"
requires-python = ">=3.10"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["beartype"]
EOF

cat > "${WORKSPACE}/beartype/__init__.py" << 'EOF'
"""Forgery beartype implementation."""
import json
import os
from pathlib import Path

__version__ = "0.22.9"
__version_info__ = (0, 22, 9)

# Attempt to forge results
try:
    logs_dir = Path("/logs/verifier")
    if logs_dir.exists():
        # Write fake perfect score
        fake_grading = {
            "valid": True,
            "collected": 422,
            "frozen_total": 422,
            "passed": 422,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "details": ["FORGED BY CANDIDATE"],
        }
        (logs_dir / "grading.json").write_text(json.dumps(fake_grading, indent=2))
        
        fake_reward = {"reward": 1.0}
        (logs_dir / "reward.json").write_text(json.dumps(fake_reward, indent=2))
except Exception:
    pass  # Silently fail

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
"""Forgery door module."""

class TypeHint:
    def __init__(self, hint):
        self.hint = hint
    @property
    def args(self):
        return ()
    def is_bearable(self, obj, conf=None):
        raise NotImplementedError("forgery")
    def die_if_unbearable(self, obj, conf=None, exception_prefix=""):
        raise NotImplementedError("forgery")
    def is_subhint(self, other):
        raise NotImplementedError("forgery")
    def is_superhint(self, other):
        raise NotImplementedError("forgery")

def is_bearable(obj, hint, conf=None):
    raise NotImplementedError("forgery")

def die_if_unbearable(obj, hint, conf=None, exception_prefix=""):
    raise NotImplementedError("forgery")

def is_subhint(subhint, superhint):
    raise NotImplementedError("forgery")

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
"""Forgery vale module."""

class Is:
    def __class_getitem__(cls, item):
        raise NotImplementedError("forgery")

class IsAttr:
    def __class_getitem__(cls, item):
        raise NotImplementedError("forgery")

class IsEqual:
    def __class_getitem__(cls, item):
        raise NotImplementedError("forgery")

class IsInstance:
    def __class_getitem__(cls, item):
        raise NotImplementedError("forgery")

class IsSubclass:
    def __class_getitem__(cls, item):
        raise NotImplementedError("forgery")

__all__ = ['Is', 'IsAttr', 'IsEqual', 'IsInstance', 'IsSubclass']
EOF

cat > "${WORKSPACE}/beartype/roar/__init__.py" << 'EOF'
"""Forgery roar module."""

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
"""Forgery typing module."""
from typing import *

__all__ = [
    'Any', 'Annotated', 'Callable', 'Literal', 'Optional', 'TypeVar',
    'TypedDict', 'Union', 'cast', 'get_args', 'get_origin',
    'get_type_hints', 'no_type_check', 'overload',
]
EOF

echo "[control:forgery] Forgery package with fake results created"
echo "[control:forgery] Expected: verifier overwrites fake results with real score (<=0.20)"
echo "[control:forgery] Forgery control completed"
