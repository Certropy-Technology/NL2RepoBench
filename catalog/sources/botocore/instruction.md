# Build `botocore`

## Project Description

Create an installable Python package named `botocore` from an empty workspace.
It is a local, data-driven AWS core for sessions, service models, request
construction, Signature Version 4 signing, retries, exceptions, and `Stubber`.
The contract is offline and does not require an AWS account or a live service.

## Natural Language Instruction

Implement five connected capabilities: session/configuration and credentials;
local service-model and client creation; request preparation and signing;
ordered stub responses; and typed errors/retry helpers. Keep APIs modular and
installable, include the local S3 and DynamoDB model data, and preserve public
exception identities. Do not call metadata services, credential processes,
`curl`, `wget`, `git`, CRT, or live AWS endpoints.

## Supports or Environment Configuration

- CPython 3.12 on Linux amd64 with glibc.
- Package name/import name `botocore`; install with `pip install .` or the
  equivalent source build.
- Runtime dependencies are `jmespath==1.0.1`,
  `python-dateutil==2.9.0.post0`, and `urllib3==2.5.0`. The package version
  must be stable and exposed as `botocore.__version__`.
- Agent, candidate, verifier, Oracle, controls, and runtime use
  `network_mode=no-network`; all model data and test inputs are local.

## Project Directory Structure

```text
workspace/
├── setup.py
├── pyproject.toml
└── botocore/
    ├── __init__.py
    ├── session.py
    ├── config.py
    ├── awsrequest.py
    ├── auth.py
    ├── stub.py
    ├── exceptions.py
    ├── retryhandler.py
    ├── translate.py
    └── data/
        ├── s3/2006-03-01/service-2.json
        └── dynamodb/2012-08-10/service-2.json
```

Include package data in installation and preserve the import paths above.

## API Usage Guide

`botocore.session.get_session() -> Session` returns a fresh session. `Session`
implements `set_config_variable(name, value)`, `get_config_variable(name)`,
`set_credentials(access_key, secret_key, token=None, account_id=None)`,
`get_credentials()`, `get_available_services()`,
`get_available_regions(service_name)`, `get_service_model(service_name)`,
`get_paginator_model(service_name)`, `get_waiter_model(service_name)`, and
`create_client(service_name, region_name=None, aws_access_key_id=None,
aws_secret_access_key=None, aws_session_token=None, endpoint_url=None,
config=None)`. Explicit session values take precedence over environment values;
credential records expose `access_key`, `secret_key`, `token`, and `method`.

```python
from botocore.session import get_session
session = get_session()
session.set_config_variable("region", "us-east-1")
session.set_credentials("access", "secret")
print(session.get_available_services())
```

`botocore.config.Config(region_name=None, signature_version=None,
connect_timeout=60, read_timeout=60, retries=None, s3=None,
user_agent_extra=None)` is immutable-like; `merge(other) -> Config` returns a
new object. `botocore.UNSIGNED` disables signing. `Session.get_service_model("s3")`
loads local JSON and exposes service metadata, operation names, operation
lookup, and input shapes; a created client exposes modeled operations such as
`list_objects_v2` and `put_object` without making a request at construction.

`botocore.awsrequest.AWSRequest(method, url, data=None, headers=None)` stores a
request; `prepare() -> AWSPreparedRequest` normalizes headers/body. `botocore.auth.SigV4Auth(credentials,
service_name, region_name).add_auth(request)` adds deterministic
`Authorization`, `X-Amz-Date`, and payload-hash headers. Fixed credentials,
request, and timestamp give stable output.

`botocore.stub.Stubber(client)` is a context manager. `add_response(operation,
response, expected_params=None)` queues a response and `add_client_error(operation,
error_code, error_message=None, expected_params=None, modeled_fields=None)`
queues an error. Activation consumes calls in insertion order; unexpected,
mismatched, or exhausted calls raise `StubAssertionError`,
`StubResponseError`, or `UnStubbedResponseError` as appropriate.

Preserve `ClientError`, `NoCredentialsError`, `ParamValidationError`,
`ProfileNotFound`, and the stub exceptions. `retryhandler.create_retry_handler(config,
operation_name=None) -> callable` and `translate.build_retry_config(config) ->
dict` accept documented local shapes and provide deterministic capped retry
behavior for success and throttling.

## Implementation Notes

Load models from installed package data instead of hard-coding remote answers.
Preserve insertion order where request/model output exposes it. Keep signing
and stub state local to the relevant request/client. Invalid configuration,
unknown services, absent credentials, malformed requests, and unexpected stub
calls must retain typed failures.

## Examples

```python
from botocore.config import Config
base = Config(region_name="us-east-1")
merged = base.merge(Config(user_agent_extra="local"))
```

```python
from botocore.stub import Stubber
client = get_session().create_client("s3", region_name="us-east-1")
with Stubber(client) as stubber:
    stubber.add_response("list_objects_v2", {"Contents": []})
```

## Error Handling and Boundary Conditions

- Missing credentials raise the documented credential exception and must not
  trigger metadata-service access.
- `Config.merge` leaves both input objects unchanged; invalid config shapes
  raise typed validation errors.
- `UNSIGNED` leaves an AWS request without SigV4 authorization headers.
- Stub queues are ordered: an unexpected operation or parameter mismatch fails
  immediately, and an unused queued response is reported when the context ends.
