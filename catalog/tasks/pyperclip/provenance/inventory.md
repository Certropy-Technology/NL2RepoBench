# Pyperclip Repair Inventory

- Source: `asweigart/pyperclip`, revision `f5326bfd7c5448b40051dd261a7304657977b838`, BSD-3-Clause, archive SHA-256 `4e80effb92cd84116a2541bb5aa4df7d7832761c04600322f558265ba73c0275`.
- Runtime: Python 3.12.4 on linux/amd64; pinned base digest is in `evidence/environment-lock.json`. Core runtime dependency closure is empty.
- Test boundary: 10 fixed pytest leaves, each invoking the candidate through an external JSON-line fixture runner. The runner uses an in-memory adapter only as a deterministic test double.
- Covered behavior: imports/exports, lazy headless selection, explicit unavailable backend, JSON-safe coercion, invalid manual selection, UTF-8 xclip I/O, Wayland empty-copy clear semantics, and CLI stdin/stdout behavior.
- Platform evidence: no GUI service is required. Real Windows/macOS/Cygwin/WSL/Qt/helper programs were not exercised in the Linux container; bounded mocked backend probes cover portable argument/encoding contracts. This is evidence, not an automatic exclusion.
