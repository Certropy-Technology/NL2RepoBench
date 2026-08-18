# Python Package Candidate Discovery v1

## Scope

This is a `discover`-stage report for the next NL2RepoBench task batch. It does not modify the catalog and does not claim that any candidate is publishable. The search produced 25 package candidates and a deeper static review of 10 projects.

The existing legacy baseline contains 104 task IDs. Deduplication used normalized package names and the baseline hash `sha256:31fd544eb261f084ffca370ea02515950a8538cdf144b0fdb9052f67b5e76cc7`.

Selection favored permissive licenses, active upstream maintenance, visible tests, Python-dominant repositories, useful public API surface, and offline-freezable behavior. Network, subprocess, native-extension, packaging-backend, and large dependency risks are recorded rather than silently discarded.

## Shortlist

| Package | Repository | Category | Stars | License | Python | Last push | Status |
| --- | --- | --- | ---: | --- | ---: | --- | --- |
| attrs | [python-attrs/attrs](https://github.com/python-attrs/attrs) | data model | 5,832 | MIT | 100% | 2026-08-07 | candidate |
| pydantic | [pydantic/pydantic](https://github.com/pydantic/pydantic) | validation | 28,561 | MIT | 83% | 2026-08-17 | conditional: native `pydantic-core` |
| cattrs | [python-attrs/cattrs](https://github.com/python-attrs/cattrs) | serialization | 1,051 | MIT | 100% | 2026-08-09 | candidate |
| marshmallow | [marshmallow-code/marshmallow](https://github.com/marshmallow-code/marshmallow) | validation | 7,242 | MIT | 100% | 2026-08-14 | candidate |
| jsonschema | [python-jsonschema/jsonschema](https://github.com/python-jsonschema/jsonschema) | validation | 4,972 | MIT | 100% | 2026-08-17 | candidate, test layout audit pending |
| click | [pallets/click](https://github.com/pallets/click) | CLI | 17,626 | BSD-3-Clause | 100% | 2026-08-16 | candidate, subprocess tests |
| typer | [fastapi/typer](https://github.com/fastapi/typer) | CLI | 19,899 | MIT | 100% | 2026-08-12 | candidate |
| prompt-toolkit | [prompt-toolkit/python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) | terminal | 10,555 | BSD-3-Clause | 100% | 2026-07-26 | candidate |
| pre-commit | [pre-commit/pre-commit](https://github.com/pre-commit/pre-commit) | developer tool | 15,506 | MIT | 97% | 2026-08-17 | conditional: subprocess/tool downloads |
| pyparsing | [pyparsing/pyparsing](https://github.com/pyparsing/pyparsing) | parser | 2,484 | MIT | 97% | 2026-08-12 | candidate, large parser surface |
| lark | [lark-parser/lark](https://github.com/lark-parser/lark) | parser | 5,958 | MIT | 100% | 2026-08-13 | candidate |
| tomlkit | [python-poetry/tomlkit](https://github.com/python-poetry/tomlkit) | serialization | 842 | MIT | 100% | 2026-08-17 | candidate |
| mistune | [lepture/mistune](https://github.com/lepture/mistune) | Markdown | 3,065 | BSD-3-Clause | 100% | 2026-08-14 | candidate |
| build | [pypa/build](https://github.com/pypa/build) | packaging | 854 | MIT | 100% | 2026-08-18 | conditional: build subprocesses |
| jmespath | [jmespath/jmespath.py](https://github.com/jmespath/jmespath.py) | query | 2,452 | MIT | 100% | 2026-04-20 | candidate |
| httpx | [encode/httpx](https://github.com/encode/httpx) | HTTP client | 15,427 | BSD-3-Clause | 100% | 2026-03-29 | conditional: network-heavy tests |
| anyio | [agronholm/anyio](https://github.com/agronholm/anyio) | async | 2,530 | MIT | 100% | 2026-08-17 | conditional: backend/timing matrix |
| requests | [psf/requests](https://github.com/psf/requests) | HTTP client | 54,245 | Apache-2.0 | 99% | 2026-08-17 | conditional: deterministic transport needed |
| urllib3 | [urllib3/urllib3](https://github.com/urllib3/urllib3) | HTTP client | 4,051 | MIT | 99% | 2026-08-10 | conditional: TLS/network tests |
| platformdirs | [tox-dev/platformdirs](https://github.com/tox-dev/platformdirs) | filesystem | 968 | MIT | 100% | 2026-08-17 | candidate |
| filelock | [tox-dev/filelock](https://github.com/tox-dev/filelock) | filesystem | 975 | MIT | 100% | 2026-08-17 | conditional: large subprocess test surface |
| cachetools | [tkem/cachetools](https://github.com/tkem/cachetools) | caching | 2,776 | MIT | 100% | 2026-08-01 | candidate |
| hypothesis | [HypothesisWorks/hypothesis](https://github.com/HypothesisWorks/hypothesis) | testing | 8,894 | MPL-2.0 on PyPI; GitHub API reports NOASSERTION | 98% | 2026-08-16 | conditional: reconcile license and large test surface |
| pluggy | [pytest-dev/pluggy](https://github.com/pytest-dev/pluggy) | testing | 1,682 | MIT | 100% | 2026-08-17 | candidate |
| beartype | [beartype/beartype](https://github.com/beartype/beartype) | typing | 3,486 | MIT | 99% | 2026-08-15 | conditional: metaprogramming surface |

`markdown-it-py` was not retained in the final 25 because its GitHub language mix was only 55% Python. `pypa/build` replaced it as the packaging candidate.

## Deep Ten

Package-only SLOC and static test definitions were derived from shallow clones at the revisions below. They are ranking evidence, not frozen test denominators.

| Package | Revision | Difficulty | Source SLOC | API estimate | Test files / defs | Runtime deps | Recommendation |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| cachetools | `01af8e5b7ce44432b357e26c7d67eb7fa055ae72` | Easy | 1,261 | 18 | 14 / 132 | 0 | Strong pilot |
| jmespath | `2812594e69d43098ef60f81f4efc404c071b0418` | Easy | 1,274 | 46 | 8 / 81 | 0 | Strong pilot |
| platformdirs | `d3cf61ce5e729f2c35f830b69e14adb7b6970a00` | Medium | 2,305 | 66 | 8 / 105 | 0 | Strong pilot |
| pluggy | `d23f110b240d67ee503eba0082f30cae73f3e1e3` | Easy | 1,341 | 20 | 11 / 127 | 0 | Strong pilot |
| attrs | `c1dc5dcba16ed827aa6dcad896b41a3afedb4e32` | Hard | 5,646 | 148 | 32 / 680 | 0 | Strong pilot |
| cattrs | `f2e42f3c69dabd48dd1a5b8fb1aad9c1d39c339a` | Hard | 5,980 | 150 | 70 / 436 | 3 | Candidate after attrs closure |
| marshmallow | `c7b559a1fa3aba57ca6dba0ab336841c5038a782` | Medium | 3,937 | 87 | 19 / 652 | 2 | Strong pilot |
| tomlkit | `d8ed1e3cdb024dfc2c6f12b45a0dfd4d4d91f727` | Hard | 4,631 | 81 | 12 / 241 | 0 | Strong pilot |
| lark | `9bae96161b45a5bf70011c75b1ef41228d3f4caa` | Hard | 7,076 | 202 | 18 / 318 | 4 | Candidate after dependency freeze |
| click | `cbd7a4109da16ce58f54c2a618b4c986e3041fcf` | Hard | 9,483 | 125 | 46 / 541 | 0 | Candidate with test adapter |

License evidence was checked both in the repository LICENSE file and through the GitHub license endpoint. PyPI versions at discovery included `cachetools 7.1.7`, `jmespath 1.1.0`, `platformdirs 4.11.3`, `pluggy 1.6.0`, `attrs 26.1.0`, `cattrs 26.1.0`, `marshmallow 4.3.1`, `tomlkit 0.15.1`, `lark 1.3.1`, and `click 8.4.2`.

## Next Gate

The recommended first pilot is `cachetools`, `jmespath`, `platformdirs`, `pluggy`, and `marshmallow`, with `attrs` and `tomlkit` as larger controls. Before any candidate advances beyond `screened`:

1. Freeze the complete upstream commit, license evidence, environment, and dependency wheelhouse.
2. Adapt hidden tests to the Phase 2 subprocess verifier contract where direct candidate imports are unsafe.
3. Run clean offline collection and full upstream tests; record JUnit, frozen total, wall time, and image digest.
4. Produce an Oracle bundle and run Oracle three times, then execute empty, stub, forgery, and offline controls.
5. Write a bidirectional instruction/test traceability review and keep unresolved provenance or environment gaps `blocked`.

No candidate in this report is yet a published NL2RepoBench task.
