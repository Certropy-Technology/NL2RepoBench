FROM --platform=linux/amd64 docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848

COPY dependencies /opt/npm-bundle
COPY runtime /tests/runtime
COPY command-plan.json /tests/command-plan.json
COPY --chmod=0500 private /tests/private
COPY --chmod=0555 test.sh /tests/test.sh
RUN useradd --uid 10001 --create-home candidate \
  && chmod -R 0500 /tests/private \
  && chmod -R 0555 /tests/runtime
WORKDIR /tests
