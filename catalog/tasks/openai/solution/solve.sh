#!/bin/sh
set -eu

revision="555ac487f450f24928d859478ea2f41b58906206"
expected_archive="3fee3c1832ceafd565161d3a0c42555823c7bdb7ca20dc2f217e8f7437365720"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
git -C /workspace init -q
git -C /workspace remote add origin https://github.com/openai/openai-python
git -C /workspace fetch -q --depth=1 origin "$revision"

resolved="$(git -C /workspace rev-parse FETCH_HEAD)"
test "$resolved" = "$revision"
archive="$(git -C /workspace archive --format=tar FETCH_HEAD | sha256sum | cut -d' ' -f1)"
test "$archive" = "$expected_archive"

git -C /workspace checkout -q --detach FETCH_HEAD
rm -rf /workspace/.git
python -m pip install --no-deps /workspace
