FROM --platform=linux/amd64 docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848 AS node-runtime

FROM --platform=linux/amd64 nl2repobench/openhands-sdk-fork@sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f

LABEL org.nl2repobench.agent-runtime-image="nl2repobench/openhands-sdk-fork@sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f" \
  org.nl2repobench.agent-runtime-image-id="sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f" \
  org.nl2repobench.agent-dependency-build="npm-offline-bundle-v1"

COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm   && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx   && test "$(node --version)" = "v24.19.0"   && test "$(npm --version)" = "11.17.0"   && test -x /opt/openhands-sdk-venv/bin/python

RUN dpkg-query -W ca-certificates >/dev/null \
  && dpkg-query -W git >/dev/null

COPY npm-bundle /opt/npm-bundle
ENV npm_config_cache=/opt/npm-bundle/npm-cache \
    npm_config_offline=true \
    npm_config_ignore_scripts=true \
    npm_config_audit=false \
    npm_config_fund=false


WORKDIR /workspace
