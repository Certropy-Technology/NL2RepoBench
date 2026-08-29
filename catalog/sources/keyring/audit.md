# Keyring task audit

The frozen project is an MIT-licensed Python credential-storage facade with a backend plugin system, command-line interface, configuration loading, credential value objects, and optional operating-system integrations. Its full upstream suite is healthy, but most backend integration cases are skipped on a headless Linux host because they require D-Bus, a desktop session, Windows Credential Manager, macOS Keychain, or a third-party backend.

The production verifier therefore uses a task-specific child adapter. Every case imports and executes candidate code as UID 10001 in a bounded subprocess. Deterministic in-memory backend fixtures exercise the public facade, backend base class, chainer, credential objects, config selection, descriptors, CLI, plugin loading, and `PasswordMgr`. Trusted code never imports candidate modules or adds the candidate target to its own `sys.path`.

Platform backends are still part of the documented project surface, but this task does not claim to validate live Secret Service, KWallet, Windows, or macOS services. Those integrations are intentionally outside the fixed offline denominator. The agent and verifier have no network; only the trusted Oracle receives a run-scoped authorization for the exact upstream host.
