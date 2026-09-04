# Adapter assessment

The requested revision is the `step` PKI CLI, not a bounded library. Static
inspection found 11 top-level command groups, approximately 151 command
constructors, and 65 source files touching network/TLS, external processes,
platform or terminal behavior, OAuth/ACME, or KMS/TPM/HSM integration.

Observed contracts include HTTP/TLS and TCP listeners, remote CA and OAuth
providers, browser opening, TTY/password prompts, SSH-agent state, filesystem
and system trust-store mutation, OS-specific syscalls, pager/plugin execution,
and optional hardware-backed keys. These are observable behavior, not optional
implementation details.

The current Go production verifier exposes a separate typed subprocess bridge.
It has no reviewed deterministic fixture or protocol for the above network,
PKI, host, terminal, process, platform, or hardware contracts. A pure helper
subset would not be a faithful implementation of this CLI, so authoring is
blocked pending an explicit scoped contract and adapter design.
