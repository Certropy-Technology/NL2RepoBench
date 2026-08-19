# Harbor Pilot Status v1

The development dataset `nl2repobench-harbor-pilot` contains ten active
catalog-backed Harbor tasks. Every active task has a valid Oracle score of
`1.0` using Harbor `0.21.0`, task schema `1.4`, a separate verifier, and a
digest-pinned legacy verifier image.

| task | Oracle | status |
| --- | ---: | --- |
| aiofiles | 211/211 | active |
| arguably | 70/70 | active |
| cerberus | 248/248 | active |
| decouple | 67/67 | active |
| ftfy | 336/336 | active |
| parse | 96/96 | active |
| six | 200/200 | active |
| jsonlines | 27/27 | active |
| freezegun | 133/133 | active |
| tinydb | 204/204 | active |
| boltons | 407/423 | blocked: source/test drift |
| humanize | 573/607 | blocked: source/test drift |
| tenacity | 120/124 | blocked: source/test drift |
| pytz | n/a | blocked: generated zoneinfo dependency |

All catalog and Harbor agent timeouts are `3600` seconds. Run outputs are kept
under `.nl2repo/runs/` and are not committed as task assets.

## Model Evidence

- `openai/gpt-5.6-sol`, `reasoning_effort=max`: `ftfy` 1.0 and `parse` 1.0.
- `anthropic/claude-fable-5`, `reasoning_effort=max`: `arguably` produced an
  invalid grading result because the candidate package could not be imported;
  no model score is reported.
- `decouple` and `six` GPT runs ended with API/provider failures. Their verifier
  output is not interpreted as a model score.

The OpenHands SDK adapter passes instructions through a file to avoid host
`ARG_MAX` failures on large NL2Repo instructions and forwards the explicit
reasoning effort into the SDK `LLM` configuration.

## Residual Risks

- This remains a development pilot. Dependency closure and all private assets
  are not yet repackaged as production `PrivateArtifactResolver` bundles.
- Oracle controls have not yet been repeated three times for every active task.
- A configured independent reviewer could not start because the local subagent
  entry has an invalid `runner.type`; repository tests and static gates were
  used instead.
