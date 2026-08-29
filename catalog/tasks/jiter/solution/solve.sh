#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/pydantic/jiter"
readonly UPSTREAM_REVISION="0fc3c06b4555bb814d3c44ba08d715d9d064da3d"
readonly SOURCE_ARCHIVE_SHA256="093d45e8a53c7d8be9472abbc0e6ff822b9d6987ce17a61bcb75092a11b01693"
readonly FETCH_ROOT="/tmp/jiter-oracle-source"
readonly ROOT="/workspace"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
mkdir -p "$ROOT/jiter"
cat > "$ROOT/pyproject.toml" <<'EOF'
[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "setuptools.build_meta"
[project]
name = "jiter"
version = "0.1.0"
requires-python = ">=3.9"
[tool.setuptools]
packages = ["jiter"]
EOF
cat > "$ROOT/jiter/__init__.py" <<'PY'
from __future__ import annotations
import json
import math
from decimal import Decimal

_cache: set[str] = set()

class LosslessFloat:
    def __init__(self, json_float: bytes):
        if not isinstance(json_float, bytes):
            raise TypeError("json_float must be bytes")
        text = json_float.decode("utf-8")
        json.loads(text)
        if not any(ch in text for ch in ".eE"):
            raise ValueError("not a float token")
        self._raw = json_float
    def as_decimal(self): return Decimal(self._raw.decode())
    def __float__(self): return float(self._raw.decode())
    def __bytes__(self): return self._raw
    def __str__(self): return self._raw.decode()
    def __repr__(self): return f"LosslessFloat({self})"

def cache_clear(): _cache.clear()
def cache_usage(): return len(_cache)

def from_json(json_data, /, *, allow_inf_nan=True, cache_mode='all', partial_mode=False, catch_duplicate_keys=False, float_mode='float'):
    if not isinstance(json_data, (bytes, bytearray, memoryview)):
        raise TypeError("JSON input must be bytes")
    if cache_mode is True: cache_mode = 'all'
    if cache_mode is False: cache_mode = 'none'
    if cache_mode not in ('all', 'keys', 'none'):
        raise ValueError("Invalid cache mode")
    if partial_mode is True: partial_mode = 'on'
    if partial_mode is False: partial_mode = 'off'
    if partial_mode not in ('off', 'on', 'trailing-strings'):
        raise ValueError("Invalid partial mode")
    if float_mode not in ('float', 'decimal', 'lossless-float'):
        raise ValueError("Invalid float mode")
    raw = bytes(json_data)
    try: text = raw.decode('utf-8')
    except UnicodeDecodeError as exc:
        if partial_mode == 'trailing-strings':
            text = raw[:exc.start].decode('utf-8')
        else: raise ValueError('invalid unicode code point') from exc
    def parse_float(value):
        if float_mode == 'decimal': return Decimal(value)
        if float_mode == 'lossless-float': return LosslessFloat(value.encode())
        return float(value)
    def parse_constant(value):
        if not allow_inf_nan: raise ValueError('expected value')
        return {'NaN': math.nan, 'Infinity': math.inf, '-Infinity': -math.inf}[value]
    def pairs(items):
        result = {}
        for key, value in items:
            if catch_duplicate_keys and key in result: raise ValueError(f'Detected duplicate key "{key}"')
            result[key] = value
            if cache_mode in ('all', 'keys'): _cache.add(key)
        return result
    decoder = json.JSONDecoder(parse_float=parse_float, parse_constant=parse_constant, object_pairs_hook=pairs)
    stripped = text.lstrip()
    parse_text = stripped.rstrip()
    try:
        value, end = decoder.raw_decode(parse_text)
        if end != len(parse_text): raise ValueError('trailing characters')
    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        if partial_mode == 'off': raise ValueError(str(exc)) from exc
        if not stripped: return None
        if stripped.startswith('['):
            comma = stripped.rfind(',')
            if comma < 0: return []
            prefix = stripped[:comma] + ']'
            complete = json.loads(prefix)
            if partial_mode == 'trailing-strings':
                tail = stripped[comma + 1:].lstrip()
                if tail.startswith('"') and not tail.endswith('"'):
                    complete.append(tail[1:].encode('utf-8', 'ignore').decode('utf-8', 'ignore'))
            return complete
        if stripped.startswith('{'):
            comma = stripped.rfind(',')
            if comma < 0: return {}
            prefix = stripped[:comma] + '}'
            complete = json.loads(prefix)
            if partial_mode == 'trailing-strings':
                tail = stripped[comma + 1:].lstrip()
                if tail.startswith('"'):
                    key_end = tail.find('"', 1)
                    key = tail[1:key_end]
                    remainder = tail[key_end + 1:].lstrip()
                    if remainder.startswith(':'):
                        value_text = remainder[1:].lstrip()
                        if value_text.startswith('"') and not value_text.endswith('"'):
                            complete[key] = value_text[1:].encode('utf-8', 'ignore').decode('utf-8', 'ignore')
            return complete
        if partial_mode == 'trailing-strings' and stripped.startswith('"'):
            return stripped[1:].encode('utf-8', 'ignore').decode('utf-8', 'ignore')
        raise ValueError(str(exc)) from exc
    if cache_mode == 'all':
        def add_values(item):
            if isinstance(item, str): _cache.add(item)
            elif isinstance(item, list):
                for x in item: add_values(x)
            elif isinstance(item, dict):
                for k, v in item.items(): _cache.add(k); add_values(v)
        add_values(value)
    return value
PY
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION and built deterministic Python oracle"
