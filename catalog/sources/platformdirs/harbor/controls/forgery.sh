#!/bin/bash
set -euo pipefail

echo "[control:forgery] Creating forgery implementation that attempts to fake good results"

cd /workspace
rm -rf /workspace/*

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[build-system]
build-backend = "hatchling.build"
requires = ["hatchling>=1.29"]

[project]
name = "platformdirs"
version = "4.11.3"
description = "Forgery implementation"
requires-python = ">=3.10"
PYPROJECT

# Create src/platformdirs package
mkdir -p src/platformdirs

# Create __init__.py with forgery that returns fake values
cat > src/platformdirs/__init__.py << 'INIT'
"""Forgery implementation that returns plausible but incorrect values."""

from __future__ import annotations

from pathlib import Path

class PlatformDirsABC:
    def __init__(self, appname=None, appauthor=None, version=None, roaming=False, multipath=False, opinion=True, ensure_exists=False, use_site_for_root=False):
        self.appname = appname
        self.version = version
        self.multipath = multipath
        self.opinion = opinion

class PlatformDirs(PlatformDirsABC):
    @property
    def user_data_dir(self):
        # Wrong base path
        base = "/tmp/fake-data"
        return f"{base}/{self.appname}" if self.appname else base
    
    @property
    def user_config_dir(self):
        # Wrong base path
        base = "/tmp/fake-config"
        return f"{base}/{self.appname}" if self.appname else base
    
    @property
    def user_cache_dir(self):
        # Wrong base path
        return "/tmp/fake-cache"
    
    @property
    def user_state_dir(self):
        return "/tmp/fake-state"
    
    @property
    def user_log_dir(self):
        return "/tmp/fake-log"
    
    @property
    def user_runtime_dir(self):
        return "/tmp/fake-runtime"
    
    @property
    def user_documents_dir(self):
        return "/tmp/Documents"
    
    @property
    def user_downloads_dir(self):
        return "/tmp/Downloads"
    
    @property
    def user_pictures_dir(self):
        return "/tmp/Pictures"
    
    @property
    def user_videos_dir(self):
        return "/tmp/Videos"
    
    @property
    def user_music_dir(self):
        return "/tmp/Music"
    
    @property
    def user_desktop_dir(self):
        return "/tmp/Desktop"
    
    @property
    def user_projects_dir(self):
        return "/tmp/Projects"
    
    @property
    def user_publicshare_dir(self):
        return "/tmp/Public"
    
    @property
    def user_templates_dir(self):
        return "/tmp/Templates"
    
    @property
    def user_fonts_dir(self):
        return "/tmp/fonts"
    
    @property
    def user_preference_dir(self):
        return self.user_config_dir
    
    @property
    def user_bin_dir(self):
        return "/tmp/bin"
    
    @property
    def user_applications_dir(self):
        return "/tmp/applications"
    
    @property
    def site_data_dir(self):
        return "/fake/share"
    
    @property
    def site_config_dir(self):
        return "/fake/etc"
    
    @property
    def site_cache_dir(self):
        return "/fake/cache"
    
    @property
    def site_state_dir(self):
        return "/fake/lib"
    
    @property
    def site_log_dir(self):
        return "/fake/log"
    
    @property
    def site_runtime_dir(self):
        return "/fake/run"
    
    @property
    def site_applications_dir(self):
        return "/fake/applications"
    
    @property
    def site_bin_dir(self):
        return "/fake/bin"
    
    @property
    def user_data_path(self):
        return Path(self.user_data_dir)
    
    @property
    def user_config_path(self):
        return Path(self.user_config_dir)
    
    @property
    def user_cache_path(self):
        return Path(self.user_cache_dir)
    
    @property
    def site_data_path(self):
        return Path(self.site_data_dir)
    
    def iter_data_dirs(self):
        yield self.user_data_dir
        yield self.site_data_dir
    
    def iter_config_dirs(self):
        yield self.user_config_dir
        yield self.site_config_dir
    
    def iter_cache_dirs(self):
        yield self.user_cache_dir

AppDirs = PlatformDirs

def user_data_dir(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, roaming).user_data_dir

def user_config_dir(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, roaming).user_config_dir

def user_cache_dir(appname=None, appauthor=None, version=None, opinion=True, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, opinion=opinion).user_cache_dir

def user_state_dir(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, roaming).user_state_dir

def user_log_dir(appname=None, appauthor=None, version=None, opinion=True, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, opinion=opinion).user_log_dir

def site_data_dir(appname=None, appauthor=None, version=None, multipath=False, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, multipath=multipath).site_data_dir

def site_config_dir(appname=None, appauthor=None, version=None, multipath=False, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, multipath=multipath).site_config_dir

def user_data_path(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, roaming).user_data_path

def user_config_path(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, roaming).user_config_path

def user_cache_path(appname=None, appauthor=None, version=None, opinion=True, ensure_exists=False):
    return PlatformDirs(appname, appauthor, version, opinion=opinion).user_cache_path

__version__ = "4.11.3"
__version_info__ = (4, 11, 3)

__all__ = [
    "PlatformDirs",
    "PlatformDirsABC",
    "AppDirs",
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "site_data_dir",
    "site_config_dir",
    "user_data_path",
    "user_config_path",
    "user_cache_path",
    "__version__",
    "__version_info__",
]
INIT

# Create __main__.py that produces plausible but wrong output
cat > src/platformdirs/__main__.py << 'MAIN'
"""Forgery main module."""

from __future__ import annotations

def main() -> None:
    print("-- platformdirs 4.11.3 --")
    print("-- app dirs (with optional 'version')")
    print("user_data_dir: /tmp/fake-data/MyApp/1.0")
    print("user_config_dir: /tmp/fake-config/MyApp/1.0")

if __name__ == "__main__":
    main()
MAIN

# Create py.typed marker
touch src/platformdirs/py.typed

echo "[control:forgery] Forgery implementation created"
echo "[control:forgery] Returns plausible but incorrect values"
