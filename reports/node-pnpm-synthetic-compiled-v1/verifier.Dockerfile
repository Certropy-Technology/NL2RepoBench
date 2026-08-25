FROM --platform=linux/amd64 docker.io/library/node@sha256:8607a9064d4a571140998ae9e52a3b3fcf9cff361d04642d5971e6cd76d39e27 AS node-runtime
FROM --platform=linux/amd64 python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
  && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

RUN npm install --global pnpm@9.15.0
COPY python-runtime /opt/nl2repobench-runtime
COPY verifier-requirements.lock.txt /tmp/verifier-requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes \
  -r /tmp/verifier-requirements.lock.txt
COPY dependencies /opt/pnpm-bundle
COPY runtime /tests/runtime
COPY command-plan.json /tests/command-plan.json
COPY --chmod=0500 private /tests/private
COPY --chmod=0555 test.sh /tests/test.sh
RUN useradd --uid 10001 --create-home candidate \
  && chmod -R 0555 /opt/nl2repobench-runtime \
  && chmod -R 0500 /tests/private \
  && chmod -R 0555 /tests/runtime
WORKDIR /tests
