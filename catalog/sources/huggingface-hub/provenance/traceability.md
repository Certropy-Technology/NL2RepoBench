# Public Contract Traceability

| Contract area | Public instruction | Private deterministic coverage |
| --- | --- | --- |
| Version and root re-exports | Supports; Root exports | version, classes, functions, exception exports |
| URL path construction | URL construction | model, dataset, space, revision, subfolder, endpoint cases |
| Header precedence and user-agent | Request headers | token, false token, library marker, string/mapping UA, explicit headers |
| Repository validation | Validation and URI parsing | valid ids and each invalid shape |
| Hub URI parsing | Validation and URI parsing | bare, hf URI, model/dataset/space HTTPS, foreign host |
| Metadata records | Metadata and commit records | ModelInfo, DatasetInfo, SpaceInfo, file metadata |
| Commit records | Metadata and commit records | bytes upload hash/size, delete auto/explicit and invalid paths |
| Pure utility behavior | Local helpers | UTC parsing, allow/ignore patterns, cache folder naming |
| API configuration | Local helpers and API configuration | HfApi normalization and HfFileSystem protocol/token |

The full upstream suite remains diagnostic provenance only. The hidden 40-leaf
contract is authored from the documented public behavior and does not expose
upstream tests, private assertions, or reference implementation bytes.
