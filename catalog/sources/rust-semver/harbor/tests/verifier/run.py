from __future__ import annotations

import json
import os
import pwd
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

# The frozen public denominator: 25 bridge scenarios plus one feature leaf that
# run.py evaluates itself. Every failure path must report all 26 leaves.
EXPECTED = [
    "version-parse-canonical",
    "version-leading-zero-and-structure-errors",
    "version-whitespace-and-empty-segment-errors",
    "version-overflow-and-charset-errors",
    "prerelease-and-build-metadata-acceptance",
    "ord-versus-precedence-with-build",
    "semver-precedence-chain",
    "constructors-traits-and-debug",
    "requirement-parse-canonical",
    "requirement-parse-errors",
    "comparator-normalization-projection",
    "caret-semantics",
    "tilde-semantics",
    "wildcard-and-exact-semantics",
    "comparison-operators-and-intersection",
    "prerelease-matching-rule",
    "build-metadata-ignored-in-matching",
    "prerelease-validation",
    "build-metadata-validation",
    "requirement-default-and-star",
    "error-trait-contract",
    "display-roundtrip-stability",
    "auto-trait-surface",
    "identifier-ordering",
    "comparator-level-matching",
]
FEATURE_LEAF = "feature-compatibility"
LEAF_IDS = [f"semver.{name}" for name in EXPECTED] + [f"semver.{FEATURE_LEAF}"]
REPORT_FORMAT = "rust-semver-bridge-v1"

MAX_LINE_BYTES = 64 * 1024
MAX_PIPE_BYTES = 4 * 1024 * 1024


def report(message: str) -> str:
    """Always emit the full frozen denominator; candidate failures score zero."""
    note = "".join(c for c in message if c not in '"\\\n\r\t')[:200]
    leaves = [{"id": leaf, "status": "failed", "message": note} for leaf in LEAF_IDS]
    return json.dumps(
        {"schema_version": "1.0", "framework": "rust",
         "report_format": REPORT_FORMAT, "leaves": leaves},
        separators=(",", ":"),
    )


def bounded_pipe(command, cwd, env, timeout):
    """Run a process, capping each stream and always reaping its group."""
    process = subprocess.Popen(
        command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
    )
    outputs = {process.stdout.fileno(): bytearray(), process.stderr.fileno(): bytearray()}
    import selectors
    selector = selectors.DefaultSelector()
    SPAWNED_GROUPS.add(process.pid)
    selector.register(process.stdout, selectors.EVENT_READ)
    selector.register(process.stderr, selectors.EVENT_READ)
    try:
        deadline = time.monotonic() + timeout
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                return None
            for key, _ in selector.select(min(remaining, 0.25)):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                buffer = outputs[key.fileobj.fileno()]
                if len(buffer) + len(chunk) > MAX_PIPE_BYTES:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    return subprocess.CompletedProcess(command, 125, bytes(outputs[process.stdout.fileno()]), b"output limit exceeded")
                buffer.extend(chunk)
        process.wait()
        return subprocess.CompletedProcess(
            command, process.returncode,
            bytes(outputs[process.stdout.fileno()]),
            bytes(outputs[process.stderr.fileno()]),
        )
    finally:
        sweep_group(process.pid)
        SPAWNED_GROUPS.discard(process.pid)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        selector.close()


# Process groups this verifier actually spawned. Cleanup is scoped to them on
# purpose: a global uid-based sweep would reach into unrelated concurrent
# Harbor tasks that share the numeric candidate uid on a shared host.
SPAWNED_GROUPS: set[int] = set()


