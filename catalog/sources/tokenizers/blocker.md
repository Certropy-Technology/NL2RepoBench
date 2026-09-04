# `tokenizers` blocked status

The task has a frozen native source revision, a separate verifier, and a
digest-bound source-derived reference wheel. It cannot currently be published
as a Python checked-in Harbor projection: the production compiler places the
private wheel in `solution/` so the trusted Oracle can install it, while the
repository gate rejects vendored Python wheels in `catalog/tasks`.

The wheel must not be removed from the Oracle bundle or replaced with a stub.
The task remains blocked until the compiler can keep private Oracle payloads
outside the checked-in projection while still making them available to the
trusted Oracle run. After that change, recompile the final task and rerun the
Oracle and all controls before changing this status.
