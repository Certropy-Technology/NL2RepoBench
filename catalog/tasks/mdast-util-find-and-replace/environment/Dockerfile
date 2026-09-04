FROM --platform=linux/amd64 docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848 AS node-runtime

FROM --platform=linux/amd64 nl2repobench/openhands-sdk-fork:930e9b1da-bookworm

LABEL org.nl2repobench.agent-runtime-image="nl2repobench/openhands-sdk-fork:930e9b1da-bookworm" \
  org.nl2repobench.agent-runtime-image-id="sha256:3b9288ec42f69da761f0aedb9a72c6888376e9395f9122192aca67e81d913c79" \
  org.nl2repobench.agent-dependency-build="npm-offline-bundle-v1"

COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm   && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx   && test "$(node --version)" = "v24.19.0"   && test "$(npm --version)" = "11.17.0"   && test -x /opt/openhands-sdk-venv/bin/python

RUN test "$(dpkg-query -W -f='${Version}' git)" = 1:2.39.5-0+deb12u3

COPY npm-bundle /opt/npm-bundle
ENV npm_config_cache=/opt/npm-bundle/npm-cache \
    npm_config_offline=true \
    npm_config_ignore_scripts=true \
    npm_config_audit=false \
    npm_config_fund=false


WORKDIR /workspace
