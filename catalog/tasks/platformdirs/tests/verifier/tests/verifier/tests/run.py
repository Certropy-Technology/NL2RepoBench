"""Private deterministic scenarios for the platformdirs public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    # Import and version scenarios
    (
        "import-platformdirs",
        "import platformdirs\nresult = hasattr(platformdirs, '__version__')",
        {"ok": True, "value": True},
    ),
    (
        "version-info",
        "import platformdirs\nresult = [hasattr(platformdirs, '__version__'), hasattr(platformdirs, '__version_info__')]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "version-format",
        "import platformdirs\nresult = [isinstance(platformdirs.__version__, str), len(platformdirs.__version__) > 0]",
        {"ok": True, "value": [True, True]},
    ),
    
    # PlatformDirs class scenarios
    (
        "platformdirs-class-exists",
        "import platformdirs\nresult = hasattr(platformdirs, 'PlatformDirs')",
        {"ok": True, "value": True},
    ),
    (
        "appdirs-alias",
        "import platformdirs\nresult = hasattr(platformdirs, 'AppDirs')",
        {"ok": True, "value": True},
    ),
    (
        "platformdirsabc-exists",
        "import platformdirs\nresult = hasattr(platformdirs, 'PlatformDirsABC')",
        {"ok": True, "value": True},
    ),
    
    # Constructor scenarios
    (
        "constructor-no-args",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = pd is not None",
        {"ok": True, "value": True},
    ),
    (
        "constructor-with-appname",
        "import platformdirs\npd = platformdirs.PlatformDirs('myapp')\nresult = 'myapp' in pd.user_data_dir",
        {"ok": True, "value": True},
    ),
    (
        "constructor-with-version",
        "import platformdirs\npd = platformdirs.PlatformDirs('myapp', version='1.0')\nresult = '1.0' in pd.user_data_dir",
        {"ok": True, "value": True},
    ),
    (
        "constructor-appauthor-ignored",
        "import platformdirs\npd1 = platformdirs.PlatformDirs('myapp', appauthor='author')\npd2 = platformdirs.PlatformDirs('myapp')\nresult = pd1.user_data_dir == pd2.user_data_dir",
        {"ok": True, "value": True},
    ),
    
    # User directory properties
    (
        "user-data-dir",
        "import platformdirs\nimport os\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(pd.user_data_dir, str), len(pd.user_data_dir) > 0, 'testapp' in pd.user_data_dir]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "user-config-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(pd.user_config_dir, str), 'testapp' in pd.user_config_dir]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-cache-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(pd.user_cache_dir, str), 'testapp' in pd.user_cache_dir]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-state-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(pd.user_state_dir, str), 'testapp' in pd.user_state_dir]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-log-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(pd.user_log_dir, str), 'testapp' in pd.user_log_dir, 'log' in pd.user_log_dir]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "user-log-dir-no-opinion",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp', opinion=False)\nresult = 'log' not in pd.user_log_dir.split('/')[-1]",
        {"ok": True, "value": True},
    ),
    (
        "user-runtime-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = isinstance(pd.user_runtime_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-documents-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = [isinstance(pd.user_documents_dir, str), len(pd.user_documents_dir) > 0]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-downloads-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = [isinstance(pd.user_downloads_dir, str), len(pd.user_downloads_dir) > 0]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-pictures-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_pictures_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-videos-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_videos_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-music-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_music_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-desktop-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_desktop_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-projects-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_projects_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-publicshare-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_publicshare_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-templates-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_templates_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-fonts-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_fonts_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-preference-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = pd.user_preference_dir == pd.user_config_dir",
        {"ok": True, "value": True},
    ),
    (
        "user-bin-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_bin_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "user-applications-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.user_applications_dir, str)",
        {"ok": True, "value": True},
    ),
    
    # Site directory properties
    (
        "site-data-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(pd.site_data_dir, str), 'testapp' in pd.site_data_dir]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "site-config-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(pd.site_config_dir, str), 'testapp' in pd.site_config_dir]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "site-cache-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = isinstance(pd.site_cache_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "site-state-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = isinstance(pd.site_state_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "site-log-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = isinstance(pd.site_log_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "site-runtime-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = isinstance(pd.site_runtime_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "site-applications-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = isinstance(pd.site_applications_dir, str)",
        {"ok": True, "value": True},
    ),
    (
        "site-bin-dir",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = isinstance(pd.site_bin_dir, str)",
        {"ok": True, "value": True},
    ),
    
    # Multipath scenarios
    (
        "multipath-site-data",
        "import platformdirs\nimport os\npd = platformdirs.PlatformDirs('testapp', multipath=True)\nresult = [isinstance(pd.site_data_dir, str), os.pathsep in pd.site_data_dir or len(pd.site_data_dir) > 0]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "multipath-site-config",
        "import platformdirs\nimport os\npd = platformdirs.PlatformDirs('testapp', multipath=True)\nresult = isinstance(pd.site_config_dir, str)",
        {"ok": True, "value": True},
    ),
    
    # Path properties (pathlib.Path versions)
    (
        "user-data-path",
        "import platformdirs\nfrom pathlib import Path\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(pd.user_data_path, Path), str(pd.user_data_path) == pd.user_data_dir]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-config-path",
        "import platformdirs\nfrom pathlib import Path\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(pd.user_config_path, Path), str(pd.user_config_path) == pd.user_config_dir]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-cache-path",
        "import platformdirs\nfrom pathlib import Path\npd = platformdirs.PlatformDirs('testapp')\nresult = isinstance(pd.user_cache_path, Path)",
        {"ok": True, "value": True},
    ),
    (
        "site-data-path",
        "import platformdirs\nfrom pathlib import Path\npd = platformdirs.PlatformDirs('testapp')\nresult = isinstance(pd.site_data_path, Path)",
        {"ok": True, "value": True},
    ),
    
    # Convenience functions
    (
        "user-cache-dir-function",
        "import platformdirs\nresult = [isinstance(platformdirs.user_cache_dir('testapp'), str), 'testapp' in platformdirs.user_cache_dir('testapp')]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-config-dir-function",
        "import platformdirs\nresult = [isinstance(platformdirs.user_config_dir('testapp'), str), 'testapp' in platformdirs.user_config_dir('testapp')]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-data-dir-function",
        "import platformdirs\nresult = [isinstance(platformdirs.user_data_dir('testapp'), str), 'testapp' in platformdirs.user_data_dir('testapp')]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-log-dir-function",
        "import platformdirs\nresult = [isinstance(platformdirs.user_log_dir('testapp'), str), 'testapp' in platformdirs.user_log_dir('testapp')]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "user-state-dir-function",
        "import platformdirs\nresult = isinstance(platformdirs.user_state_dir('testapp'), str)",
        {"ok": True, "value": True},
    ),
    (
        "site-data-dir-function",
        "import platformdirs\nresult = isinstance(platformdirs.site_data_dir('testapp'), str)",
        {"ok": True, "value": True},
    ),
    (
        "site-config-dir-function",
        "import platformdirs\nresult = isinstance(platformdirs.site_config_dir('testapp'), str)",
        {"ok": True, "value": True},
    ),
    
    # Path convenience functions
    (
        "user-cache-path-function",
        "import platformdirs\nfrom pathlib import Path\nresult = isinstance(platformdirs.user_cache_path('testapp'), Path)",
        {"ok": True, "value": True},
    ),
    (
        "user-config-path-function",
        "import platformdirs\nfrom pathlib import Path\nresult = isinstance(platformdirs.user_config_path('testapp'), Path)",
        {"ok": True, "value": True},
    ),
    (
        "user-data-path-function",
        "import platformdirs\nfrom pathlib import Path\nresult = isinstance(platformdirs.user_data_path('testapp'), Path)",
        {"ok": True, "value": True},
    ),
    
    # Iterator functions
    (
        "iter-data-dirs",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(list(pd.iter_data_dirs()), list), len(list(pd.iter_data_dirs())) >= 1]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "iter-config-dirs",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = [isinstance(list(pd.iter_config_dirs()), list), len(list(pd.iter_config_dirs())) >= 1]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "iter-cache-dirs",
        "import platformdirs\npd = platformdirs.PlatformDirs('testapp')\nresult = isinstance(list(pd.iter_cache_dirs()), list)",
        {"ok": True, "value": True},
    ),
    
    # Module command scenario
    (
        "main-command-output",
        "import subprocess\nimport sys\nresult = subprocess.run([sys.executable, '-m', 'platformdirs'], capture_output=True, text=True)\nout = result.stdout\nresult = [result.returncode == 0, '-- platformdirs' in out, 'user_data_dir' in out]",
        {"ok": True, "value": [True, True, True]},
    ),
    
    # XDG environment behavior scenarios
    (
        "xdg-data-home-override",
        "import platformdirs\nimport os\nos.environ['XDG_DATA_HOME'] = '/tmp/custom-data'\npd = platformdirs.PlatformDirs('testapp')\nresult = '/tmp/custom-data' in pd.user_data_dir",
        {"ok": True, "value": True},
    ),
    (
        "xdg-config-home-override",
        "import platformdirs\nimport os\nos.environ['XDG_CONFIG_HOME'] = '/tmp/custom-config'\npd = platformdirs.PlatformDirs('testapp')\nresult = '/tmp/custom-config' in pd.user_config_dir",
        {"ok": True, "value": True},
    ),
    (
        "xdg-cache-home-override",
        "import platformdirs\nimport os\nos.environ['XDG_CACHE_HOME'] = '/tmp/custom-cache'\npd = platformdirs.PlatformDirs('testapp')\nresult = '/tmp/custom-cache' in pd.user_cache_dir",
        {"ok": True, "value": True},
    ),
    
    # Ensure exists scenarios
    (
        "ensure-exists-false",
        "import platformdirs\nimport os\npd = platformdirs.PlatformDirs('nonexistent-test-app-xyz', ensure_exists=False)\ndir_path = pd.user_cache_dir\nresult = isinstance(dir_path, str)",
        {"ok": True, "value": True},
    ),
    
    # Version/appname combinations
    (
        "no-appname-no-version",
        "import platformdirs\npd = platformdirs.PlatformDirs()\nresult = [isinstance(pd.user_data_dir, str), len(pd.user_data_dir) > 0]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "appname-with-version",
        "import platformdirs\npd1 = platformdirs.PlatformDirs('myapp')\npd2 = platformdirs.PlatformDirs('myapp', version='2.0')\nresult = [len(pd2.user_data_dir) > len(pd1.user_data_dir), '2.0' in pd2.user_data_dir]",
        {"ok": True, "value": [True, True]},
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
