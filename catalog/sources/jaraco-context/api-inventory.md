# API Inventory

## Frozen Runtime

The candidate is the pure-Python `jaraco.context` package at revision
`bfcb95c784e110521fa907e890b2eea34b0ef349` (tree
`d47521686d049a7aa36dbcbd42b4d594bf81b47a`). The runtime consists of one
422-line implementation module and the `py.typed` marker. It has no native
extension and no selected runtime dependency on CPython 3.12.

## Public Names

The task instruction covers these callable and class exports:

| Name | Contract exercised |
| --- | --- |
| `pushd` | change directory, yield the supplied path, restore on normal and exceptional exit |
| `tarball` | stream extraction, strip the root component, reject traversal, clean up |
| `tarball_cwd` | compose `tarball` and `pushd` and restore the caller directory |
| `strip_first_component` | mutate and return the same `TarInfo` object |
| `_compose_tarfile_filters` / `_default_filter` | left-to-right filter composition and safe extraction |
| `_compose` | dependent context-manager composition from right to left |
| `remove_readonly` / `robust_remover` | Windows retry callback and platform remover selection |
| `temp_dir` / `robust_temp_dir` | temporary directory lifetime and custom remover support |
| `repo_context` | git/hg clone command construction and output routing |
| `ExceptionTrap` | matching exception capture, truth value, decorators, and metadata |
| `suppress` | `contextlib.suppress` semantics plus decorator support |
| `on_interrupt` | ignore, suppress, or translate `KeyboardInterrupt` |

The verifier invokes all candidate imports in a UID-isolated child adapter. The
trusted verifier never imports candidate code or places the candidate directory
on its own import path.
