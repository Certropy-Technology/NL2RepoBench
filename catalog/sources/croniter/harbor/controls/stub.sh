#!/bin/bash
set -euo pipefail

# Stub control - minimal packaging structure with empty implementations
WORKSPACE="/workspace"

echo "[CONTROL:STUB] Creating stub implementation"

# Create directory structure
mkdir -p "${WORKSPACE}/src/croniter"

# Create pyproject.toml
cat > "${WORKSPACE}/pyproject.toml" << 'PYPROJECT'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "croniter"
version = "0.0.1"
dependencies = ["python-dateutil"]

[tool.hatch.build.targets.wheel]
packages = ["src/croniter"]
PYPROJECT

# Create __init__.py with exports but stub implementations
cat > "${WORKSPACE}/src/croniter/__init__.py" << 'INIT'
class CroniterError(ValueError):
    pass

class CroniterBadCronError(CroniterError):
    pass

class CroniterBadDateError(CroniterError):
    pass

class CroniterBadTypeRangeError(TypeError):
    pass

class CroniterNotAlphaError(CroniterBadCronError):
    pass

class CroniterUnsupportedSyntaxError(CroniterBadCronError):
    pass

class croniter:
    def __init__(self, expr_format, start_time=None, ret_type=float, day_or=True, 
                 max_years_between_matches=None, is_prev=False, hash_id=None,
                 implement_cron_bug=False, second_at_beginning=False,
                 expand_from_start_time=False):
        raise NotImplementedError("Stub implementation")
    
    def get_next(self, ret_type=None, start_time=None, update_current=True):
        raise NotImplementedError("Stub implementation")
    
    def get_prev(self, ret_type=None, start_time=None, update_current=True):
        raise NotImplementedError("Stub implementation")
    
    @classmethod
    def is_valid(cls, expression, hash_id=None, encoding='UTF-8', 
                 second_at_beginning=False, strict=False, strict_year=None):
        return False
    
    @classmethod
    def expand(cls, expr_format, hash_id=None, second_at_beginning=False,
               from_timestamp=None, strict=False, strict_year=None):
        raise NotImplementedError("Stub implementation")

def croniter_range(start, stop, expr_format, ret_type=None, day_or=True,
                   exclude_ends=False, _croniter=None, second_at_beginning=False,
                   expand_from_start_time=False):
    raise NotImplementedError("Stub implementation")
    yield  # Make it a generator

def datetime_to_timestamp(d):
    raise NotImplementedError("Stub implementation")

# Constants
MINUTE_FIELD = 0
HOUR_FIELD = 1
DAY_FIELD = 2
MONTH_FIELD = 3
SECOND_FIELD = 5
YEAR_FIELD = 6
UTC_DT = None
OVERFLOW32B_MODE = False

__all__ = [
    "croniter", "croniter_range", "datetime_to_timestamp",
    "CroniterError", "CroniterBadCronError", "CroniterBadDateError",
    "CroniterBadTypeRangeError", "CroniterNotAlphaError",
    "CroniterUnsupportedSyntaxError",
    "MINUTE_FIELD", "HOUR_FIELD", "DAY_FIELD", "MONTH_FIELD",
    "SECOND_FIELD", "YEAR_FIELD", "UTC_DT", "OVERFLOW32B_MODE"
]
INIT

# Create empty croniter.py
cat > "${WORKSPACE}/src/croniter/croniter.py" << 'CRONITER'
# Stub implementation - functionality in __init__.py
pass
CRONITER

echo "[CONTROL:STUB] Stub created"
ls -la "${WORKSPACE}/"
ls -la "${WORKSPACE}/src/croniter/"
