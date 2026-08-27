# Lodash controls

- `empty.sh`: leaves the workspace unimplemented.
- `stub.sh`: creates an installable package whose methods return `null`.
- `forgery.sh`: adds forged workspace grading files to the same stub.
- `timeout.sh`: hangs only `chunk`; the per-call supervisor must terminate it
  while the remaining leaves and trusted grading complete.

The compiler's `prepare-control` command directly supports `stub` and
`forgery`. Empty and timeout controls are derived task-local copies of the
compiled bundle with the corresponding script installed as `solution/solve.sh`.
