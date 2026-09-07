# beartype provenance

- **Package:** `beartype`
- **Version:** `0.22.9`
- **Upstream URL:** https://github.com/beartype/beartype
- **License:** MIT (`LICENSE` in the supplied archive)
- **Source authority:** the campaign-supplied sdist
  `.nl2repo/authoring-live/python-wave1/beartype.tar.gz`
- **Source SHA-256:** `8f82b54aa723a2848a56008d18875f91c1db02c32ef6a62319a002e3e25a975f`
- **Python requirement:** `>=3.10`
- **Runtime dependency closure:** empty; development/documentation extras are not
  part of the candidate runtime.

## Bindability rationale

The frozen package exposes a meaningful, mostly pure-Python public contract:
`beartype.beartype`, configuration enums and `BeartypeConf`, DOOR's
`is_bearable`/`die_if_unbearable`/`is_subhint` and `TypeHint`, validator factories
under `beartype.vale`, a public exception/warning hierarchy under `beartype.roar`,
and compatibility typing names under `beartype.typing`. These can be tested as
black-box behavior using ordinary Python values and annotations without exposing
private generated code.

The specification deliberately avoids exact generated wrapper source, stack
frames, diagnostic message wording, private helper names, cache layout, and
implementation-specific import-hook internals. The package's extensive optional
integrations (NumPy, Pandera, third-party plugins, and documentation/test
extras) are not runtime requirements and are not asserted in this first task
slice.

The supplied artifact is a PyPI sdist and does not embed a full VCS commit SHA.
Accordingly, `task.toml` records the immutable sdist authority and its exact
hash, while the missing upstream commit is an explicit follow-up for source
freeze reconciliation rather than an invented commit identifier.
