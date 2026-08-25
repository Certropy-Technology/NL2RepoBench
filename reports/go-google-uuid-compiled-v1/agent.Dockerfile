FROM --platform=linux/amd64 docker.io/library/golang@sha256:53eeac89074db483fdf0ab3be1df32bf6e47562263d2d0d6baa7f26acb4957dd

COPY go-module-bundle /opt/go-module-bundle
WORKDIR /workspace
