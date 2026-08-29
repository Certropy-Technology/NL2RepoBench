from __future__ import annotations

import contextlib
import importlib.metadata
import inspect
import io
import json
import os
import resource
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

RESULT_PREFIX = "JARACO_CONTEXT_RESULT="


def archive_bytes(name: str = "root/file.txt", content: bytes = b"hello") -> io.BytesIO:
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w") as archive:
        member = tarfile.TarInfo(name)
        member.size = len(content)
        archive.addfile(member, io.BytesIO(content))
    data.seek(0)
    return data


def exercise(name: str):
    import jaraco.context as jc

    if name == "exports":
        names = [
            "pushd",
            "tarball",
            "tarball_cwd",
            "strip_first_component",
            "_default_filter",
            "_compose_tarfile_filters",
            "_compose",
            "remove_readonly",
            "robust_remover",
            "temp_dir",
            "robust_temp_dir",
            "repo_context",
            "ExceptionTrap",
            "suppress",
            "on_interrupt",
        ]
        return {
            "all_present": all(hasattr(jc, item) for item in names),
            "module": jc.__name__,
            "tarfile_module": jc.tarfile.__name__,
        }

    if name == "metadata":
        on_interrupt_parameters = inspect.signature(jc.on_interrupt).parameters
        return {
            "version": importlib.metadata.version("jaraco.context"),
            "typed_marker": Path(jc.__file__).with_name("py.typed").is_file(),
            "pushd_parameters": list(inspect.signature(jc.pushd).parameters),
            "tarball_target_default": inspect.signature(jc.tarball)
            .parameters["target_dir"]
            .default,
            "on_interrupt_signature": [
                on_interrupt_parameters["action"].kind.name,
                on_interrupt_parameters["code"].default,
            ],
        }

    if name == "pushd":
        with tempfile.TemporaryDirectory() as root:
            before = os.getcwd()
            with jc.pushd(root) as yielded:
                inside = [os.getcwd() == root, os.fspath(yielded) == root]
            return {"restored": os.getcwd() == before, "inside": inside}

    if name == "pushd_exception":
        with tempfile.TemporaryDirectory() as root:
            before = os.getcwd()
            try:
                with jc.pushd(root):
                    raise ValueError("sentinel")
            except ValueError as exc:
                captured = str(exc)
            return {"restored": os.getcwd() == before, "error": captured}

    if name == "temp_dir":
        seen: list[str] = []
        with jc.temp_dir(remover=lambda path: seen.append(path)) as path:
            custom_exists = os.path.isdir(path)
        custom_still_exists = os.path.exists(path)
        shutil.rmtree(path)
        with jc.temp_dir() as default_path:
            Path(default_path, "value").write_text("x", encoding="utf-8")
        return {
            "custom_exists": custom_exists,
            "custom_remover_called": seen == [path],
            "custom_still_exists": custom_still_exists,
            "default_removed": not os.path.exists(default_path),
        }

    if name == "robust_remover":
        with jc.robust_temp_dir() as path:
            Path(path, "value").write_text("x", encoding="utf-8")
        return {
            "is_rmtree": jc.robust_remover() is shutil.rmtree,
            "removed": not os.path.exists(path),
        }

    if name == "compose":
        events: list[str] = []

        @contextlib.contextmanager
        def inner(value):
            events.append("inner-enter")
            try:
                yield value + 1
            finally:
                events.append("inner-exit")

        @contextlib.contextmanager
        def outer(value):
            events.append("outer-enter")
            try:
                yield value * 2
            finally:
                events.append("outer-exit")

        with jc._compose(outer, inner)(3) as result:
            events.append("body")
        return {"result": result, "events": events}

    if name == "exception_trap":
        with jc.ExceptionTrap(ValueError) as trap:
            raise ValueError("bad")
        return {
            "bool": bool(trap),
            "type": trap.type.__name__,
            "value": str(trap.value),
            "tb": trap.tb is not None,
        }

    if name == "exception_trap_nonmatch":
        trap = jc.ExceptionTrap(ValueError)
        try:
            with trap:
                raise KeyError("key")
        except KeyError as exc:
            propagated = type(exc).__name__
        return {"bool": bool(trap), "type": trap.type, "propagated": propagated}

    if name == "trap_decorators":

        @jc.ExceptionTrap(ValueError).raises
        def fails():
            """fails doc"""
            raise ValueError("x")

        @jc.ExceptionTrap(ValueError).passes
        def succeeds():
            return 42

        return {
            "raises": fails(),
            "passes": succeeds(),
            "name": fails.__name__,
            "doc": fails.__doc__,
        }

    if name == "suppress":

        @jc.suppress(KeyError)
        def missing():
            {}["x"]

        context_suppressed = False
        with jc.suppress(KeyError):
            context_suppressed = True
            {}["x"]
        return {
            "decorator_returned": missing(),
            "context": context_suppressed,
            "subclass": issubclass(jc.suppress, contextlib.ContextDecorator),
        }

    if name == "on_interrupt":
        results = {}
        for action in ("suppress", "error", "ignore"):

            def interrupt():
                raise KeyboardInterrupt()

            try:
                jc.on_interrupt(action, code=7)(interrupt)()
            except BaseException as exc:
                results[action] = {"type": type(exc).__name__, "code": getattr(exc, "code", None)}
            else:
                results[action] = None
        try:
            with jc.on_interrupt("suppress"):
                raise ValueError("other")
        except ValueError as exc:
            results["other"] = type(exc).__name__
        return results

    if name == "strip_filter":
        member = tarfile.TarInfo("top/inner.txt")
        filtered = jc.strip_first_component(member, object())
        return {"same": filtered is member, "name": filtered.name}

    if name == "filter_compose":
        events = []

        def left(member, path):
            events.append(["left", member])
            return member + "L"

        def right(member, path):
            events.append(["right", member])
            return member + "R"

        result = jc._compose_tarfile_filters(left, right)("x", object())
        return {"events": events, "result": result}

    if name == "tar_filter_cases":
        members = [
            "dummy_dir/legitimate_file.txt",
            "dummy_dir/subdir/../legitimate_file.txt",
            "dummy_dir/../../tmp/pwned_by_zipslip.txt",
            "dummy_dir/../../../../home/pwned_home.txt",
            "dummy_dir/../escaped.txt",
        ]
        results = []
        for index, member_name in enumerate(members):
            with tarfile.open(fileobj=archive_bytes(member_name), mode="r") as archive:
                member = archive.next()
                with tempfile.TemporaryDirectory() as root:
                    try:
                        archive.extract(member, Path(root, str(index)), filter=jc._default_filter)
                    except BaseException as exc:
                        results.append(type(exc).__name__)
                    else:
                        results.append("ok")
        return results

    if name == "tarball":
        original = urllib.request.urlopen
        urllib.request.urlopen = lambda url: archive_bytes("bundle/content.txt", b"payload")
        try:
            with tempfile.TemporaryDirectory() as root:
                target = os.path.join(root, "out")
                with jc.tarball(
                    "https://example.invalid/archive.tgz", target_dir=target
                ) as extracted:
                    inside = [
                        os.path.isdir(extracted),
                        Path(extracted, "content.txt").read_text(encoding="utf-8"),
                    ]
                return {"inside": inside, "cleaned": not os.path.exists(target)}
        finally:
            urllib.request.urlopen = original

    if name == "tarball_default_target":
        original = urllib.request.urlopen
        urllib.request.urlopen = lambda url: archive_bytes("bundle/x", b"x")
        try:
            with tempfile.TemporaryDirectory() as root:
                old = os.getcwd()
                os.chdir(root)
                try:
                    with jc.tarball("https://example.invalid/thing.tar.gz") as extracted:
                        value = [extracted, os.path.basename(extracted), os.path.exists(extracted)]
                finally:
                    os.chdir(old)
                return {"value": value, "cleaned": not os.path.exists(os.path.join(root, "thing"))}
        finally:
            urllib.request.urlopen = original

    if name == "tarball_error":
        original = urllib.request.urlopen
        urllib.request.urlopen = lambda url: (_ for _ in ()).throw(RuntimeError("download failed"))
        with tempfile.TemporaryDirectory() as root:
            target = os.path.join(root, "out")
            try:
                with jc.tarball("https://example.invalid/archive.tgz", target_dir=target):
                    pass
            except RuntimeError as exc:
                result = {"type": type(exc).__name__, "cleaned": not os.path.exists(target)}
        urllib.request.urlopen = original
        return result

    if name == "tarball_cwd":
        original = urllib.request.urlopen
        urllib.request.urlopen = lambda url: archive_bytes("bundle/x", b"x")
        try:
            with tempfile.TemporaryDirectory() as root:
                old = os.getcwd()
                os.chdir(root)
                try:
                    with jc.tarball_cwd("https://example.invalid/thing.tgz") as extracted:
                        value = [
                            os.path.isfile("x"),
                            os.getcwd() == os.path.join(root, extracted),
                        ]
                finally:
                    os.chdir(old)
                return {
                    "value": value,
                    "after": [os.getcwd() == old, not os.path.exists(os.path.join(root, "thing"))],
                }
        finally:
            urllib.request.urlopen = original

    if name in {"repo_context", "repo_context_hg"}:
        calls = []
        original = subprocess.check_call
        subprocess.check_call = lambda command, **kwargs: calls.append(
            [command, kwargs.get("stdout"), kwargs.get("stderr")]
        )

        @contextlib.contextmanager
        def destination():
            with tempfile.TemporaryDirectory() as path:
                yield path

        try:
            if name == "repo_context":
                url = "https://example.invalid/repo.git"
                branch = "stable"
                quiet = True
            else:
                url = "https://example.invalid/repo"
                branch = None
                quiet = False
            with jc.repo_context(url, branch=branch, quiet=quiet, dest_ctx=destination) as path:
                yielded = os.path.isdir(path)
        finally:
            subprocess.check_call = original
        command, stdout, stderr = calls[0]
        normalized = ["<destination>" if part == path else part for part in command]
        return {
            "command": normalized,
            "quiet": [
                stdout is (subprocess.DEVNULL if quiet else None),
                stderr is (subprocess.DEVNULL if quiet else None),
            ],
            "yielded": yielded,
        }

    if name == "remove_readonly":
        original_remove = os.remove
        called = []
        try:
            with tempfile.TemporaryDirectory() as root:
                path = Path(root, "value")
                path.write_text("x", encoding="utf-8")

                def fake_remove(candidate):
                    called.append(os.fspath(candidate))

                os.remove = fake_remove
                os.chmod(path, 0o400)
                try:
                    raise PermissionError(13, "denied")
                except PermissionError:
                    jc.remove_readonly(os.remove, path, sys.exc_info())
                retry = {
                    "called": called == [os.fspath(path)],
                    "mode": oct(stat.S_IMODE(path.stat().st_mode)),
                }
        finally:
            os.remove = original_remove
        try:
            raise PermissionError(1, "not access denied")
        except PermissionError:
            try:
                jc.remove_readonly(lambda candidate: None, "unused", sys.exc_info())
            except PermissionError as exc:
                reraised = type(exc).__name__
        return {"retry": retry, "reraised": reraised}

    raise ValueError(name)


def main() -> None:
    candidate_site = sys.argv[sys.argv.index("--candidate-site") + 1]
    sys.path.insert(0, candidate_site)
    name = sys.argv[sys.argv.index("--scenario") + 1]
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))
    try:
        payload = {"ok": True, "value": exercise(name)}
    except BaseException as exc:
        payload = {
            "ok": False,
            "type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "message": str(exc),
        }
    print(RESULT_PREFIX + json.dumps(payload, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
