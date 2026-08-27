ARG PYTHON_BASE=python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

FROM --platform=linux/amd64 ${PYTHON_BASE} AS builder

RUN python -m pip install --no-cache-dir uv==0.11.32

COPY . /src
WORKDIR /src

RUN uv export --frozen --no-dev --package openhands-tools \
        --no-emit-project --format requirements-txt \
        --output-file /tmp/tools-requirements.txt \
    && uv export --frozen --no-dev --package openhands-agent-server \
        --no-emit-project --format requirements-txt \
        --output-file /tmp/server-requirements.txt \
    && sed -i '/^-e \.\/openhands-sdk$/d' /tmp/tools-requirements.txt \
    && sed -i -E '/^[A-Za-z0-9_.-]+[<>~!]/d' /tmp/tools-requirements.txt \
    && awk 'BEGIN { found = 0 } \
        /^fastapi==/ { found = 1 } \
        found { print } \
        found && /^$/ { exit }' \
        /tmp/server-requirements.txt >> /tmp/tools-requirements.txt

RUN uv build --wheel --package openhands-sdk --out-dir /tmp/wheels \
    && uv build --wheel --package openhands-tools --out-dir /tmp/wheels

RUN python -m venv /opt/openhands-sdk-venv \
    && cd / \
    && uv pip install --python /opt/openhands-sdk-venv/bin/python \
        --require-hashes --no-deps -r /tmp/tools-requirements.txt \
    && uv pip install --python /opt/openhands-sdk-venv/bin/python \
        --no-deps /tmp/wheels/openhands_sdk-*.whl /tmp/wheels/openhands_tools-*.whl

FROM --platform=linux/amd64 ${PYTHON_BASE}

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git tmux \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/openhands-sdk-venv /opt/openhands-sdk-venv

LABEL org.nl2repobench.openhands-fork-commit="930e9b1daee0f5d2c7f3b261f045527a0ddae87d" \
      org.nl2repobench.litellm-version="1.93.0"

RUN /opt/openhands-sdk-venv/bin/python - <<'PY'
from importlib.metadata import version
from openhands.sdk.agent.utils import parse_tool_call_arguments

assert version("openhands-sdk") == "1.43.1"
assert version("openhands-tools") == "1.43.1"
assert version("litellm") == "1.93.0"
assert parse_tool_call_arguments('{}{"command":"pwd"}') == {"command": "pwd"}
print("OPENHANDS_FORK_RUNTIME_OK")
PY

WORKDIR /workspace
