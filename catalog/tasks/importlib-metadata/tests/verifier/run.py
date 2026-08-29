from __future__ import annotations

import json
import textwrap

from nl2repobench.verification.candidate_client import execute_script


SCENARIOS: tuple[tuple[str, str, object], ...] = (
    (
        "package.version-exports-requires",
        """
        import importlib_metadata as m
        requirements = m.requires("importlib_metadata")
        result = {
            "exports": m.__all__,
            "requires": [req for req in requirements if 'extra ==' not in req],
            "version": m.version("importlib_metadata"),
        }
        """,
        {
            "exports": [
                "Distribution",
                "DistributionFinder",
                "PackageMetadata",
                "PackageNotFoundError",
                "PackagePath",
                "MetadataNotFound",
                "SimplePath",
                "distribution",
                "distributions",
                "entry_points",
                "files",
                "metadata",
                "packages_distributions",
                "requires",
                "version",
            ],
            "requires": ["zipp>=3.20"],
            "version": "8.9.1.dev28+g9757b400e",
        },
    ),
    (
        "errors.package-not-found",
        """
        import importlib_metadata as m
        try:
            m.version("nl2repo-definitely-missing")
        except Exception as exc:
            result = {
                "args": list(exc.args),
                "message": str(exc),
                "name": exc.name,
                "type": type(exc).__name__,
            }
        """,
        {
            "args": ["nl2repo-definitely-missing"],
            "message": "No package metadata was found for nl2repo-definitely-missing",
            "name": "nl2repo-definitely-missing",
            "type": "PackageNotFoundError",
        },
    ),
    (
        "entry-point.parse",
        """
        import importlib_metadata as m
        ep = m.EntryPoint("tool", "pkg.mod:factory.run [fast, test_2]", "demo")
        result = {
            "attr": ep.attr,
            "extras": ep.extras,
            "group": ep.group,
            "module": ep.module,
            "name": ep.name,
            "repr": repr(ep),
            "value": ep.value,
        }
        """,
        {
            "attr": "factory.run",
            "extras": ["fast", "test_2"],
            "group": "demo",
            "module": "pkg.mod",
            "name": "tool",
            "repr": "EntryPoint(name='tool', value='pkg.mod:factory.run [fast, test_2]', group='demo')",
            "value": "pkg.mod:factory.run [fast, test_2]",
        },
    ),
    (
        "entry-point.invalid-reference",
        """
        import importlib_metadata as m
        try:
            m.EntryPoint("bad", "not-valid!", "demo")
        except Exception as exc:
            result = {"args": list(exc.args), "type": type(exc).__name__}
        """,
        {
            "args": [
                "Invalid object reference. See https://packaging.python.org/en/latest/specifications/entry-points/#data-model",
                "not-valid!",
            ],
            "type": "ValueError",
        },
    ),
    (
        "entry-point.value-semantics",
        """
        import importlib_metadata as m
        a = m.EntryPoint("a", "json:loads", "g")
        b = m.EntryPoint("b", "json:dumps", "g")
        same = m.EntryPoint("a", "json:loads", "g")
        try:
            a.name = "changed"
        except Exception as exc:
            immutable = type(exc).__name__
        result = {
            "equal": a == same,
            "hash_equal": hash(a) == hash(same),
            "immutable": immutable,
            "sorted": [ep.name for ep in sorted([b, a])],
        }
        """,
        {
            "equal": True,
            "hash_equal": True,
            "immutable": "AttributeError",
            "sorted": ["a", "b"],
        },
    ),
    (
        "entry-point.load",
        """
        import importlib_metadata as m
        ep = m.EntryPoint("decode", "json:loads", "demo")
        loaded = ep.load()
        result = {"call": loaded('{"answer": 42}'), "name": loaded.__name__}
        """,
        {"call": {"answer": 42}, "name": "loads"},
    ),
    (
        "entry-points.select-index",
        """
        import importlib_metadata as m
        eps = m.EntryPoints([
            m.EntryPoint("alpha", "json:loads", "one"),
            m.EntryPoint("beta", "json:dumps", "one"),
            m.EntryPoint("alpha", "pathlib:Path", "two"),
        ])
        try:
            eps["missing"]
        except Exception as exc:
            missing = type(exc).__name__
        result = {
            "by_group": [ep.name for ep in eps.select(group="one")],
            "by_name": [ep.group for ep in eps.select(name="alpha")],
            "groups": sorted(eps.groups),
            "lookup": eps["beta"].value,
            "missing": missing,
            "names": sorted(eps.names),
            "repr_prefix": repr(eps).startswith("EntryPoints(("),
        }
        """,
        {
            "by_group": ["alpha", "beta"],
            "by_name": ["one", "two"],
            "groups": ["one", "two"],
            "lookup": "json:dumps",
            "missing": "KeyError",
            "names": ["alpha", "beta"],
            "repr_prefix": True,
        },
    ),
    (
        "distribution.metadata",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "Demo_Pkg-1.2.dist-info")
            info.mkdir()
            info.joinpath("METADATA").write_text(
                "Metadata-Version: 2.4\\nName: Demo-Pkg\\nVersion: 1.2\\nSummary: demo summary\\n\\nbody\\n",
                encoding="utf-8",
            )
            dist = m.Distribution.at(info)
            result = {
                "metadata_version": dist.metadata["Metadata-Version"],
                "name": dist.name,
                "summary": dist.metadata["Summary"],
                "version": dist.version,
            }
        """,
        {
            "metadata_version": "2.4",
            "name": "Demo-Pkg",
            "summary": "demo summary",
            "version": "1.2",
        },
    ),
    (
        "distribution.metadata-json",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "demo-1.dist-info")
            info.mkdir()
            info.joinpath("METADATA").write_text(
                "Metadata-Version: 2.4\\nName: demo\\nVersion: 1\\nProject-URL: Home, https://example.invalid\\nProject-URL: Docs, https://docs.invalid\\nKeywords: One, Two\\n\\nLong body\\n",
                encoding="utf-8",
            )
            data = m.Distribution.at(info).metadata.json
            result = {
                "description": data["description"],
                "keywords": data["keywords"],
                "name": data["name"],
                "project_url": data["project_url"],
            }
        """,
        {
            "description": "Long body\n",
            "keywords": ["One,", "Two"],
            "name": "demo",
            "project_url": [
                "Home, https://example.invalid",
                "Docs, https://docs.invalid",
            ],
        },
    ),
    (
        "distribution.requires-dist-info",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "demo-1.dist-info")
            info.mkdir()
            info.joinpath("METADATA").write_text(
                "Metadata-Version: 2.4\\nName: demo\\nVersion: 1\\nRequires-Dist: one>=1\\nRequires-Dist: two; python_version >= '3.10'\\n\\n",
                encoding="utf-8",
            )
            result = m.Distribution.at(info).requires
        """,
        ["one>=1", "two; python_version >= '3.10'"],
    ),
    (
        "distribution.entry-points",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "demo-1.dist-info")
            info.mkdir()
            info.joinpath("METADATA").write_text("Name: demo\\nVersion: 1\\n\\n", encoding="utf-8")
            info.joinpath("entry_points.txt").write_text(
                "[console_scripts]\\nhello = json:loads\\n\\n[demo.plugins]\\nplug = pathlib:Path [x]\\n",
                encoding="utf-8",
            )
            dist = m.Distribution.at(info)
            eps = dist.entry_points
            result = [
                {"dist": ep.dist.name, "extras": ep.extras, "group": ep.group, "name": ep.name, "value": ep.value}
                for ep in eps
            ]
        """,
        [
            {
                "dist": "demo",
                "extras": [],
                "group": "console_scripts",
                "name": "hello",
                "value": "json:loads",
            },
            {
                "dist": "demo",
                "extras": ["x"],
                "group": "demo.plugins",
                "name": "plug",
                "value": "pathlib:Path [x]",
            },
        ],
    ),
    (
        "distribution.files-record",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            info = root / "demo-1.dist-info"
            info.mkdir()
            (root / "demo.py").write_text("value = 7\\n", encoding="utf-8")
            info.joinpath("METADATA").write_text("Name: demo\\nVersion: 1\\n\\n", encoding="utf-8")
            info.joinpath("RECORD").write_text(
                "demo.py,sha256=abc,10\\ndemo-1.dist-info/METADATA,,\\n",
                encoding="utf-8",
            )
            files = m.Distribution.at(info).files
            result = [
                {
                    "hash": None if item.hash is None else [item.hash.mode, item.hash.value, repr(item.hash)],
                    "path": str(item),
                    "size": item.size,
                    "text": item.read_text() if str(item) == "demo.py" else None,
                }
                for item in files
            ]
        """,
        [
            {
                "hash": ["sha256", "abc", "<FileHash mode: sha256 value: abc>"],
                "path": "demo.py",
                "size": 10,
                "text": "value = 7\n",
            },
            {
                "hash": None,
                "path": "demo-1.dist-info/METADATA",
                "size": None,
                "text": None,
            },
        ],
    ),
    (
        "distribution.files-skip-missing",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            info = root / "demo-1.dist-info"
            info.mkdir()
            info.joinpath("METADATA").write_text("Name: demo\\nVersion: 1\\n\\n", encoding="utf-8")
            info.joinpath("RECORD").write_text("missing.py,,\\ndemo-1.dist-info/METADATA,,\\n", encoding="utf-8")
            result = [str(item) for item in m.Distribution.at(info).files]
        """,
        ["demo-1.dist-info/METADATA"],
    ),
    (
        "distribution.files-none",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "demo-1.dist-info")
            info.mkdir()
            info.joinpath("METADATA").write_text("Name: demo\\nVersion: 1\\n\\n", encoding="utf-8")
            result = m.Distribution.at(info).files
        """,
        None,
    ),
    (
        "distribution.direct-url-origin",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "demo-1.dist-info")
            info.mkdir()
            info.joinpath("METADATA").write_text("Name: demo\\nVersion: 1\\n\\n", encoding="utf-8")
            info.joinpath("direct_url.json").write_text(
                '{"url":"https://example.invalid/repo","vcs_info":{"commit_id":"abc","vcs":"git"}}',
                encoding="utf-8",
            )
            origin = m.Distribution.at(info).origin
            result = {"commit": origin.vcs_info.commit_id, "url": origin.url, "vcs": origin.vcs_info.vcs}
        """,
        {"commit": "abc", "url": "https://example.invalid/repo", "vcs": "git"},
    ),
    (
        "distribution.missing-metadata",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "demo-1.dist-info")
            info.mkdir()
            try:
                m.Distribution.at(info).metadata
            except Exception as exc:
                result = {"message": str(exc), "type": type(exc).__name__}
        """,
        {"message": "No package metadata was found.", "type": "MetadataNotFound"},
    ),
    (
        "discovery.normalized-name",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            info = root / "My.Pkg_Name-2.0.dist-info"
            info.mkdir()
            info.joinpath("METADATA").write_text("Name: My.Pkg-Name\\nVersion: 2.0\\n\\n", encoding="utf-8")
            result = {
                query: [dist.version for dist in m.Distribution.discover(name=query, path=[root])]
                for query in ["my-pkg-name", "MY.PKG_NAME", "my__pkg--name"]
            }
        """,
        {
            "MY.PKG_NAME": ["2.0"],
            "my-pkg-name": ["2.0"],
            "my__pkg--name": ["2.0"],
        },
    ),
    (
        "discovery.prefix-not-matched",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            for stem, name in [("foo-1.dist-info", "foo"), ("foobar-2.dist-info", "foobar")]:
                info = root / stem
                info.mkdir()
                info.joinpath("METADATA").write_text(f"Name: {name}\\nVersion: 1\\n\\n", encoding="utf-8")
            result = [dist.name for dist in m.Distribution.discover(name="foo", path=[root])]
        """,
        ["foo"],
    ),
    (
        "discovery.context-contract",
        """
        import importlib_metadata as m
        context = m.DistributionFinder.Context(name="demo", path=["a", "b"], realm="private")
        try:
            list(m.Distribution.discover(context=context, name="other"))
        except Exception as exc:
            invalid = [type(exc).__name__, str(exc)]
        result = {
            "invalid": invalid,
            "name": context.name,
            "path": context.path,
            "realm": context.realm,
        }
        """,
        {
            "invalid": ["ValueError", "cannot accept context and kwargs"],
            "name": "demo",
            "path": ["a", "b"],
            "realm": "private",
        },
    ),
    (
        "egg-info.requires-sections",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "demo.egg-info")
            info.mkdir()
            info.joinpath("PKG-INFO").write_text("Name: demo\\nVersion: 1\\n\\n", encoding="utf-8")
            info.joinpath("requires.txt").write_text(
                "base>=1\\n\\n[extra]\\noptional\\n\\n[:python_version < '3.13']\\nconditional\\n\\n[feature:sys_platform == 'linux']\\nboth\\n",
                encoding="utf-8",
            )
            result = m.Distribution.at(info).requires
        """,
        [
            "base>=1",
            'optional; extra == "extra"',
            "conditional; python_version < '3.13'",
            'both; (sys_platform == \'linux\') and extra == "feature"',
        ],
    ),
    (
        "egg-info.versionless",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "Demo_Pkg.egg-info")
            info.mkdir()
            info.joinpath("PKG-INFO").write_text("Name: Demo-Pkg\\nVersion: 4.5\\n\\n", encoding="utf-8")
            result = [dist.version for dist in m.Distribution.discover(name="demo-pkg", path=[pathlib.Path(td)])]
        """,
        ["4.5"],
    ),
    (
        "packages-distributions.declared",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            info = root / "Demo-1.dist-info"
            info.mkdir()
            info.joinpath("METADATA").write_text("Name: Demo-Dist\\nVersion: 1\\n\\n", encoding="utf-8")
            info.joinpath("top_level.txt").write_text("alpha\\nbeta\\n", encoding="utf-8")
            dist = m.Distribution.at(info)
            m.distributions = lambda: [dist]
            result = m.packages_distributions()
        """,
        {"alpha": ["Demo-Dist"], "beta": ["Demo-Dist"]},
    ),
    (
        "packages-distributions.inferred",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            info = root / "Demo-1.dist-info"
            info.mkdir()
            (root / "solo.py").write_text("", encoding="utf-8")
            (root / "pkg").mkdir()
            (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
            info.joinpath("METADATA").write_text("Name: Demo-Dist\\nVersion: 1\\n\\n", encoding="utf-8")
            info.joinpath("RECORD").write_text("solo.py,,\\npkg/__init__.py,,\\nDemo-1.dist-info/METADATA,,\\n", encoding="utf-8")
            dist = m.Distribution.at(info)
            m.distributions = lambda: [dist]
            result = m.packages_distributions()
        """,
        {"pkg": ["Demo-Dist"], "solo": ["Demo-Dist"]},
    ),
    (
        "zip.distribution",
        """
        import importlib_metadata as m
        import pathlib, tempfile, zipfile
        with tempfile.TemporaryDirectory() as td:
            archive = pathlib.Path(td, "packages.zip")
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("zipdemo-3.4.dist-info/METADATA", "Name: zipdemo\\nVersion: 3.4\\nRequires-Dist: zipp>=3\\n\\n")
                zf.writestr("zipdemo-3.4.dist-info/entry_points.txt", "[demo]\\nitem = json:loads\\n")
                zf.writestr("zipdemo.py", "value = 9\\n")
                zf.writestr("zipdemo-3.4.dist-info/RECORD", "zipdemo.py,,10\\n")
            dist = next(iter(m.Distribution.discover(name="zipdemo", path=[archive])))
            result = {
                "entry": dist.entry_points["item"].value,
                "file": dist.files[0].read_text(),
                "name": dist.name,
                "requires": dist.requires,
                "version": dist.version,
            }
        """,
        {
            "entry": "json:loads",
            "file": "value = 9\n",
            "name": "zipdemo",
            "requires": ["zipp>=3"],
            "version": "3.4",
        },
    ),
    (
        "zip.case-insensitive-name",
        """
        import importlib_metadata as m
        import pathlib, tempfile, zipfile
        with tempfile.TemporaryDirectory() as td:
            archive = pathlib.Path(td, "packages.zip")
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("Mixed_Name-1.0.dist-info/METADATA", "Name: Mixed-Name\\nVersion: 1.0\\n\\n")
            result = [dist.name for dist in m.Distribution.discover(name="mixed-name", path=[archive])]
        """,
        ["Mixed-Name"],
    ),
    (
        "discovery.invalidate-caches",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            before = list(m.Distribution.discover(name="late", path=[root]))
            info = root / "late-1.dist-info"
            info.mkdir()
            info.joinpath("METADATA").write_text("Name: late\\nVersion: 1\\n\\n", encoding="utf-8")
            m.MetadataPathFinder.invalidate_caches()
            after = [dist.version for dist in m.Distribution.discover(name="late", path=[root])]
            result = {"after": after, "before": len(before)}
        """,
        {"after": ["1"], "before": 0},
    ),
    (
        "distribution.abc-enforced",
        """
        import importlib_metadata as m
        try:
            m.Distribution()
        except Exception as exc:
            result = {"contains": "abstract", "message_has_abstract": "abstract" in str(exc), "type": type(exc).__name__}
        """,
        {"contains": "abstract", "message_has_abstract": True, "type": "TypeError"},
    ),
    (
        "entry-point.disallow-dist-match",
        """
        import importlib_metadata as m
        ep = m.EntryPoint("item", "json:loads", "demo")
        try:
            ep.matches(dist="anything")
        except Exception as exc:
            result = {"message": str(exc), "type": type(exc).__name__}
        """,
        {
            "message": '"dist" is not suitable for matching. Instead, use Distribution.entry_points.select() on a located distribution.',
            "type": "ValueError",
        },
    ),
    (
        "entry-points.global-filter",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            info = root / "demo-1.dist-info"
            info.mkdir()
            info.joinpath("METADATA").write_text("Name: demo\\nVersion: 1\\n\\n", encoding="utf-8")
            info.joinpath("entry_points.txt").write_text("[one]\\na = json:loads\\nb = json:dumps\\n[two]\\na = pathlib:Path\\n", encoding="utf-8")
            dist = m.Distribution.at(info)
            m.distributions = lambda: [dist]
            eps = m.entry_points(group="one", name="a")
            result = [[ep.name, ep.value, ep.group] for ep in eps]
        """,
        [["a", "json:loads", "one"]],
    ),
    (
        "distribution.at-string-path",
        """
        import importlib_metadata as m
        import pathlib, tempfile
        with tempfile.TemporaryDirectory() as td:
            info = pathlib.Path(td, "demo-1.dist-info")
            info.mkdir()
            info.joinpath("METADATA").write_text("Name: demo\\nVersion: 1\\n\\n", encoding="utf-8")
            dist = m.Distribution.at(str(info))
            result = {"name": dist.name, "path_type": type(dist._path).__name__, "version": dist.version}
        """,
        {"name": "demo", "path_type": "PosixPath", "version": "1"},
    ),
)


def main() -> None:
    leaves: list[dict[str, str]] = []
    for leaf_id, source, expected in SCENARIOS:
        response = execute_script(textwrap.dedent(source), timeout_sec=12.0)
        if response.ok and response.value == expected:
            leaves.append({"id": leaf_id, "status": "passed"})
            continue
        observed = response.value if response.ok else {
            "exception_message": response.exception_message,
            "exception_type": response.exception_type,
        }
        message = f"expected={expected!r}; observed={observed!r}"[:2000]
        leaves.append({"id": leaf_id, "message": message, "status": "failed"})

    print(json.dumps({"leaves": leaves, "schema_version": "1.0"}, sort_keys=True))


if __name__ == "__main__":
    main()
