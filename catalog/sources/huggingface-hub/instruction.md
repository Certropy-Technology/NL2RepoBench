# Project Description

Build a clean-room Python package named `huggingface_hub` compatible with the
frozen 1.29.0.dev0 public client-library contract. The package is the local,
deterministic part of a model and dataset hub client: it constructs Hub URLs
and request headers, validates repository identifiers, represents Hub metadata,
describes commit operations, and provides local filtering and filesystem
helpers. The evaluation never requires a live Hugging Face account or service.

## Natural Language Instruction

Create the `huggingface_hub` package from an empty `workspace/`. Implement the
offline URL, header, validation, metadata, commit-operation, filtering, cache,
and filesystem configuration APIs described below. Preserve import paths,
exception identity, attribute values, URL quoting, mapping insertion order,
and deterministic JSON-safe behavior.

The package must be useful for local construction and inspection of Hub
requests without making a request. Do not replace a local result with a live
Hub call or require credentials, a service, or external metadata.

## Supports

- CPython 3.12 on Linux amd64. Install from an empty workspace with
  `python -m pip install --no-deps --no-build-isolation .`.
- A conventional setuptools `src` layout, package name `huggingface_hub`, and
  importable top-level re-exports. Set `__version__` to `1.29.0.dev0`.
- Runtime dependencies are already present in the image: `click==8.4.2`,
  `filelock==3.32.3`, `fsspec==2026.7.0`, `httpx==0.28.1`, `packaging==26.3`,
  `pyyaml==6.0.3`, `tqdm==4.70.0`, and `typing-extensions==4.16.0`.
- All behavior tested here is offline and deterministic. Do not contact
  `huggingface.co`, a model provider, a package registry, or a metadata service
  during import or while executing the local APIs below.

## Project Directory Structure

```text
workspace/
├── pyproject.toml or setup.py
├── src/
│   └── huggingface_hub/
│       ├── __init__.py
│       ├── constants.py
│       ├── hf_api.py
│       ├── hf_file_system.py
│       ├── hf_file_metadata.py
│       ├── commit_operation.py
│       └── utils/
│           ├── __init__.py
│           ├── _validators.py
│           └── _http.py
└── README.md
```

The root re-exports named in the API guide. Keep module names and exception
locations importable, but do not add service credentials, evaluator files, or
runtime network configuration to the generated project.

## API Usage Guide

### Root exports and URL construction

Expose `HfApi`, `ModelInfo`, `DatasetInfo`, `SpaceInfo`, `RepoUrl`,
`HfFileMetadata`, `CommitOperationAdd`, `CommitOperationDelete`, `HfFileSystem`,
`hf_hub_url`, and `__version__` from `huggingface_hub`. Re-exports may be lazy,
but accessing them must return the documented class or function.

`hf_hub_url(repo_id, filename, *, subfolder=None, repo_type=None,
revision=None, endpoint=None) -> str` validates the repository id and returns
`{endpoint}/{repo-prefix}/{repo_id}/resolve/{revision}/{path}`. The default
endpoint is `https://huggingface.co`, revision is `main`, dataset URLs have a
`datasets/` prefix, space URLs have a `spaces/` prefix, and a subfolder is
joined before the filename with URL-safe path quoting. Preserve the endpoint
string as supplied, including a trailing slash, because it is observable.

### Request headers

`build_hf_headers(*, token=None, library_name=None, library_version=None,
user_agent=None, headers=None) -> dict[str, str]` returns a new mapping. The
default user-agent contains `hf_hub/1.29.0.dev0`, the running Python version,
and `agent/pi`. Add `library_name/library_version` as `name/version`; a string
or mapping `user_agent` is appended deterministically. A string token adds
`authorization: Bearer <token>`; `False` and `None` omit authorization.
Explicit entries in `headers` win over generated entries, without mutating the
input mapping. The current `HfApi` constructor retains a supplied headers
mapping rather than copying it.

### Validation and URI parsing

