"""Harbor compiler for the first Java/Maven task profile.

The compiler owns Java-specific image construction and verifier wiring. The
catalog compiler, artifact resolver, fixed-denominator evaluator, and Harbor
task writer remain shared with the other runtime adapters.
"""

# Generated Docker and shell payloads remain compact for reproducible bundles.
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler, DeclarativeTaskSource
from nl2repobench.domain.models import ArtifactRef, HarborExecutionProfile, TaskManifest
from nl2repobench.domain.runtime import PackageManager, RuntimeDiscriminator, RuntimeLanguage
from nl2repobench.package_managers.maven import MavenPackageManager
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.storage.files import atomic_write

from .bundle_io import BundleLimits
from .java_toolchain import load_java_toolchain_lock
from .task_writer import (
    TaskWriterError,
    copy_python_verifier_runtime,
    copy_tree,
    extract_private_bundle,
    write_file_manifest,
    write_instruction,
)

JAVA_MAVEN = RuntimeDiscriminator(
    language=RuntimeLanguage.JAVA,
    package_manager=PackageManager.MAVEN,
)
JAVA_RUNTIME_LOCK_FILES = (
    "src/nl2repobench/package_managers/maven.py",
    "src/nl2repobench/verification/java_candidate.py",
    "src/nl2repobench/verification/java_bridge.py",
    "src/nl2repobench/verification/java_grader.py",
    "src/nl2repobench/verification/java_process.py",
    "src/nl2repobench/verification/normalize/junit_open_test_report.py",
)


class JavaHarborCompileError(ValueError):
    """Raised when a Java task cannot satisfy the selected compiler profile."""


