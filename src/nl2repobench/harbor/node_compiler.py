"""Node/npm Harbor compiler for canonical task sources."""

# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import tempfile
from pathlib import Path
from typing import Any, cast

import tomli_w

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.domain.canonical_contract import (
    PackageManager,
    RuntimeLanguage,
    TaskManifest,
)
from nl2repobench.domain.canonical_models import ArtifactRef
from nl2repobench.package_managers.pnpm import validate_pnpm_lock_data
from nl2repobench.storage.artifacts import (
    ArtifactStoreError,
    FileArtifactStore,
    LocalArtifactResolver,
)
from nl2repobench.storage.files import atomic_write
from nl2repobench.storage.materialize import ArchiveKind
from nl2repobench.verification.node_command_plan import (
    NodeVerifierCommandPlan,
    expected_node_command_plan,
    load_node_command_plan,
)

from .bundle_io import BundleLimits
from .dependency_contract import DependencyContractError, validate_dependency_artifacts
from .node_dependencies import (
    NodeDependencyError,
    validate_npm_dependency_bundle,
    validate_npm_lock_data,
)
from .node_toolchain import NodeRuntimeManifest, load_node_toolchain_lock
from .private_artifacts import categorized_private_artifacts
from .task_writer import (
    _PYTHON_VERIFIER_FILES,
    TaskWriterError,
    copy_python_verifier_runtime,
    copy_tree,
    extract_private_bundle,
    python_runtime_manifest,
    write_file_manifest,
    write_instruction,
)

NODE_BUNDLE_MANIFEST_SCHEMA = "2.0"
NODE_RUNTIME_ROOT = "/opt/nl2repobench-node"
NODE_EXECUTABLE = f"{NODE_RUNTIME_ROOT}/bin/node"
NPM_LAUNCHER = f"{NODE_RUNTIME_ROOT}/lib/npm/bin/npm-cli.js"
PNPM_LAUNCHER = f"{NODE_RUNTIME_ROOT}/lib/pnpm/bin/pnpm.cjs"
NODE_VERIFIER_FILES = (
    "candidate_runner.mjs",
    "copy_workspace.mjs",
    "grade-report.mjs",
    "run_tests.mjs",
    "validate-command-plan.mjs",
    "validate-package.mjs",
    "validate-pnpm-command-plan.mjs",
)
NODE_PYTHON_ADAPTER_ROOT = "/opt/nl2repobench-node-adapter"


class NodeHarborCompileError(ValueError):
    """Raised when a canonical Node task cannot be safely compiled."""


