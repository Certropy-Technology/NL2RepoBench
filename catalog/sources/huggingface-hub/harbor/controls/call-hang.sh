#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/huggingface_hub
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "huggingface_hub"
version = "1.29.0.dev0"
[tool.setuptools]
packages = ["huggingface_hub"]
TOML
cat > /workspace/huggingface_hub/__init__.py <<'PY'
import time

__version__ = '1.29.0.dev0'

class HfApi: pass
class ModelInfo: pass
class DatasetInfo: pass
class SpaceInfo: pass
class RepoUrl: pass
class HfFileMetadata: pass
class CommitOperationAdd: pass
class CommitOperationDelete: pass
class HfFileSystem: pass

def hf_hub_url(*args, **kwargs):
    time.sleep(10)

PY
cat > /workspace/huggingface_hub/utils.py <<'PY'
def validate_repo_id(value):
    return None

def build_hf_headers(**kwargs):
    return {}

def parse_datetime(value):
    return None

def filter_repo_objects(items, **kwargs):
    return iter(())
PY
cat > /workspace/huggingface_hub/hf_api.py <<'PY'
def repo_type_and_id_from_hf_id(value, hub_url=None):
    return (None, '', '')
PY
cat > /workspace/huggingface_hub/file_download.py <<'PY'
def repo_folder_name(**kwargs):
    return ''
PY
PY
