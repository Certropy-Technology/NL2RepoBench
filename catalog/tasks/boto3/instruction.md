# Build `boto3`

## Project Description

Implement a clean-room Python package named `boto3`, version `1.43.78`, as a
high-level AWS SDK. It wraps local Botocore models and exposes sessions,
clients, resources, DynamoDB expressions, S3 transfer helpers, and documenters.
All scored behavior is local and deterministic with fake credentials and
stubs; it must never contact AWS or instance metadata.

## Natural Language Instruction

Build an installable `boto3` package with these capability groups: session and
credential configuration; low-level client and high-level resource creation;
DynamoDB conditions and type conversion; S3 transfer configuration and
delegation; and service/resource documentation. Preserve public re-exports,
typed exceptions, lazy model loading, resource identifiers and collections,
and optional CRT fallback behavior. Use local Botocore data and do not turn
unavailable remote operations into fabricated successful responses.

## Supports or Environment Configuration

- CPython 3.12.14 on Linux amd64, Debian 12 image.
- Install with `pip install --no-deps --no-build-isolation .`; package and
  import name are both `boto3`.
- The frozen runtime closure is `botocore==1.43.78`, `jmespath==1.0.1`,
  `s3transfer==0.19.0`, plus declared build/test packages. Apache-2.0 metadata
  and version `1.43.78` must be present. `awscrt` is optional.
- Agent, candidate, verifier, Oracle, controls, and runtime use
  `network_mode=no-network`. Do not use AWS credentials, AWS CLI, metadata
  endpoints, DNS, or any external service.

## Project Directory Structure

```text
workspace/
├── setup.py
├── pyproject.toml
├── boto3/
│   ├── __init__.py
│   ├── session.py
│   ├── compat.py
│   ├── crt.py
│   ├── exceptions.py
│   ├── utils.py
│   ├── s3/transfer.py
│   ├── dynamodb/conditions.py
│   ├── dynamodb/table.py
│   ├── dynamodb/types.py
│   ├── dynamodb/transform.py
│   ├── resources/base.py
│   ├── resources/collection.py
│   ├── resources/factory.py
│   ├── resources/model.py
│   ├── resources/action.py
│   ├── docs/action.py
│   ├── docs/attr.py
│   ├── docs/client.py
│   ├── docs/collection.py
│   ├── docs/resource.py
│   └── docs/service.py
└── boto3/data/
    ├── s3/2006-03-01/resources-1.json
    └── dynamodb/2012-08-10/resources-1.json
```

The root must export `Session`, `client`, `resource`, `setup_default_session`,
`set_stream_logger`, `__version__`, and the documented exception and transfer
names. Package data required for local models must be installed with the code.

## API Usage Guide

`boto3.__version__ == "1.43.78"`. `setup_default_session(**kwargs) -> None`
replaces the lazy default. `client(service_name, *args, **kwargs)` and
`resource(service_name, *args, **kwargs)` delegate to that session. `set_stream_logger(name="boto3",
level=logging.DEBUG, format_string=None) -> None` installs a stream handler
without making a request.

`boto3.session.Session(aws_access_key_id=None, aws_secret_access_key=None,
aws_session_token=None, region_name=None, botocore_session=None,
profile_name=None, aws_account_id=None)` preserves supplied Botocore state and
complete credentials. Expose `profile_name`, `region_name`, `events`, and
`available_profiles`; `get_credentials()`, `get_available_services()`,
`get_available_resources()`, `get_available_partitions()`,
`get_available_regions(service_name, partition_name="aws",
allow_non_regional=False)`, and `get_partition_for_region(region_name)` return
the documented list or credential shapes. `client(service_name, region_name=None,
api_version=None, use_ssl=True, verify=None, endpoint_url=None,
aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None,
config=None, aws_account_id=None)` creates a local client. `resource(...)` has
the same argument contract and creates identifiers, actions, collections,
waiters, and subresources lazily. Missing resources raise
`ResourceNotExistsError`; unavailable versions raise `UnknownAPIVersionError`.

```python
import boto3
session = boto3.Session(aws_access_key_id="a", aws_secret_access_key="s", region_name="us-east-1")
print(session.get_available_services())
```

Under `boto3.dynamodb.conditions`, `Attr(name)` and `Key(name)` provide
`eq`, `ne`, `lt`, `lte`, `gt`, `gte`, `begins_with`, `contains`, `between`,
`exists`, and `not_exists`; `&`, `|`, and `~` compose expressions. Their
placeholder name/value maps preserve deterministic insertion order. Under
`boto3.dynamodb.types`, `Binary`, `TypeSerializer`, and `TypeDeserializer`
preserve supported Python scalar, set, list, map, null, boolean, and binary
shapes. `BatchWriter` queues table writes with its documented context-manager
behavior.

`boto3.s3.transfer.S3Transfer` and `TransferConfig` expose constructor
validation, `upload_file`, `download_file`, and `copy`, callback forwarding,
path checks, retry propagation, and context-manager close behavior. The
optional `boto3.crt` names retain availability checks; without `awscrt`, use
the documented warning/fallback/error instead of importing a substitute.

`boto3.docs.generate_docs` and documenter classes under `boto3.docs` accept
local service/resource models and emit deterministic reStructuredText-style
sections for actions, attributes, collections, clients, services, subresources,
and waiters. `boto3.utils` provides `import_module`, `lazy_call`, attribute
injection, append-mode and deprecation helpers; preserve their typed errors.

## Implementation Notes

Do not eagerly create credentials or perform network I/O during import or
client construction. Keep default-session and logging state resettable. Model
and documentation ordering must be stable. Preserve Python exceptions rather
than converting them to strings, including `NoCredentialsError`, resource
errors, transfer argument errors, and expression/type errors.

## Examples

```python
from boto3.dynamodb.conditions import Key, Attr
expression = Key("pk").eq("users") & Attr("active").eq(True)
```

```python
from boto3.s3.transfer import TransferConfig
config = TransferConfig(max_concurrency=2, multipart_threshold=8 * 1024 * 1024)
```

## Error Handling and Boundary Conditions

- A client constructed with fake credentials must not contact AWS; a request
  only occurs when the returned low-level client is explicitly called.
- An account ID without complete credentials raises `NoCredentialsError`.
- Unknown services/resources and unsupported resource API versions retain their
  distinct exception classes.
- Missing `awscrt` degrades according to the CRT contract; it must not make the
  core package import fail or silently claim native acceleration.