class NodeHarborCompiler:
    """Generate a schema 1.4 development bundle without Docker execution."""

    MAX_BUNDLE_MEMBERS = 10_000
    MAX_BUNDLE_MEMBER_BYTES = 512 * 1024 * 1024
    MAX_BUNDLE_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
    runtime_package_manager = PackageManager.NPM
    candidate_install_id = "npm-pack-offline-v1"

    def __init__(
        self,
        toolchain_path: Path,
        *,
        artifact_resolver: LocalArtifactResolver | None = None,
    ) -> None:
        try:
            self.toolchain = load_node_toolchain_lock(toolchain_path)
        except ValueError as exc:
            raise NodeHarborCompileError(str(exc)) from exc
        self.toolchain_path = toolchain_path
        self.artifact_resolver = artifact_resolver
        harbor_lock = toolchain_path.parent / self.toolchain.harbor.lock_file
        if not harbor_lock.is_file():
            raise NodeHarborCompileError(f"Harbor runner lock is missing: {harbor_lock}")
        digest = f"sha256:{hashlib.sha256(harbor_lock.read_bytes()).hexdigest()}"
        if digest != self.toolchain.harbor.lock_sha256:
            raise NodeHarborCompileError("Harbor runner lock digest does not match Node toolchain")
        if self.toolchain.status == "locked":
            runtime_digest = self._node_runtime_digest()
            if runtime_digest != self.toolchain.node_runtime_sha256:
                raise NodeHarborCompileError(
                    "locked Node toolchain runtime helper digest does not match"
                )
        requirements = toolchain_path.parent / self.toolchain.verifier_requirements_lock
        if not requirements.is_file():
            raise NodeHarborCompileError(f"verifier requirements lock is missing: {requirements}")
        if self.toolchain.verifier_requirements_sha256 is not None:
            digest = f"sha256:{hashlib.sha256(requirements.read_bytes()).hexdigest()}"
            if digest != self.toolchain.verifier_requirements_sha256:
                raise NodeHarborCompileError(
                    "verifier requirements lock digest does not match Node toolchain"
                )
        self.verifier_requirements_path = requirements

    @staticmethod
    def _node_runtime_digest() -> str:
        runtime_root = Path(__file__).parents[1] / "verification/node"
        digest = hashlib.sha256()
        for path in sorted(path for path in runtime_root.rglob("*") if path.is_file()):
            relative = path.relative_to(runtime_root).as_posix().encode("utf-8")
            digest.update(relative)
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        return f"sha256:{digest.hexdigest()}"

    def compile_task(
        self,
        source_dir: Path,
        output_root: Path,
        *,
        allow_incomplete: bool = False,
    ) -> Path:
        source = CatalogCompiler.load_task(source_dir)
        runtime = source.environment.runtime
        if runtime is None or runtime.language is not RuntimeLanguage.NODE:
            raise NodeHarborCompileError("Node compiler requires a canonical Node runtime")
        if runtime.package_manager is not self.runtime_package_manager:
            raise NodeHarborCompileError(
                "Node compiler requires package_manager="
                f"{self.runtime_package_manager.value}"
            )
        if source.harbor is None:
            raise NodeHarborCompileError("Node task source is missing [harbor] settings")
        if self.toolchain.status != "development-only" and allow_incomplete:
            raise NodeHarborCompileError(
                "allow_incomplete is only valid for development toolchains"
            )

        with tempfile.TemporaryDirectory(prefix="nl2repo-node-canonical-") as temporary:
            root = Path(temporary)
            compiled = CatalogCompiler(FileArtifactStore(root / "artifacts")).compile_task(
                source_dir, root / "canonical"
            )
            manifest = compiled.manifest
        gaps = manifest.publication_gaps()
        if gaps and not allow_incomplete:
            raise NodeHarborCompileError(
                "Node production output is unsupported until locked artifacts are supplied: "
                + ", ".join(gaps)
            )
        assert manifest.harbor is not None
        if not allow_incomplete and (
            manifest.harbor.agent_network_mode != "no-network"
            or manifest.harbor.agent_allowed_hosts
        ):
            raise NodeHarborCompileError(
                "production Agent runtime must be no-network with no static allowed hosts"
            )
        if self.toolchain.status == "development-only" and not allow_incomplete:
            raise NodeHarborCompileError(
                "Node toolchain is development-only; pass allow_incomplete for a fixture bundle"
            )
        if not allow_incomplete:
            if self.artifact_resolver is None:
                raise NodeHarborCompileError("private artifact resolver is required")
            try:
                self.artifact_resolver.assert_scope(
                    task_id=manifest.task_id,
                    manifest_digest=manifest.content_digest(),
                    purpose="compile",
                )
            except ArtifactStoreError as exc:
                raise NodeHarborCompileError(
                    f"private artifact authorization mismatch: {exc}"
                ) from exc

        final_root = output_root / manifest.task_id
        if final_root.exists() or final_root.is_symlink():
            raise NodeHarborCompileError(f"Harbor output already exists: {final_root}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary_prefix = re.sub(r"[^A-Za-z0-9._-]+", "_", manifest.task_id)
        temporary_root = Path(tempfile.mkdtemp(prefix=f".{temporary_prefix}-", dir=output_root))
        try:
            self._write_instruction(source_dir, source.instruction, temporary_root)
            self._write_environment(manifest, temporary_root, allow_incomplete)
            self._write_verifier(source_dir, manifest, temporary_root, allow_incomplete)
            self._write_solution(
                source_dir, manifest.oracle_bundle, temporary_root, allow_incomplete
            )
            self._write_controls(source_dir, temporary_root)
            self._write_task_toml(manifest, temporary_root)
            self._write_readme(manifest, temporary_root, allow_incomplete)
            self._write_bundle_manifest(manifest, temporary_root, allow_incomplete)
            final_root.parent.mkdir(parents=True, exist_ok=True)
            os.rename(temporary_root, final_root)
        except Exception:
            shutil.rmtree(temporary_root, ignore_errors=True)
            raise
        return final_root

    def prepare_control_bundle(
        self,
        task_root: Path,
        kind: str,
        output_root: Path,
    ) -> Path:
        """Create a supported Node control without mutating the source bundle."""

        if kind not in {
            "empty",
            "stub",
            "forgery",
            "hang",
            "timeout",
            "call-hang",
            "offline",
            "install-hang",
            "install-script",
            "loader-hook",
            "oversized-output",
        }:
            raise NodeHarborCompileError(f"unsupported control kind: {kind}")
        script = task_root / "controls" / f"{kind}.sh"
        if not script.is_file():
            raise NodeHarborCompileError(f"control script is missing: {script}")
        target_name = f"{task_root.name}-{kind}"
        target = output_root / target_name
        if target.exists() or target.is_symlink():
            raise NodeHarborCompileError(f"control output already exists: {target}")
        output_root.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{target_name}-", dir=output_root))
        try:
            self._copy_tree(task_root, temporary)
            solve = temporary / "solution/solve.sh"
            atomic_write(solve, script.read_bytes())
            os.chmod(solve, 0o755)
            self._refresh_bundle_manifest(temporary, kind)
            os.rename(temporary, target)
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True)
            raise
        return target

    def _write_controls(self, source_dir: Path, task_root: Path) -> None:
        controls = source_dir / "harbor/controls"
        if controls.is_dir():
            self._copy_tree(controls, task_root / "controls")

    def _write_node_runtime(self, destination: Path) -> None:
        """Copy only verifier-owned Node scripts; candidate installers stay Python."""

        source = Path(__file__).parents[1] / "verification/node"
        for relative in NODE_VERIFIER_FILES:
            path = source / relative
            if path.is_symlink() or not path.is_file():
                raise NodeHarborCompileError(f"Node verifier runtime file is missing: {relative}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target, path.read_bytes())

    def _write_node_python_adapter(self, destination: Path) -> None:
        """Package the reviewed Python Node installer and its minimal dependencies."""

        files = tuple(_PYTHON_VERIFIER_FILES) + (
            "verification/node_candidate_client.py",
            "verification/node_candidate_install.py",
            "harbor/node_dependencies.py",
            "harbor/__init__.py",
            "storage/files.py",
            "storage/__init__.py",
        )
        package_root = Path(__file__).parents[1]
        for relative in files:
            source = package_root / relative
            if source.is_symlink() or not source.is_file():
                raise NodeHarborCompileError(f"Node Python adapter file is missing: {relative}")
            target = destination / "nl2repobench" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target, source.read_bytes())

    @staticmethod
    def _write_npm_adapter(destination: Path) -> None:
        """Write the fixed Python entrypoint for npm candidate installation."""

        atomic_write(
            destination,
            b'''#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

sys.path.insert(0, "/opt/nl2repobench-node-adapter")
from nl2repobench.verification.node_candidate_install import install_candidate

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--target", type=Path, required=True)
parser.add_argument("--cache", type=Path, required=True)
args = parser.parse_args()
result = install_candidate(args.source, args.target, cache=args.cache)
raise SystemExit(0 if result.get("outcome") == "success" else (70 if result.get("outcome") == "internal-error" else 71))
''',
        )

    @staticmethod
    def _write_python_runtime_manifest_check(tests_root: Path) -> None:
        """Write the fixed image-side checker for the shared Python runtime."""

        atomic_write(
            tests_root / "python-runtime-manifest-check.py",
            b'''#!/usr/bin/env python3
import argparse
import hashlib
import json
import stat
from pathlib import Path, PurePosixPath

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
parser.add_argument("--manifest", type=Path, required=True)
args = parser.parse_args()
manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
root = args.root
if manifest.get("schema_version") != "1.0" or manifest.get("digest_algorithm") != "sha256:path-nul-raw-file-sha256-v1":
    raise SystemExit("invalid Python runtime manifest identity")
if manifest.get("runtime_root") != str(root):
    raise SystemExit("Python runtime manifest root mismatch")
entries = manifest.get("files")
if not isinstance(entries, list):
    raise SystemExit("Python runtime manifest files must be a list")
declared = set()
digest = hashlib.sha256()
for entry in entries:
    if not isinstance(entry, dict):
        raise SystemExit("invalid Python runtime manifest entry")
    relative = entry.get("path")
    if not isinstance(relative, str) or relative in declared:
        raise SystemExit("invalid or duplicate Python runtime path")
    path = PurePosixPath(relative)
    if path.is_absolute() or not relative or ".." in path.parts:
        raise SystemExit("Python runtime path escapes root")
    declared.add(relative)
    target = root / Path(*path.parts)
    metadata = target.lstat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise SystemExit("Python runtime entry is not a regular unique file")
    data = target.read_bytes()
    if (entry.get("type") != "file" or len(data) != entry.get("size_bytes") or
            stat.S_IMODE(metadata.st_mode) != entry.get("mode") or
            hashlib.sha256(data).hexdigest() != entry.get("sha256")):
        raise SystemExit("Python runtime entry metadata or digest mismatch")
    digest.update(relative.encode("utf-8"))
    digest.update(b"\\0")
    digest.update(hashlib.sha256(data).digest())
actual = set()
for path in root.rglob("*"):
    metadata = path.lstat()
    if stat.S_ISDIR(metadata.st_mode):
        continue
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise SystemExit("Python runtime contains an unsafe unlisted entry")
    actual.add(path.relative_to(root).as_posix())
if actual != declared or manifest.get("runtime_sha256") != "sha256:" + digest.hexdigest():
    raise SystemExit("Python runtime closed-tree digest mismatch")
''',
        )

    @staticmethod
    def _write_pnpm_adapter(destination: Path) -> None:
        """Write a trusted Python adapter using the shared Node supervisor."""

        atomic_write(
            destination,
            b'''#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, "/opt/nl2repobench-node-adapter")
from nl2repobench.verification.node_candidate_client import run_node_command

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--target", type=Path, required=True)
parser.add_argument("--store", type=Path, required=True)
args = parser.parse_args()
node = "/opt/nl2repobench-node/bin/node"
pnpm = "/opt/nl2repobench-node/lib/pnpm/bin/pnpm.cjs"
environment = {
    "HOME": str(args.target / "home"),
    "TMPDIR": str(args.target / "tmp"),
    "npm_config_cache": str(args.store),
    "npm_config_ignore_scripts": "true",
    "npm_config_offline": "true",
    "npm_config_auto_install_peers": "false",
    "npm_config_exclude_links_from_lockfile": "false",
}
def run(arguments: list[str], cwd: Path) -> None:
    result = run_node_command([node, pnpm, *arguments], cwd=cwd, write_root=args.target,
                              timeout_sec=90.0, environment=environment, context="install")
    if result.verifier_invalid:
        raise SystemExit(70)
    if result.returncode != 0:
        raise SystemExit(71)
run(["install", "--offline", "--frozen-lockfile", "--ignore-scripts", f"--store-dir={args.store}"], args.source)
run(["pack", "--pack-destination", str(args.target)], args.source)
tarballs = sorted(args.target.glob("*.tgz"))
if len(tarballs) != 1:
    raise SystemExit(71)
run(["install", str(tarballs[0]), "--offline", "--ignore-scripts", f"--store-dir={args.store}", f"--dir={args.target}"], args.target)
''',
        )

    def _write_instruction(self, source_dir: Path, relative: str, task_root: Path) -> None:
        try:
            write_instruction(source_dir, relative, task_root)
        except TaskWriterError as exc:
            raise NodeHarborCompileError(
                str(exc).replace("instruction", "Node instruction", 1)
            ) from exc

    def _write_environment(
        self, manifest: TaskManifest, task_root: Path, allow_incomplete: bool
    ) -> None:
        node_image = self._runtime_image(manifest)
        runtime_manifest = self._runtime_manifest_payload(
            node_image, allow_incomplete=allow_incomplete
        )
        runtime_manifest_check = self._runtime_manifest_check(node_image)
        atomic_write(
            task_root / "environment/node-runtime.manifest.json",
            json.dumps(runtime_manifest, sort_keys=True, separators=(",", ":")).encode()
            + b"\n",
        )
        agent_image = self.toolchain.agent_runtime.image
        system_checks = self._system_packages_check(manifest)
        dependency_setup = self._agent_dependency_setup()
        runtime_stage_extra = self._runtime_stage_extra(allow_incomplete)
        runtime_manifest_stage = self._runtime_manifest_stage(node_image, allow_incomplete)
        runtime_manifest_final = (
            "" if allow_incomplete else "COPY node-runtime.manifest.json "
            f"{NODE_RUNTIME_ROOT}/runtime.manifest.json\n"
        )
        dockerfile = f"""FROM --platform=linux/amd64 {node_image} AS node-runtime

RUN resolved_node="$(readlink -f /usr/local/bin/node)" \\
  && test -f "$resolved_node" \\
  && test "$(/usr/local/bin/node --version)" = "v{self.toolchain.runtime.runtime_version}" \\
  && mkdir -p {NODE_RUNTIME_ROOT}/bin {NODE_RUNTIME_ROOT}/lib \\
  && cp --dereference "$resolved_node" {NODE_EXECUTABLE} \\
  && cp -aL /usr/local/lib/node_modules/npm {NODE_RUNTIME_ROOT}/lib/npm \\
  && test -f {NODE_RUNTIME_ROOT}/lib/npm/bin/npm-cli.js \\
{runtime_stage_extra}  && chmod 0555 {NODE_EXECUTABLE} \\
  && find {NODE_RUNTIME_ROOT} -type f ! -path {NODE_EXECUTABLE} -exec chmod 0444 {{}} + \\
  && chmod -R a-w {NODE_RUNTIME_ROOT}
{runtime_manifest_stage}

FROM --platform=linux/amd64 {agent_image}

LABEL org.nl2repobench.agent-runtime-image="{agent_image}" \\
  org.nl2repobench.agent-runtime-image-id="{self.toolchain.agent_runtime.image_id}" \\
  org.nl2repobench.agent-dependency-build="npm-offline-bundle-v1"

COPY --from=node-runtime {NODE_RUNTIME_ROOT} {NODE_RUNTIME_ROOT}
{runtime_manifest_final}
RUN test -f {NODE_RUNTIME_ROOT}/runtime.manifest.json \
  && test -f {NODE_EXECUTABLE} \
  && test ! -L {NODE_EXECUTABLE} \
  && test "$( {NODE_EXECUTABLE} --version)" = "v{self.toolchain.runtime.runtime_version}" \
  && test "$( {NODE_EXECUTABLE} {NPM_LAUNCHER} --version)" = "{self.toolchain.runtime.npm_version}" \
  && test -x /opt/openhands-sdk-venv/bin/python

{runtime_manifest_check}

{system_checks}{dependency_setup}

WORKDIR /workspace
"""
        atomic_write(task_root / "environment/Dockerfile", dockerfile.encode())

    def _agent_dependency_setup(self) -> str:
        return """COPY npm-bundle /opt/npm-bundle
ENV npm_config_cache=/opt/npm-bundle/npm-cache \\
    npm_config_offline=true \\
    npm_config_ignore_scripts=true \\
    npm_config_audit=false \\
    npm_config_fund=false
"""

    def _runtime_stage_extra(self, allow_incomplete: bool) -> str:
        del allow_incomplete
        return ""

    def _runtime_manifest_stage(self, source_image: str, allow_incomplete: bool) -> str:
        if not allow_incomplete:
            return (
                "COPY node-runtime.manifest.json /tmp/node-runtime.manifest.json\n"
                f"RUN cp /tmp/node-runtime.manifest.json {NODE_RUNTIME_ROOT}/runtime.manifest.json\n"
            )
        values = {
            "source_image": source_image,
            "runtime_version": self.toolchain.runtime.runtime_version,
            "npm_version": self.toolchain.runtime.npm_version,
            "pnpm_version": self.toolchain.runtime.pnpm_version,
        }
        script = (
            "const f=require('fs'),c=require('crypto'),r='/opt/nl2repobench-node',"
            f"v={json.dumps(values,separators=(',', ':'))},a=[];"
            "const w=(d,p)=>{for(const e of f.readdirSync(d,{withFileTypes:true})){"
            "const q=d+'/'+e.name,x=p?p+'/'+e.name:e.name,s=f.lstatSync(q);"
            "if(e.isDirectory())w(q,x);else{if(!e.isFile()||s.nlink!==1)throw Error('unsafe runtime');"
            "const b=f.readFileSync(q),h=c.createHash('sha256').update(b).digest('hex');"
            "a.push({path:x,sha256:h,size_bytes:b.length,mode:s.mode&0o777,type:'file'})}}};"
            "w(r,'');a.sort((x,y)=>Buffer.from(x.path).compare(Buffer.from(y.path)));"
            "const h=c.createHash('sha256');for(const x of a){h.update(Buffer.from(x.path));"
            "h.update(Buffer.from([0]));h.update(Buffer.from(x.sha256,'hex'))}"
            "const by=new Map(a.map(x=>[x.path,x])),id=(name,path)=>({...by.get(path),name});"
            "const m={schema_version:'1.0',ecosystem:'node',platform:'linux/amd64',"
            "root:r,source_image:v.source_image,runtime_version:v.runtime_version,"
            "npm_version:v.npm_version,pnpm_version:v.pnpm_version,digest_algorithm:'sha256',"
            "files:a,executables:[id('node','bin/node')],launchers:[id('npm','lib/npm/bin/npm-cli.js')],"
            "tree_sha256:'sha256:'+h.digest('hex')};"
            "if(v.pnpm_version)m.launchers.push(id('pnpm','lib/pnpm/bin/pnpm.cjs'));"
            "f.writeFileSync(r+'/runtime.manifest.json',JSON.stringify(m)+String.fromCharCode(10))"
        )
        return f"RUN {NODE_EXECUTABLE} -e {shlex.quote(script)}\n"

    def _runtime_manifest_check(self, source_image: str) -> str:
        """Validate every staged file and the canonical tree digest in Docker."""

        expected = json.dumps(
            {
                "ecosystem": "node",
                "platform": "linux/amd64",
                "root": NODE_RUNTIME_ROOT,
                "source_image": source_image,
                "runtime_version": self.toolchain.runtime.runtime_version,
                "npm_version": self.toolchain.runtime.npm_version,
                "pnpm_version": self.toolchain.runtime.pnpm_version,
                "digest_algorithm": "sha256",
                "executables": [{"name": "node", "path": "bin/node"}],
                "launchers": [
                    {"name": "npm", "path": "lib/npm/bin/npm-cli.js"},
                    *(
                        [{"name": "pnpm", "path": "lib/pnpm/bin/pnpm.cjs"}]
                        if self.toolchain.runtime.pnpm_version is not None
                        else []
                    ),
                ],
            },
            separators=(",", ":"),
        )
        check = (
            "const fs=require('fs'),c=require('crypto'),r='/opt/nl2repobench-node',"
            f"m=JSON.parse(fs.readFileSync(r+'/runtime.manifest.json')),e={expected},a=[];"
            "for(const k of ['ecosystem','platform','root','source_image','runtime_version','npm_version','pnpm_version','digest_algorithm'])if(m[k]!==e[k])throw Error('runtime manifest identity mismatch: '+k);"
            "const w=(d,p)=>{for(const e of fs.readdirSync(d,{withFileTypes:true})){"
            "const q=d+'/'+e.name,x=p?p+'/'+e.name:e.name,s=fs.lstatSync(q);"
            "if(x==='runtime.manifest.json')continue;if(e.isDirectory())w(q,x);else{if(!e.isFile()||s.nlink!==1||(s.mode&0o6000))"
            "throw Error('unsafe runtime entry '+x);a.push(x)}}};w(r,'');a.sort();"
            "const f=m.files.map(x=>x.path);if(JSON.stringify(a)!==JSON.stringify(f))"
            "throw Error('runtime manifest file set mismatch');const h=c.createHash('sha256');"
            "for(const x of m.files){const q=r+'/'+x.path,s=fs.lstatSync(q),b=fs.readFileSync(q),"
            "z=c.createHash('sha256').update(b).digest('hex');if(s.size!==x.size_bytes||z!==x.sha256||"
            "(s.mode&0o777)!==x.mode)throw Error('runtime manifest file digest mismatch: '+x.path);"
            "h.update(Buffer.from(x.path));h.update(Buffer.from([0]));h.update(Buffer.from(z,'hex'))}"
            "if('sha256:'+h.digest('hex')!==m.tree_sha256)throw Error('runtime manifest tree digest mismatch');"
            "const identity=(x)=>x.map(y=>y.name+':'+y.path).sort().join(',');"
            "if(identity(m.executables||[])!==identity(e.executables)||identity(m.launchers||[])!==identity(e.launchers))throw Error('runtime manifest launcher identity mismatch');"
            "for(const x of [...(m.executables||[]),...(m.launchers||[])])if(!f.includes(x.path))"
            "throw Error('runtime identity is not in tree')"
        )
        return f"RUN {NODE_EXECUTABLE} -e {shlex.quote(check)}\n"

    def _runtime_image(self, manifest: TaskManifest) -> str:
        """Return the task-pinned Node image for production bundles."""

        if self.toolchain.status != "locked":
            return self.toolchain.images.agent_base
        environment = manifest.environment_lock
        if environment.base_image is None or environment.base_image_digest is None:
            raise NodeHarborCompileError("production Node image is not locked")
        image_name = environment.base_image.split("@", 1)[0]
        return f"{image_name}@{environment.base_image_digest}"

    @staticmethod
    def _system_packages_check(manifest: TaskManifest) -> str:
        checks: list[str] = []
        for requirement in manifest.environment_lock.system_packages:
            package, separator, version = requirement.partition("=")
            quoted_package = shlex.quote(package)
            if separator:
                checks.append(
                    "test \"$(dpkg-query -W -f='${Version}' "
                    f'{quoted_package})" = {shlex.quote(version)}'
                )
            else:
                checks.append(f"dpkg-query -W {quoted_package} >/dev/null")
        if not checks:
            return ""
        return "RUN " + " \\\n  && ".join(checks) + "\n\n"

    def _write_verifier(
        self,
        source_dir: Path,
        manifest: TaskManifest,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        tests_root = task_root / "tests"
        tests_root.mkdir(parents=True)
        runtime_root = tests_root / "runtime"
        runtime_root.mkdir()
        self._write_node_runtime(runtime_root / "node")
        self._write_python_verifier_runtime(tests_root)
        self._write_node_python_adapter(tests_root / "python-adapter")
        self._write_python_runtime_manifest_check(tests_root)
        self._write_npm_adapter(runtime_root / "node/install_npm.py")
        self._write_pnpm_adapter(runtime_root / "node/install_pnpm.py")
        command_plan = self._resolve_node_command_plan(manifest, allow_incomplete)
        atomic_write(
            tests_root / "command-plan.json",
            json.dumps(
                command_plan.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
            + b"\n",
        )

        dependencies_root = tests_root / "dependencies"
        dependencies_root.mkdir()
        if not allow_incomplete:
            self._validate_canonical_dependencies(manifest)
            raise NodeHarborCompileError(
                "private-staging-contract-missing: production npm closure staging requires F0.5"
            )
        else:
            self._write_empty_npm_bundle(dependencies_root)
        try:
            validate_npm_dependency_bundle(
                dependencies_root,
                expected_npm_version=self.toolchain.runtime.npm_version,
            )
        except NodeDependencyError as exc:
            raise NodeHarborCompileError(str(exc)) from exc
        self._copy_tree(dependencies_root, task_root / "environment/npm-bundle")

        private_root = tests_root / "private"
        if manifest.tests.test_bundle is not None and not allow_incomplete:
            self._extract_private_bundle(
                manifest.tests.test_bundle, private_root, ArchiveKind.TEST_BUNDLE
            )
        else:
            fixture = source_dir / "harbor/tests"
            if not fixture.is_dir():
                raise NodeHarborCompileError("development Node task is missing harbor/tests")
            self._copy_tree(fixture, private_root)

        image = self._runtime_image(manifest)
        python_image = self.toolchain.images.verifier_python_base
        runtime_manifest = self._runtime_manifest_payload(image, allow_incomplete=allow_incomplete)
        atomic_write(
            tests_root / "node-runtime.manifest.json",
            json.dumps(runtime_manifest, sort_keys=True, separators=(",", ":")).encode()
            + b"\n",
        )
        dockerfile = f"""FROM --platform=linux/amd64 {image} AS node-runtime

RUN resolved_node="$(readlink -f /usr/local/bin/node)" \\
  && test -f "$resolved_node" \\
  && test "$(/usr/local/bin/node --version)" = "v{self.toolchain.runtime.runtime_version}" \\
  && mkdir -p {NODE_RUNTIME_ROOT}/bin {NODE_RUNTIME_ROOT}/lib \\
  && cp --dereference "$resolved_node" {NODE_EXECUTABLE} \\
  && cp -a /usr/local/lib/node_modules/npm {NODE_RUNTIME_ROOT}/lib/npm \\
  && test -f {NODE_RUNTIME_ROOT}/lib/npm/bin/npm-cli.js \\
  && chmod 0555 {NODE_EXECUTABLE} \\
  && chmod -R a-w {NODE_RUNTIME_ROOT}
FROM --platform=linux/amd64 {python_image}

COPY --from=node-runtime {NODE_RUNTIME_ROOT} {NODE_RUNTIME_ROOT}
COPY node-runtime.manifest.json {NODE_RUNTIME_ROOT}/runtime.manifest.json
RUN test -f {NODE_RUNTIME_ROOT}/runtime.manifest.json \\
  && test -f {NODE_EXECUTABLE} \\
  && test ! -L {NODE_EXECUTABLE} \\
  && test "$( {NODE_EXECUTABLE} --version)" = "v{self.toolchain.runtime.runtime_version}" \\
  && test "$( {NODE_EXECUTABLE} {NPM_LAUNCHER} --version)" = "{self.toolchain.runtime.npm_version}"

COPY python-runtime /opt/nl2repobench-runtime
COPY python-runtime-manifest.json /tests/python-runtime-manifest.json
COPY python-runtime-manifest-check.py /tests/python-runtime-manifest-check.py
COPY python-adapter /opt/nl2repobench-node-adapter
COPY verifier-requirements.lock.txt /tmp/verifier-requirements.lock.txt
RUN /usr/local/bin/python3 -I -B /tests/python-runtime-manifest-check.py \
  --root /opt/nl2repobench-runtime/nl2repobench --manifest /tests/python-runtime-manifest.json
RUN python -m pip install --no-cache-dir --require-hashes \\
  -r /tmp/verifier-requirements.lock.txt
COPY dependencies /opt/npm-bundle
COPY runtime /tests/runtime
COPY command-plan.json /tests/command-plan.json
COPY --chmod=0500 private /tests/private
COPY --chmod=0555 test.sh /tests/test.sh
RUN useradd --uid 10001 --create-home candidate \\
  && chmod -R 0555 /opt/nl2repobench-runtime \\
  && chmod -R 0555 /opt/nl2repobench-node-adapter \\
  && chmod -R 0500 /tests/private \\
  && chmod -R 0555 /tests/runtime
WORKDIR /tests
"""
        atomic_write(tests_root / "Dockerfile", dockerfile.encode())
        atomic_write(
            tests_root / "docker-compose.yaml", b"services:\n  main:\n    network_mode: none\n"
        )
        atomic_write(tests_root / "test.sh", self._test_script(manifest).encode())
        os.chmod(tests_root / "test.sh", 0o755)

    def _runtime_manifest_payload(
        self, source_image: str, *, allow_incomplete: bool
    ) -> dict[str, Any]:
        """Load locked closure bytes, or emit an explicitly incomplete fixture envelope."""

        reference = self.toolchain.runtime.node_runtime_manifest
        path = self.toolchain_path.parent / reference
        if not allow_incomplete:
            if not path.is_file():
                raise NodeHarborCompileError(
                    f"Node runtime closure manifest is unavailable: {path}"
                )
            data = path.read_bytes()
            digest = f"sha256:{hashlib.sha256(data).hexdigest()}"
            if digest != self.toolchain.runtime.node_runtime_manifest_sha256:
                raise NodeHarborCompileError(
                    "Node runtime closure manifest digest does not match lock"
                )
            try:
                payload = json.loads(data)
            except json.JSONDecodeError as exc:
                raise NodeHarborCompileError(
                    "Node runtime closure manifest is not JSON"
                ) from exc
            try:
                validated = NodeRuntimeManifest.model_validate(payload)
            except ValueError as exc:
                raise NodeHarborCompileError(
                    f"Node runtime closure manifest is invalid: {exc}"
                ) from exc
            if validated.source_image != source_image:
                raise NodeHarborCompileError(
                    "Node runtime closure manifest image does not match lock"
                )
            if validated.tree_sha256 != self.toolchain.runtime.node_runtime_tree_sha256:
                raise NodeHarborCompileError(
                    "Node runtime closure tree digest does not match lock"
                )
            return cast(dict[str, Any], payload)
        return {
            "schema_version": "1.0",
            "ecosystem": "node",
            "platform": "linux/amd64",
            "root": NODE_RUNTIME_ROOT,
            "source_image": source_image,
            "runtime_version": self.toolchain.runtime.runtime_version,
            "npm_version": self.toolchain.runtime.npm_version,
            "pnpm_version": self.toolchain.runtime.pnpm_version,
            "digest_algorithm": "sha256",
            "files": [],
            "executables": [],
            "launchers": [],
            "tree_sha256": self.toolchain.runtime.node_runtime_tree_sha256,
        }

    def _resolve_node_command_plan(
        self,
        manifest: TaskManifest,
        allow_incomplete: bool,
    ) -> NodeVerifierCommandPlan:
        if allow_incomplete:
            return expected_node_command_plan(self.candidate_install_id)
        reference = manifest.tests.commands_artifact
        if reference is None or self.artifact_resolver is None:
            raise NodeHarborCompileError("production Node task requires commands_artifact")
        if reference.media_type != "application/vnd.nl2repobench.command-plan+json":
            raise NodeHarborCompileError("canonical runtime requires command-plan media type")
        try:
            data = self.artifact_resolver.read_bytes(reference, max_bytes=4 * 1024 * 1024)
            return load_node_command_plan(
                data,
                candidate_install=self.candidate_install_id,  # type: ignore[arg-type]
            )
        except (ArtifactStoreError, OSError, ValueError) as exc:
            raise NodeHarborCompileError(f"invalid Node command plan: {exc}") from exc

    def _validate_canonical_dependencies(self, manifest: TaskManifest) -> None:
        if self.artifact_resolver is None:
            raise NodeHarborCompileError("private artifact resolver is required")
        try:
            validated = validate_dependency_artifacts(
                manifest.dependency_bundle,
                identity=f"node+{self.runtime_package_manager.value}",
                toolchain_digest=(
                    f"sha256:{hashlib.sha256(self.toolchain_path.read_bytes()).hexdigest()}"
                ),
                resolver=self.artifact_resolver,
            )
        except DependencyContractError as exc:
            raise NodeHarborCompileError(str(exc)) from exc
        expected_lock = (
            "package-lock.json"
            if self.runtime_package_manager is PackageManager.NPM
            else "pnpm-lock.yaml"
        )
        if set(validated.lock_files) != {expected_lock}:
            raise NodeHarborCompileError(
                f"canonical Node dependency lock must contain only {expected_lock}"
            )
        runtime = manifest.environment_lock.runtime
        assert runtime is not None and runtime.package_manager_version is not None
        try:
            if self.runtime_package_manager is PackageManager.NPM:
                validate_npm_lock_data(
                    validated.lock_files[expected_lock],
                    expected_npm_version=runtime.package_manager_version,
                )
            else:
                validate_pnpm_lock_data(
                    validated.lock_files[expected_lock],
                    expected_toolchain=runtime.package_manager_version,
                )
        except (NodeDependencyError, ValueError) as exc:
            raise NodeHarborCompileError(f"invalid canonical Node lock: {exc}") from exc

    def _write_python_verifier_runtime(self, tests_root: Path) -> None:
        try:
            copy_python_verifier_runtime(tests_root / "python-runtime")
        except TaskWriterError as exc:
            raise NodeHarborCompileError(str(exc)) from exc
        atomic_write(
            tests_root / "python-runtime-manifest.json",
            json.dumps(
                python_runtime_manifest(
                    tests_root / "python-runtime/nl2repobench",
                    runtime_root="/opt/nl2repobench-runtime/nl2repobench",
                ),
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
            + b"\n",
        )
        atomic_write(
            tests_root / "verifier-requirements.lock.txt",
            self.verifier_requirements_path.read_bytes(),
        )

    def _write_empty_npm_bundle(self, root: Path) -> None:
        atomic_write(
            root / "package-lock.json",
            b'{"lockfileVersion":3,"packages":{"":{"name":"node-synthetic","version":"2.0.0"}}}\n',
        )
        (root / "npm-cache").mkdir()
        manifest = {
            "schema_version": "1.0",
            "ecosystem": "npm",
            "lockfile_version": "3",
            "package_manager": "npm",
            "package_manager_version": self.toolchain.runtime.npm_version,
            "install_mode": "offline",
            "lifecycle_scripts": "ignore-scripts",
            "cache_entries": [],
            "files": [],
        }
        atomic_write(
            root / "bundle.manifest.json", json.dumps(manifest, sort_keys=True).encode() + b"\n"
        )

    def _write_solution(
        self,
        source_dir: Path,
        oracle_bundle: ArtifactRef | None,
        task_root: Path,
        allow_incomplete: bool,
    ) -> None:
        solution_root = task_root / "solution"
        if oracle_bundle is not None and not allow_incomplete:
            self._extract_private_bundle(oracle_bundle, solution_root, ArchiveKind.ORACLE_BUNDLE)
        else:
            fixture = source_dir / "harbor/solution"
            if not fixture.is_dir():
                raise NodeHarborCompileError("development Node task is missing harbor/solution")
            self._copy_tree(fixture, solution_root)
        solve = solution_root / "solve.sh"
        if not solve.is_file() or solve.is_symlink():
            raise NodeHarborCompileError("Node Oracle bundle must contain solve.sh")
        os.chmod(solve, 0o755)

    def _write_task_toml(self, manifest: TaskManifest, task_root: Path) -> None:
        assert manifest.harbor is not None
        runtime = manifest.environment_lock.runtime
        metadata = {
            "difficulty": manifest.metadata.difficulty,
            "category": manifest.metadata.category,
            "tags": list(manifest.metadata.tags),
            "language": "node",
            "runtime": "node",
            "runtime_version": runtime.version
            if runtime is not None
            else self.toolchain.runtime.runtime_version,
            "package_manager": self.runtime_package_manager.value,
            "package_manager_version": runtime.package_manager_version
            if runtime is not None
            else self.toolchain.runtime.npm_version,
            "test_framework": "node:test",
            "metric_contract": manifest.metric.contract_id,
            "expected_test_count": manifest.tests.expected_total,
            "canonical_manifest_digest": manifest.content_digest(),
            "toolchain_lock_digest": self.toolchain.content_digest(),
        }
        data: dict[str, Any] = {
            "schema_version": self.toolchain.harbor.task_schema,
            "artifacts": [manifest.harbor.workspace_artifact],
            "task": {
                "name": self._harbor_task_name(manifest.task_id),
                "version": manifest.version,
                "description": manifest.harbor.description,
                "authors": [{"name": "NL2RepoBench"}],
                "keywords": list(manifest.harbor.keywords),
            },
            "metadata": metadata,
            "agent": {"timeout_sec": manifest.harbor.agent_timeout_sec},
            "verifier": {
                "timeout_sec": manifest.harbor.verifier_timeout_sec,
                "environment_mode": "separate",
                "network_mode": "no-network",
                "environment": {
                    "network_mode": "no-network",
                    "build_timeout_sec": 600.0,
                    "cpus": 1,
                    "memory_mb": max(1024, manifest.harbor.memory_mb // 2),
                    "storage_mb": max(4096, manifest.harbor.storage_mb * 2),
                },
            },
            "environment": {
                "network_mode": manifest.harbor.agent_network_mode,
                "build_timeout_sec": 600.0,
                "cpus": manifest.harbor.cpus,
                "memory_mb": manifest.harbor.memory_mb,
                "storage_mb": manifest.harbor.storage_mb,
            },
        }
        if manifest.harbor.agent_network_mode == "allowlist":
            # Harbor only accepts allowed_hosts in allowlist mode. The catalog
            # schema has already restricted these to exact registry hostnames.
            data["environment"]["allowed_hosts"] = list(manifest.harbor.agent_allowed_hosts)
        atomic_write(task_root / "task.toml", tomli_w.dumps(data).encode())

    @staticmethod
    def _harbor_task_name(task_id: str) -> str:
        """Map an npm task id to Harbor's single-slash package name grammar."""

        if task_id.startswith("@"):
            scope, package = task_id[1:].split("/", 1)
            return f"nl2repobench/{scope}-{package}"
        return f"nl2repobench/{task_id}"

    def _test_script(self, manifest: TaskManifest) -> str:
        assert manifest.harbor is not None
        expected = manifest.tests.expected_total
        return f"""#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/grading.json \
  /logs/verifier/report.json /logs/verifier/network.json
rm -rf /tmp/candidate-source /tmp/candidate-site /tmp/npm-cache

PYTHON=/usr/local/bin/python3
PYTHON_ENV=(env -i PATH=/usr/bin:/bin HOME=/nonexistent PYTHONDONTWRITEBYTECODE=1)
NETWORK_CHECK='import sys; sys.path.insert(0, "/opt/nl2repobench-runtime");'
NETWORK_CHECK+='from nl2repobench.verification.network_check import main; main()'
"${{PYTHON_ENV[@]}}" "$PYTHON" -I -B -c "$NETWORK_CHECK" \
  --output /logs/verifier/network.json
network_exit=$?
if [[ "$network_exit" -eq 1 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason verifier-network-available \\
    --output /logs/verifier
  exit 0
elif [[ "$network_exit" -ne 0 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason verifier-internal-error \\
    --output /logs/verifier
  exit 0
fi

install -d -o candidate -g candidate -m 0700 /tmp/npm-cache
cp -a /opt/npm-bundle/npm-cache/. /tmp/npm-cache/
chown -R candidate:candidate /tmp/npm-cache

if ! {NODE_EXECUTABLE} /tests/runtime/node/copy_workspace.mjs \\
  --source /workspace \\
  --destination /tmp/candidate-source; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason candidate-workspace-rejected \\
    --output /logs/verifier
  exit 0
fi
mkdir -p /tmp/candidate-site /tmp/candidate-site/home /tmp/candidate-site/tmp
chown -R candidate:candidate /tmp/candidate-source /tmp/candidate-site
install_exit=0
/usr/local/bin/python3 -I -B /tests/runtime/node/install_npm.py \\
  --source /tmp/candidate-source --target /tmp/candidate-site --cache /tmp/npm-cache || install_exit=$?
if [[ "$install_exit" -eq 70 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason verifier-internal-error \\
    --output /logs/verifier
  exit 0
elif [[ "$install_exit" -ne 0 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason candidate-installation-failed \\
    --output /logs/verifier
  exit 0
fi
tarball=$(find /tmp/candidate-site -maxdepth 1 -name '*.tgz' -type f | head -1)
if [[ -z "$tarball" ]] || ! {NODE_EXECUTABLE} /tests/runtime/node/validate-package.mjs "$tarball"; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason candidate-installation-failed \\
    --output /logs/verifier
  exit 0
fi

export NODE_CANDIDATE_SITE=/tmp/candidate-site
export NODE_TEST_CLIENT=/tests/private/test_client.mjs
if ! {NODE_EXECUTABLE} /tests/runtime/node/validate-command-plan.mjs \\
  --path /tests/command-plan.json; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason verifier-internal-error \\
    --output /logs/verifier
  exit 0
fi
runner_exit_code=0
{NODE_EXECUTABLE} /tests/runtime/node/run_tests.mjs \\
  --tests /tests/private \\
  --candidate /tmp/candidate-site \\
  --expected {expected} \\
  --output /logs/verifier/report.json || runner_exit_code=$?
if [[ "$runner_exit_code" -eq 70 ]]; then
  {NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs \\
    --expected {expected} \\
    --reason candidate-call-failed \\
    --output /logs/verifier
  exit 0
fi
{NODE_EXECUTABLE} /tests/runtime/node/grade-report.mjs \\
  --expected {expected} \\
  --report /logs/verifier/report.json \\
  --runner-exit-code "$runner_exit_code" \\
  --output /logs/verifier
exit 0
"""

    def _extract_private_bundle(
        self, reference: ArtifactRef, destination: Path, kind: ArchiveKind
    ) -> None:
        try:
            extract_private_bundle(
                reference,
                destination,
                kind=kind,
                artifact_resolver=self.artifact_resolver,
                limits=BundleLimits(
                    max_members=self.MAX_BUNDLE_MEMBERS,
                    max_member_bytes=self.MAX_BUNDLE_MEMBER_BYTES,
                    max_total_bytes=self.MAX_BUNDLE_TOTAL_BYTES,
                ),
            )
        except TaskWriterError as exc:
            raise NodeHarborCompileError(str(exc)) from exc

    def _copy_tree(self, source: Path, destination: Path) -> None:
        try:
            copy_tree(source, destination)
        except TaskWriterError as exc:
            raise NodeHarborCompileError(str(exc)) from exc

    def _write_readme(
        self, manifest: TaskManifest, task_root: Path, allow_incomplete: bool
    ) -> None:
        mode = "development-only fixture" if allow_incomplete else "production"
        text = f"""# `{manifest.task_id}` Harbor Bundle

Generated by the additive Node/npm compiler.

- Mode: {mode}
- Node runtime: `{self.toolchain.runtime.runtime_version}`
- npm: `{self.toolchain.runtime.npm_version}`
- Image lock: `{self.toolchain.status}`
- Metric: `{manifest.metric.contract_id}`
- Expected leaf tests: `{manifest.tests.expected_total}`
- Verifier: separate environment, no network

"""
        atomic_write(task_root / "README.md", text.encode())

    def _write_bundle_manifest(
        self, manifest: TaskManifest, task_root: Path, allow_incomplete: bool
    ) -> None:
        payload = {
            "task_id": manifest.task_id,
            "task_version": manifest.version,
            "mode": "development" if allow_incomplete else "production",
            "canonical_manifest_digest": manifest.content_digest(),
            "toolchain_lock_digest": self.toolchain.content_digest(),
            "private_artifacts": categorized_private_artifacts(manifest).model_dump(mode="json"),
        }
        write_file_manifest(
            task_root, payload=payload, schema_version=NODE_BUNDLE_MANIFEST_SCHEMA
        )

    def _refresh_bundle_manifest(self, task_root: Path, kind: str) -> None:
        path = task_root / "bundle.manifest.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise NodeHarborCompileError(f"invalid source bundle manifest: {path}: {exc}") from exc
        payload["mode"] = f"control-{kind}"
        payload.pop("files", None)
        payload.pop("schema_version", None)
        write_file_manifest(
            task_root, payload=payload, schema_version=NODE_BUNDLE_MANIFEST_SCHEMA
        )
