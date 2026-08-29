from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
import tempfile
import warnings
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


def _memory_class(ctx, priority=5, initial=None):
    class MemoryBackend(ctx.backend.KeyringBackend):
        def __init__(self):
            self.store = dict(initial or {})
            super().__init__()

        @ctx.properties.classproperty
        def priority(cls):
            return priority

        def get_password(self, service, username):
            return self.store.get((service, username))

        def set_password(self, service, username, password):
            self.store[(service, username)] = password

        def delete_password(self, service, username):
            try:
                del self.store[(service, username)]
            except KeyError:
                raise ctx.errors.PasswordDeleteError("not found") from None

    return MemoryBackend


def packaging_surface(ctx):
    from importlib import metadata

    return {
        "all": list(ctx.keyring.__all__),
        "callables": all(callable(getattr(ctx.keyring, name)) for name in ctx.keyring.__all__),
        "console": len(metadata.entry_points(group="console_scripts", name="keyring")),
        "version": metadata.version("keyring"),
    }


def simple_credential(ctx):
    cred = ctx.credentials.SimpleCredential("alice", "s3cret")
    return {"username": cred.username, "password": cred.password, "vars": cred._vars()}


def anonymous_credential(ctx):
    cred = ctx.credentials.AnonymousCredential("token")
    try:
        cred.username
    except Exception as error:
        exception = [type(error).__name__, str(error)]
    return {"password": cred.password, "vars": cred._vars(), "username_error": exception}


def environ_credential(ctx):
    first = ctx.credentials.EnvironCredential("KR_USER", "KR_PASS")
    equal = first == ctx.credentials.EnvironCredential("KR_USER", "KR_PASS")
    unequal = first == ctx.credentials.EnvironCredential("KR_USER", "OTHER")
    with mock.patch.dict(os.environ, {"KR_USER": "ada", "KR_PASS": "secret"}, clear=False):
        values = first._vars()
    with mock.patch.dict(os.environ, {}, clear=True):
        try:
            first.username
        except Exception as error:
            missing = [type(error).__name__, str(error)]
    return {"equal": equal, "missing": missing, "unequal": unequal, "values": values}


def credential_abstract(ctx):
    try:
        ctx.credentials.Credential()
    except Exception as error:
        return {"message_has_abstract": "abstract" in str(error), "type": type(error).__name__}


def exception_hierarchy(ctx):
    return {
        "delete": issubclass(ctx.errors.PasswordDeleteError, ctx.errors.KeyringError),
        "locked": issubclass(ctx.errors.KeyringLocked, ctx.errors.KeyringError),
        "no_keyring_runtime": issubclass(ctx.errors.NoKeyringError, RuntimeError),
        "set": issubclass(ctx.errors.PasswordSetError, ctx.errors.KeyringError),
    }


def exception_context(ctx):
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        with ctx.errors.ExceptionRaisedContext(ValueError) as trapped:
            raise ValueError("bad")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with ctx.errors.ExceptionRaisedContext(ValueError) as clear:
            pass
    return {
        "clear": bool(clear),
        "message": str(trapped.value),
        "suppressed": bool(trapped),
        "type": trapped.type.__name__,
        "warning": seen[0].category.__name__,
    }


def null_backend(ctx):
    ring = ctx.null_backend.Keyring()
    return {
        "delete": ring.delete_password("svc", "user"),
        "get": ring.get_password("svc", "user"),
        "priority": ring.priority,
        "set": ring.set_password("svc", "user", "pw"),
    }


def fail_backend(ctx):
    ring = ctx.fail_backend.Keyring()
    failures = []
    for call in (
        lambda: ring.get_password("svc", "user"),
        lambda: ring.set_password("svc", "user", "pw"),
        lambda: ring.delete_password("svc", "user"),
    ):
        try:
            call()
        except Exception as error:
            failures.append([type(error).__name__, "No recommended backend" in str(error)])
    return {"failures": failures, "priority": ring.priority}


def null_crypter(ctx):
    value = {"nested": [1, 2]}
    crypter = ctx.backend.NullCrypter()
    return {"decrypt_identity": crypter.decrypt(value) is value, "encrypt_identity": crypter.encrypt(value) is value}


def scheme_default(ctx):
    selector = ctx.backend.SchemeSelectable()
    return {"full": selector._query("svc", "alice", extra="x"), "service": selector._query("svc")}


