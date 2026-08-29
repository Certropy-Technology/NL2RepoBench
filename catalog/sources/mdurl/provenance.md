# mdurl provenance

The authoring workspace is `.nl2repo/authoring-work/mdurl`. Source acquisition
used a no-checkout clone followed by an exact commit fetch and detached checkout.
The archive was produced with `git archive --format=tar HEAD`; its digest and
the MIT license digest are recorded in `audit.md` and `task.toml`.

Commands used for the ground-truth probe:

```text
git clone --filter=blob:none --no-checkout https://github.com/executablebooks/mdurl.git
git fetch --no-tags origin 524d2edbbcb8bb48301ba716c7482827bcabb281
git archive --format=tar HEAD
PYTHONPATH=src python -m pytest -q --collect-only
PYTHONPATH=src python -m pytest -q
```

The source tree was not copied into the public task source. The private
verifier fixture and Oracle bundle are materialized through the local CAS at
compile time, and the normal model run receives no source-host authorization.
