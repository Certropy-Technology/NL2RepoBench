FROM --platform=linux/amd64 docker.io/library/golang@sha256:53eeac89074db483fdf0ab3be1df32bf6e47562263d2d0d6baa7f26acb4957dd AS go-runtime

FROM --platform=linux/amd64 nl2repobench/openhands-sdk-fork:930e9b1da-bookworm

LABEL org.nl2repobench.agent-runtime-image="nl2repobench/openhands-sdk-fork:930e9b1da-bookworm" \
  org.nl2repobench.agent-runtime-image-id="sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f" \
  org.nl2repobench.agent-dependency-build="go-offline-module-bundle-v1"

COPY --from=go-runtime /usr/local/go /usr/local/go
ENV PATH=/usr/local/go/bin:$PATH     GOPROXY=off     GOSUMDB=off     GOWORK=off     GOTOOLCHAIN=local
RUN case "$(/usr/local/go/bin/go version)" in *"go1.26.5"*) true;; *) exit 1;; esac   && test -x /opt/openhands-sdk-venv/bin/python
COPY go-module-bundle /opt/go-module-bundle
WORKDIR /workspace