def scheme_keepass(ctx):
    selector = ctx.backend.SchemeSelectable()
    selector.scheme = "KeePassXC"
    return {"full": selector._query("svc", "alice"), "service": selector._query("svc")}


def backend_identity(ctx):
    cls = _memory_class(ctx, priority=4.5)
    ring = cls()
    return {
        "name_suffix": ring.name.endswith("MemoryBackend"),
        "priority": ring.priority,
        "string_priority": "priority: 4.5" in str(ring),
        "string_suffix": str(ring).split(" (")[0].endswith("MemoryBackend"),
    }


def backend_viability(ctx):
    good = _memory_class(ctx, priority=2)

    class Bad(ctx.backend.KeyringBackend):
        @ctx.properties.classproperty
        def priority(cls):
            raise RuntimeError("unavailable")

        def get_password(self, service, username):
            return None

        def set_password(self, service, username, password):
            pass

    viable = list(ctx.backend.KeyringBackend.get_viable_backends())
    return {"bad": Bad.viable, "good": good.viable, "listed": good in viable and Bad not in viable}


def backend_registration(ctx):
    cls = _memory_class(ctx)
    return {"registered": cls in ctx.backend.KeyringBackend._classes}


def backend_default_credential(ctx):
    ring = _memory_class(ctx, initial={("svc", "alice"): "pw"})()
    found = ring.get_credential("svc", "alice")
    return {
        "found": found._vars(),
        "missing": ring.get_credential("svc", "nobody"),
        "none_username": ring.get_credential("svc", None),
    }


def backend_default_delete(ctx):
    class NoDelete(ctx.backend.KeyringBackend):
        priority = 1

        def get_password(self, service, username):
            return None

        def set_password(self, service, username, password):
            pass

    try:
        NoDelete().delete_password("svc", "user")
    except Exception as error:
        return {"message": str(error), "type": type(error).__name__}


def backend_empty_username(ctx):
    ring = _memory_class(ctx)()
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        ring.set_password("svc", "", "pw")
    return {"stored": ring.get_password("svc", ""), "warning": seen[0].category.__name__}


def backend_env_properties(ctx):
    with mock.patch.dict(os.environ, {"KEYRING_PROPERTY_FOO_BAR": "fizz buzz", "OTHER": "ignored"}, clear=True):
        ring = _memory_class(ctx)()
    return {"foo_bar": ring.foo_bar, "other": hasattr(ring, "other")}


def backend_with_properties(ctx):
    ring = _memory_class(ctx)()
    alt = ring.with_properties(foo="bar")
    return {"alt": alt.foo, "independent": alt is not ring, "original_has": hasattr(ring, "foo")}


def core_facade(ctx):
    ring = _memory_class(ctx)()
    ctx.keyring.set_keyring(ring)
    ctx.keyring.set_password("svc", "alice", "pw")
    before = ctx.keyring.get_password("svc", "alice")
    credential = ctx.keyring.get_credential("svc", "alice")._vars()
    ctx.keyring.delete_password("svc", "alice")
    return {"before": before, "credential": credential, "same": ctx.keyring.get_keyring() is ring, "after": ctx.keyring.get_password("svc", "alice")}


def core_set_keyring_validation(ctx):
    try:
        ctx.keyring.set_keyring(object())
    except Exception as error:
        return {"message": str(error), "type": type(error).__name__}


def core_load_env(ctx):
    with mock.patch.dict(os.environ, {"PYTHON_KEYRING_BACKEND": "keyring.backends.null.Keyring"}, clear=False):
        loaded = ctx.core.load_env()
    with mock.patch.dict(os.environ, {}, clear=True):
        missing = ctx.core.load_env()
    return {"loaded": type(loaded).__module__ + "." + type(loaded).__name__, "missing": missing}


def core_load_config_missing(ctx):
    with tempfile.TemporaryDirectory() as temp:
        original = ctx.core._config_path
        ctx.core._config_path = lambda: Path(temp) / "missing.cfg"
        try:
            return {"value": ctx.core.load_config()}
        finally:
            ctx.core._config_path = original


def core_load_config_backend(ctx):
    with tempfile.TemporaryDirectory() as temp:
        config = Path(temp) / "keyringrc.cfg"
        config.write_text("[backend]\ndefault-keyring=keyring.backends.null.Keyring\n", encoding="utf-8")
        original = ctx.core._config_path
        ctx.core._config_path = lambda: config
        try:
            loaded = ctx.core.load_config()
        finally:
            ctx.core._config_path = original
    return {"class": type(loaded).__module__ + "." + type(loaded).__name__, "priority": loaded.priority}


