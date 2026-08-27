# OpenHands Agent Runtime

The runtime is a prebuilt, local Docker image.  The image tag is only the
lookup name used by Docker build; `image_id` and `image_digest` are the
content identity recorded for the exact build.  `scripts/build_openhands_runtime.sh`
must pass before a locked toolchain is used.  It verifies the local tag's
image ID, RepoDigest, fork commit label, SDK/tool versions, and offline probe.

There are two locked variants:

- `runtime.json`: Debian trixie based image for Python tasks.
- `runtime.bookworm.json`: Debian bookworm based image for Node and Go tasks.

Each toolchain lock repeats the selected tag and image ID.  Compiler output
records the same ID in the Agent Dockerfile label and in the bundle's
toolchain digest.  Rebuilding a runtime changes that identity and requires
updating its metadata, regenerating affected bundles, and rerunning the
selected-task gate.
