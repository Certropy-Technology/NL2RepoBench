#!/usr/bin/env bash
# Background process: leaves processes running
set -euo pipefail

mkdir -p /workspace/src/blinker

echo 'import subprocess
subprocess.Popen(["sleep", "3600"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

from .base import Signal, NamedSignal, Namespace, signal, default_namespace, ANY
__all__ = ["Signal", "NamedSignal", "Namespace", "signal", "default_namespace", "ANY"]' > /workspace/src/blinker/__init__.py

echo 'class Symbol:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

def make_id(obj):
    return id(obj)

def make_ref(obj, callback=None):
    import weakref
    return weakref.ref(obj, callback)' > /workspace/src/blinker/_utilities.py

echo 'class Symbol:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

ANY = Symbol("ANY")

class Signal:
    ANY = ANY
    def __init__(self, doc=None):
        raise NotImplementedError()

class NamedSignal(Signal):
    def __init__(self, name, doc=None):
        self.name = name
        raise NotImplementedError()

class Namespace(dict):
    def signal(self, name, doc=None):
        raise NotImplementedError()

default_namespace = Namespace()
signal = default_namespace.signal' > /workspace/src/blinker/base.py

echo '[project]
name = "blinker"
version = "1.9.0"
description = "Background process"

[build-system]
requires = ["flit-core<4"]
build-backend = "flit_core.buildapi"' > /workspace/pyproject.toml

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