`validate_repo_id(repo_id: str | None) -> None` accepts `None`, one component,
or `namespace/name` made from letters, digits, `_`, `-`, and `.`, with no
leading/trailing `-` or `.` and at most 96 characters. Raise
`huggingface_hub.utils.HFValidationError` for spaces, empty components, more
than one slash, or invalid punctuation.

`repo_type_and_id_from_hf_id(hf_id: str, hub_url: str | None = None) ->
tuple[str | None, str, str]` parses bare ids and `hf://` or Hub HTTPS URLs.
Return `(None, namespace, name)` for models, `("dataset", namespace, name)`
for dataset URLs, and `("space", namespace, name)` for spaces. An unrelated
host or malformed URI raises `ValueError` with a diagnostic message.

### Metadata and commit records

`ModelInfo`, `DatasetInfo`, and `SpaceInfo` are keyword-oriented metadata
records that accept unknown optional fields and preserve supplied values as
attributes. Their `repr` identifies the class and supplied fields. `HfFileMetadata`
has fields `commit_hash`, `etag`, `location`, `size`, and `xet_file_data`.

`CommitOperationAdd(path_in_repo, path_or_fileobj)` stores both values and
creates `upload_info` with the byte size and SHA-256 bytes value for bytes, paths, or
file-like objects. `CommitOperationDelete(path_in_repo, is_folder="auto")`
normalizes `"auto"` to a boolean based on a trailing slash and retains an
explicit boolean. Both reject unsafe or empty repository paths with a typed
`ValueError`.

### Local helpers and API configuration

`filter_repo_objects(items, *, allow_patterns=None, ignore_patterns=None,
key=None)` yields the original objects in input order. Shell-style patterns
support strings or lists; allow patterns are inclusive and ignore patterns
remove matches. `parse_datetime(value)` accepts Hub UTC forms ending in `Z`
and returns an aware UTC `datetime`.

`repo_folder_name(*, repo_id, repo_type) -> str` returns a deterministic cache
folder name using the `--` separator and the `models--`, `datasets--`, or
`spaces--` prefix. `HfApi(endpoint=None, token=None, library_name=None,
library_version=None, user_agent=None, headers=None)` normalizes the endpoint
and retains the configuration without performing a request. `HfFileSystem`
must initialize with protocol `hf` and the supplied token.

## Implementation Notes

Keep public import paths and exception identity compatible with the names above.
Use ordinary dataclasses or equivalent records, preserve insertion order in
observable mappings, and avoid global network activity. The hidden verifier
calls the candidate from a separate bounded process and only checks the
JSON-safe local contract described here. Live uploads/downloads, OAuth,
Inference Providers, Xet/native acceleration, credential files, CLI network
operations, and platform-specific Windows behavior are outside this task's
deterministic denominator; keep their public modules importable where practical
but do not substitute network access for a local implementation.

## Examples

```python
from huggingface_hub import hf_hub_url

hf_hub_url("org/model", "config.json", revision="main")
```

```python
from huggingface_hub import build_hf_headers, validate_repo_id

validate_repo_id("org/model")
headers = build_hf_headers(token="local-token", library_name="demo",
                           library_version="1.0")
```

```python
from huggingface_hub import CommitOperationDelete, repo_folder_name

CommitOperationDelete("weights/model.bin")
repo_folder_name(repo_id="org/model", repo_type="model")
```

## Error Handling and Boundary Conditions

- Invalid repository identifiers and unsafe repository paths raise the typed
  validation/value errors described above; empty components and excess slashes
  are not silently normalized.
- Header and user-agent inputs produce a new deterministic mapping except for
  the explicitly documented `HfApi` header-retention behavior.
- URL construction preserves endpoint and revision semantics, while local
  filtering preserves input order and does not mutate input objects.
- `parse_datetime` returns aware UTC values for supported `Z` forms. Live Hub
  requests, uploads, downloads, OAuth, and credential discovery are outside the
  local contract and must not be used as fallbacks.
- Agent, candidate, verifier, Oracle, and controls runs are NoNetwork.
