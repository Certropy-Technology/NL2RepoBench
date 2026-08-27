# `jsonpointer` authoring record

Status: `controls-passed`; review and pilot remain pending.

The task freezes commit `5998f951dcc5ace60f67f35afe6778c445401a07` from
`https://github.com/stefankoegl/python-json-pointer`. The unprefixed Git archive
has SHA-256 `f8379acb630446222410697e7e7f33830294f07681de2ae941db723dd4ae989c`.
The root `LICENSE.txt` is BSD-3-Clause and has SHA-256
`d8b24f15d472885f788a2d6e985850f264627b86012a17bb242c83f310d907e5`.
There are no submodules and no runtime package dependencies.

The frozen upstream suite contains 28 collected leaves: specification examples,
pointer parsing and representation, comparisons and joining, mutation,
alternative `__getitem__` objects, error cases, `to_last`, and doctests for the
module functions. The private custom verifier retains a 28-leaf fixed
denominator and checks the JSON-safe equivalent behavior through the generic
candidate subprocess boundary.

Harbor 0.21.0 gates against the production bundle established Oracle 28/28 at
reward 1.0, empty workspace 0, installable stub 1/28, forged reward 1/28, and
an install-phase hang terminated by the candidate supervisor at reward 0. Each
separate verifier receipt reports `public_network_available=false`. Final
receipt paths and content hashes are recorded in `production-evidence.json` and
`evidence/controls-passed.json`.

The image uses the pinned Debian 13 amd64 Python 3.12.14 base digest declared
in `task.toml`. Git `1:2.47.3-0+deb13u1` plus hash-locked setuptools and wheel
are installed during image build. Agent and verifier run phases are no-network. The trusted Oracle
bundle fetches only the frozen revision under a run-scoped source-host override,
then verifies both the commit and raw archive digest. Oracle solution bytes are
not included in an evaluation Agent run.
