#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
rm -f /tmp/java-report.xml
PYTHON_ROOT='import sys; sys.path.insert(0, "/usr/local/lib/python3.12/site-packages");'
grade() {
  python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.cli import main; main()" \
    --runtime java --expected 8 --metric-contract fixed-test-pass-rate-v1 --output /logs/verifier "$@"
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
if ! python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.java_candidate import main; main()" \
  --root /tmp/java-candidate; then
  grade --reason candidate-installation-failed
  exit 0
fi
rm -rf /tmp/java-harness /tmp/java-private /tmp/java-dependencies
set +e
python3 -I -m nl2repobench.verification.java_private_artifacts \
  --refs /tests/private-artifact-refs.json \
  --cas /nl2repo/private-cas \
  --dependencies /tmp/java-dependencies \
  --verifier /tmp/java-private
private_artifact_exit=$?
set -e
if [ "$private_artifact_exit" -ne 0 ]; then
  grade --reason verifier-internal-error
  exit 0
fi
cp -a /tmp/java-private/harness /tmp/java-harness
cp -a /tmp/java-candidate/src/main/java/. /tmp/java-harness/src/main/java/

mkdir -p /tmp/java-harness/classes
chmod -R u+rwX /tmp/java-harness
chown -R candidate:candidate /tmp/java-harness /tmp/java-candidate
rm -rf /tmp/java-harness/candidate-src /tmp/java-harness/candidate-main-src   /tmp/java-harness/trusted-src   /tmp/java-harness/candidate-classes /tmp/java-harness/trusted-classes
mkdir -p /tmp/java-harness/candidate-src /tmp/java-harness/candidate-main-src   /tmp/java-harness/trusted-src   /tmp/java-harness/candidate-classes   /tmp/java-harness/trusted-classes   /tmp/java-harness/candidate-main-src/nl2repobench/harness   /tmp/java-harness/trusted-src/nl2repobench/harness
chown candidate:candidate /tmp/java-harness/candidate-classes
cp -a /tmp/java-candidate/src/main/java/. /tmp/java-harness/candidate-src/
cp /tmp/java-private/harness/src/main/java/nl2repobench/harness/CandidateMain.java   /tmp/java-harness/candidate-main-src/nl2repobench/harness/CandidateMain.java
cp /tmp/java-private/harness/src/main/java/nl2repobench/harness/ContractMain.java   /tmp/java-harness/trusted-src/nl2repobench/harness/ContractMain.java
find /tmp/java-harness/candidate-src /tmp/java-harness/candidate-main-src   /tmp/java-harness/trusted-src -type d -exec chmod 0555 {} +
find /tmp/java-harness/candidate-src /tmp/java-harness/candidate-main-src   /tmp/java-harness/trusted-src -type f -exec chmod 0444 {} +
set +e
python3 -I -m nl2repobench.verification.java_process \
  --report /logs/verifier/maven-process.json \
  --stderr-path /logs/verifier/maven-stderr.txt \
  --cwd /tmp/java-harness --uid 10001 \
  --timeout-sec 90 \
  --env MAVEN_OPTS="-Xmx256m -XX:MaxMetaspaceSize=128m -XX:CompressedClassSpaceSize=64m -Djava.awt.headless=true" -- \
  /opt/maven/bin/mvn --offline --batch-mode --no-transfer-progress --strict-checksums \
  -Dmaven.repo.local=/tmp/java-dependencies/maven-repository -f /tmp/java-harness/pom.xml validate
maven_process_exit=$?
set -e
if [ "$maven_process_exit" -eq 2 ]; then
  grade --reason candidate-timeout
  exit 0
elif [ "$maven_process_exit" -eq 3 ]; then
  grade --reason verifier-internal-error
  exit 0
elif [ "$maven_process_exit" -ne 0 ]; then
  grade --reason candidate-installation-failed
  exit 0
fi
set +e
python3 -I -m nl2repobench.verification.java_process   --report /logs/verifier/javac-process.json   --stderr-path /logs/verifier/javac-stderr.txt   --cwd /tmp/java-harness --uid 10001   --timeout-sec 90   --release 21   --source-root /tmp/java-harness/candidate-src   --source-root /tmp/java-harness/candidate-main-src   --classes-dir /tmp/java-harness/candidate-classes
javac_process_exit=$?
set -e
if [ "$javac_process_exit" -eq 2 ]; then
  grade --reason candidate-timeout
  exit 0
elif [ "$javac_process_exit" -eq 3 ]; then
  grade --reason verifier-internal-error
  exit 0
elif [ "$javac_process_exit" -ne 0 ]; then
  grade --reason candidate-installation-failed
  exit 0
fi
set +e
python3 -I -m nl2repobench.verification.java_process   --report /logs/verifier/trusted-javac-process.json   --stderr-path /logs/verifier/trusted-javac-stderr.txt   --cwd /tmp/java-harness --uid 0   --timeout-sec 90   --release 21   --source-root /tmp/java-harness/trusted-src   --classes-dir /tmp/java-harness/trusted-classes
trusted_javac_process_exit=$?
set -e
if [ "$trusted_javac_process_exit" -ne 0 ]; then
  grade --reason verifier-internal-error
  exit 0
fi
chown -R root:root /tmp/java-harness
rm -rf /tmp/java-harness/src /tmp/java-harness/candidate-src   /tmp/java-harness/candidate-main-src /tmp/java-harness/trusted-src
find /tmp/java-harness -type d -exec chmod 0555 {} +
find /tmp/java-harness -type f -exec chmod 0444 {} +
chmod 0700 /tmp/java-harness/trusted-classes
find /tmp/java-harness/trusted-classes -type f -exec chmod 0400 {} +
set +e
python3 -I -m nl2repobench.verification.java_process   --report /logs/verifier/java-process.json   --stdout-path /tmp/java-report.xml   --stderr-path /logs/verifier/java-stderr.txt   --cwd /tmp/java-harness --uid 0   --timeout-sec 300 --   /opt/java/openjdk/bin/java -Xmx256m -XX:MaxMetaspaceSize=128m   -XX:CompressedClassSpaceSize=64m -Djava.awt.headless=true   -Dnl2repobench.candidate.timeout=300   -Dnl2repobench.candidate.classpath=/tmp/java-harness/candidate-classes   -cp /tmp/java-harness/trusted-classes   nl2repobench.harness.ContractMain
runner_process_exit=$?
python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.process_cleanup import terminate_uid_processes; terminate_uid_processes(10001)"
candidate_cleanup_exit=$?
set -e
runner_exit=$(python3 -I -c 'import json, sys; value=json.load(open(sys.argv[1]))["return_code"]; print(value if value is not None else 2)' /logs/verifier/java-process.json)
if [ "$candidate_cleanup_exit" -ne 0 ]; then
  grade --reason verifier-internal-error
elif [ "$runner_process_exit" -eq 2 ]; then
  grade --reason candidate-timeout
elif [ "$runner_process_exit" -eq 3 ] || [ "$runner_exit" -gt 1 ]; then
  grade --reason verifier-internal-error --runner-exit-code "$runner_exit"
else
  grade --report /tmp/java-report.xml --runner-exit-code "$runner_exit"
fi
exit 0
