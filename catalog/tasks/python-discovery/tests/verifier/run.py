from __future__ import annotations

import json
from typing import Any, Callable

from nl2repobench.verification.candidate_client import CandidateCallResult, execute_script


def _check(
    leaves: list[dict[str, str]],
    leaf_id: str,
    source: str,
    expected: Any = None,
    predicate: Callable[[Any], bool] | None = None,
) -> None:
    observed: CandidateCallResult = execute_script(source, timeout_sec=12.0)
    if not observed.ok:
        leaves.append({"id": leaf_id, "status": "failed", "message": observed.exception_message or "candidate error"})
        return
    value = observed.value
    passed = predicate(value) if predicate is not None else value == expected
    leaves.append({"id": leaf_id, "status": "passed" if passed else "failed", "message": repr(value)})


def main() -> None:
    leaves: list[dict[str, str]] = []
    _check(
        leaves,
        "exports",
        """
import python_discovery as p
from python_discovery._cache import NoOpCache
from python_discovery._py_info import VersionInfo
expected = {'KNOWN_ARCHITECTURES', 'KNOWN_IMPLEMENTATIONS', 'ContentStore', 'DiskCache', 'PyInfoCache', 'PythonInfo', 'PythonSpec', 'SimpleSpecifier', 'SimpleSpecifierSet', 'SimpleVersion', '__version__', 'get_interpreter', 'iter_interpreters', 'normalize_isa'}
result = expected.issubset(set(p.__all__)) and p.__version__ and isinstance(NoOpCache().py_info(None), object) and VersionInfo(3, 12, 0, 'final', 0).major == 3
""",
        predicate=bool,
    )
    _check(
        leaves,
        "isa-normalization",
        """
from python_discovery import normalize_isa
result = [normalize_isa(x) for x in ('amd64', 'aarch64', 'i686', 'powerpc64le', 'sparcv9', 'Alpha')]
""",
        ["x86_64", "arm64", "x86", "ppc64le", "sparc64", "alpha"],
    )
    _check(
        leaves,
        "version-value-semantics",
        """
from python_discovery._specifier import SimpleVersion
a = SimpleVersion.from_string('3.12.11')
result = [str(a), repr(a), a.release, SimpleVersion.from_string('3.12a1') < a, a >= SimpleVersion.from_string('3.12')]
""",
        ["3.12.11", "SimpleVersion('3.12.11')", [3, 12, 11], True, True],
    )
    _check(
        leaves,
        "version-invalid",
        """
from python_discovery._specifier import SimpleVersion
try:
    SimpleVersion.from_string('not-a-version')
except ValueError as exc:
    result = type(exc).__name__
else:
    result = 'accepted'
""",
        "ValueError",
    )
    _check(
        leaves,
        "version-equality-hash",
        """
from python_discovery._specifier import SimpleVersion
a = SimpleVersion.from_string('3.12')
b = SimpleVersion.from_string('3.12')
result = [a == b, hash(a) == hash(b), a != SimpleVersion.from_string('3.12.1')]
""",
        [True, True, True],
    )
    _check(
        leaves,
        "specifier-operators",
        """
from python_discovery._specifier import SimpleSpecifier
result = [SimpleSpecifier.from_string(x).contains('3.12.11') for x in ('>=3.12', '<3.12', '==3.12.*', '!=3.11.*', '~=3.12', '===3.12.11')]
""",
        [True, False, True, True, True, True],
    )
    _check(
        leaves,
        "specifier-set",
        """
from python_discovery._specifier import SimpleSpecifierSet
s = SimpleSpecifierSet.from_string('>=3.10,<4')
result = [s.contains('3.12.11'), s.contains('4.0'), list(map(str, s)), repr(s)]
""",
        [True, False, [">=3.10", "<4"], "SimpleSpecifierSet('>=3.10,<4')"],
    )
    _check(
        leaves,
        "specifier-malformed-items",
        """
from python_discovery._specifier import SimpleSpecifierSet
filtered = SimpleSpecifierSet.from_string('>=3.10,bad,<4,,')
empty = SimpleSpecifierSet.from_string('bad')
result = [list(map(str, filtered)), filtered.contains('3.12'), filtered.contains('4.0'), empty.contains('3.12')]
""",
        [[">=3.10", "<4"], True, False, True],
    )
    _check(
        leaves,
        "spec-parsing",
        """
from python_discovery import PythonSpec
items = [PythonSpec.from_string_spec(x) for x in ('3.12.11', 'cpython3.12t', 'python>=3.12', '3.12-64-x86_64', 'graalvm3')]
result = [(x.implementation, x.major, x.minor, x.micro, x.architecture, x.machine, x.free_threaded) for x in items]
""",
        [[None, 3, 12, 11, None, None, False], ["cpython", 3, 12, None, None, None, True], [None, None, None, None, None, None, None], [None, 3, 12, None, 64, "x86_64", False], ["graalpy", 3, None, None, None, None, False]],
    )
    _check(
        leaves,
        "spec-versionifier",
        """
from python_discovery import PythonSpec
q = PythonSpec.from_string_spec('python>=3.12')
result = [q.version_specifier.contains('3.12.11'), q.version_specifier.contains('2.7'), repr(q)]
""",
        [True, False, "PythonSpec(version_specifier=>=3.12)"],
    )
    _check(
        leaves,
        "spec-regex",
        """
from python_discovery import PythonSpec
regex = PythonSpec.from_string_spec('3.12').generate_re(windows=False)
result = [bool(regex.fullmatch(x)) for x in ('python3.12', 'python3.13', 'cpython3.12', 'python3.12t')]
""",
        [True, False, False, False],
    )
    _check(
        leaves,
        "spec-satisfies",
        """
from python_discovery import PythonSpec
result = [PythonSpec.from_string_spec(a).satisfies(PythonSpec.from_string_spec(b)) for a, b in (('3.12.11', '3.12'), ('3.12.11', '3.13'), ('cpython3.12', 'python3.12'), ('3.12-64-x86_64', '3.12-32-x86_64'))]
""",
        [True, False, True, False],
    )
    _check(
        leaves,
        "python-info-properties",
        """
import python_discovery
info = python_discovery.PythonInfo.current()
result = [info.implementation, info.version_info.major, info.version_info.minor, info.version_str, info.version_release_str, info.python_name, info.architecture, info.machine, info.is_venv, info.is_old_virtualenv, info.has_venv]
""",
        predicate=lambda x: isinstance(x, list) and x[0] == "CPython" and x[1:3] == [3, 12] and x[3].startswith("3.12.") and x[4] == "3.12" and x[5] == "python3.12" and x[6] == 64 and x[7] == "x86_64" and isinstance(x[8], bool) and x[9] is False and isinstance(x[10], bool),
    )
    _check(
        leaves,
        "python-info-roundtrip",
        """
import python_discovery
info = python_discovery.PythonInfo.current()
restored = python_discovery.PythonInfo.from_json(info.to_json())
result = [restored.to_dict() == info.to_dict(), restored.spec == info.spec, isinstance(restored.version_info, tuple)]
""",
        [True, True, True],
    )
    _check(
        leaves,
        "python-info-from-exe",
        """
import sys
from python_discovery import PythonInfo
info = PythonInfo.from_exe(sys.executable, resolve_to_host=False)
result = [info is not None, info.version_info.major if info else 0, info.version_info.minor if info else 0, info.executable == sys.executable if info else False]
""",
        [True, 3, 12, True],
    )
    _check(
        leaves,
        "python-info-satisfies",
        """
from python_discovery import PythonInfo, PythonSpec
info = PythonInfo.current()
result = [info.satisfies(PythonSpec.from_string_spec('3.12'), impl_must_match=False), info.satisfies(PythonSpec.from_string_spec('3.13'), impl_must_match=False), info.satisfies(PythonSpec.from_string_spec('3.12-x86_64'), impl_must_match=False)]
""",
        [True, False, True],
    )
    _check(
        leaves,
        "python-info-paths",
        """
from python_discovery import PythonInfo
info = PythonInfo.current()
result = [bool(info.system_prefix), bool(info.system_exec_prefix), bool(info.sysconfig_path('purelib')), info.sysconfig_path('missing') == '']
""",
        [True, True, True, True],
    )
    _check(
        leaves,
        "disk-cache",
        """
from pathlib import Path
from tempfile import TemporaryDirectory
from python_discovery import DiskCache
with TemporaryDirectory() as d:
    store = DiskCache(Path(d)).py_info(Path('/usr/bin/python3'))
    before = [store.exists(), store.read()]
    store.write({'x': 1})
    after = [store.exists(), store.read()]
    store.remove()
    result = [before, after, store.exists()]
""",
        [[False, None], [True, {"x": 1}], False],
    )
    _check(
        leaves,
        "disk-cache-corrupt",
        """
from pathlib import Path
from tempfile import TemporaryDirectory
from python_discovery import DiskCache
with TemporaryDirectory() as d:
    store = DiskCache(Path(d)).py_info(Path('/usr/bin/python3'))
    store._folder.mkdir(parents=True)
    store._file.write_text('{broken', encoding='utf-8')
    result = [store.read(), store._file.exists()]
""",
        [None, False],
    )
    _check(
        leaves,
        "disk-cache-key-lock",
        """
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from python_discovery import DiskCache
with TemporaryDirectory() as d:
    executable = Path('/usr/bin/python3')
    store = DiskCache(Path(d)).py_info(executable)
    with store.locked():
        locked = True
    expected = hashlib.sha256(str(executable).encode()).hexdigest() + '.json'
    result = [store._file.name == expected, store._file.parent.as_posix().endswith('/py_info/4'), locked]
""",
        [True, True, True],
    )
    _check(
        leaves,
        "noop-cache",
        """
from pathlib import Path
from python_discovery._cache import NoOpCache
store = NoOpCache().py_info(Path('/tmp/python'))
store.write({'x': 1})
result = [store.exists(), store.read()]
""",
        [False, None],
    )
    _check(
        leaves,
        "path-discovery",
        """
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from python_discovery._discovery import get_paths
with TemporaryDirectory() as d:
    root = Path(d)
    (root / 'first').mkdir()
    (root / 'second').mkdir()
    (root / 'first' / 'python').write_text('', encoding='utf-8')
    result = [x.name for x in get_paths({'PATH': os.pathsep.join([str(root / 'first'), str(root / 'second')])})]
""",
        ["first"],
    )
    _check(
        leaves,
        "path-executable-finder",
        """
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from python_discovery import PythonSpec
from python_discovery._discovery import path_exe_finder
with TemporaryDirectory() as d:
    root = Path(d)
    for name in ('python3.12', 'cpython3.12'):
        path = root / name
        path.write_text('', encoding='utf-8')
        os.chmod(path, 0o755)
    result = [(x.name, match) for x, match in path_exe_finder(PythonSpec.from_string_spec('3.12'))(root)]
""",
        [["python3.12", True]],
    )
    _check(
        leaves,
        "explicit-discovery",
        """
import sys
from python_discovery import get_interpreter
info = get_interpreter(sys.executable)
result = [info is not None, info.implementation if info else None, info.version_str if info else None]
""",
        predicate=lambda x: isinstance(x, list) and x[0:2] == [True, "CPython"] and isinstance(x[2], str) and x[2].startswith("3.12."),
    )
    _check(
        leaves,
        "specifier-discovery",
        """
from python_discovery import get_interpreter
info = get_interpreter('>=3.12')
result = [info is not None, info.version_release_str if info else None]
""",
        [True, "3.12"],
    )
    _check(
        leaves,
        "discovery-not-found",
        """
from python_discovery import get_interpreter
result = get_interpreter('99.0') is None
""",
        True,
    )
    _check(
        leaves,
        "discovery-fallback",
        """
import sys
from python_discovery import get_interpreter
info = get_interpreter(['definitely-not-an-interpreter', sys.executable])
result = info is not None and info.implementation == 'CPython'
""",
        True,
    )
    _check(
        leaves,
        "interpreter-iteration",
        """
import sys
from python_discovery import iter_interpreters
items = list(iter_interpreters(sys.executable))
result = [len(items), items[0].version_release_str if items else None, len({x.executable for x in items})]
""",
        [1, "3.12", 1],
    )
    _check(
        leaves,
        "interpreter-predicate",
        """
import sys
from python_discovery import get_interpreter
result = [get_interpreter(sys.executable, predicate=lambda _: False) is None, get_interpreter(sys.executable, predicate=lambda _: True) is not None]
""",
        [True, True],
    )
    _check(
        leaves,
        "try-first-dedup",
        """
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from python_discovery import iter_interpreters
with TemporaryDirectory() as d:
    alias = Path(d) / 'python3.12'
    alias.symlink_to(sys.executable)
    items = list(iter_interpreters('3.12', try_first_with=[str(alias), sys.executable], env={'PATH': ''}))
    result = [len(items), bool(items) and os.path.realpath(items[0].executable) == os.path.realpath(sys.executable)]
""",
        [1, True],
    )
    _check(
        leaves,
        "relative-version-spec",
        """
from python_discovery import PythonSpec
result = [PythonSpec.from_string_spec('python3').implementation is None, PythonSpec.from_string_spec('python3').major == 3, PythonSpec.from_string_spec('python3').minor is None]
""",
        [True, True, True],
    )
    _check(
        leaves,
        "public-submodules",
        """
from python_discovery import _py_info, _py_spec, _specifier
result = [hasattr(_py_info, 'PythonInfo'), hasattr(_py_spec, 'PythonSpec'), hasattr(_specifier, 'SimpleVersion')]
""",
        [True, True, True],
    )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
