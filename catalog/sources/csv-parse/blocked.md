# csv-parse blocked remediation record

Status: **blocked**. The exact upstream source and package license are frozen,
but the repository is an npm workspace monorepo rather than an isolated package
task. Its root lock contains workspace links and unrelated tooling, the package
test command relies on a transitive `tsx` loader, and generated dist provenance
is not frozen. No standalone npm v3 cache closure, private `node:test` adapter,
separate verifier, Oracle, controls, or runtime task exists.

The safe future scope is limited to the JSON-compatible `csv-parse/sync`
subpath. Stream, callback, browser, sibling workspace, root, Lerna, and
network behavior remain out of scope.

Reopen only after creating a reviewed isolated npm v3 lock/cache closure,
freezing generated sync artifacts, authoring a bounded adapter/denominator,
and running official Harbor Oracle plus empty, stub, forgery, and offline
controls.
