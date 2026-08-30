from __future__ import annotations

import json
from typing import Callable

from nl2repobench.verification.candidate_client import (
    CandidateCallResult,
    execute_script,
    metadata_requires,
    run_console,
    run_module,
)


leaves: list[dict[str, str]] = []


def record(leaf_id: str, passed: bool, message: str = "") -> None:
    leaf = {"id": leaf_id, "status": "passed" if passed else "failed"}
    if not passed:
        leaf["message"] = message[-1000:] or "contract mismatch"
    leaves.append(leaf)


def script_check(leaf_id: str, source: str) -> None:
    observed = execute_script(source, timeout_sec=2.0)
    record(
        leaf_id,
        observed.ok and observed.value is True,
        observed.exception_message or repr(observed.value),
    )


SCRIPTS = {
    "distribution-metadata": """
import importlib.metadata as metadata
d = metadata.distribution("trove-classifiers")
entries = [(ep.group, ep.name, ep.value) for ep in d.entry_points]
result = (
    d.metadata["Name"] == "trove-classifiers"
    and d.version == "2026.6.1.19"
    and entries.count(("console_scripts", "trove-classifiers", "trove_classifiers.__main__:cli")) == 1
)
""",
    "package-import-and-exports": """
import trove_classifiers as tc
result = tc.__all__ == [
    "all_classifiers", "classifiers", "deprecated_classifiers", "sorted_classifiers"
]
""",
    "exported-container-types": """
import trove_classifiers as tc
result = (
    type(tc.sorted_classifiers) is list
    and type(tc.classifiers) is set
    and type(tc.deprecated_classifiers) is dict
    and type(tc.all_classifiers) is list
)
""",
    "typing-marker": """
from importlib.resources import files
result = files("trove_classifiers").joinpath("py.typed").is_file()
""",
    "core-counts": """
import trove_classifiers as tc
result = (
    len(tc.sorted_classifiers) == 895
    and len(tc.classifiers) == 895
    and len(tc.deprecated_classifiers) == 8
    and len(tc.all_classifiers) == 903
)
""",
    "set-list-relationship": """
import trove_classifiers as tc
result = tc.classifiers == set(tc.sorted_classifiers)
""",
    "all-classifier-relationship": """
import trove_classifiers as tc
result = tc.all_classifiers == sorted(
    tc.sorted_classifiers + list(tc.deprecated_classifiers)
)
""",
    "unique-valid-classifiers": """
import trove_classifiers as tc
result = len(tc.sorted_classifiers) == len(set(tc.sorted_classifiers))
""",
    "root-families": """
import trove_classifiers as tc
roots = {value.split(" :: ", 1)[0] for value in tc.sorted_classifiers}
result = roots == {
    "Development Status", "Environment", "Framework", "Intended Audience",
    "License", "Natural Language", "Operating System", "Programming Language",
    "Topic", "Typing",
}
""",
    "root-counts": """
from collections import Counter
import trove_classifiers as tc
counts = Counter(value.split(" :: ", 1)[0] for value in tc.sorted_classifiers)
result = counts == {
    "Development Status": 7, "Environment": 74, "Framework": 185,
    "Intended Audience": 14, "License": 84, "Natural Language": 64,
    "Operating System": 43, "Programming Language": 102, "Topic": 320,
    "Typing": 2,
}
""",
    "classifier-grammar": """
import trove_classifiers as tc
def valid(value):
    parts = value.split(" :: ")
    return (
        len(parts) >= 2
        and all(part and part.strip() == part for part in parts)
        and all(":" not in part for part in parts)
        and all(not part.casefold().startswith("private") for part in parts)
    )
result = all(type(value) is str and valid(value) for value in tc.sorted_classifiers)
""",
    "parent-closure": """
import trove_classifiers as tc
values = set(tc.sorted_classifiers)
result = all(
    " :: ".join(parts[:depth]) in values
    for value in values
    for parts in [value.split(" :: ")]
    for depth in range(2, len(parts))
)
""",
    "development-status-family": """
import trove_classifiers as tc
result = [x for x in tc.sorted_classifiers if x.startswith("Development Status :: ")] == [
    "Development Status :: 1 - Planning",
    "Development Status :: 2 - Pre-Alpha",
    "Development Status :: 3 - Alpha",
    "Development Status :: 4 - Beta",
    "Development Status :: 5 - Production/Stable",
    "Development Status :: 6 - Mature",
    "Development Status :: 7 - Inactive",
]
""",
    "environment-samples": """
import trove_classifiers as tc
required = {
    "Environment :: Console", "Environment :: GPU :: NVIDIA CUDA :: 4.1",
    "Environment :: GPU :: NVIDIA CUDA :: 11.3", "Environment :: MacOS X :: Carbon",
    "Environment :: X11 Applications :: Qt", "Environment :: Cygwin (MS Windows)",
}
result = required <= tc.classifiers
""",
    "framework-samples": """
import trove_classifiers as tc
required = {
    "Framework :: AWS CDK", "Framework :: Django :: 5", "Framework :: MkDocs",
    "Framework :: Pycsou", "Framework :: tox", "Framework :: Litestar",
}
result = required <= tc.classifiers
""",
    "intended-audience-samples": """
import trove_classifiers as tc
required = {
    "Intended Audience :: Customer Service", "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Legal Industry", "Intended Audience :: Religion",
    "Intended Audience :: Telecommunications Industry",
}
result = required <= tc.classifiers
""",
    "license-samples": """
import trove_classifiers as tc
required = {
    "License :: Aladdin Free Public License (AFPL)",
    "License :: OSI Approved :: Attribution Assurance License",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "License :: OSI Approved :: Open Group Test Suite License",
    "License :: Repoze Public License",
}
result = required <= tc.classifiers
""",
    "natural-language-samples": """
import trove_classifiers as tc
required = {
    "Natural Language :: Afrikaans", "Natural Language :: English",
    "Natural Language :: Japanese", "Natural Language :: Romanian",
    "Natural Language :: Yiddish", "Natural Language :: Ukrainian",
}
result = required <= tc.classifiers
""",
    "operating-system-samples": """
import trove_classifiers as tc
required = {
    "Operating System :: Android", "Operating System :: Microsoft :: Windows :: Windows 8",
    "Operating System :: OS Independent", "Operating System :: POSIX :: GNU Hurd",
    "Operating System :: iOS",
}
result = required <= tc.classifiers
""",
    "programming-language-samples": """
import trove_classifiers as tc
required = {
    "Programming Language :: APL", "Programming Language :: Java",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: Free Threading :: 3 - Stable",
    "Programming Language :: Zope",
}
result = required <= tc.classifiers
""",
    "topic-samples": """
import trove_classifiers as tc
required = {
    "Topic :: Adaptive Technologies", "Topic :: File Formats :: JSON :: JSON Schema",
    "Topic :: Office/Business :: Financial :: Spreadsheet",
    "Topic :: Software Development :: Widget Sets", "Topic :: Utilities",
}
result = required <= tc.classifiers
""",
    "typing-family": """
import trove_classifiers as tc
result = [x for x in tc.sorted_classifiers if x.startswith("Typing :: ")] == [
    "Typing :: Stubs Only", "Typing :: Typed"
]
""",
    "revision-additions": """
import trove_classifiers as tc
required = {
    "Framework :: Django :: 6.1", "Framework :: Django CMS :: 5.1",
    "Framework :: Plone :: 6.3", "Framework :: Wagtail :: 8",
    "Framework :: Litestar :: 1", "Framework :: Litestar :: 2",
    "Framework :: Litestar :: 3", "Programming Language :: Python :: 3.16",
    "Topic :: Scientific/Engineering :: Instrument Drivers :: IVI Conformant",
}
result = required <= tc.classifiers
""",
    "python-natural-order": """
import trove_classifiers as tc
expected = [f"Programming Language :: Python :: 3.{minor}" for minor in range(8, 17)]
indices = [tc.sorted_classifiers.index(value) for value in expected]
result = indices == list(range(indices[0], indices[0] + len(expected)))
""",
    "order-boundaries": """
import trove_classifiers as tc
result = (
    tc.sorted_classifiers[:2] == [
        "Development Status :: 1 - Planning", "Development Status :: 2 - Pre-Alpha"
    ]
    and tc.sorted_classifiers[-2:] == ["Typing :: Stubs Only", "Typing :: Typed"]
)
""",
    "deprecated-map": """
import trove_classifiers as tc
result = tc.deprecated_classifiers == {
    "Framework :: Django CMS :: 4.2": ["Framework :: Django CMS :: 5.0"],
    "License :: OSI Approved :: Intel Open Source License": [],
    "License :: OSI Approved :: Jabber Open Source License": [],
    "License :: OSI Approved :: MITRE Collaborative Virtual Workspace License (CVW)": [],
    "License :: OSI Approved :: Sun Industry Standards Source License (SISSL)": [],
    "License :: OSI Approved :: X.Net License": [],
    "Natural Language :: Ukranian": ["Natural Language :: Ukrainian"],
    "Topic :: Communications :: Chat :: AOL Instant Messenger": [],
}
""",
    "deprecated-disjoint": """
import trove_classifiers as tc
result = set(tc.deprecated_classifiers).isdisjoint(tc.classifiers)
""",
    "deprecated-replacements": """
import trove_classifiers as tc
result = all(
    replacement in tc.classifiers
    for replacements in tc.deprecated_classifiers.values()
    for replacement in replacements
)
""",
    "positive-membership": """
import trove_classifiers as tc
result = all(value in tc.classifiers for value in [
    "License :: OSI Approved", "Programming Language :: Python :: 3",
    "Framework :: Django", "Topic :: Software Development", "Typing :: Typed",
])
""",
    "negative-membership": """
import trove_classifiers as tc
result = all(value not in tc.classifiers for value in [
    "Fuzzy :: Wuzzy :: Was :: A :: Bear", "Natural Language :: Ukranian",
    "Framework :: Django CMS :: 4.2", "Private :: Internal", "Programming Language :: Python :: 99",
])
""",
    "mutable-containers": """
import trove_classifiers as tc
tc.sorted_classifiers.append("Example :: List")
tc.classifiers.add("Example :: Set")
tc.deprecated_classifiers["Example :: Old"] = ["Example :: New"]
tc.all_classifiers.append("Example :: All")
result = (
    tc.sorted_classifiers[-1] == "Example :: List"
    and "Example :: Set" in tc.classifiers
    and tc.deprecated_classifiers["Example :: Old"] == ["Example :: New"]
    and tc.all_classifiers[-1] == "Example :: All"
)
""",
    "cli-function": """
import contextlib
import io
import trove_classifiers as tc
from trove_classifiers.__main__ import cli
stream = io.StringIO()
with contextlib.redirect_stdout(stream):
    returned = cli()
result = returned is None and stream.getvalue().splitlines() == tc.sorted_classifiers
""",
}


for leaf_id, source in SCRIPTS.items():
    script_check(leaf_id, source)


requires: CandidateCallResult = metadata_requires("trove-classifiers")
record(
    "runtime-dependencies",
    requires.ok and requires.value in (None, []),
    requires.exception_message or repr(requires.value),
)


def check_cli(
    leaf_id: str,
    invoke: Callable[[], object],
) -> None:
    expected = execute_script(
        "import trove_classifiers as tc\nresult = tc.sorted_classifiers",
        timeout_sec=2.0,
    )
    completed = invoke()
    output = completed.stdout.splitlines()
    ok = (
        expected.ok
        and completed.returncode == 0
        and completed.stderr == ""
        and completed.stdout.endswith("\n")
        and output == expected.value
    )
    record(
        leaf_id,
        ok,
        f"returncode={completed.returncode} stderr={completed.stderr[-300:]!r} "
        f"lines={len(output)} expected_ok={expected.ok}",
    )


check_cli("module-cli-output", lambda: run_module("trove_classifiers", []))
check_cli("console-cli-output", lambda: run_console("trove-classifiers", []))

print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
