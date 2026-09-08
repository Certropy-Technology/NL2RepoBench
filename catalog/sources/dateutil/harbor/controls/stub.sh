#!/bin/bash
set -euo pipefail

cd /workspace

# Create stub package structure
mkdir -p src/dateutil/parser src/dateutil/tz

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT_EOF'
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
PYPROJECT_EOF

# Create setup.cfg
cat > setup.cfg << 'SETUP_EOF'
[metadata]
name = python-dateutil
version = 2.9.0.post0
install_requires = six >= 1.5

[options]
package_dir =
    =src
packages = find:
zip_safe = True

[options.packages.find]
where = src
SETUP_EOF

# Create setup.py
cat > setup.py << 'SETUP_PY_EOF'
from setuptools import setup
setup()
SETUP_PY_EOF

# Stub __init__.py with NotImplementedError for all functions
cat > src/dateutil/__init__.py << 'INIT_EOF'
__version__ = "2.9.0.post0"
__all__ = ['easter', 'parser', 'relativedelta', 'rrule', 'tz', 'utils']

def __getattr__(name):
    if name in __all__:
        import importlib
        return importlib.import_module("." + name, __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
INIT_EOF

# Stub relativedelta
cat > src/dateutil/relativedelta.py << 'REL_EOF'
class relativedelta:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

MO = TU = WE = TH = FR = SA = SU = None
__all__ = ["relativedelta", "MO", "TU", "WE", "TH", "FR", "SA", "SU"]
REL_EOF

# Stub parser
cat > src/dateutil/parser/__init__.py << 'PARSER_EOF'
class ParserError(Exception):
    pass

def parse(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def isoparse(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

class parser:
    def parse(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")

class parserinfo:
    pass

__all__ = ['parse', 'parser', 'parserinfo', 'isoparse', 'isoparser', 'ParserError']
PARSER_EOF

# Stub rrule
cat > src/dateutil/rrule.py << 'RRULE_EOF'
DAILY = WEEKLY = MONTHLY = YEARLY = HOURLY = MINUTELY = SECONDLY = 0
MO = TU = WE = TH = FR = SA = SU = None

class rrule:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def __iter__(self):
        return iter([])

def rrulestr(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

class rruleset:
    def __init__(self):
        pass
    
    def rrule(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def rdate(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def __iter__(self):
        return iter([])

__all__ = ['rrule', 'rrulestr', 'rruleset', 'DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY', 'HOURLY', 'MINUTELY', 'SECONDLY', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
RRULE_EOF

# Stub easter
cat > src/dateutil/easter.py << 'EASTER_EOF'
EASTER_WESTERN = 1
EASTER_ORTHODOX = 2
EASTER_JULIAN = 3

def easter(year, method=EASTER_WESTERN):
    raise NotImplementedError("Stub implementation")

__all__ = ['easter', 'EASTER_WESTERN', 'EASTER_ORTHODOX', 'EASTER_JULIAN']
EASTER_EOF

# Stub tz
cat > src/dateutil/tz/__init__.py << 'TZ_EOF'
class tzinfo:
    def tzname(self, dt):
        return "Stub"

UTC = None

def gettz(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def tzutc():
    raise NotImplementedError("Stub implementation")

def tzlocal():
    raise NotImplementedError("Stub implementation")

def tzoffset(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def tzstr(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def tzrange(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def enfold(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

resolve_imaginary = None

__all__ = ['UTC', 'tzutc', 'tzlocal', 'tzoffset', 'tzstr', 'tzrange', 'gettz', 'enfold', 'resolve_imaginary']
TZ_EOF

# Stub utils
cat > src/dateutil/utils.py << 'UTILS_EOF'
def today(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def default_tzinfo(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

def within_delta(*args, **kwargs):
    raise NotImplementedError("Stub implementation")

__all__ = ['today', 'default_tzinfo', 'within_delta']
UTILS_EOF

# Install
python -m pip install --no-build-isolation --no-deps --no-index -e .