class JavaHarborCompiler:
    """Generate a deterministic Java/Maven Harbor bundle."""

    def __init__(
        self,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> None:
        try:
            self.toolchain = load_java_toolchain_lock(toolchain_path)
        except ValueError as exc:
            raise JavaHarborCompileError(str(exc)) from exc
        self.toolchain_path = toolchain_path
        self.artifact_resolver = artifact_resolver
        if self.toolchain.status == "locked":
            self._validate_locked_runtime()

    def _validate_locked_runtime(self) -> None:
        root = self.toolchain_path.parent
        digest = hashlib.sha256()
        for relative in JAVA_RUNTIME_LOCK_FILES:
            path = root / relative
            try:
                data = path.read_bytes()
            except OSError as exc:
                raise JavaHarborCompileError(f"Java runtime file is missing: {relative}") from exc
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(hashlib.sha256(data).digest())
        expected = self.toolchain.java_runtime_sha256
        if expected is not None and expected != f"sha256:{digest.hexdigest()}":
            raise JavaHarborCompileError("Java runtime helper digest does not match toolchain lock")

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        source = CatalogCompiler.load_task(source_dir)
        if not isinstance(source, DeclarativeTaskSource) or source.metadata.language != "java":
            raise JavaHarborCompileError(
                "Java compiler accepts only an explicit language=java source"
            )
        if source.dependencies.installer != "maven":
            raise JavaHarborCompileError("Java source requires dependencies.installer=maven")
        if source.environment.runtime is None:
            raise JavaHarborCompileError("Java source requires an explicit environment.runtime")
        if source.environment.runtime.package_manager != "maven":
            raise JavaHarborCompileError("Java source runtime must use Maven")
        if source.harbor is None:
            raise JavaHarborCompileError("Java source is missing [harbor] settings")
        if not allow_incomplete and self.toolchain.status != "locked":
            raise JavaHarborCompileError("Java production output requires a locked Java toolchain")
        if allow_incomplete and self.toolchain.status not in {"observed-not-production", "locked"}:
            raise JavaHarborCompileError("invalid Java toolchain status")

        with tempfile.TemporaryDirectory(prefix="nl2repo-java-canonical-") as temp:
            root = Path(temp)
            compiled = CatalogCompiler(FileArtifactStore(root / "artifacts")).compile_task(
                source_dir, root / "canonical"
            )
            manifest = compiled.manifest
        if not isinstance(manifest, TaskManifest):
            raise JavaHarborCompileError("Java source did not produce a v1 manifest")
        gaps = manifest.publication_gaps()
        if gaps and not allow_incomplete:
            raise JavaHarborCompileError("Java production source is incomplete: " + ", ".join(gaps))

        fixture = source_dir / "harbor"
        required = (
            ("dependencies", "tests/private", "solution/solve.sh") if allow_incomplete else ()
        )
        for relative in required:
            path = fixture / relative
            if not path.exists() or path.is_symlink():
                raise JavaHarborCompileError(f"Java fixture is missing harbor/{relative}")
        final_root = output_root / source.task_id
        if final_root.exists() or final_root.is_symlink():
            raise JavaHarborCompileError(f"Harbor output already exists: {final_root}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = output_root / f".{source.task_id}-tmp"
        if temporary.exists():
            shutil.rmtree(temporary)
        try:
            write_instruction(source_dir, source.instruction, temporary)
            self._write_environment(temporary)
            maven_release = self._write_dependencies(source, fixture, temporary, allow_incomplete)
            self._write_verifier(source, fixture, temporary, allow_incomplete, maven_release)
            self._write_solution(source, fixture, temporary, allow_incomplete)
            self._write_controls(fixture, temporary)
            self._write_task_toml(manifest, temporary)
            self._write_readme(source, temporary, allow_incomplete)
            write_file_manifest(
                temporary,
                payload={
                    "task_id": source.task_id,
                    "task_version": source.version,
                    "mode": "development" if allow_incomplete else "production",
                    "runtime": "java",
                    "package_manager": "maven",
                    "jdk_version": self.toolchain.jdk_version,
                    "maven_version": self.toolchain.maven_version,
                    "canonical_manifest_digest": manifest.content_digest(),
                    "toolchain_lock_digest": self._toolchain_digest(),
                },
                schema_version="1.0",
            )
            os.rename(temporary, final_root)
        except (OSError, TaskWriterError, JavaHarborCompileError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            if isinstance(exc, JavaHarborCompileError):
                raise
            raise JavaHarborCompileError(str(exc)) from exc
        return final_root

    def prepare_control_bundle(self, task_root: Path, kind: str, output_root: Path) -> Path:
        supported = {"empty", "stub", "forgery", "install-failure", "hang", "offline"}
        if kind not in supported:
            raise JavaHarborCompileError(f"unsupported Java control kind: {kind}")
        script = task_root / "controls" / f"{kind}.sh"
        if not script.is_file() or script.is_symlink():
            raise JavaHarborCompileError(f"Java control script is missing: {script}")
        target = output_root / f"{task_root.name}-{kind}"
        if target.exists() or target.is_symlink():
            raise JavaHarborCompileError(f"control output already exists: {target}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = output_root / f".{target.name}-tmp"
        if temporary.exists():
            shutil.rmtree(temporary)
        try:
            copy_tree(task_root, temporary)
            atomic_write(temporary / "solution/solve.sh", script.read_bytes())
            os.chmod(temporary / "solution/solve.sh", 0o755)
            payload = json.loads((temporary / "bundle.manifest.json").read_text(encoding="utf-8"))
            payload.pop("files", None)
            payload["control_kind"] = kind
            write_file_manifest(temporary, payload=payload, schema_version="1.0")
            os.rename(temporary, target)
        except (OSError, TaskWriterError, ValueError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            raise JavaHarborCompileError(str(exc)) from exc
        return target

    def _write_environment(self, task_root: Path) -> None:
        image = self.toolchain.agent_runtime_base_ref
        atomic_write(
            task_root / "environment/Dockerfile",
            f"""FROM --platform=linux/amd64 {self.toolchain.runtime_base_ref} AS java-runtime

FROM --platform=linux/amd64 {image}

LABEL org.nl2repobench.agent-runtime-image=\"{self.toolchain.agent_runtime_image}\" \\
  org.nl2repobench.agent-runtime-image-id=\"{self.toolchain.agent_runtime_image_id}\" \\
  org.nl2repobench.agent-dependency-build=\"maven-offline-v1\"

COPY --from=java-runtime /opt/java/openjdk /opt/java/openjdk
COPY --from=java-runtime /opt/maven /opt/maven
ENV JAVA_HOME=/opt/java/openjdk \\
    MAVEN_HOME=/opt/maven \\
    PATH=/opt/java/openjdk/bin:/opt/maven/bin:$PATH
RUN test \"$(java -version 2>&1 | awk -F'\\\"' '/version/{{print $2}}')\" = \"21.0.12\" \\
  && test \"$(mvn -version 2>&1 | awk '/^Apache Maven/{{print $3}}')\" = \"{self.toolchain.maven_version}\"
WORKDIR /workspace
""".encode(),
        )

    def _write_dependencies(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
    ) -> int:
        destination = task_root / "tests/dependencies"
        if allow_incomplete:
            copy_tree(fixture / "dependencies", destination)
        else:
            reference = source.dependencies.maven_bundle
            if reference is None:
                raise JavaHarborCompileError(
                    "Java production task requires dependencies.maven_bundle"
                )
            self._extract_private_bundle(reference, destination)
        lock = destination / "maven-lock-v1.json"
        repository = destination / "maven-repository"
        inventory = destination / "maven-store.manifest.json"
        if not repository.exists():
            repository.mkdir(parents=True)
        try:
            summary = MavenPackageManager().validate_lock(
                lock, expected_version=self.toolchain.maven_version
            )
            MavenPackageManager().validate_offline_store(
                repository,
                lockfile=lock,
                manifest=inventory,
                expected_version=self.toolchain.maven_version,
            )
        except ValueError as exc:
            raise JavaHarborCompileError(f"invalid Maven offline closure: {exc}") from exc
        return summary.release

    def _write_verifier(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
        maven_release: int,
    ) -> None:
        tests_root = task_root / "tests"
        tests_root.mkdir(parents=True, exist_ok=True)
        copy_python_verifier_runtime(tests_root / "runtime")
        requirements_path = self.toolchain_path.parent / self.toolchain.verifier_requirements_lock
        if requirements_path.is_symlink() or not requirements_path.is_file():
            raise JavaHarborCompileError(
                f"verifier requirements lock is missing: {requirements_path}"
            )
        requirements = requirements_path.read_bytes()
        if (
            f"sha256:{hashlib.sha256(requirements).hexdigest()}"
            != self.toolchain.verifier_requirements_sha256
        ):
            raise JavaHarborCompileError(
                "verifier requirements lock digest does not match Java toolchain"
            )
        atomic_write(tests_root / "requirements.lock.txt", requirements)
        private = tests_root / "private"
        if allow_incomplete:
            copy_tree(fixture / "tests/private", private)
        else:
            if source.verifier is None:
                raise JavaHarborCompileError("Java production task requires [verifier]")
            self._extract_private_bundle(source.verifier.bundle, private)
        if (
            not (private / "harness/pom.xml").is_file()
            or not (private / "harness/src/main/java").is_dir()
            or not (
                private
                / "harness/src/main/java/nl2repobench/harness/CandidateMain.java"
            ).is_file()
        ):
            raise JavaHarborCompileError(
                "Java verifier requires a harness POM, trusted contract, and CandidateMain"
            )
        profile = source.harbor
        assert profile is not None
        atomic_write(
            tests_root / "test.sh",
            self._test_script(source.tests.expected_total, profile, maven_release).encode(),
        )
        os.chmod(tests_root / "test.sh", 0o755)
        base = self.toolchain.agent_runtime_base_ref
        atomic_write(
            tests_root / "Dockerfile",
            f"""FROM --platform=linux/amd64 {base} AS python-runtime
FROM --platform=linux/amd64 {self.toolchain.runtime_base_ref} AS java-runtime
FROM python-runtime
COPY --from=java-runtime /opt/java/openjdk /opt/java/openjdk
COPY --from=java-runtime /opt/maven /opt/maven
ENV JAVA_HOME=/opt/java/openjdk MAVEN_HOME=/opt/maven PATH=/opt/java/openjdk/bin:/opt/maven/bin:$PATH
COPY runtime/nl2repobench /usr/local/lib/python3.12/site-packages/nl2repobench
COPY requirements.lock.txt /tmp/requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes --index-url https://pypi.org/simple -r /tmp/requirements.lock.txt
COPY --chmod=0555 test.sh /tests/test.sh
COPY --chmod=0500 private /tests/private
COPY --from=java-runtime /opt/maven /opt/maven
COPY dependencies/maven-repository /opt/maven/repository
RUN useradd --uid 10001 --create-home candidate \\
  && chmod -R 0555 /usr/local/lib/python3.12/site-packages/nl2repobench
WORKDIR /tests
""".encode(),
        )
        atomic_write(
            tests_root / "docker-compose.yaml", b"services:\n  main:\n    network_mode: none\n"
        )

    def _write_solution(
        self,
        source: DeclarativeTaskSource,
        fixture: Path,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        solution = task_root / "solution"
        if allow_incomplete:
            copy_tree(fixture / "solution", solution)
        else:
            if source.oracle_bundle is None:
                raise JavaHarborCompileError("Java production task requires oracle_bundle")
            self._extract_private_bundle(source.oracle_bundle, solution)
        solve = solution / "solve.sh"
        if solve.is_symlink() or not solve.is_file():
            raise JavaHarborCompileError("Java Oracle bundle must contain solve.sh")
        os.chmod(solve, 0o755)

    @staticmethod
    def _write_controls(fixture: Path, task_root: Path) -> None:
        controls = fixture / "controls"
        if controls.is_dir():
            copy_tree(controls, task_root / "controls")

    def _write_task_toml(self, manifest: TaskManifest, task_root: Path) -> None:
        profile = manifest.harbor
        if profile is None:
            raise JavaHarborCompileError("Java task is missing Harbor execution profile")
        data: dict[str, Any] = {
            "schema_version": "1.4",
            "artifacts": [profile.workspace_artifact],
            "task": {
                "name": f"nl2repobench/{manifest.task_id}",
                "version": manifest.version,
                "description": profile.description,
                "authors": [{"name": "NL2RepoBench"}],
                "keywords": list(profile.keywords),
            },
            "metadata": {
                "difficulty": manifest.metadata.difficulty,
                "category": manifest.metadata.category,
                "tags": list(manifest.metadata.tags),
                "language": "java",
                "runtime": "jdk",
                "runtime_version": self.toolchain.jdk_version,
                "package_manager": "maven",
                "package_manager_version": self.toolchain.maven_version,
                "metric_contract": manifest.metric.contract_id,
                "expected_test_count": manifest.tests.expected_total,
                "canonical_manifest_digest": manifest.content_digest(),
                "toolchain_lock_digest": self._toolchain_digest(),
            },
            "agent": {"timeout_sec": profile.agent_timeout_sec},
            "verifier": {
                "timeout_sec": profile.verifier_timeout_sec,
                "environment_mode": "separate",
                "network_mode": "no-network",
            },
            "environment": {
                "network_mode": profile.agent_network_mode,
                "cpus": profile.cpus,
                "memory_mb": profile.memory_mb,
                "storage_mb": profile.storage_mb,
            },
        }
        atomic_write(task_root / "task.toml", tomli_w.dumps(data).encode())

    def _write_readme(
        self, source: DeclarativeTaskSource, task_root: Path, allow_incomplete: bool
    ) -> None:
        mode = "development-only fixture" if allow_incomplete else "production"
        atomic_write(
            task_root / "README.md",
            (
                f"# `{source.task_id}` Harbor Bundle\n\n"
                f"- Mode: {mode}\n"
                f"- JDK: `{self.toolchain.jdk_version}`\n"
                f"- Maven: `{self.toolchain.maven_version}`\n"
                "- Candidate execution: verifier-owned offline Maven harness\n"
            ).encode(),
        )

    def _extract_private_bundle(self, reference: ArtifactRef, destination: Path) -> None:
        try:
            extract_private_bundle(
                reference,
                destination,
                artifact_resolver=self.artifact_resolver,
                limits=BundleLimits(
                    max_members=10_000,
                    max_member_bytes=512 * 1024 * 1024,
                    max_total_bytes=2 * 1024 * 1024 * 1024,
                ),
            )
        except TaskWriterError as exc:
            raise JavaHarborCompileError(str(exc)) from exc

    def _toolchain_digest(self) -> str:
        return f"sha256:{hashlib.sha256(self.toolchain_path.read_bytes()).hexdigest()}"

    @staticmethod
    def _test_script(
        expected: int, profile: HarborExecutionProfile, maven_release: int = 21
    ) -> str:
        return f"""#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
rm -f /tmp/java-report.xml
PYTHON_ROOT='import sys; sys.path.insert(0, "/usr/local/lib/python3.12/site-packages");'
grade() {{
  python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.cli import main; main()" \\
    --runtime java --expected {expected} --metric-contract fixed-test-pass-rate-v1 --output /logs/verifier "$@"
}}
if ! python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.network_check import main; main()" \\
  --output /logs/verifier/network.json; then
  grade --reason verifier-network-available
  exit 0
fi
if ! python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.workspace_copy import main; main()" \\
  --source /workspace --destination /tmp/java-candidate; then
  grade --reason candidate-workspace-rejected
  exit 0
fi
if ! python3 -I -c "$PYTHON_ROOT from nl2repobench.verification.java_candidate import main; main()" \\
  --root /tmp/java-candidate; then
  grade --reason candidate-installation-failed
  exit 0
fi
rm -rf /tmp/java-harness
cp -a /tests/private/harness /tmp/java-harness
cp -a /tmp/java-candidate/src/main/java/. /tmp/java-harness/src/main/java/
mkdir -p /tmp/java-harness/classes
chmod -R u+rwX /tmp/java-harness
chown -R candidate:candidate /tmp/java-harness /tmp/java-candidate
rm -rf /tmp/java-harness/candidate-src /tmp/java-harness/candidate-main-src \
  /tmp/java-harness/trusted-src \
  /tmp/java-harness/candidate-classes /tmp/java-harness/trusted-classes
mkdir -p /tmp/java-harness/candidate-src /tmp/java-harness/candidate-main-src \
  /tmp/java-harness/trusted-src \
  /tmp/java-harness/candidate-classes \
  /tmp/java-harness/trusted-classes \
  /tmp/java-harness/candidate-main-src/nl2repobench/harness \
  /tmp/java-harness/trusted-src/nl2repobench/harness
chown candidate:candidate /tmp/java-harness/candidate-classes
cp -a /tmp/java-candidate/src/main/java/. /tmp/java-harness/candidate-src/
cp /tests/private/harness/src/main/java/nl2repobench/harness/CandidateMain.java \
  /tmp/java-harness/candidate-main-src/nl2repobench/harness/CandidateMain.java
cp /tests/private/harness/src/main/java/nl2repobench/harness/ContractMain.java \
  /tmp/java-harness/trusted-src/nl2repobench/harness/ContractMain.java
find /tmp/java-harness/candidate-src /tmp/java-harness/candidate-main-src \
  /tmp/java-harness/trusted-src -type d -exec chmod 0555 {{}} +
find /tmp/java-harness/candidate-src /tmp/java-harness/candidate-main-src \
  /tmp/java-harness/trusted-src -type f -exec chmod 0444 {{}} +
set +e
python3 -I -m nl2repobench.verification.java_process \\
  --report /logs/verifier/maven-process.json \\
  --stderr-path /logs/verifier/maven-stderr.txt \\
  --cwd /tmp/java-harness --uid 10001 \\
  --timeout-sec {int(profile.candidate_install_timeout_sec)} \\
  --env MAVEN_OPTS="-Xmx256m -XX:MaxMetaspaceSize=128m -XX:CompressedClassSpaceSize=64m -Djava.awt.headless=true" -- \\
  /opt/maven/bin/mvn --offline --batch-mode --no-transfer-progress --strict-checksums \\
  -Dmaven.repo.local=/opt/maven/repository -f /tmp/java-harness/pom.xml validate
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
python3 -I -m nl2repobench.verification.java_process \
  --report /logs/verifier/javac-process.json \
  --stderr-path /logs/verifier/javac-stderr.txt \
  --cwd /tmp/java-harness --uid 10001 \
  --timeout-sec {int(profile.candidate_install_timeout_sec)} \
  --release {maven_release} \
  --source-root /tmp/java-harness/candidate-src \
  --source-root /tmp/java-harness/candidate-main-src \
  --classes-dir /tmp/java-harness/candidate-classes
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
python3 -I -m nl2repobench.verification.java_process \
  --report /logs/verifier/trusted-javac-process.json \
  --stderr-path /logs/verifier/trusted-javac-stderr.txt \
  --cwd /tmp/java-harness --uid 0 \
  --timeout-sec {int(profile.candidate_install_timeout_sec)} \
  --release {maven_release} \
  --source-root /tmp/java-harness/trusted-src \
  --classes-dir /tmp/java-harness/trusted-classes
trusted_javac_process_exit=$?
set -e
if [ "$trusted_javac_process_exit" -ne 0 ]; then
  grade --reason verifier-internal-error
  exit 0
fi
chown -R root:root /tmp/java-harness
rm -rf /tmp/java-harness/src /tmp/java-harness/candidate-src \
  /tmp/java-harness/candidate-main-src /tmp/java-harness/trusted-src
find /tmp/java-harness -type d -exec chmod 0555 {{}} +
find /tmp/java-harness -type f -exec chmod 0444 {{}} +
chmod 0700 /tmp/java-harness/trusted-classes
find /tmp/java-harness/trusted-classes -type f -exec chmod 0400 {{}} +
set +e
python3 -I -m nl2repobench.verification.java_process \
  --report /logs/verifier/java-process.json \
  --stdout-path /tmp/java-report.xml \
  --stderr-path /logs/verifier/java-stderr.txt \
  --cwd /tmp/java-harness --uid 0 \
  --timeout-sec {int(profile.candidate_total_timeout_sec)} -- \
  /opt/java/openjdk/bin/java -Xmx256m -XX:MaxMetaspaceSize=128m \
  -XX:CompressedClassSpaceSize=64m -Djava.awt.headless=true \
  -Dnl2repobench.candidate.classpath=/tmp/java-harness/candidate-classes \
  -cp /tmp/java-harness/trusted-classes \
  nl2repobench.harness.ContractMain
runner_process_exit=$?
set -e
runner_exit=$(python3 -I -c 'import json, sys; value=json.load(open(sys.argv[1]))["return_code"]; print(value if value is not None else 2)' /logs/verifier/java-process.json)
if [ "$runner_process_exit" -eq 2 ]; then
  grade --reason candidate-timeout
elif [ "$runner_process_exit" -eq 3 ] || [ "$runner_exit" -gt 1 ]; then
  grade --reason verifier-internal-error --runner-exit-code "$runner_exit"
else
  grade --report /tmp/java-report.xml --runner-exit-code "$runner_exit"
fi
exit 0
"""


__all__ = ["JAVA_MAVEN", "JavaHarborCompileError", "JavaHarborCompiler"]
