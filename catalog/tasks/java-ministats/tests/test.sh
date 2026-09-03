#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
rm -f /tmp/java-report.xml
PYTHON_ROOT='import sys; sys.path.insert(0, "/usr/local/lib/python3.12/site-packages");'
grade() {
  python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.cli import main; main()" \
    --runtime java --expected 3 --metric-contract fixed-test-pass-rate-v1 --output /logs/verifier "$@"
}
if ! python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.network_check import main; main()" \
  --output /logs/verifier/network.json; then
  grade --reason verifier-network-available
  exit 0
fi
if ! python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.workspace_copy import main; main()" \
  --source /workspace --destination /tmp/java-candidate; then
  grade --reason candidate-workspace-rejected
  exit 0
fi
if ! runuser -u candidate -- python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.java_candidate import main; main()" \
  --root /tmp/java-candidate; then
  grade --reason candidate-installation-failed
  exit 0
fi
rm -rf /tmp/java-harness
cp -a /tests/private/harness /tmp/java-harness
cp -a /tmp/java-candidate/src/main/java/. /tmp/java-harness/src/main/java/
mkdir -p /tmp/maven-repository /tmp/java-harness/classes
chmod -R u+rwX /tmp/java-harness /tmp/maven-repository
chown -R candidate:candidate /tmp/java-harness /tmp/java-candidate /tmp/maven-repository
if ! runuser -u candidate -- env MAVEN_OPTS='-Djava.awt.headless=true' \
  /opt/maven/bin/mvn --offline --batch-mode --no-transfer-progress --strict-checksums \
  -Dmaven.repo.local=/tmp/maven-repository -f /tmp/java-harness/pom.xml validate; then
  cat > /tmp/java-report.xml <<'XML'
<e:events xmlns:e="https://schemas.opentest4j.org/reporting/events/0.1.0"
 xmlns:j="https://schemas.junit.org/open-test-reporting">
<e:started id="c" name="Java contract" time="2026-01-01T00:00:00Z"
 uniqueId="[engine:nl2repobench]" type="CONTAINER"/>
<e:started id="t" parentId="c" name="public API" time="2026-01-01T00:00:00Z"
 uniqueId="[engine:nl2repobench]/[test:public-api]" type="TEST"/>
<e:finished id="t" time="2026-01-01T00:00:00.010Z"><j:result status="FAILED"/></e:finished>
<e:finished id="c" time="2026-01-01T00:00:00.020Z"><j:result status="SUCCESSFUL"/></e:finished>
</e:events>
XML
  grade --report /tmp/java-report.xml --runner-exit-code 1
  exit 0
fi
if ! timeout --signal=KILL 90s   runuser -u candidate -- sh -c 'find /tmp/java-harness/src/main/java -name "*.java" -print0 | xargs -0 /opt/java/openjdk/bin/javac -encoding UTF-8 -d /tmp/java-harness/classes'; then
  grade --reason candidate-installation-failed
  exit 0
fi
set +e
timeout --signal=KILL 300s   runuser -u candidate -- /opt/java/openjdk/bin/java   -cp /tmp/java-harness/classes nl2repobench.harness.ContractMain > /tmp/java-report.xml
runner_exit=$?
set -e
if [ "$runner_exit" -eq 124 ] || [ "$runner_exit" -eq 137 ]; then
  python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.process_cleanup import main; main()"     --uid 10001 || true
  grade --reason verifier-timeout --runner-exit-code "$runner_exit"
elif [ "$runner_exit" -gt 1 ]; then
  grade --reason verifier-internal-error --runner-exit-code "$runner_exit"
else
  grade --report /tmp/java-report.xml --runner-exit-code "$runner_exit"
fi
exit 0
