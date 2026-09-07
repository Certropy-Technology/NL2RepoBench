from __future__ import annotations

import os
import subprocess
from pathlib import Path


def main() -> int:
    candidate = Path(os.environ["NL2REPO_RUST_CANDIDATE"]).resolve()
    adapter = Path("/tmp/rustc-hash-adapter")
    hidden = Path("/tmp/rustc-hash-hidden")
    for path in (adapter, hidden):
        subprocess.run(["rm", "-rf", str(path)], check=True)
        (path / "src").mkdir(parents=True)
    (adapter / "src/main.rs").write_bytes((Path(__file__).parent / "src/adapter.rs").read_bytes())
    (hidden / "src/main.rs").write_bytes((Path(__file__).parent / "src/main.rs").read_bytes())
    (adapter / "Cargo.toml").write_text(
        "[package]\nname=\"rustc_hash_adapter\"\nversion=\"0.1.0\"\nedition=\"2021\"\n[dependencies]\nrustc-hash={path=\"%s\"}\n" % candidate,
        encoding="utf-8",
    )
    (hidden / "Cargo.toml").write_text("[package]\nname=\"rustc_hash_hidden\"\nversion=\"0.1.0\"\nedition=\"2021\"\n", encoding="utf-8")
    env = os.environ.copy(); env.update({"CARGO_NET_OFFLINE": "true", "CARGO_TERM_COLOR": "never"})
    for path in (adapter, hidden):
        lock = subprocess.run(["/usr/local/cargo/bin/cargo", "generate-lockfile", "--offline", "--manifest-path", str(path / "Cargo.toml")], cwd=path, env=env, capture_output=True, text=True, timeout=60)
        if lock.returncode: return 1
    build = subprocess.run(["/usr/local/cargo/bin/cargo", "build", "--locked", "--offline", "--manifest-path", str(adapter / "Cargo.toml")], cwd=adapter, env=env, capture_output=True, text=True, timeout=300)
    if build.returncode: return 1
    adapter_bin = adapter / "target/debug/rustc_hash_adapter"
    run = subprocess.run(["/usr/local/cargo/bin/cargo", "run", "--locked", "--offline", "--manifest-path", str(hidden / "Cargo.toml")], cwd=hidden, env={**env, "NL2REPO_RUST_ADAPTER": str(adapter_bin)}, capture_output=True, text=True, timeout=300)
    if run.returncode: return 1
    print(run.stdout.strip().splitlines()[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
