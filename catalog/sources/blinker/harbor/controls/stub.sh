#!/usr/bin/env bash
# Stub implementation: minimal structure with NotImplementedError
set -euo pipefail

mkdir -p /workspace/src/blinker

cat > /workspace/src/blinker/__init__.py << 'STUB_INIT'
from .base import Signal, NamedSignal, Namespace, signal, default_namespace, ANY
__all__ = ['Signal', 'NamedSignal', 'Namespace', 'signal', 'default_namespace', 'ANY']
STUB_INIT

cat > /workspace/src/blinker/_utilities.py << 'STUB_UTIL'
class Symbol:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

def make_id(obj):
    return id(obj)

def make_ref(obj, callback=None):
    import weakref
    return weakref.ref(obj, callback)
STUB_UTIL

cat > /workspace/src/blinker/base.py << 'STUB_BASE'
class Symbol:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

ANY = Symbol("ANY")

class Signal:
    ANY = ANY
    def __init__(self, doc=None):
        raise NotImplementedError("Signal not implemented")
    def connect(self, receiver, sender=ANY, weak=True):
        raise NotImplementedError("connect not implemented")
    def disconnect(self, receiver, sender=ANY):
        raise NotImplementedError("disconnect not implemented")
    def send(self, sender=None, /, **kwargs):
        raise NotImplementedError("send not implemented")
    def has_receivers_for(self, sender):
        raise NotImplementedError("has_receivers_for not implemented")
    def receivers_for(self, sender):
        raise NotImplementedError("receivers_for not implemented")
    def connect_via(self, sender, weak=False):
        raise NotImplementedError("connect_via not implemented")
    def connected_to(self, receiver, sender=ANY):
        raise NotImplementedError("connected_to not implemented")
    def muted(self):
        raise NotImplementedError("muted not implemented")

class NamedSignal(Signal):
    def __init__(self, name, doc=None):
        self.name = name
        raise NotImplementedError("NamedSignal not implemented")

class Namespace(dict):
    def signal(self, name, doc=None):
        raise NotImplementedError("Namespace.signal not implemented")

default_namespace = Namespace()
signal = default_namespace.signal
STUB_BASE

cat > /workspace/pyproject.toml << 'STUB_TOML'
[project]
name = "blinker"
version = "1.9.0"
description = "Stub implementation"

[build-system]
requires = ["flit-core<4"]
build-backend = "flit_core.buildapi"
STUB_TOML

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
