#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/grading.json /logs/verifier/report.json
rm -rf /tmp/candidate-source /tmp/candidate-site /tmp/npm-cache
install -d -o candidate -g candidate -m 0700 /tmp/npm-cache
cp -a /opt/npm-bundle/npm-cache/. /tmp/npm-cache/
chown -R candidate:candidate /tmp/npm-cache

if ! node /tests/runtime/node/copy_workspace.mjs \
  --source /workspace \
  --destination /tmp/candidate-source; then
  node /tests/runtime/node/grade-report.mjs \
    --expected 17 \
    --reason candidate-workspace-rejected \
    --output /logs/verifier
  exit 0
fi
mkdir -p /tmp/candidate-site /tmp/candidate-site/home /tmp/candidate-site/tmp
chown -R candidate:candidate /tmp/candidate-source /tmp/candidate-site
if ! runuser -u candidate -- \
  env PATH=/usr/local/bin:/usr/bin:/bin \
  /usr/local/bin/node /tests/runtime/node/install_candidate.mjs \
    --source /tmp/candidate-source \
    --target /tmp/candidate-site \
    --cache /tmp/npm-cache; then
  node /tests/runtime/node/grade-report.mjs \
    --expected 17 \
    --reason candidate-installation-failed \
    --output /logs/verifier
  exit 0
fi
tarball=$(find /tmp/candidate-site -maxdepth 1 -name '*.tgz' -type f | head -1)
if [[ -z "$tarball" ]] || ! node /tests/runtime/node/validate-package.mjs "$tarball"; then
  node /tests/runtime/node/grade-report.mjs \
    --expected 17 \
    --reason candidate-installation-failed \
    --output /logs/verifier
  exit 0
fi

export NODE_CANDIDATE_SITE=/tmp/candidate-site
export NODE_TEST_CLIENT=/tests/private/test_client.mjs
if ! node /tests/runtime/node/validate-command-plan.mjs \
  --path /tests/command-plan.json; then
  node /tests/runtime/node/grade-report.mjs \
    --expected 17 \
    --reason verifier-internal-error \
    --output /logs/verifier
  exit 0
fi
runner_exit_code=0
node /tests/runtime/node/run_tests.mjs \
  --tests /tests/private \
  --candidate /tmp/candidate-site \
  --expected 17 \
  --output /logs/verifier/report.json || runner_exit_code=$?
node /tests/runtime/node/grade-report.mjs \
  --expected 17 \
  --report /logs/verifier/report.json \
  --runner-exit-code "$runner_exit_code" \
  --output /logs/verifier
exit 0
