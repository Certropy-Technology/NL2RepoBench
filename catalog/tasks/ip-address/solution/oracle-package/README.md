# Private Oracle package

This directory is a task-local reference runtime and is never exposed to the
model agent. `solve.sh` independently fetches and verifies the frozen upstream
revision before installing these prebuilt bytes into the Oracle workspace.
