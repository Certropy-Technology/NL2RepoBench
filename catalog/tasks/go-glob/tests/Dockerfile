FROM --platform=linux/amd64 docker.io/library/golang@sha256:53eeac89074db483fdf0ab3be1df32bf6e47562263d2d0d6baa7f26acb4957dd

RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*
COPY runtime /opt/nl2repobench-runtime
COPY verifier-requirements.lock.txt /tmp/verifier-requirements.lock.txt
RUN python3 -m pip install --break-system-packages --no-cache-dir --require-hashes \
  -r /tmp/verifier-requirements.lock.txt
COPY --chmod=0500 private /tests/private
COPY dependencies /opt/go-module-bundle
COPY --chmod=0555 test.sh /tests/test.sh
RUN useradd --uid 10001 --create-home candidate \
  && chmod -R 0555 /opt/nl2repobench-runtime
WORKDIR /tests
