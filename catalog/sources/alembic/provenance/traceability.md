# Public Contract Traceability

| Public commitment | Private coverage | Boundary |
| --- | --- | --- |
| Package exports expose the documented configuration, command, and operation surfaces | Package metadata leaf | One JSON request to an unprivileged child. |
| `Config` supports defaults, option mutation, INI parsing, attributes, and output streams | Five configuration leaves | Child returns scalar values and buffered public output. |
| `MigrationContext` chooses SQLite/PostgreSQL and supports offline generation | Context and five offline SQL leaves | No database connection or socket is created. |
| `Operations` renders deterministic create/add/index/drop/execute SQL | Five fixed dialect leaves | Trusted parent compares bounded strings returned by child. |
| Operation objects preserve public properties and reversible behavior | Five operation-model leaves | Child returns names, scalar attributes, and reverse class names. |
| Generic migration environments and revisions are generated locally | Three command/script leaves | Child uses a fresh temporary directory for each request. |
| Revision IDs have the documented public shape | Revision-ID leaf | Only the stable hexadecimal shape is asserted. |

The frozen denominator is 20 unique leaf IDs. Error messages and implementation-private helpers are not scored.
