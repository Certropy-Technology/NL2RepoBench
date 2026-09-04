# Adapter assessment

The current Go runtime profile accepts one fixed `custom-json-v1` leaf and
requires a separate verifier. `go-alcless` does not expose a stable pure-Go
library contract for that profile. Its observable operations enumerate and
mutate host accounts, create sudoers rules, invoke `sudo`/`su`, synchronize
files with `rsync`, inspect or install Homebrew, and optionally require a PTY.

The sole upstream test calls an unexported naming helper and does not exercise
these operations. A task-specific fake host would therefore define new behavior
rather than preserve the frozen project semantics. No adapter was authored and
no Harbor compile or Oracle/control run was attempted after the blocker was
established. Reopen only after an explicit product/verifier decision and a
reviewed deterministic host fixture contract.