def reap_groups() -> None:
    """Kill only the process groups we created, then reap them."""
    for pgid in list(SPAWNED_GROUPS):
        try:
            os.killpg(pgid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    SPAWNED_GROUPS.clear()


def sweep_group(pgid: int) -> None:
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def freeze_tree(root: Path) -> bool:
    """Refuse symlinks/special files and make everything root-owned read-only."""
    for path in (root, *root.rglob("*")):
        try:
            info = path.lstat()
        except OSError:
            return False
        import stat as stat_module
        if stat_module.S_ISLNK(info.st_mode):
            return False
        if not (stat_module.S_ISREG(info.st_mode) or stat_module.S_ISDIR(info.st_mode)):
            return False
        try:
            os.chown(path, 0, 0, follow_symlinks=False)
            os.chmod(path, 0o555 if path.is_dir() else 0o444, follow_symlinks=False)
        except OSError:
            return False
        if path.lstat().st_mode & 0o222:
            return False
    return True


def safe_workspace(candidate: Path) -> bool:
    """Reject candidate trees containing links or non-regular entries."""
    import stat as stat_module
    for path in (candidate, *candidate.rglob("*")):
        try:
            info = path.lstat()
        except OSError:
            return False
        if path == candidate:
            continue
        if stat_module.S_ISLNK(info.st_mode):
            return False
        if not (stat_module.S_ISREG(info.st_mode) or stat_module.S_ISDIR(info.st_mode)):
            return False
    return True


def main() -> int:
    candidate = Path(os.environ.get("NL2REPO_RUST_CANDIDATE", ""))
    if candidate.is_symlink() or not candidate.is_dir():
        print(report("candidate workspace is missing"))
        return 0
    if not (candidate / "Cargo.toml").is_file() or not (candidate / "src" / "lib.rs").is_file():
        print(report("candidate Cargo.toml or src/lib.rs is missing"))
        return 0
    if not safe_workspace(candidate):
        print(report("candidate workspace contains a symlink or special file"))
        return 0

    account = pwd.getpwnam("candidate") if os.geteuid() == 0 else None

    # runuser resets PATH, so the locked toolchain must be absolute and explicit.
    cargo = "/usr/local/cargo/bin/cargo"
    rustc = "/usr/local/cargo/bin/rustc"
    if not (Path(cargo).is_file() and Path(rustc).is_file()):
        cargo = shutil.which("cargo") or cargo
        rustc = shutil.which("rustc") or rustc
    if not (Path(cargo).is_file() and Path(rustc).is_file()):
        print(report("locked Rust toolchain is unavailable"))
        return 0

    root = Path(tempfile.mkdtemp(prefix="rust-semver-bridge-"))
    feature = Path(tempfile.mkdtemp(prefix="rust-semver-feature-"))
    try:
        # runuser resets PATH, and the trusted CARGO_HOME is root-owned, so the
        # candidate builds inside a private, writable cargo home. It is still
        # pinned to the image's vendored store, so no network resolution exists.
        private_cargo_home = root / "cargo-home"
        private_cargo_home.mkdir()
        trusted_home = Path(os.environ.get("CARGO_HOME", "/opt/nl2repo-cargo"))
        vendor = trusted_home / "vendor"
        if not vendor.is_dir():
            vendor = Path("/opt/nl2repo-cargo/vendor")
        if vendor.is_dir():
            shutil.copytree(vendor, private_cargo_home / "vendor", symlinks=False)
            (private_cargo_home / "config.toml").write_text(
                "[source.crates-io]\nreplace-with = \"vendored-sources\"\n\n"
                "[source.vendored-sources]\ndirectory = \"%s\"\n"
                % (private_cargo_home / "vendor"),
                encoding="utf-8",
            )
        env = {
            **os.environ,
            "PATH": "/usr/local/cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "CARGO_HOME": str(private_cargo_home),
            "CARGO_NET_OFFLINE": "true",
            "CARGO_TERM_COLOR": "never",
            "CARGO_INCREMENTAL": "0",
            "RUSTUP_HOME": os.environ.get("RUSTUP_HOME", "/usr/local/rustup"),
            "RUSTUP_TOOLCHAIN": "",
        }
        prefix = ["runuser", "-u", "candidate", "--"] if account is not None else []
        verifier = Path(__file__).parent

        # 1. Build the candidate as a path dependency in a scratch package.
        build_root = root / "build"
        (build_root / "src").mkdir(parents=True)
        (build_root / "src" / "main.rs").write_text("fn main() {}\n", encoding="utf-8")
        # The agent's own workspace legitimately contains a root-owned target/
        # from running cargo check. Copying it would hand the unprivileged build
        # root-owned stale artifacts it cannot replace, so build outputs and VCS
        # metadata are excluded and the crate is rebuilt from source.
        shutil.copytree(
            candidate,
            build_root / "candidate",
            symlinks=False,
            ignore=shutil.ignore_patterns("target", ".git", "*.rlib", "*.rmeta"),
        )
        (build_root / "Cargo.toml").write_text(
            '[package]\nname = "semver_bridge_build"\nversion = "0.1.0"\nedition = "2021"\n'
            'publish = false\n\n[dependencies]\nsemver = { path = "candidate" }\n',
            encoding="utf-8",
        )
        target = root / "target"
        target.mkdir()
        env["CARGO_TARGET_DIR"] = str(target)
        # The scratch root must be traversable (not listable) by the candidate so
        # it can reach its own build, cargo home and target directories. The
        # checker directory stays root-only below.
        os.chmod(root, 0o711)
        if account is not None:
            for path in (build_root, private_cargo_home, target,
                         *build_root.rglob("*"), *private_cargo_home.rglob("*"),
                         *target.rglob("*")):
                try:
                    os.chown(path, account.pw_uid, account.pw_gid)
                except OSError:
                    pass
        lock = bounded_pipe(prefix + [cargo, "generate-lockfile", "--offline",
                                     "--manifest-path", str(build_root / "Cargo.toml")],
                            build_root, env, 90)
        if lock is None or lock.returncode != 0:
            print(report("candidate Cargo.lock generation failed or timed out"))
            return 0
        build = bounded_pipe(prefix + [cargo, "build", "--locked", "--offline",
                                       "--manifest-path", str(build_root / "Cargo.toml")],
                             build_root, env, 300)
        if build is None or build.returncode != 0:
            print(report("candidate library build failed or timed out"))
            return 0
        libs = sorted((target / "debug" / "deps").glob("libsemver-*.rlib"))
        if len(libs) != 1:
            print(report("candidate library artifact is missing or ambiguous"))
            return 0

        # 2. Feature leaf: a separate no_std consumer must compile offline.
        (feature / "src").mkdir(parents=True)
        (feature / "src" / "lib.rs").write_text(
            '#![no_std]\nextern crate alloc;\n',
            encoding="utf-8",
        )
        (feature / "Cargo.toml").write_text(
            '[package]\nname = "semver_feature_check"\nversion = "0.1.0"\nedition = "2018"\n'
            'publish = false\n\n[dependencies]\nsemver = { path = '
            + json.dumps(str(build_root / "candidate"))
            + ', default-features = false }\n',
            encoding="utf-8",
        )
        if account is not None:
            for path in (feature, *feature.rglob("*")):
                try:
                    os.chown(path, account.pw_uid, account.pw_gid)
                except OSError:
                    pass
        feature_lock = bounded_pipe(prefix + [cargo, "generate-lockfile", "--offline",
                                             "--manifest-path", str(feature / "Cargo.toml")],
                                    feature, env, 90)
        feature_ok = False
        if feature_lock is not None and feature_lock.returncode == 0:
            checked = bounded_pipe(prefix + [cargo, "check", "--locked", "--offline",
                                             "--manifest-path", str(feature / "Cargo.toml")],
                                   feature, env, 240)
            feature_ok = bool(checked is not None and checked.returncode == 0)

        # 3. Freeze the candidate-derived tree before any trusted linking.
        if not freeze_tree(build_root / "candidate"):
            print(report("candidate tree is not freezable as read-only"))
            return 0

        # 4. Compile the candidate-linked adapter and the candidate-free checker.
        adapter_dir = root / "adapter"
        hidden_dir = root / "hidden"
        adapter_dir.mkdir()
        hidden_dir.mkdir()
        shutil.copyfile(verifier / "src" / "adapter.rs", adapter_dir / "adapter.rs")
        shutil.copyfile(verifier / "src" / "main.rs", hidden_dir / "main.rs")
        adapter_bin = adapter_dir / "adapter"
        checker_bin = hidden_dir / "bridge"
        compiled_adapter = bounded_pipe(
            [rustc, "--edition=2018", str(adapter_dir / "adapter.rs"),
             "--extern", f"semver={libs[0]}",
             "-L", f"dependency={target / 'debug' / 'deps'}",
             "-o", str(adapter_bin)],
            adapter_dir, env, 240)
        if compiled_adapter is None or compiled_adapter.returncode != 0:
            print(report("candidate adapter compilation failed"))
            return 0
        compiled_checker = bounded_pipe(
            [rustc, "--edition=2018", str(hidden_dir / "main.rs"), "-o", str(checker_bin)],
            hidden_dir, env, 240)
        if compiled_checker is None or compiled_checker.returncode != 0:
            print(report("trusted checker compilation failed"))
            return 0

        # 5. Least privilege: checker and its expected values are root-only.
        for path in (adapter_dir, adapter_bin, hidden_dir, checker_bin):
            os.chown(path, 0, 0)
        os.chmod(adapter_bin, 0o111)
        os.chmod(hidden_dir, 0o500)
        os.chmod(checker_bin, 0o500)
        env["NL2REPO_RUST_ADAPTER"] = str(adapter_bin)
        result = bounded_pipe([str(checker_bin)], root, env, 300)
        if result is None or result.returncode != 0:
            print(report("candidate bridge execution failed or timed out"))
            return 0
        if len(result.stdout) > MAX_PIPE_BYTES:
            print(report("bridge output exceeded the verifier bound"))
            return 0
        try:
            payload = json.loads(result.stdout.decode("utf-8").strip().splitlines()[-1])
        except (UnicodeDecodeError, IndexError, json.JSONDecodeError):
            print(report("trusted bridge emitted a malformed report"))
            return 0

        # 6. The checker, not the candidate, owns the report's shape.
        leaves = payload.get("leaves") if isinstance(payload, dict) else None
        if not isinstance(leaves, list) or payload.get("report_format") != REPORT_FORMAT:
            print(report("bridge report has an unexpected shape"))
            return 0
        ids = [leaf.get("id") for leaf in leaves if isinstance(leaf, dict)]
        if ids != LEAF_IDS:
            print(report("bridge report leaf ids do not match the frozen set"))
            return 0
        # The checker cannot raise the feature leaf; only run.py's own offline
        # no-std cargo check decides it.
        statuses = ["passed" if leaf.get("status") == "passed" else "failed" for leaf in leaves]
        statuses[-1] = "passed" if feature_ok else "failed"
        print(json.dumps(
            {"schema_version": "1.0", "framework": "rust", "report_format": REPORT_FORMAT,
             "leaves": [{"id": leaf_id, "status": status}
                        for leaf_id, status in zip(LEAF_IDS, statuses)]},
            separators=(",", ":"),
        ))
        return 0
    finally:
        reap_groups()
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(feature, ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        reap_groups()