def core_disable(ctx):
    with tempfile.TemporaryDirectory() as temp:
        config = Path(temp) / "keyringrc.cfg"
        with mock.patch.object(ctx.core.platform, "config_root", return_value=Path(temp)):
            ctx.core.disable()
            content = config.read_text(encoding="utf-8")
            try:
                ctx.core.disable()
            except Exception as error:
                second = [type(error).__name__, "Refusing to overwrite" in str(error)]
    return {"content": content, "second": second}


def core_detect_priority(ctx):
    low = _memory_class(ctx, priority=1)()
    high = _memory_class(ctx, priority=8)()
    with mock.patch.object(ctx.core, "load_env", return_value=None), mock.patch.object(ctx.core, "load_config", return_value=None), mock.patch.object(ctx.backend, "get_all_keyring", return_value=[low, high]):
        selected = ctx.core._detect_backend()
        recommended = ctx.core._detect_backend(ctx.core.recommended)
    return {"recommended": recommended.priority, "selected": selected.priority}


def chainer_priority(ctx):
    one = _memory_class(ctx, priority=2)()
    two = _memory_class(ctx, priority=3)()
    with mock.patch.object(ctx.backend, "get_all_keyring", return_value=[one]):
        single = ctx.chainer.ChainerBackend.priority
    with mock.patch.object(ctx.backend, "get_all_keyring", return_value=[one, two]):
        multiple = ctx.chainer.ChainerBackend.priority
        order = [ring.priority for ring in ctx.chainer.ChainerBackend.backends]
    return {"multiple": multiple, "order": order, "single": single}


def chainer_read(ctx):
    low = _memory_class(ctx, priority=1, initial={("svc", "alice"): "low"})()
    high = _memory_class(ctx, priority=9, initial={("svc", "alice"): "high"})()
    with mock.patch.object(ctx.backend, "get_all_keyring", return_value=[low, high]):
        value = ctx.chainer.ChainerBackend().get_password("svc", "alice")
    return {"value": value}


def chainer_write_delete(ctx):
    class Reject(_memory_class(ctx, priority=9)):
        def set_password(self, service, username, password):
            raise NotImplementedError

        def delete_password(self, service, username):
            raise NotImplementedError

    reject = Reject()
    target = _memory_class(ctx, priority=2)()
    with mock.patch.object(ctx.backend, "get_all_keyring", return_value=[reject, target]):
        chain = ctx.chainer.ChainerBackend()
        chain.set_password("svc", "alice", "pw")
        stored = target.get_password("svc", "alice")
        chain.delete_password("svc", "alice")
    return {"deleted": target.get_password("svc", "alice"), "stored": stored}


def chainer_credential(ctx):
    low = _memory_class(ctx, priority=1, initial={("svc", "alice"): "low"})()
    high = _memory_class(ctx, priority=9, initial={("svc", "alice"): "high"})()
    with mock.patch.object(ctx.backend, "get_all_keyring", return_value=[low, high]):
        cred = ctx.chainer.ChainerBackend().get_credential("svc", "alice")
    return cred._vars()


def non_data_property(ctx):
    class Sample:
        @ctx.properties.NonDataProperty
        def value(self):
            return 3

    sample = Sample()
    before = sample.value
    sample.value = 4
    return {"before": before, "class_descriptor": type(Sample.__dict__["value"]).__name__, "override": sample.value}


def classproperty_mutation(ctx):
    class Sample(metaclass=ctx.properties.classproperty.Meta):
        stored = 1

        @ctx.properties.classproperty
        def value(cls):
            return cls.stored

        @value.setter
        def value(cls, new):
            cls.stored = new

    sample = Sample()
    sample.value = 5
    return {"class": Sample.value, "instance": sample.value, "instance_vars": vars(sample)}


def classproperty_readonly(ctx):
    class Sample(metaclass=ctx.properties.classproperty.Meta):
        @ctx.properties.classproperty
        def value(cls):
            return "fixed"

    try:
        Sample.value = "changed"
    except Exception as error:
        return {"message": str(error), "type": type(error).__name__, "value": Sample.value}


def cli_strip(ctx):
    fn = ctx.cli.CommandLineTool.strip_last_newline
    return {"empty": fn(""), "many": fn("a\n\n"), "none": fn("abc"), "one": fn("abc\n")}


