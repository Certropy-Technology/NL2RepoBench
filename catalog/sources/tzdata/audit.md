# tzdata authoring audit

## Source and license

The full selected commit exists upstream, has no submodules, and produces a
stable raw Git archive. The frozen metadata and both tracked license files
identify Apache-2.0. No reference source bytes are copied into the public task
source or agent image.

## API and data boundary

The project exposes two Python constants and package resources rather than
ordinary functions. The verifier therefore observes metadata, resource
traversal, installed-wheel contents, and standard-library `zoneinfo` behavior.
The candidate is imported only by the UID-10001 candidate runner. The trusted
custom verifier never inserts the candidate target into its own `sys.path` and
the candidate cannot read expected values or write trusted grading outputs.

## Data-heavy adaptation

Testing exact hashes for all 598 TZif resources would make the task a source
retrieval exercise. The public contract instead requires complete manifest
coverage and valid TZif resources, then checks representative historical,
alias, fractional-offset, fold, and future behaviors. The behavior table
explicitly covers the 2026c Alberta, Morocco, and Western Sahara changes that
distinguish this revision from the locked image's system tzdata 2026b.

## Network and dependency closure

The agent and separate verifier run with no network. The two-package Python
build closure is hash-locked and installed from the package index only during
Docker build. Candidate installation uses no dependencies and no build
isolation. The model run receives neither a source host nor a registry host;
only an Oracle invocation may receive a run-scoped `github.com` authorization.
