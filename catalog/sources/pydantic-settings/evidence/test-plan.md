# Bounded test plan

The frozen upstream suite is broad and includes optional AWS, Azure, and GCP SDKs. This task intentionally freezes 20 local behavioral checks for the core API. Checks are adapted from `tests/test_settings.py`, `tests/test_precedence_and_merging.py`, and `tests/test_source_cli.py` at the locked revision.

| Check | Public contract |
| --- | --- |
| exports | Required root imports and version string |
| defaults | Defaults and initialization validation |
| environment | Case-insensitive environment loading |
| env-prefix | Prefixed environment names |
| ignore-empty | Empty environment values omitted |
| complex-json | JSON decoding for list/set/dict/nested model |
| invalid-json | `SettingsError` for malformed complex input |
| nested-delimiter | Nested environment expansion and override |
| nested-max-split | Bounded delimiter splitting |
| aliases | Alias priority with populate-by-name |
| init-over-env | Default source precedence |
| env-over-dotenv | Environment precedence over dotenv |
| dotenv-over-secrets | Dotenv precedence over file secrets |
| secrets-over-default | File secrets precedence over defaults |
| merge-sources | Deep merge across init/environment/dotenv |
| custom-source-order | `settings_customise_sources` ordering |
| parse-none-enum | `env_parse_none_str` and enum-name parsing |
| no-force-decode | `NoDecode` and `ForceDecode` annotations |
| cli-run | CLI parsing and sync/async command execution |
| cli-serialize | JSON/lazy/argparse and env dictionary styles |

Each check runs in a fresh subprocess. The controller sends one JSON request on stdin and accepts exactly one JSON object on stdout. Candidate exceptions are serialized to data. The controller and grader never import `pydantic_settings`.
