from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections import OrderedDict
from pathlib import Path


def command(*args: str, cwd: Path, timeout: int = 12) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "virtualenv", *args], cwd=cwd, capture_output=True,
        text=True, timeout=timeout, check=False, env=os.environ.copy(),
    )


def create(root: Path, name: str = "env", *extra: str) -> tuple[Path, subprocess.CompletedProcess[str]]:
    target = root / name
    result = command(*extra, str(target), "--no-seed", cwd=root)
    assert result.returncode == 0, result.stderr
    return target, result


def config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def run_case(name: str) -> None:
    import virtualenv
    from virtualenv.create.pyenv_cfg import PyEnvCfg
    from virtualenv.run import cli_run, session_via_cli

    with tempfile.TemporaryDirectory(prefix="virtualenv-task-") as raw:
        root = Path(raw)
        if name == "import_version":
            assert virtualenv.__version__ == "21.7.5"
        elif name == "module_help":
            result = command("--help", cwd=root)
            assert result.returncode == 0 and "virtualenv" in result.stdout.lower()
        elif name == "module_version":
            result = command("--version", cwd=root)
            assert result.returncode == 0 and "21.7.5" in result.stdout
        elif name == "run_exports":
            assert callable(cli_run) and callable(session_via_cli)
        elif name == "session_parse":
            session = session_via_cli([str(root / "later"), "--no-seed"], setup_logging=False)
            assert not (root / "later").exists() and hasattr(session, "creator")
        elif name == "help_flags":
            result = command("--help", cwd=root)
            assert all(flag in result.stdout for flag in ("--no-seed", "--clear", "--prompt", "--activators"))
        elif name == "basic_create":
            target, _ = create(root)
            assert (target / "bin" / "python").exists() and (target / "pyvenv.cfg").is_file()
        elif name == "created_python_runs":
            target, _ = create(root)
            output = subprocess.check_output([target / "bin" / "python", "-c", "print('ok')"], text=True).strip()
            assert output == "ok"
        elif name == "isolated_prefix":
            target, _ = create(root)
            output = subprocess.check_output([target / "bin" / "python", "-c", "import sys; print(sys.prefix != sys.base_prefix)"], text=True).strip()
            assert output == "True"
        elif name == "config_has_home":
            target, _ = create(root)
            assert config(target / "pyvenv.cfg").get("home")
        elif name == "config_has_version":
            target, _ = create(root)
            assert config(target / "pyvenv.cfg").get("version", "").count(".") >= 2
        elif name == "site_packages_exists":
            target, _ = create(root)
            assert any(path.is_dir() for path in (target / "lib").rglob("site-packages"))
        elif name == "default_gitignore":
            target, _ = create(root)
            assert (target / ".gitignore").read_text(encoding="utf-8").splitlines() == ["# created by virtualenv automatically", "*"]
        elif name == "default_bash_activation":
            target, _ = create(root)
            assert "VIRTUAL_ENV" in (target / "bin" / "activate").read_text(encoding="utf-8")
        elif name == "empty_activators":
            target, _ = create(root, "env", "--activators", "")
            assert not (target / "bin" / "activate").exists()
        elif name == "no_vcs_ignore":
            target, _ = create(root, "env", "--no-vcs-ignore")
            assert not (target / ".gitignore").exists()
        elif name == "existing_gitignore_preserved":
            target = root / "env"
            target.mkdir()
            (target / ".gitignore").write_text("keep\n", encoding="utf-8")
            result = command(str(target), "--no-seed", cwd=root)
            assert result.returncode == 0 and (target / ".gitignore").read_text(encoding="utf-8") == "keep\n"
        elif name == "prompt_value":
            target, _ = create(root, "env", "--prompt", "named prompt")
            assert config(target / "pyvenv.cfg").get("prompt") == "named prompt"
        elif name == "prompt_dot":
            target, _ = create(root, "env", "--prompt", ".")
            assert config(target / "pyvenv.cfg").get("prompt") == root.name
        elif name == "clear_removes_marker":
            target, _ = create(root)
            (target / "marker").write_text("remove", encoding="utf-8")
            result = command(str(target), "--no-seed", "--clear", cwd=root)
            assert result.returncode == 0 and not (target / "marker").exists()
        elif name == "system_site_packages_true":
            target, _ = create(root, "env", "--system-site-packages")
            assert config(target / "pyvenv.cfg").get("include-system-site-packages", "").lower() == "true"
        elif name == "system_site_packages_default_false":
            target, _ = create(root)
            assert config(target / "pyvenv.cfg").get("include-system-site-packages", "").lower() == "false"
        elif name == "copies_create":
            target, _ = create(root, "env", "--copies")
            assert (target / "bin" / "python").exists()
        elif name == "symlinks_create":
            target, _ = create(root, "env", "--symlinks")
            assert (target / "bin" / "python").is_symlink()
        elif name == "python_selector":
            target, _ = create(root, "env", "--python", sys.executable)
            assert (target / "bin" / "python").exists()
        elif name == "creator_venv":
            target, _ = create(root, "env", "--creator", "venv")
            assert (target / "bin" / "python").exists()
        elif name == "app_data_reset":
            app_data = root / "cache"
            app_data.mkdir()
            (app_data / "old").write_text("old", encoding="utf-8")
            target, _ = create(root, "env", "--app-data", str(app_data), "--reset-app-data")
            assert target.exists() and not (app_data / "old").exists()
        elif name == "builtin_discovery":
            target, _ = create(root, "env", "--discovery", "builtin")
            assert target.exists()
        elif name == "invalid_discovery":
            result = command("--discovery", "pyenv", str(root / "env"), "--no-seed", cwd=root)
            assert result.returncode != 0 and "pyenv" in (result.stdout + result.stderr)
        elif name == "invalid_interpreter":
            result = command("--python", str(root / "missing-python"), str(root / "env"), "--no-seed", cwd=root)
            assert result.returncode != 0
        elif name == "destination_file_error":
            target = root / "file"
            target.write_text("x", encoding="utf-8")
            assert command(str(target), "--no-seed", cwd=root).returncode != 0
        elif name == "path_separator_error":
            assert command(str(root / "a:b"), "--no-seed", cwd=root).returncode != 0
        elif name == "pyenvcfg_from_file":
            path = root / "pyvenv.cfg"
            path.write_text("first = one\nprompt = 'two words'\n", encoding="utf-8")
            value = PyEnvCfg.from_file(path)
            assert value["first"] == "one" and value["prompt"] == "two words"
        elif name == "pyenvcfg_write_refresh":
            path = root / "pyvenv.cfg"
            value = PyEnvCfg(OrderedDict(), path)
            value["first"] = "one"
            value.update({"second": "two"})
            value.write()
            assert list(value.refresh()) == ["first", "second"]
        elif name == "pyenvcfg_prompt_quotes":
            path = root / "pyvenv.cfg"
            value = PyEnvCfg(OrderedDict([("prompt", "two words")]), path)
            value.write()
            assert 'prompt = "two words"' in path.read_text(encoding="utf-8")
        elif name == "cli_run_creates":
            target = root / "env"
            session = cli_run([str(target), "--no-seed", "--activators", ""], setup_logging=False)
            assert target.exists() and hasattr(session, "creator")
        else:
            raise AssertionError(f"unknown scenario {name}")


def main() -> None:
    try:
        run_case(sys.argv[1])
    except BaseException as error:
        print(json.dumps({"ok": False, "message": f"{type(error).__name__}: {error}"}))
    else:
        print(json.dumps({"ok": True}))


if __name__ == "__main__":
    main()
