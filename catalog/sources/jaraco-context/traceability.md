# Traceability

| Public requirement | Private leaves |
| --- | --- |
| installable package, version, typed marker, exports | `exports/*`, `metadata/*` |
| `pushd` restoration | `pushd/behavior`, `pushd_exception/exception-cleanup` |
| temporary directories and platform remover | `temp_dir/*`, `robust_remover/*`, `remove_readonly/*` |
| context-manager composition | `compose/order-and-result`, `filter_compose/right-to-left`, `tarball_cwd/*` |
| exception and decorator contracts | `exception_trap/*`, `exception_trap_nonmatch/*`, `trap_decorators/*`, `suppress/*`, `on_interrupt/*` |
| safe tar extraction | `strip_filter/strip`, `tar_filter_cases/*` |
| tarball download/extract/cleanup | `tarball/*`, `tarball_default_target/*`, `tarball_error/*`, `tarball_cwd/*` |
| repository command behavior | `repo_context/*`, `repo_context_hg/*` |

The public specification describes observable behavior and does not include
private assertions, reference source, or verifier implementation details.
