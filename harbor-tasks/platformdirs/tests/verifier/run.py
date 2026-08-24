"""Private custom-json-v1 verifier for the deterministic Unix platformdirs slice."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

EXPECTED_TOTAL = 20
PREFIX = r'''
import contextlib
import io
import json
import os
import runpy
import sys
import tempfile
from pathlib import Path
candidate = os.environ.get("PLATFORMDIRS_CANDIDATE", "/tmp/candidate-site")
sys.path.insert(0, candidate)
import platformdirs
from platformdirs.unix import Unix

def emit(value):
    print(json.dumps(value, sort_keys=True, default=str))
'''


def _case(name: str, body: str, expected: object, env: dict[str, str] | None = None) -> dict[str, object]:
    return {"id": name, "body": body, "expected": expected, "env": env or {}}


def _run_case(case: dict[str, object], home: Path) -> tuple[str, str | None]:
    environment = {
        "HOME": str(home),
        "USERPROFILE": str(home),
        "PATH": os.environ.get("PATH", ""),
        "LANG": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "DISPLAY": "",
        "WAYLAND_DISPLAY": "",
        "TMPDIR": "/tmp",
        "PLATFORMDIRS_CANDIDATE": os.environ.get("PLATFORMDIRS_CANDIDATE", "/tmp/candidate-site"),
    }
    for name in (
        "XDG_DATA_HOME",
        "XDG_CONFIG_HOME",
        "XDG_CACHE_HOME",
        "XDG_STATE_HOME",
        "XDG_RUNTIME_DIR",
        "XDG_DATA_DIRS",
        "XDG_CONFIG_DIRS",
        "XDG_DOCUMENTS_DIR",
        "XDG_DOWNLOAD_DIR",
        "XDG_PICTURES_DIR",
        "XDG_VIDEOS_DIR",
        "XDG_MUSIC_DIR",
        "XDG_DESKTOP_DIR",
        "XDG_PROJECTS_DIR",
        "XDG_PUBLICSHARE_DIR",
        "XDG_TEMPLATES_DIR",
    ):
        environment.pop(name, None)
    environment.update({str(key): str(value) for key, value in dict(case["env"]).items()})
    script = PREFIX + "\n" + str(case["body"]) + "\n\nemit(result)\n"
    try:
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", script],
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return "failed", f"child process error: {exc}"
    if completed.returncode != 0:
        return "failed", f"child exit {completed.returncode}: {completed.stderr[-1000:]}"
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        return "failed", f"child output was not one JSON line: {completed.stdout[-1000:]}"
    try:
        actual = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return "failed", f"child output was invalid JSON: {exc}"
    if actual != case["expected"]:
        return "failed", f"expected {case['expected']!r}, got {actual!r}"
    return "passed", None


def _cases(home: Path) -> list[dict[str, object]]:
    data_base = home / ".local" / "share"
    config_base = home / ".config"
    cache_base = home / ".cache"
    state_base = home / ".local" / "state"
    return [
        _case(
            "exports-and-version",
            "result = {\n"
            "  'version': platformdirs.__version__,\n"
            "  'version_info': list(platformdirs.__version_info__),\n"
            "  'alias': platformdirs.AppDirs is platformdirs.PlatformDirs,\n"
            "  'abc': issubclass(platformdirs.PlatformDirs, platformdirs.PlatformDirsABC),\n"
            "  'class': platformdirs.PlatformDirs.__name__,\n"
            "  'all': all(name in platformdirs.__all__ for name in ('user_data_dir', 'user_data_path', 'site_data_dir', 'site_data_path')),\n"
            "}",
            {"abc": True, "alias": True, "all": True, "class": "Unix", "version": "4.11.3", "version_info": [4, 11, 3]},
        ),
        _case(
            "constructor-and-app-components",
            "dirs = Unix(appname='Acme', appauthor='Example', version='1.2', opinion=False)\n"
            "result = {'data': dirs.user_data_dir, 'config': dirs.user_config_dir, 'state': dirs.user_state_dir, 'log': dirs.user_log_dir}",
            {"config": str(config_base / "Acme" / "1.2"), "data": str(data_base / "Acme" / "1.2"), "log": str(state_base / "Acme" / "1.2"), "state": str(state_base / "Acme" / "1.2")},
        ),
        _case(
            "xdg-user-overrides",
            "dirs = Unix(appname='Acme', version='1.2')\n"
            "result = {'data': dirs.user_data_dir, 'config': dirs.user_config_dir, 'cache': dirs.user_cache_dir, 'state': dirs.user_state_dir, 'runtime': dirs.user_runtime_dir}",
            {"cache": "/custom/cache/Acme/1.2", "config": "/custom/config/Acme/1.2", "data": "/custom/data/Acme/1.2", "runtime": "/custom/runtime/Acme/1.2", "state": "/custom/state/Acme/1.2"},
            {"XDG_DATA_HOME": " /custom/data ", "XDG_CONFIG_HOME": " /custom/config ", "XDG_CACHE_HOME": " /custom/cache ", "XDG_STATE_HOME": " /custom/state ", "XDG_RUNTIME_DIR": " /custom/runtime "},
        ),
        _case(
            "xdg-multipath-order",
            "dirs = Unix(appname='Acme', multipath=True)\n"
            "result = {'data': dirs.site_data_dir, 'data_path': str(dirs.site_data_path), 'config': dirs.site_config_dir, 'config_path': str(dirs.site_config_path), 'apps': dirs.site_applications_dir}",
            {"apps": "/one/applications:/two/applications", "config": "/etc-one/Acme:/etc-two/Acme", "config_path": "/etc-one/Acme", "data": "/one/Acme:/two/Acme", "data_path": "/one/Acme"},
            {"XDG_DATA_DIRS": "/one:: /two ", "XDG_CONFIG_DIRS": "/etc-one::/etc-two",},
        ),
        _case(
            "xdg-blank-fallback",
            "dirs = Unix(appname='Acme')\nresult = {'data': dirs.site_data_dir, 'config': dirs.site_config_dir, 'apps': dirs.site_applications_dir}",
            {"apps": "/usr/local/share/applications", "config": "/etc/xdg/Acme", "data": "/usr/local/share/Acme"},
            {"XDG_DATA_DIRS": " : ", "XDG_CONFIG_DIRS": ":"},
        ),
        _case(
            "media-env-expansion",
            "result = {'documents': Unix().user_documents_dir, 'desktop': Unix().user_desktop_dir}",
            {"desktop": str(home / "Desk"), "documents": str(home / "Docs")},
            {"XDG_DOCUMENTS_DIR": "~/Docs", "XDG_DESKTOP_DIR": " ~/Desk "},
        ),
        _case(
            "user-dirs-file",
            "config = Path(os.environ['HOME']) / '.config'\nconfig.mkdir(parents=True)\n(config / 'user-dirs.dirs').write_text('XDG_DOCUMENTS_DIR=\"$HOME/MyDocs\"\\n')\nresult = {'documents': Unix().user_documents_dir, 'downloads': Unix().user_downloads_dir}",
            {"documents": str(home / "MyDocs"), "downloads": str(home / "Downloads")},
        ),
        _case(
            "iterators",
            "dirs = Unix(appname='Acme')\nresult = {'data': list(dirs.iter_data_dirs()), 'config': list(dirs.iter_config_dirs())}",
            {"config": ["/home/user/config/Acme", "/etc-one/Acme", "/etc-two/Acme"], "data": ["/home/user/data/Acme", "/share-one/Acme", "/share-two/Acme"]},
            {"XDG_DATA_HOME": "/home/user/data", "XDG_DATA_DIRS": "/share-one:/share-two", "XDG_CONFIG_HOME": "/home/user/config", "XDG_CONFIG_DIRS": "/etc-one:/etc-two"},
        ),
        _case(
            "path-properties",
            "dirs = Unix(appname='Acme')\nresult = {'type': type(dirs.user_data_path).__name__, 'same': str(dirs.user_data_path) == dirs.user_data_dir, 'config_type': type(dirs.user_config_path).__name__}",
            {"config_type": "PosixPath", "same": True, "type": "PosixPath"},
        ),
        _case(
            "ensure-exists-disabled",
            "base = Path(os.environ['HOME']) / 'data'\nresult_path = Unix(appname='Acme').user_data_path\nresult = {'path': str(result_path), 'exists': result_path.exists()}",
            {"exists": False, "path": str(home / ".local" / "share" / "Acme")},
        ),
        _case(
            "ensure-exists-enabled",
            "base = Path(os.environ['XDG_DATA_HOME'])\nresult_path = Unix(appname='Acme', ensure_exists=True).user_data_path\nresult = {'path': str(result_path), 'exists': result_path.exists(), 'is_dir': result_path.is_dir()}",
            {"exists": True, "is_dir": True, "path": "/tmp/platformdirs-contract/data/Acme"},
            {"XDG_DATA_HOME": "/tmp/platformdirs-contract/data"},
        ),
        _case(
            "opinionated-log",
            "result = {'on': Unix(appname='Acme').user_log_dir, 'off': Unix(appname='Acme', opinion=False).user_log_dir}",
            {"off": str(state_base / "Acme"), "on": str(state_base / "Acme" / "log")},
        ),
        _case(
            "runtime-override-both-scopes",
            "dirs = Unix(appname='Acme')\nresult = {'user': dirs.user_runtime_dir, 'site': dirs.site_runtime_dir}",
            {"site": "/runtime/Acme", "user": "/runtime/Acme"},
            {"XDG_RUNTIME_DIR": "/runtime"},
        ),
        _case(
            "root-site-redirect",
            "import platformdirs.unix as unix\nunix.getuid = lambda: 0\nresult = {'data': Unix(appname='Acme', use_site_for_root=True).user_data_dir, 'config': Unix(appname='Acme', use_site_for_root=True).user_config_dir}",
            {"config": "/etc/xdg/Acme", "data": "/usr/local/share/Acme"},
        ),
        _case(
            "media-defaults",
            "dirs = Unix()\nPath(os.environ['HOME'], '.config', 'user-dirs.dirs').unlink(missing_ok=True)\nresult = {'documents': dirs.user_documents_dir, 'downloads': dirs.user_downloads_dir, 'pictures': dirs.user_pictures_dir, 'videos': dirs.user_videos_dir, 'music': dirs.user_music_dir, 'desktop': dirs.user_desktop_dir, 'projects': dirs.user_projects_dir, 'public': dirs.user_publicshare_dir, 'templates': dirs.user_templates_dir}",
            {"desktop": str(home / "Desktop"), "documents": str(home / "Documents"), "downloads": str(home / "Downloads"), "music": str(home / "Music"), "pictures": str(home / "Pictures"), "projects": str(home / "Projects"), "public": str(home / "Public"), "templates": str(home / "Templates"), "videos": str(home / "Videos")},
        ),
        _case(
            "convenience-functions",
            "result = {'data': platformdirs.user_data_dir('Acme', version='1.2'), 'config': platformdirs.user_config_dir('Acme', version='1.2'), 'data_path': str(platformdirs.user_data_path('Acme', version='1.2')), 'cache_path': str(platformdirs.user_cache_path('Acme', version='1.2'))}",
            {"cache_path": str(cache_base / "Acme" / "1.2"), "config": str(config_base / "Acme" / "1.2"), "data": str(data_base / "Acme" / "1.2"), "data_path": str(data_base / "Acme" / "1.2")},
        ),
        _case(
            "fonts-and-applications",
            "dirs = Unix(appname='Acme')\nresult = {'fonts': dirs.user_fonts_dir, 'user_apps': dirs.user_applications_dir, 'site_apps': dirs.site_applications_dir, 'bin': dirs.user_bin_dir}",
            {"bin": str(home / ".local" / "bin"), "fonts": str(data_base / "fonts"), "site_apps": "/usr/local/share/applications", "user_apps": str(data_base / "applications")},
        ),
        _case(
            "module-report",
            "out = io.StringIO()\nwith contextlib.redirect_stdout(out):\n    runpy.run_module('platformdirs', run_name='__main__')\ntext = out.getvalue()\nresult = {'header': text.startswith('-- platformdirs 4.11.3 --'), 'has_data': 'user_data_dir:' in text, 'has_runtime': 'site_runtime_dir:' in text}",
            {"has_data": True, "has_runtime": True, "header": True},
        ),
        _case(
            "user-preference-alias",
            "dirs = Unix(appname='Acme')\nresult = {'same': dirs.user_preference_dir == dirs.user_config_dir, 'state_type': type(dirs.user_state_dir).__name__}",
            {"same": True, "state_type": "str"},
        ),
        _case(
            "site-path-first-item",
            "dirs = Unix(appname='Acme', multipath=True)\nresult = {'cache': str(dirs.site_cache_path), 'state': str(dirs.site_state_path), 'apps': str(dirs.site_applications_path)}",
            {"apps": "/one/applications:/two/applications", "cache": "/var/cache/Acme", "state": "/var/lib/Acme"},
            {"XDG_DATA_DIRS": "/one:/two"},
        ),
    ]


def main() -> int:
    leaves: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="platformdirs-verifier-") as temporary:
        home = Path(temporary) / "home"
        home.mkdir()
        for case in _cases(home):
            status, message = _run_case(case, home)
            leaf = {"id": str(case["id"]), "status": status}
            if message:
                leaf["message"] = message
            leaves.append(leaf)
    if len(leaves) != EXPECTED_TOTAL or len({leaf["id"] for leaf in leaves}) != EXPECTED_TOTAL:
        leaves = [{"id": f"platformdirs-case-{index:02d}", "status": "failed"} for index in range(EXPECTED_TOTAL)]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