def cli_set_pipe(ctx):
    ring = _memory_class(ctx)()
    ctx.keyring.set_keyring(ring)
    stdin = io.StringIO("pipe-secret\n")
    with mock.patch.object(sys, "stdin", stdin):
        ctx.cli.main(["set", "svc", "alice"])
    return {"stored": ring.get_password("svc", "alice")}


def cli_get_plain(ctx):
    ring = _memory_class(ctx, initial={("svc", "alice"): "pw"})()
    ctx.keyring.set_keyring(ring)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        ctx.cli.main(["--mode", "creds", "get", "svc", "alice"])
    return {"lines": output.getvalue().splitlines()}


def cli_get_json(ctx):
    ring = _memory_class(ctx, initial={("svc", "alice"): "pw"})()
    ctx.keyring.set_keyring(ring)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        ctx.cli.main(["--mode", "creds", "--output", "json", "get", "svc", "alice"])
    return json.loads(output.getvalue())


def cli_missing_args(ctx):
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        try:
            ctx.cli.main(["set", "svc"])
        except SystemExit as error:
            code = error.code
    return {"code": code, "requires": "set requires service and username" in stderr.getvalue()}


def cli_parser_contract(ctx):
    parser = ctx.cli.CommandLineTool().parser
    return {"formats": parser._output_formats, "modes": parser._get_modes, "operations": parser._operations}


def completion_missing(ctx):
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        try:
            ctx.cli.main(["--print-completion", "bash"])
        except SystemExit as error:
            code = error.code
    return {"code": code, "notice": "Install keyring[completion]" in stderr.getvalue()}


def http_password_mgr_existing(ctx):
    ring = _memory_class(ctx, initial={("realm", "ada"): "stored"})()
    ctx.keyring.set_keyring(ring)
    manager = ctx.http.PasswordMgr()
    with mock.patch.object(ctx.http.getpass, "getuser", return_value="ada"):
        value = manager.find_user_password("realm", "https://example.test")
    return {"value": list(value)}


def http_password_mgr_prompt(ctx):
    ring = _memory_class(ctx)()
    ctx.keyring.set_keyring(ring)
    manager = ctx.http.PasswordMgr()
    with mock.patch.object(ctx.http.getpass, "getuser", return_value="ada"), mock.patch.object(ctx.http.getpass, "getpass", return_value="prompted") as prompt:
        value = manager.find_user_password("realm", "https://example.test")
    return {"prompt_has_context": "ada@realm" in prompt.call_args.args[0], "stored": ring.get_password("realm", "ada"), "value": list(value)}


def http_password_mgr_clear(ctx):
    ring = _memory_class(ctx, initial={("realm", "ada"): "stored"})()
    ctx.keyring.set_keyring(ring)
    with mock.patch.object(ctx.http.getpass, "getuser", return_value="ada"):
        ctx.http.PasswordMgr().clear_password("realm", "https://example.test")
    return {"remaining": ring.get_password("realm", "ada")}


def plugin_loading(ctx):
    called = []

    class EntryPoint:
        name = "fixture"

        def load(self):
            return lambda: called.append("loaded")

        def __str__(self):
            return self.name

    with mock.patch.object(ctx.backend.metadata, "entry_points", return_value=[EntryPoint()]):
        ctx.backend._load_plugins()
    return {"called": called}


OPERATIONS = {name: value for name, value in globals().copy().items() if callable(value) and not name.startswith("_")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--dependency-site")
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.candidate_site)
    if args.dependency_site:
        sys.path.insert(1, args.dependency_site)

    import keyring
    from keyring import backend, cli, core, credentials, errors, http
    from keyring.backends import chainer, fail as fail_backend, null as null_backend
    from keyring.compat import properties

    ctx = SimpleNamespace(
        backend=backend,
        chainer=chainer,
        cli=cli,
        core=core,
        credentials=credentials,
        errors=errors,
        fail_backend=fail_backend,
        http=http,
        keyring=keyring,
        null_backend=null_backend,
        properties=properties,
    )
    request = json.loads(args.request)
    try:
        value = OPERATIONS[request["operation"]](ctx)
        response = {"ok": True, "value": value}
    except Exception as error:
        response = {"ok": False, "exception_type": type(error).__name__, "exception_message": str(error)}
    print(json.dumps(response, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
