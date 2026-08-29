# API And Test Inventory

The frozen source exposes root aliases for `Coverage`, `CoverageData`, the
coverage exception hierarchy, and plugin protocol classes. The main modules
are `control.py`, `sqldata.py`, `data.py`, `cmdline.py`, `config.py`,
`jsonreport.py`, `xmlreport.py`, `lcovreport.py`, `html.py`, `annotate.py`,
`plugin.py`, and `exceptions.py`.

The upstream suite contains focused tests for API/control behavior, SQLite data
round trips, arcs and contexts, configuration, reports (JSON/XML/LCOV/HTML and
annotate), CLI commands, parser behavior, and plugin protocols. The production
contract freezes twelve deterministic leaves derived from those public areas:

| Leaf | Public behavior |
| --- | --- |
| `basic-measurement` | line tracing, save, measured files, report percentage |
| `branch-measurement` | branch arcs and analysis missing lines |
| `data-roundtrip` | line data, context, SQLite persistence |
| `data-arcs` | arc data, queried context, deterministic files |
| `contexts` | dynamic context switching and line context lookup |
| `reports` | JSON/XML/LCOV/HTML/annotated outputs |
| `lifecycle` | current instance and collect context manager |
| `configuration` | explicit branch/timid/data-file configuration |
| `combine-data` | merging parallel data files and cleanup |
| `cli` | `coverage run` and `coverage report` module commands |
| `errors` | source-dir and no-data exception contracts |
| `plugin-protocol` | plugin, tracer, and reporter subclass protocol |

All leaves call only public documented operations and compare stable values.
The adapter normalizes temporary filenames to basenames where needed.
