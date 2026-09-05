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
from nl2repobench.package_managers.dependency_artifacts import (
    load_dependency_inventory,
    materialize_dependency_archive,
)
from nl2repobench.package_managers.maven import MavenPackageManager
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver
from nl2repobench.storage.files import atomic_write

from .bundle_io import BundleLimits
from .java_toolchain import load_java_toolchain_lock
from .task_writer import (
    PYTHON_VERIFIER_FILES,
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
JAVA_RUNTIME_LOCK_FILES = tuple(
    f"src/nl2repobench/{relative}" for relative in PYTHON_VERIFIER_FILES
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
        harbor_lock = self._locked_file(root, self.toolchain.harbor_lock, "Harbor runner lock")
        harbor_digest = f"sha256:{hashlib.sha256(harbor_lock.read_bytes()).hexdigest()}"
        if harbor_digest != self.toolchain.harbor_lock_sha256:
            raise JavaHarborCompileError("Harbor runner lock digest does not match toolchain lock")
        digest = hashlib.sha256()
        for relative in JAVA_RUNTIME_LOCK_FILES:
            path = self._locked_file(root, relative, "Java runtime file")
            data = path.read_bytes()
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(hashlib.sha256(data).digest())
        expected = self.toolchain.java_runtime_sha256
        if expected != f"sha256:{digest.hexdigest()}":
            raise JavaHarborCompileError("Java runtime helper digest does not match toolchain lock")
        oracle_agent = self._locked_file(
            root, "src/nl2repobench/harbor_java_oracle.py", "Java Oracle agent"
        )
        oracle_digest = f"sha256:{hashlib.sha256(oracle_agent.read_bytes()).hexdigest()}"
        if self.toolchain.java_oracle_agent_sha256 != oracle_digest:
            raise JavaHarborCompileError("Java Oracle agent digest does not match toolchain lock")

    @staticmethod
    def _locked_file(root: Path, relative: str, label: str) -> Path:
        value = Path(relative)
        if value.is_absolute() or not relative or any(part in {"", ".", ".."} for part in value.parts):
            raise JavaHarborCompileError(f"{label} path must be relative and confined")
        resolved_root = root.resolve()
        candidate = root / value
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            raise JavaHarborCompileError(f"{label} is missing: {candidate}") from exc
        if not resolved.is_relative_to(resolved_root):
            raise JavaHarborCompileError(f"{label} escapes the toolchain root")
        current = root
        for part in value.parts:
            current = current / part
            if current.is_symlink():
                raise JavaHarborCompileError(f"{label} path contains a symlink")
        if not candidate.is_file():
            raise JavaHarborCompileError(f"{label} must be a regular file")
        return candidate

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
        if source.dependencies.package_manager != "maven":
            raise JavaHarborCompileError(
                "Java source requires dependencies.package_manager=maven"
            )
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
            maven_release = self._write_dependencies(
                source, fixture, temporary, allow_incomplete
            )
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

    def prepare_control_bundle(
        self,
        task_root: Path,
        kind: str,
        output_root: Path,
        *,
        private_cas_root: Path | None = None,
    ) -> Path:
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
        prepared_root = output_root / f".{task_root.name}-control-prepared"
        control_cas_parent = (private_cas_root or output_root / ".private-cas") / target.name
        prepared_root.mkdir(parents=True, exist_ok=True)
        try:
            prepared = self.prepare_run_bundle(
                task_root,
                "model",
                prepared_root,
                private_cas_root=control_cas_parent,
            )
            atomic_write(prepared / "solution/solve.sh", script.read_bytes())
            os.chmod(prepared / "solution/solve.sh", 0o755)
            payload = json.loads((prepared / "bundle.manifest.json").read_text(encoding="utf-8"))
            payload.pop("files", None)
            payload["control_kind"] = kind
            write_file_manifest(prepared, payload=payload, schema_version="1.0")
            os.rename(prepared, target)
            shutil.rmtree(prepared_root, ignore_errors=True)
        except (OSError, TaskWriterError, ValueError) as exc:
            shutil.rmtree(prepared_root, ignore_errors=True)
            shutil.rmtree(control_cas_parent, ignore_errors=True)
            raise JavaHarborCompileError(str(exc)) from exc
        return target

    def prepare_run_bundle(
        self,
        task_root: Path,
        role: str,
        output_root: Path,
        private_cas_root: Path | None = None,
    ) -> Path:
        """Prepare a Java task with a verifier-only scoped CAS mount."""

        if role not in {"model", "oracle"}:
            raise JavaHarborCompileError(f"unsupported Java run role: {role}")
        target = output_root / f"{task_root.name}-{role}"
        cas_parent = private_cas_root or (output_root / ".private-cas")
        cas_root = cas_parent / f"{task_root.name}-{role}"
        if target.exists() or target.is_symlink() or cas_root.exists() or cas_root.is_symlink():
            raise JavaHarborCompileError(f"prepared Java run already exists: {target}")
        if self.artifact_resolver is None:
            raise JavaHarborCompileError("private artifact resolver is required")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = output_root / f".{target.name}-tmp"
        temporary_cas = cas_parent / f".{target.name}-tmp"
        shutil.rmtree(temporary, ignore_errors=True)
        shutil.rmtree(temporary_cas, ignore_errors=True)
        try:
            copy_tree(task_root, temporary)
            verifier_refs = self._load_generated_refs(
                temporary / "tests/private-artifact-refs.json",
                keys={
                    "schema_version",
                    "dependency_refs",
                    "verifier_ref",
                    "toolchain_digest",
                    "maven_version",
                },
            )
            dependency_refs = verifier_refs.get("dependency_refs")
            if not isinstance(dependency_refs, dict):
                raise JavaHarborCompileError("generated Java dependency refs are invalid")
            references = [
                self._artifact_ref(dependency_refs.get(name), f"dependency_refs.{name}")
                for name in ("lock", "offline_store", "inventory")
            ]
            references.append(
                self._artifact_ref(verifier_refs.get("verifier_ref"), "verifier_ref")
            )
            oracle_ref: ArtifactRef | None = None
            if role == "oracle":
                oracle_data = self._load_generated_refs(
                    temporary / "solution/oracle-ref.json",
                    keys={"schema_version", "oracle_ref"},
                )
                oracle_ref = self._artifact_ref(oracle_data.get("oracle_ref"), "oracle_ref")
            scoped = self.artifact_resolver.scoped(
                frozenset(reference.digest for reference in references)
                | ({oracle_ref.digest} if oracle_ref is not None else set())
            )
            for reference in references:
                self._copy_scoped_artifact(reference, scoped, temporary_cas)
            self._bind_scoped_cas(temporary, temporary_cas, cas_root)
            if oracle_ref is not None:
                self._extract_scoped_oracle(oracle_ref, scoped, temporary)
            elif role == "model":
                (temporary / "solution/oracle-ref.json").unlink(missing_ok=True)
                (temporary / "solution/solve.sh").unlink(missing_ok=True)
            payload = json.loads(
                (temporary / "bundle.manifest.json").read_text(encoding="utf-8")
            )
            payload.pop("files", None)
            payload["prepared_run_role"] = role
            write_file_manifest(temporary, payload=payload, schema_version="1.0")
            cas_parent.mkdir(parents=True, exist_ok=True)
            temporary_cas.rename(cas_root)
            temporary.rename(target)
        except (OSError, TaskWriterError, ValueError) as exc:
            shutil.rmtree(temporary, ignore_errors=True)
            shutil.rmtree(temporary_cas, ignore_errors=True)
            shutil.rmtree(cas_root, ignore_errors=True)
            if isinstance(exc, JavaHarborCompileError):
                raise
            raise JavaHarborCompileError(str(exc)) from exc
        return target

    @staticmethod
    def _load_generated_refs(path: Path, *, keys: set[str]) -> dict[str, Any]:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise JavaHarborCompileError(f"generated Java refs are missing: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or set(data) != keys or data.get("schema_version") != "1.0":
            raise JavaHarborCompileError(f"generated Java refs are invalid: {path}")
        return data

    @staticmethod
    def _artifact_ref(value: object, name: str) -> ArtifactRef:
        try:
            return ArtifactRef.model_validate(value)
        except ValueError as exc:
            raise JavaHarborCompileError(f"generated Java {name} is invalid") from exc

    @staticmethod
    def _copy_scoped_artifact(
        reference: ArtifactRef,
        resolver: LocalArtifactResolver,
        cas_root: Path,
    ) -> None:
        source = resolver.resolve(reference)
        digest = reference.digest.removeprefix("sha256:")
        target = cas_root / "private/sha256" / digest[:2] / digest
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(target, source.read_bytes())
        os.chmod(target, 0o400)
        for parent in (target.parent, target.parent.parent, target.parent.parent.parent):
            os.chmod(parent, 0o500)

    @staticmethod
    def _bind_scoped_cas(task: Path, temporary_cas: Path, final_cas: Path) -> None:
        compose = task / "tests/docker-compose.yaml"
        text = compose.read_text(encoding="utf-8")
        marker = "${NL2REPO_PRIVATE_CAS:?NL2REPO_PRIVATE_CAS is required}"
        if text.count(marker) != 1:
            raise JavaHarborCompileError("generated Java verifier CAS mount is invalid")
        # The temporary directory becomes final before Harbor reads the compose file.
        atomic_write(compose, text.replace(marker, str(final_cas.resolve())).encode())

    @staticmethod
    def _extract_scoped_oracle(
        reference: ArtifactRef,
        resolver: LocalArtifactResolver,
        task: Path,
    ) -> None:
        solution = task / "solution"
        oracle = solution / "oracle-bundle"
        try:
            extract_private_bundle(
                reference,
                oracle,
                artifact_resolver=resolver,
                limits=BundleLimits(
                    max_members=10_000,
                    max_member_bytes=512 * 1024 * 1024,
                    max_total_bytes=2 * 1024 * 1024 * 1024,
                ),
            )
        except TaskWriterError as exc:
            raise JavaHarborCompileError(str(exc)) from exc
        solve = oracle / "solve.sh"
        if solve.is_symlink() or not solve.is_file():
            raise JavaHarborCompileError("Java Oracle artifact must contain solve.sh")
        os.chmod(solve, 0o500)

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
RUN ln -sf /opt/java/openjdk/bin/java /usr/local/bin/java \
  && ln -sf /opt/java/openjdk/bin/javac /usr/local/bin/javac \
  && ln -sf /opt/maven/bin/mvn /usr/local/bin/mvn
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
        if allow_incomplete:
            destination = task_root / "tests/dependencies"
            copy_tree(fixture / "dependencies", destination)
        else:
            with tempfile.TemporaryDirectory(prefix="nl2repo-java-dependency-check-") as temp:
                destination = Path(temp) / "dependencies"
                self._materialize_dependencies(source, destination)
                return self._validate_dependencies(destination, allow_incomplete=False)
        lock = destination / "maven-lock-v1.json"
        repository = destination / "maven-repository"
        inventory = destination / "maven-store.manifest.json"
        if not repository.exists():
            repository.mkdir(parents=True)
        try:
            summary = MavenPackageManager().validate_lock(
                lock, expected_version=self.toolchain.maven_version
            )
            if allow_incomplete:
                MavenPackageManager().validate_offline_store(
                    repository,
                    lockfile=lock,
                    manifest=inventory,
                    expected_version=self.toolchain.maven_version,
                )
            else:
                MavenPackageManager().validate_store_payload(
                    repository,
                    lockfile=lock,
                    expected_version=self.toolchain.maven_version,
                )
        except ValueError as exc:
            raise JavaHarborCompileError(f"invalid Maven offline closure: {exc}") from exc
        return summary.release

    def _validate_dependencies(self, destination: Path, *, allow_incomplete: bool) -> int:
        lock = destination / "maven-lock-v1.json"
        repository = destination / "maven-repository"
        inventory = destination / "maven-store.manifest.json"
        if not repository.exists():
            repository.mkdir(parents=True)
        try:
            summary = MavenPackageManager().validate_lock(
                lock, expected_version=self.toolchain.maven_version
            )
            if allow_incomplete:
                MavenPackageManager().validate_offline_store(
                    repository,
                    lockfile=lock,
                    manifest=inventory,
                    expected_version=self.toolchain.maven_version,
                )
            else:
                MavenPackageManager().validate_store_payload(
                    repository,
                    lockfile=lock,
                    expected_version=self.toolchain.maven_version,
                )
        except ValueError as exc:
            raise JavaHarborCompileError(f"invalid Maven offline closure: {exc}") from exc
        return summary.release

    def _materialize_dependencies(
        self, source: DeclarativeTaskSource, destination: Path
    ) -> None:
        bundle = source.dependencies
        if (
            self.artifact_resolver is None
            or bundle.lock is None
            or bundle.offline_store is None
        ):
            raise JavaHarborCompileError(
                "Java production task requires dependency lock/store/inventory"
            )
        inventory = load_dependency_inventory(
            bundle,
            resolver=self.artifact_resolver,
            expected_identity="java+maven",
            expected_toolchain_digest=self._toolchain_digest(),
            expected_adapter_version="maven-offline-v1",
        )
        with tempfile.TemporaryDirectory(prefix="nl2repo-java-dependencies-") as temp:
            root = Path(temp)
            lock_root = root / "lock"
            store_root = root / "store"
            materialize_dependency_archive(
                bundle.lock,
                inventory.lock,
                lock_root,
                resolver=self.artifact_resolver,
            )
            materialize_dependency_archive(
                bundle.offline_store,
                inventory.store,
                store_root,
                resolver=self.artifact_resolver,
            )
            copy_tree(lock_root, destination)
            for path in store_root.iterdir():
                target = destination / path.name
                if path.is_dir():
                    copy_tree(path, target)
                else:
                    atomic_write(target, path.read_bytes())

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
        copy_python_verifier_runtime(
            tests_root / "runtime", include_java_private=True
        )
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
            with tempfile.TemporaryDirectory(prefix="nl2repo-java-harness-check-") as temp:
                private_check = Path(temp) / "private"
                self._extract_private_bundle(source.verifier.bundle, private_check)
                self._validate_harness(private_check, source.verifier.contract_sha256)
            self._write_private_artifact_refs(tests_root, source)
        if allow_incomplete:
            contract_path = (
                private
                / "harness/src/main/java/nl2repobench/harness/ContractMain.java"
            )
            development_digest = (
                "sha256:" + hashlib.sha256(contract_path.read_bytes()).hexdigest()
                if contract_path.is_file()
                else None
            )
            self._validate_harness(private, development_digest)
        profile = source.harbor
        assert profile is not None
        atomic_write(
            tests_root / "test.sh",
            self._test_script(
                source.tests.expected_total,
                profile,
                maven_release,
                allow_incomplete=allow_incomplete,
            ).encode(),
        )
        os.chmod(tests_root / "test.sh", 0o755)
        base = self.toolchain.agent_runtime_base_ref
        verifier_inputs = (
            "COPY --chmod=0500 private /tests/private\n"
            if allow_incomplete
            else "COPY private-artifact-refs.json /tests/private-artifact-refs.json\n"
        )
        dependency_inputs = (
            "COPY --from=java-runtime /opt/maven /opt/maven\n"
            "COPY dependencies/maven-repository /opt/maven/repository\n"
            if allow_incomplete
            else ""
        )
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
{verifier_inputs}{dependency_inputs}
RUN useradd --uid 10001 --create-home candidate \\
  && chmod -R 0555 /usr/local/lib/python3.12/site-packages/nl2repobench
WORKDIR /tests
""".encode(),
        )
        if allow_incomplete:
            compose = b"services:\n  main:\n    network_mode: none\n"
        else:
            compose = b"""services:
  main:
    network_mode: none
    volumes:
      - type: bind
        source: ${NL2REPO_PRIVATE_CAS:?NL2REPO_PRIVATE_CAS is required}
        target: /nl2repo/private-cas
        read_only: true
"""
        atomic_write(tests_root / "docker-compose.yaml", compose)

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
            atomic_write(
                solution / "oracle-ref.json",
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "oracle_ref": source.oracle_bundle.model_dump(mode="json"),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
                + b"\n",
            )
            atomic_write(
                solution / "solve.sh",
                b"""#!/usr/bin/env bash
set -euo pipefail
bundle_dir="$(CDPATH= cd -- "$(dirname -- "$0")/oracle-bundle" && pwd)"
if [ ! -x "$bundle_dir/solve.sh" ]; then
  echo "oracle bundle is not materialized; run nl2repo harbor prepare-run" >&2
  exit 125
fi
exec "$bundle_dir/solve.sh" "$@"
""",
            )
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

    @staticmethod
    def _validate_harness(private: Path, expected_contract_sha256: str | None = None) -> None:
        required = (
            private / "harness/pom.xml",
            private / "harness/src/main/java/nl2repobench/harness/CandidateMain.java",
            private / "harness/src/main/java/nl2repobench/harness/ContractMain.java",
        )
        if not (private / "harness/src/main/java").is_dir() or not all(
            path.is_file() and not path.is_symlink() for path in required
        ):
            raise JavaHarborCompileError(
                "Java verifier requires a harness POM, trusted contract, and CandidateMain"
            )
        if expected_contract_sha256 is None:
            raise JavaHarborCompileError(
                "Java verifier must declare verifier.contract_sha256"
            )
        contract_bytes = required[2].read_bytes()
        actual_contract_sha256 = "sha256:" + hashlib.sha256(contract_bytes).hexdigest()
        if actual_contract_sha256 != expected_contract_sha256:
            raise JavaHarborCompileError("Java ContractMain digest does not match source")
        contract = contract_bytes.decode("utf-8")
        approved_launcher = '"nl2repobench.verification.candidate_process_cli"'
        if contract.count("new ProcessBuilder(") != 1 or contract.count(approved_launcher) != 1:
            raise JavaHarborCompileError("Java ContractMain process launcher is not approved")

    def _write_private_artifact_refs(
        self, tests_root: Path, source: DeclarativeTaskSource
    ) -> None:
        if source.verifier is None or source.oracle_bundle is None:
            raise JavaHarborCompileError(
                "Java production task requires verifier and Oracle artifact refs"
            )
        bundle = source.dependencies
        if bundle.lock is None or bundle.offline_store is None or bundle.inventory is None:
            raise JavaHarborCompileError(
                "Java production task requires dependency lock/store/inventory refs"
            )
        payload = {
            "schema_version": "1.0",
            "toolchain_digest": self._toolchain_digest(),
            "maven_version": self.toolchain.maven_version,
            "dependency_refs": {
                "lock": bundle.lock.model_dump(mode="json"),
                "offline_store": bundle.offline_store.model_dump(mode="json"),
                "inventory": bundle.inventory.model_dump(mode="json"),
            },
            "verifier_ref": source.verifier.bundle.model_dump(mode="json"),
        }
        atomic_write(
            tests_root / "private-artifact-refs.json",
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            + b"\n",
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
        expected: int,
        profile: HarborExecutionProfile,
        maven_release: int = 21,
        *,
        allow_incomplete: bool = False,
    ) -> str:
        if allow_incomplete:
            private_setup = """cp -a /tests/private/harness /tmp/java-harness
cp -a /tmp/java-candidate/src/main/java/. /tmp/java-harness/src/main/java/
mkdir -p /tmp/java-dependencies/maven-repository
cp -a /opt/maven/repository/. /tmp/java-dependencies/maven-repository/
"""
            maven_store = "/tmp/java-dependencies/maven-repository"
        else:
            private_setup = """set +e
python3 -I -m nl2repobench.verification.java_private_artifacts \\
  --refs /tests/private-artifact-refs.json \\
  --cas /nl2repo/private-cas \\
  --dependencies /tmp/java-dependencies \\
  --verifier /tmp/java-private
private_artifact_exit=$?
set -e
if [ "$private_artifact_exit" -ne 0 ]; then
  grade --reason verifier-internal-error
  exit 0
fi
cp -a /tmp/java-private/harness /tmp/java-harness
cp -a /tmp/java-candidate/src/main/java/. /tmp/java-harness/src/main/java/
"""
            maven_store = "/tmp/java-dependencies/maven-repository"
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
rm -rf /tmp/java-harness /tmp/java-private /tmp/java-dependencies
{private_setup}
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
cp /tmp/java-private/harness/src/main/java/nl2repobench/harness/CandidateMain.java \
  /tmp/java-harness/candidate-main-src/nl2repobench/harness/CandidateMain.java
cp /tmp/java-private/harness/src/main/java/nl2repobench/harness/ContractMain.java \
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
  -Dmaven.repo.local={maven_store} -f /tmp/java-harness/pom.xml validate
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
  -Dnl2repobench.candidate.timeout={int(profile.candidate_total_timeout_sec)} \
  -Dnl2repobench.candidate.classpath=/tmp/java-harness/candidate-classes \
  -cp /tmp/java-harness/trusted-classes \
  nl2repobench.harness.ContractMain
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
"""


__all__ = ["JAVA_MAVEN", "JavaHarborCompileError", "JavaHarborCompiler"]
