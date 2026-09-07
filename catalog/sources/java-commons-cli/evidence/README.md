# Commons CLI Authoring Evidence

This task uses the immutable `apache/commons-cli` revision recorded in
`task.toml`. The public contract is intentionally bounded to option definition,
registration, parsing, result queries, positional arguments, and parse errors.
The verifier harness uses only the Java standard library, so the Maven closure
is empty. Parent integration must register the task-scoped private refs from
`.nl2repo/authoring-work/java-commons-cli/staging-refs.json` before compiling a
Harbor runtime.
