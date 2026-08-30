# Rust/Cargo -> Harbor Task 最终实施规格 R9

状态：`approved-design / implementation-blocked`

日期：2026-08-30

目标：F0、F0.5、F1 完整集成后的 generic `rust+cargo` Harbor lane

规范边界：本文件定义完整实现合同；它不是 F0/F1、镜像、Miri、Harbor、Oracle、controls、pilot 或 publication 通过证据。

## 1. 权威合同、当前事实与硬阻塞

本规格继承且不修改以下产品决策：

- `catalog/sources/<task-id>/` 是 human-owned authoring truth；最终 production task 是 compiler-generated、refs-only、提交在 `main/catalog/tasks/<task-id>/` 的 Harbor projection。
- Rust 是 generic platform support，不是 crate-specific harness。
- F0/F0.5/F1 是 Rust synthetic proof 的共同硬门禁。共同门禁通过后，Rust synthetic proof 可与 Java vertical 并行；Rust real production/pilot/publication 必须等待 Java pilot。
- Rust v1 固定 Linux/amd64、`x86_64-unknown-linux-gnu`、单 Cargo package、一个 release-wide toolchain profile、task-specific exact feature profile、frozen candidate dependency set。
- library surface为 scalar/string/bytes/list/map/struct/enum、sync/async function、bounded opaque state handle；CLI只包含 args/stdin/stdout/stderr/exit/tempdir。
- candidate-owned build.rs、proc-macro crate、Cargo config、linker、rustflags、FFI/link/asm/global allocator均拒绝。frozen dependency-owned build.rs/proc macro可在 hash-bound、offline、untrusted isolation中运行。
- bounded serializable unsafe function不跨 bridge传 pointer/reference；每个 unsafe leaf使用 fresh process；Miri只作 Oracle validity gate；不产生 memory-safety score或claim。
- stable custom JSON由Rust normalizer转换为未修改的`LeafReport`，再由未修改的`fixed-test-pass-rate-v1` evaluator评分。
- first real task从固定三候选 funnel提升第一个 full pass；真实 publication要求两名 reviewer、2个model各2 attempts、deterministic compile、private scan、archive和generated task commit。

当前 checkout 事实：

| 严重度 | 事实 | 证据路径 | 影响 |
| --- | --- | --- | --- |
| blocker | 最新 main 与 F0 branch未集成 | main `c1b20e1114f62d9f94a45579b493d1dd456c4554`；F0 `899fb5050eeef530652093f2d2f086ceba507657`；merge-base `a76bcfcf574a3a254d539d43afbd1e31925e81c3` | 不能建立Rust implementation base |
| blocker | F0.5 production private staging缺失 | `src/nl2repobench/harbor/node_compiler.py`、`pnpm_compiler.py`、`go_compiler.py` | refs-only task无法运行 |
| blocker | F1 supervisor/CLI/policy缺失 | `src/nl2repobench/verification/subprocess_supervisor.py`、`candidate_process_cli.py`、`spawn_policy.toml`不存在 | 无可信candidate subprocess boundary |
| blocker | pre-F1 runner仍有`RLIMIT_AS` | `src/nl2repobench/verification/candidate_runner.py:36` | 与已批准F1 memory policy冲突 |
| blocker | authoritative docs/CLI仍使用旧flag | `AGENTS.md:224`、`src/nl2repobench/cli.py:231`、`scripts/run_authoring_loop.py`、`scripts/authoring_supervisor.py`及docs | 不能同时使用两个private authorization接口 |
| blocker | Rust toolchain/Agent/verifier images、Miri sysroot和run receipts不存在 | 当前worktree无`toolchain.rust.lock.toml`及对应evidence | toolchain tuple只能provisional/unlocked |

以上均是design blockers，不是失败或通过evidence。宿主机Cargo/Rust版本、公开channel manifest、代码review或本Spec不能替代实际image/probe/Harbor receipts。

## 2. 目标、支持面与非目标

### 2.1 目标

1. 只新增`rust+cargo` runtime pair，通过现有canonical contract和registries fail-closed dispatch。
2. Candidate closure继续使用generic`DependencyBundle(lock, offline_store, inventory)`；不增加Cargo专属generic字段。
3. Verifier/harness/Miri closure作为private verifier bundle authority，独立于candidate direct dependency authorization，并进入完整execution identity。
4. Committed `catalog/tasks`只存public projection、artifact refs和digests；private bytes只在repository-owned run wrapper构建的ephemeral context中materialize。
5. Trusted verifier不直接import/load candidate；candidate build/bridge/CLI只通过F1 subprocess API。
6. Synthetic fixture一次证明library+CLI+executor-neutral async+nonempty pure-Rust closure+bounded state+bounded serializable unsafe及正常/恶意controls。
7. Frozen source、license、Cargo registry snapshot、crate archives、Cargo.lock、vendor、features、target、toolchain、images、private bundles和receipts形成完整digest chain。

### 2.2 Rust v1支持面

- 单package；`src/lib.rs`；最多8个explicit binary。
- unit、bool、i8/i16/i32/i64/isize、u8/u16/u32/u64/usize、f32/f64 bit pattern、Unicode char/string、bytes、list、string-key map、named struct、named enum。
- public sync/async free function、associated function、explicit instance operation。
- 每process最多32个opaque state handles，总state bytes<=8 MiB。
- CLI observation仅args/stdin/stdout/stderr/exit/tempdir inventory。
- target-specific normal dependencies只在第8节规则下允许。

### 2.3 非目标

Cargo workspace/virtual manifest/multi-package、cross target、musl/WASM/Windows/macOS、traits/generic values/trait objects/callbacks/borrowed results/GAT/宏API、raw pointers/references across bridge、native/FFI/link/asm/global allocator/custom linker、candidate build-time code、git/path/alternate registry dependencies、runtime network、daemon/socket/TTY/signal/host process、unstable libtest JSON、memory-safety score、Java pilot前的Rust real publication、Rust discovery/controller automation。

## 3. Foundation prerequisites与唯一private CLI

### 3.1 F0 atomic migration

F0必须在同一个merge unit中完成canonical source/model/schema migration、private scoped authorization和authoritative documentation/CLI migration。唯一production compile interface固定为：

```bash
uv run nl2repo harbor compile <source-root> \
  --output <output-root> \
  --toolchain <locked-toolchain> \
  --artifact-root .nl2repo/artifacts \
  --authorize-task-private-artifacts
```

`--allow-private`和public `allow_private: bool`在runtime、CLI、scripts和authoritative docs中全部删除，不保留alias。只允许migration checker/test fixture将旧字符串作为“必须拒绝”的negative literal。

F0 atomic modified files至少包括：

```text
AGENTS.md
readme.md
docs/task-authoring-guide.zh-CN.md
docs/benchmark-operations-guide.zh-CN.md
docs/authoring-agent-remediation-guide.zh-CN.md
docs/authoring-pilot-retrospective-20260824.zh-CN.md
docs/node-foundation-status.v1.md
src/nl2repobench/cli.py
scripts/run_authoring_loop.py
scripts/authoring_supervisor.py
scripts/check_f0_runtime_contract.py
tests/test_f0_runtime_gate.py
```

authoritative interface gate：

```bash
uv run python scripts/check_f0_runtime_contract.py
! rg -n -- '--allow-private|allow_private' AGENTS.md readme.md docs src scripts \
  -g '!docs/archive/**' -g '!scripts/check_f0_runtime_contract.py'
uv run nl2repo harbor compile --help | rg -- '--authorize-task-private-artifacts'
! uv run nl2repo harbor compile --help | rg -- '--allow-private'
```

该migration未合入前，Rust命令不得使用新flag并声称当前CLI可执行；也不得保留旧flag作为临时Rust接口。

### 3.2 F0.5

F0.5提供generic task-scoped CAS materializer：验证ArtifactRef URI/digest/visibility、scoped authorization、canonical ustar、external/internal inventory、path/member/size limits；解包到`.nl2repo/compiled/<task>/<manifest>/private/` sibling temp并atomic rename；generated projection只存refs；selected Python/npm/pnpm/Go production compile x2 deterministic且不再有`private-staging-contract-missing`。

### 3.3 F1

F1提供且Rust不得修改：

```text
run_candidate_process(CandidateCommand, SubprocessLimits, CandidateProcessPolicy)
  -> SubprocessResult
python -m nl2repobench.verification.candidate_process_cli
```

F1必须先证明UID/GID10001、no_new_privs、zero capabilities、exact argv/no shell、process-group+UID cleanup、setsid/double-fork cleanup、wall/CPU/FD/file/process/output limits、CLI64/70/75 precedence、cgroup memory policy、zero direct spawn bypass和zero`RLIMIT_AS`。

### 3.4 R0 baseline

记录：`foundation_base`=F0 merge、`f1_base`=F1 merge、`rust_base`=F1后Rust修改前的exact commit。Rust seam audit只比较`rust_base...HEAD`：

- `verification/evaluator.py`零业务变化；
- generic DependencyBundle/CAS/materializer字段/API零业务变化；
- F1 supervisor/CLI/models/constants零变化；
- `harbor/task_writer.py`零变化；
- generic CLI/compiler无Rust条件分支，只允许registry/source-hook additive registration。

F1自身以`foundation_base...f1_base`单独审计其required packaging changes。

## 4. Canonical domain与registry additions

精确additions：

```text
RuntimeLanguage.RUST = "rust"
PackageManager.CARGO = "cargo"
RuntimeProfile.runtime += "rust"
allowed runtime pair += (rust,cargo)
TestManifest.framework += "rust-harness"
TestManifest.report_format += "rust-bridge-json-v1"
valid test pair += rust-harness/rust-bridge-json-v1
```

Runtime identity中的**Cargo executable version**固定预期值为：

```text
language=rust
runtime=rust
version=1.100.0-nightly
package_manager=cargo
package_manager_version=1.100.0-nightly
```

禁止`rust+none`、其他manager和其他language+cargo。更新canonical validators、conditional schemas、RuntimeDiscriminator、PackageManagerRegistry、HarborCompilerRegistry、VerifierRuntimeRegistry。

新增`RuntimeSourceAssetRegistry`：

```text
RuntimeSourceAssetValidator.identity
validate_source_assets(source_dir, TaskSource) -> None
RuntimeSourceAssetRegistry.resolve(RuntimeDiscriminator)
```

`task validate-source`在canonical load后通过registry验证`rust-profile.toml`、API plan digest、feature profile、candidate deps、CLI、limits和private verifier closure refs。`verification/cli.py`通过VerifierRuntimeRegistry解析runtime，不维护固定choices或Rust分支。

## 5. Toolchain profile：provisional到locked

### 5.1 固定候选tuple

R9选择且不提供fallback的候选tuple：

```text
channel date: 2026-08-20
channel manifest sha256: 8ccaced09f209becc9c732ff86e5ec3373cc4b45e3ccd80c1cfb06bbabd88807
rustc expected first line: rustc 1.100.0-nightly (f7d782a3b 2026-08-19)
rustc distribution commit: f7d782a3be46d6bb4b9792fe69a61db389ba1769
cargo expected first line: cargo 1.100.0-nightly (514c56dd7 2026-08-19)
cargo source commit: 514c56dd7321eecbfdcf9b6479519cf4edfab906
miri-preview expected version: 0.1.0-nightly
target/host: x86_64-unknown-linux-gnu
platform: linux/amd64
Debian base: docker.io/library/debian@sha256:5ae3c39ebd15e229dcedd5cee596b2497182493d41ff162e824ba13fc1b2b867
```

Known distribution archive hashes：cargo archive `0de1039680eb7c1c31f6c45aecde18b90fb8517a42439dfd389d287adf4f8114`、rustc archive `5ddf6a2472eb778bb4bf57c1bbe118913d5958ec59baf399283d42ed40b5d1be`、rust-std archive `64600c72503dfe1c8c6f69e3a933cb6ca984fe898016d3d65116160727dc54b2`、Miri archive `a81cfe5594285eafa010aff6d1891aaf05e204bb6acb6f8bf7ba522f04d1f44d`。rust-src archive hash从同一manifest读取并在fetch前后核对。

该tuple在实际toolchain fetch/image build/probe前严格是`provisional-unlocked`，不是verified toolchain identity。若任一actual output/hash/commit/date/host/manifest不匹配，gate hard fail并保持blocked；不得自动选择另一个nightly或改写预期值。

### 5.2 Lock schema与probe

`toolchain.rust.dev.lock.toml`允许：

```text
status="provisional-unlocked"
expected_* = 上述固定tuple
cargo_vv_sha256=null
rustc_vv_sha256=null
cargo_executable_sha256=null
rustc_executable_sha256=null
cargo_miri_executable_sha256=null
miri_sysroot_tree_digest=null
```

null只表示尚未执行；它不能进入locked identity。`toolchain.rust.lock.toml`只能在所有actual字段非空且probe通过后生成`status="locked"`，并绑定：

- full `cargo -Vv` bytes、SHA-256、first line、release、full commit、commit date、host；
- full `rustc -Vv` bytes、SHA-256、first line、full commit、commit date、host、LLVM；
- `/opt/rust/bin/cargo`、`rustc`、`cargo-miri`、`miri` executable SHA-256；
- channel manifest bytes/hash和每个installed component archive hash；
- rust-src tree digest；Miri sysroot tree digest；
- toolchain/Agent/verifier image RepoDigest和image ID；
- OpenHands fork/version、Harbor0.21/task1.4/runner lock、F1 runtime digest、Rust runtime digest、verifier requirements digest、cgroup policy digest。

actual probe：

```bash
/opt/rust/bin/cargo -Vv > /evidence/cargo-vv.txt
/opt/rust/bin/rustc -Vv > /evidence/rustc-vv.txt
sha256sum /opt/rust/bin/cargo /opt/rust/bin/rustc \
  /opt/rust/bin/cargo-miri /opt/rust/bin/miri \
  /evidence/cargo-vv.txt /evidence/rustc-vv.txt
```

只有`check_rust_release_gate.py toolchain`逐字段验证后才能把status提升为locked。R9不把上述expected values描述成已验证事实。

## 6. Authoring truth与feature function

### 6.1 Canonical task source

`task.toml`使用canonical schema1.0、metadata language rust、known environment、runtime/package-manager exact locked profile、network no-network/private-artifact/forbidden、known dependency triple、rust-harness/rust-bridge-json-v1、positive frozen denominator、private commands/test/verifier/oracle refs和fixed metric。缺locked toolchain/image/F0.5/F1时source只能处于discovered或有evidence的blocked，不得写production lifecycle。

### 6.2 `rust-profile.toml`

strict/frozen fields：

```text
schema_version="1.0"
package={name,exact version,edition:2018|2021|2024,rust_version|null,
         library_path:"src/lib.rs",binaries:sorted <=8}
target={triple:"x86_64-unknown-linux-gnu"}
features={default_features:bool,enabled:sorted unique,declarations:sorted map}
candidate_dependencies=sorted CandidateDependency[]
bridge={api_plan_digest,max_operations_per_request:64,max_state_handles:32,
        max_state_bytes:8388608,unsafe_api_ids:sorted}
cli=sorted CliProfile[]
limits={build_timeout_sec<=600,leaf_timeout_sec<=120,cpu_sec<=120,
        max_stdin_bytes<=1048576,max_output_bytes<=8388608,
        max_file_bytes<=536870912,max_open_files<=256,max_processes<=64}
```

CandidateDependency fields：name、exact version、default_features、features、`target_selector|null`。The sole canonical source `CliProfile` fields are profile_id、binary_name、argv_max_items、stdin_max_bytes、max_output_bytes、tempdir_policy、tempdir_max_entries、tempdir_max_bytes、tempdir_max_file_bytes、cli_timeout_sec、expected_exit_codes。Ranges are argv_max_items=1..64, stdin_max_bytes=0..1048576, max_output_bytes=1..8388608, tempdir_max_entries=0..256, tempdir_max_bytes=0..33554432, tempdir_max_file_bytes=0..8388608, cli_timeout_sec=0.001..120.0, and expected_exit_codes=sorted unique non-empty integers in [-128,127]. No extras or alternate CLI profile schema are accepted; adapter code consumes this validated profile directly.


`rust-profile.toml` is the sole authoring canonical profile. It is parsed with Python `tomllib` from source only, under strict top-level/section/field allowlists; duplicate TOML keys, unknown keys, wrong scalar/array/table types, noncanonical feature/dependency ordering, or any second profile file are rejected. The compiler reads only this TOML source, validates it, and emits the generated task's `rust-profile.json` as a compiler-owned projection; runtime, verifier and run wrapper read only that JSON projection and never reinterpret TOML.

Projection is lossless for the validated typed profile. It is serialized as UTF-8 canonical JSON with sorted object keys, arrays in the profile's prescribed canonical order, separators `(',', ':')`, no ASCII escaping for permitted UTF-8 strings, and exactly one final LF. `rust-profile.json` bytes are SHA-256 hashed as `rust_profile_projection_digest`; that digest, the source TOML digest, and the projection serializer version `rust-profile-projection-v1` are included in `bundle.manifest.json`, `rust_build_identity`, `rust_execution_identity`, and every profile-sensitive receipt. The compiler recomputes the projection in a sibling temporary directory and atomically installs it; it rejects an existing output whose JSON digest differs. Generated projection must contain exactly one `rust-profile.json`; source roots must contain exactly one `rust-profile.toml` and no `rust-profile.json`.

The exact reader contract is: `validate-source` reads `catalog/sources/<id>/rust-profile.toml`; `RustHarborCompiler` reads that same TOML before writing projection; generated `RustSourceAssetValidator`, `RustHarborCompiler.materialize_run_context`, verifier runtime and `rust_harbor_run.py` read only `catalog/tasks/<id>/rust-profile.json` from the recomputed manifest context. A generated task with missing, extra, malformed, stale, or duplicate profile representation is invalid. `tests/test_rust_profile.py` must contain a source-to-JSON golden fixture, LF/canonical-byte digest assertion, TOML/JSON drift rejection, source JSON rejection, generated TOML rejection, and projection identity/receipt binding tests.

### 6.3 唯一feature argv function

所有 baseline、metadata/build/test、candidate library、binary、bridge和Miri命令必须调用同一个typed function：

```text
cargo_feature_args(default_features, enabled_sorted):
  true,  []      -> ()
  false, []      -> ("--no-default-features",)
  true,  [x...]  -> ("--features", "x,...")
  false, [x...]  -> ("--no-default-features", "--features", "x,...")
```

enabled先按UTF-8 bytes排序并拒绝duplicate。函数输出是argv tuple，不是shell string；其canonical JSON digest进入build/execution identity和每个receipt。任何command手写feature flags、使用`--all-features`或与profile不一致均hard fail。

async-channel profile固定`default_features=false, enabled=["std"]`，因此其所有baseline/build/test/bridge（bridge自身features除外）receipt必须出现精确连续tokens：

```text
--no-default-features --features std
```

lexopt/humantime profile固定`false,[]`，因此出现`--no-default-features`且不出现`--features`。

## 7. Cargo closure：preparation、vendorization、consumption

### 7.1 Typed adapter

`CargoPackageManager`原样实现F0 `PackageManagerAdapter`：identity rust+cargo；lockfile_names Cargo.lock；typed LockSummary/StoreSummary/CommandSpec；只抛现有PackageManagerError codes：lock-missing、lock-malformed、toolchain-mismatch、store-malformed、inventory-mismatch、offline-smoke-failed、unsupported-profile。

### 7.2 Closure preparation（唯一networked phase）

从verified source archive在dedicated container执行，pristine home，无offline/frozen/vendor replacement：

```bash
env -i PATH=/opt/rust/bin:/usr/local/bin:/usr/bin:/bin \
  HOME=/tmp/cargo-prep CARGO_HOME=/tmp/cargo-prep \
  CARGO_NET_OFFLINE=false CARGO_INCREMENTAL=0 CARGO_TERM_COLOR=never \
  LC_ALL=C.UTF-8 \
  /opt/rust/bin/cargo generate-lockfile --manifest-path /prep/source/Cargo.toml

env -i PATH=/opt/rust/bin:/usr/local/bin:/usr/bin:/bin \
  HOME=/tmp/cargo-prep CARGO_HOME=/tmp/cargo-prep \
  CARGO_NET_OFFLINE=false CARGO_INCREMENTAL=0 CARGO_TERM_COLOR=never \
  LC_ALL=C.UTF-8 \
  /opt/rust/bin/cargo fetch --locked --target x86_64-unknown-linux-gnu \
  --manifest-path /prep/source/Cargo.toml
```

allowlist只含`index.crates.io`和`static.crates.io`。捕获并hash sparse/index snapshot、registry cache中每个`.crate` archive、Cargo.lock、Cargo/Rust executable和full `-Vv`。上游registry semver requirements允许；git/path/alternate registry/patch/replace拒绝。锁中每个registry package必须exact version/source/checksum，checksum与captured crate bytes一致。

### 7.3 Vendorization（offline、无replacement）

复制并验证immutable preparation home后：

```bash
env -i PATH=/opt/rust/bin:/usr/local/bin:/usr/bin:/bin \
  HOME=/tmp/cargo-vendor CARGO_HOME=/tmp/cargo-vendor \
  CARGO_NET_OFFLINE=true CARGO_INCREMENTAL=0 CARGO_TERM_COLOR=never \
  LC_ALL=C.UTF-8 \
  /opt/rust/bin/cargo vendor --locked --versioned-dirs \
  --manifest-path /prep/source/Cargo.toml /prep/vendor
```

store包含vendor、resolution index snapshot、crate archives和internal inventory；每个member被external generic inventory覆盖。拒绝links/special/path escape/non-NFC/duplicate/checksum mismatch。

### 7.4 Offline consumption

每个Agent/verifier/candidate/build/test/Miri Cargo command使用pristine empty HOME/CARGO_HOME，exact env allowlist，且追加：

```text
--locked --offline --frozen --target x86_64-unknown-linux-gnu
--config net.offline=true
--config source.crates-io.replace-with="vendored-sources"
--config source.vendored-sources.directory="/opt/nl2repobench-cargo/vendor"
```

环境allowlist：PATH、HOME、CARGO_HOME、CARGO_NET_OFFLINE、CARGO_INCREMENTAL、CARGO_TERM_COLOR、LC_ALL、TZ、TMPDIR、RUST_BACKTRACE，以及Miri context专用MIRI_SYSROOT/MIRIFLAGS。拒绝Cargo wrappers、target linker/runner、build target、encoded rustflags、RUSTFLAGS/RUSTDOCFLAGS、loader/proxy/credentials。扫描HOME/CARGO_HOME、`/etc/cargo/config*`、`/usr/local/etc/cargo/config*`；除trusted argv config外为空。environment/config digest进入receipt。

media types固定：package-lock tar、offline-store tar、inventory JSON；URI固定`artifact://private/sha256:<digest>`。继续使用F0 canonical ustar和inventory schema，不新增generic字段。

## 8. Target-specific dependency policy

Rust v1允许：

```toml
[target.'<cfg expression for selected target>'.dependencies]
```

但只允许normal dependencies。validator用Cargo metadata和repository-owned cfg evaluator在唯一target`x86_64-unknown-linux-gnu`上求值；selector必须只引用target_arch=x86_64、target_os=linux、target_env=gnu、target_family=unix、target_pointer_width=64或exact triple。unknown/host-dependent/env-dependent selector拒绝。

被选中的target-specific dependency必须：

- registry source、generated candidate manifest exact version；
- 在candidate dependency set中带同一target_selector；
- 出现在Cargo.lock、captured crate archives、vendor和inventory；
- source/license/hash完整；
- pure Rust：无`links`、native archive/shared object、cc/cmake/pkg-config/bindgen、external tool、custom linker、FFI/link/asm/global allocator；
- dependency-owned pure-Rust build.rs/proc macro只有在第11节untrusted build-time isolation中允许，且不得产生native/link directives。

拒绝target-specific build-dependencies、dev-dependencies（candidate manifest）、unknown target、非selected branch注入和native/link behavior。上游baseline的target dev dependencies可存在于frozen source，但只有Cargo metadata对selected target解析出的闭包进入baseline closure；例如async-channel wasm-only dev dependency在GNU target上不被执行或授权。


### 8A. Frozen target-selector grammar and identity

`target_selector` is either the exact selected triple `x86_64-unknown-linux-gnu` or this bounded grammar; no other Cargo expression is accepted:

```text
selector ::= triple | cfg(atom) | cfg(all(selector, selector+))
          | cfg(any(selector, selector+)) | cfg(not(selector))
triple   ::= "x86_64-unknown-linux-gnu"
atom     ::= target_arch="x86_64"
          | target_os="linux"
          | target_env="gnu"
          | target_family="unix"
          | target_pointer_width="64"
```

The evaluator uses this fixed target environment: `{target_arch:x86_64,target_os:linux,target_env:gnu,target_family:unix,target_pointer_width:64}`. Its recursive semantics are exact: `eval(triple)` is true iff the triple equals `x86_64-unknown-linux-gnu`; `eval(cfg(atom))` looks up the atom; `eval(cfg(all(x1,...,xn))) = AND(eval(x1),...,eval(xn))`; `eval(cfg(any(x1,...,xn))) = OR(eval(x1),...,eval(xn))`; and `eval(cfg(not(x))) = NOT(eval(x))`. Therefore `cfg(not(target_os="linux"))` is accepted syntax but evaluates false. A false selector is retained only in the source audit record, is omitted from the generated candidate manifest and selected Cargo closure, and contributes no dependency authorization. The normalized selector, evaluator version, boolean result, source manifest digest, and selected dependency list are bound into `rust_build_identity`; no implementation may silently treat a false selector as true.

Canonicalization parses only the grammar above, emits the exact `triple`/`cfg(...)` spelling with source-order children, rejects alternate names and whitespace variants, and records both canonical text and source text. The normalized selector, its evaluator version, source manifest digest, and selected dependency list are part of `rust_build_identity`. Only true-branch normal dependencies enter Cargo.lock, captured archives, vendor and inventory; false-branch declarations are not authorized or executed. Target-specific `build-dependencies` and `dev-dependencies` remain forbidden. Accepted true and false selector golden fixtures, plus rejected syntax fixtures, are mandatory in `tests/test_rust_target_dependencies.py`; the true fixture includes selected dependency identity and the false fixture proves the dependency is absent from generated `Cargo.toml`, lock, vendor and closure.

## 9. Candidate manifest/source policy

workspace最多4096entries、64MiB、single4MiB、path255。Candidate只可提交Cargo.toml、absent或byte-identical trusted Cargo.lock、src/lib.rs、allowlisted src/bin、src/**/*.rs、bounded README/LICENSE。拒绝workspace/target/tests/examples/benches/.cargo/build.rs/rust-toolchain/links/special/setuid/executable source。

Cargo.toml strict rules：package identity匹配profile；build absent/false、links absent、autolib/autobins/autoexamples/autotests/autobenches=false；explicit lib/bin；normal dependencies与允许的target-specific normal dependencies精确匹配candidate set；features精确；拒绝workspace/patch/replace/build/dev deps/profile tables。Generated candidate dependency versions必须`=x.y.z`。

Rust scanner使用syn AST和`cargo rustc` diagnostics；拒绝extern/FFI/link/no_mangle/export_name/asm/global_asm/global_allocator/native crate types；默认拒绝unsafe，只有profile allowlistedpublic unsafe free function span允许。命令使用offline config和feature function：

```bash
cargo rustc --lib <offline-consumption-args> <profile-feature-args> \
  --message-format=json -- --force-warn unsafe_code
```

每binary单独`--bin <exact-name>`。candidate-owned build-time/config/linker/flags在spawn前拒绝。

## 10. Verifier/harness closure、bridge和report

Private verifier bundle internal inventory覆盖：verifier Cargo.toml/Cargo.lock/vendor、Miri harness Cargo.toml/Cargo.lock/vendor、bridge generator/source、source scanner、normalizer plan、hidden assertions、expected values。Harness closure与candidate closure分开授权；bridge build需要的union由task-specific verifier lock冻结。Bundle、closure、toolchain、source digests进入execution identity。

Candidate namespace不挂载private tests/API plan/expected values/verifier source/logs/CAS/Oracle/provider env。Install compiler-only namespace可读candidate source、approved vendor和public generated bridge source，但无hidden expected。Call namespace只读candidate workspace、vendor、bridge executable和writable output/temp。Trusted runner在独立namespace通过bounded IPC。

Bridge RustValue grammar固定为strict tagged unit/bool/integer decimal/f32-f64 bits/char/string/base64 bytes/list/sorted map/struct/enum；depth16、nodes4096、string/bytes256KiB。Request/response schema1.0、32hex request ID、最多64operations、state handles s0..s31、statuses ok/declared-error/panic; trusted protocol failures are outside operation results；stdout恰一行canonical JSON。

Bridge generator从hash-bound API plan deterministic生成public mapping source和Cargo.toml，不含expected values。Candidate library先在F1 install编译；bridge在compiler-only namespace以offline config、bridge feature tuple和task-specific union closure编译；source/binary/manifest/lock/store/inventory digests进入execution identity。Runtime candidate process只接收bridge executable。

async固定由verifier-owned`pollster = =0.4.0`驱动，candidate API executor-neutral。state只在single leaf process。Unsafe leaf single operation/no state/fresh PID。

Trusted runner生成`rust-bridge-json-v1`，normalizer映射至LeafReport；验证count/IDs/status/exit/limits。Rust grader只调用existing metric/evaluator/writer；candidate不能写report/reward。


## 10A. Rust bridge detailed implementation contract

本节是第10节的实现性补全，优先于任何只写“bridge”或“adapter”的摘要描述。所有类型、边界和错误码均为 Rust v1 固定合同。

### 10A.1 API plan

`rust-api-plan.json` 是唯一 source-local、hash-bound 的 bridge 输入，schema `1.0` 严格拒绝额外字段。顶层字段固定为 `schema_version`、`package_name`、`api_plan_digest`、`types`、`functions`、`state_types`、`cli_profiles` 和 `unsafe_leaf_ids`。数组按 UTF-8 byte order 排序并唯一。每个 function entry 固定 `api_id`、`rust_path`、`kind=sync|async|associated|instance`、有序 `args`、`returns: TypeRef`、`error: TypeRef|null`、`state_type: TypeRef|null`、`unsafe` 和 `leaf_ids`；每个实际生成的 operation 从该列表选择且只携带一个 frozen `leaf_id`；type entry 固定 `type_id`、`kind=scalar|bytes|list|map|struct|enum` 和递归字段。`rust_path` 只能指向已审计的 public `src/lib.rs` item；不允许动态 symbol、private path、macro invocation、callback、borrowed return、pointer 或 reference。

生成器的 typed operations 固定为：

```text
validate_api_plan(plan: RustApiPlan) -> None
normalize_api_plan(plan: RustApiPlan) -> CanonicalRustApiPlan
generate_bridge_source(plan: CanonicalRustApiPlan,
                       package: PackageIdentity) -> GeneratedBridge
build_bridge(candidate: CandidateArtifact, generated: GeneratedBridge,
             closure: VerifierClosure, profile: BridgeProfile) -> BridgeArtifact
invoke_leaf(request: RustBridgeRequest, limits: LeafLimits) -> RustBridgeResponse
```

checked-in `src/nl2repobench/verification/rust_bridge.py` 只读取 canonical API plan、public template version 和 candidate package identity；它确定性输出 bridge source、bridge `Cargo.toml`、public mapping digest 和 generated manifest。它不读取或输出 hidden assertions、expected values、private test paths、provider data、Oracle bytes 或 reference source。validator 在 compile 和 run 前重新生成并比较所有 output digests；差异是 hard failure。

### 10A.2 RustValue v1 exact grammar

所有 JSON object strict、无 extra、UTF-8 canonical；整数以 decimal string，float 用固定宽度 lower-case hex bits，bytes 用 RFC 4648 canonical base64（带 padding）：

```text
{"type":"unit"}
{"type":"bool","value":true|false}
{"type":"i8|i16|i32|i64|isize|u8|u16|u32|u64|usize","value":"decimal"}
{"type":"f32","bits":"8 lowercase hex"}
{"type":"f64","bits":"16 lowercase hex"}
{"type":"char","value":"one Unicode scalar"}
{"type":"string","value":"..."}
{"type":"bytes","base64":"..."}
{"type":"list","items":[RustValue,...]}
{"type":"map","entries":[{"key":"string","value":RustValue},...]}
{"type":"struct","name":"TypeId","fields":[{"name":"Field","value":RustValue},...]}
{"type":"enum","name":"TypeId","variant":"Variant","payload":RustValue}
```

map entries、struct fields 按 UTF-8 byte order 排序且唯一；enum payload 只能是 unit/list/struct。depth<=16、nodes<=4096、每个 string/bytes<=256 KiB。validator 检查整数范围、Unicode scalar、base64 canonicality、float bit width、type/name/variant membership、map order、duplicate keys 和 canonical re-encoding；JSON number、null 作为 RustValue 和 unknown fields 均拒绝。

### 10A.3 Request/response and error semantics

每个普通 hidden leaf 启动新的 bridge process；state leaf 只允许在该 process 的一个 batch 中执行：

```text
RustBridgeRequest:
  schema_version="1.0"
  request_id=32 lowercase hex generated by trusted caller
  operations=1..64 ordered, no duplicate operation_id

RustOperation:
  operation_id=trusted per-request correlation ID, unique within request, distinct from leaf_id
  api_id=allowlisted API ID
  leaf_id=exactly one frozen leaf ID
  kind=call|state-create|state-call|state-drop
  state_handle=null or bridge-assigned s0..s31
  args=RustValue tuple

RustBridgeResponse:
  schema_version="1.0"
  request_id=exact request match
  results=one ordered result per completed operation

RustOperationResult:
  operation_id
  status=ok|declared-error|panic
  value=null or RustValue
  error_type=null or bounded string
  message=null or bounded string
  state_handle=null or bridge-assigned handle
```

stdout 必须恰好一行 response，末尾允许一个 LF；stderr 仅由 F1 aggregate capture 保存。missing/multiple line、unknown field、request mismatch、bad base64、oversize、unexpected operation/handle、duplicate operation 或 response count mismatch 都是 trusted protocol error。candidate 不能提供 request ID、leaf ID、reward、collection、JUnit、report path、feature argv 或 expected value；trusted caller 创建并校验这些字段。F1 cleanup failure 是 verifier invalid 或 infrastructure failure，不能写成 model zero。

### 10A.4 State, async, unsafe and CLI

state 最多32 handles、serialized state 总量<=8 MiB、batch<=64 operations。state-create 必须返回当前 process 中新的 `sN`；state-call/drop 只能引用 live handle。重复 drop、跨请求/跨 process handle、handle exhaustion、drop 后调用均为 trusted transport-schema or valid-bridge-invariant failure；panic、timeout、abort 后立即丢弃整个 process state。bridge 自己计算序列化大小，candidate 不得声明大小。

async API 由 bridge 将 Future 交给 verifier-owned `pollster = =0.4.0`；candidate API executor-neutral，不依赖 Tokio、async-std 或 smol。Future 必须在 leaf timeout 内完成；stream、spawned task、executor handle、background thread 均不支持。async declared error 保持 `declared-error`，panic 保持 `panic`，不可完成或进程退出则是 leaf failure。

unsafe leaf 只允许一个 operation、无 state handle、fresh candidate bridge PID。跨边界只传 profile allowlisted 的 serializable 参数和返回值，绝不传 pointer/reference；Miri 规则见第12节。该边界证明的是固定 leaf 行为，不产生 memory-safety score 或 claim。

CLI binary 不接收 bridge JSON。Rust adapter 经 unchanged F1 `CandidateProcessRequest` 传 trusted argv、relative cwd 和 request-level stdin，并只观察 F1 result 与 bounded tempdir inventory；F1 owns process limits and cleanup。tempdir 最多256 entries、32 MiB total、single file 8 MiB；拒绝 link、special file 和 path escape。CLI profile 冻结 binary name、argv max、stdin max、exit/error expectations；不测试 daemon、TTY、socket、signal 或 host process。

### 10A.5 Bridge build and report handoff

candidate library 必须先在 F1 install context 中编译。bridge generator 随后在 compiler-only context 生成 source 和 manifest，bridge build 仍经 F1 `run_candidate_process` 执行，只能读取 candidate package、public generated source 和 task-specific union closure。精确 argv 如下，`<BRIDGE_FEATURE_ARGS>` 由第6.3节同一 typed function 产生：

```bash
cargo build --manifest-path /bridge/Cargo.toml --bin nl2repo-bridge \
  --locked --offline --frozen --target x86_64-unknown-linux-gnu \
  --config net.offline=true \
  --config source.crates-io.replace-with="vendored-sources" \
  --config source.vendored-sources.directory="/opt/nl2repobench-cargo/vendor" \
  <BRIDGE_FEATURE_ARGS>
```

bridge build command、full argv、generated source/manifest/lock/store/inventory、candidate manifest、binary and toolchain digests enter `rust_execution_identity`. Call namespace receives only bridge executable, candidate workspace, approved vendor and writable output/temp. API plan, bridge source, hidden assertions, verifier source, logs, CAS root and private Oracle are absent.

trusted `rust_contract_runner.py` only emits `rust-bridge-json-v1`; normalizer maps it to unmodified `LeafReport` and existing evaluator. Report limit is 8 MiB, tests<=10000, ID<=512 bytes unique, details<=4096; statuses are only `passed|failed|error|skipped|todo|xfail`. Rust grader performs parse -> normalize -> existing `canonical_metric_contract` -> existing `evaluate_leaf_report` -> existing writer. candidate cannot write trusted report, reward, JUnit or collection.


### 10A.6 Descriptor schemas and golden compatibility

The API plan's recursive descriptors are frozen as follows:

```text
TypeDescriptor = {
  type_id: SafeId,
  kind: scalar|bytes|list|map|struct|enum,
  scalar: unit|bool|i8|i16|i32|i64|isize|u8|u16|u32|u64|usize|f32|f64|char|string|null,
  item: TypeRef|null,
  key: "string"|null,
  fields: [{name: SafeId, type: TypeRef}],
  variants: [{name: SafeId, payload: TypeRef}]
}
ApiDescriptor = {
  api_id: SafeId, rust_path: AuditedPath,
  kind: sync|async|associated|instance,
  receiver: TypeRef|null, state_type: TypeRef|null, args: [{name: SafeId, type: TypeRef}],
  returns: TypeRef, error: TypeRef|null, unsafe: bool,
  leaf_ids: [SafeId]
}
CliDescriptor = {
  profile_id: SafeId,
  binary_name: SafeId
}
```

`TypeRef` is a `type_id` string or one of the inline primitive names; `receiver` is required and non-null exactly for `instance`, and null for free and associated kinds. `state_type` is non-null exactly for `instance`, and null for free and associated kinds. A non-null `error: TypeRef` means the Rust return type is exactly `Result<returns,error>`; null means no declared error. Struct fields and enum variants are ordered and unique; list/map require their item/key descriptors; scalar/bytes require null recursive fields. `SafeId` is 1..128 ASCII bytes matching `[A-Za-z0-9_.:-]+`; `AuditedPath` is a fixed `crate::module::item` path with no `self`, `super`, generics, macro, or quoted component. A function has 1..32 arguments and at most 64 leaf IDs. The descriptor schema rejects omitted required fields, nullability mismatches, unknown fields, duplicate IDs, recursive cycles, and descriptors not proven by source scan.

Golden fixtures contain the exact generated Cargo.toml bytes and exact generated Rust source bytes for the canonical synthetic candidate, plus SHA-256 digests for both; the generated-source digest is frozen from those exact bytes and is not inferred from a future run. The mandatory zero-operation generator smoke fixture is the exact LF file `tests/fixtures/rust-bridge-golden/empty.rs` with bytes `// rust-bridge-template-v1\nfn main() {}\n` and SHA-256 `83984cbba44fd4948838b1e9a9af9b5cfc471151f041a623c5f1b3c4fa9e9cab4`; operation-bearing golden source files each carry their own exact digest. Golden fixtures contain one canonical request and response for every RustValue variant, one declared-error/panic response plus one trusted transport-schema failure fixture, state create/call/drop, async completion, and each CLI observation. Rust generated bridge tests and Python normalizer tests parse the same fixtures and compare canonical re-encoding byte-for-byte. A bridge implementation is incomplete until these cross-language fixtures pass.


### 10A.7 Rust-local CLI profile and lossless F1 conversion

Rust must preserve the generic F1 API unchanged. validated source `CliProfile` and adapter-local `RustCliInvocation` are the only Rust adapter CLI types and are never added to or substituted for F1 `CandidateCommand`, `CandidateProcessRequest`, `SubprocessLimits`, `CandidateProcessPolicy`, or `SubprocessResult`.

```text
RustCliInvocation = {
  profile_id: SafeId,
  leaf_id: SafeId,
  executable_rel: SafeRelativePath,
  argv_tail: [UTF-8 string],
  cwd_rel: SafeRelativePath,
  stdin_base64: canonical RFC4648 base64,
  tempdir_rel: SafeRelativePath|null,
  expected_stdout_base64: canonical RFC4648 base64|null,
  expected_stderr_base64: canonical RFC4648 base64|null
}
```

validated source `CliProfile` is authoritative for timeout, output/tempdir limits and expected exit codes. API-plan `CliDescriptor` contains exactly `profile_id` and `binary_name`, and no other fields. `profile_id` must equal exactly one source `CliProfile.profile_id`; the compiler resolves that profile and rejects missing, duplicate, unknown, or mismatched bindings. Limits and expected exit codes exist only in the bound source profile, never in the descriptor. `RustCliInvocation` has no timeout, output-limit, UID/GID, cgroup, policy, or absolute host path fields. `argv_tail` may be empty, but the adapter constructs F1 `CandidateCommand.argv` as the non-empty tuple `(resolved_executable, *argv_tail)`, so F1 `argv[0]` is always the executable. F1 `cwd` is the safe relative path `cwd_rel` under its trusted `staging_root`; stdin exists only in F1 `CandidateProcessRequest.stdin_base64`.


The unchanged F1 generic schemas are:

```text
CandidateCommand = {
  argv: tuple[str,...] non-empty, argv[0] executable,
  cwd: safe relative path under policy.staging_root,
  environment: exact validated map
}
SubprocessLimits = {
  timeout_sec, cpu_sec, max_stdin_bytes, max_output_bytes,
  max_file_bytes, max_open_files, uid, gid, max_processes
}
CandidateProcessPolicy = {
  task_id, staging_root, read_only_roots, write_root,
  allowed_executable_roots, allowed_environment_names,
  require_no_new_privs=true, require_empty_capabilities=true
}
CandidateProcessRequest = {
  schema_version="1.0", request_id=32 lowercase hex,
  context=install|call|bridge, command=CandidateCommand,
  limits=SubprocessLimits, policy=CandidateProcessPolicy,
  stdin_base64=canonical RFC4648 base64
}
```

F1 validates `argv` as non-empty and resolves `argv[0]` below trusted `allowed_executable_roots`; `cwd` is relative to the trusted staging root and cannot escape or contain symlink components. F1 request stdin is the only stdin field; `CandidateCommand` has no stdin, timeout, output-limit, expected-exit, tempdir, absolute host path, or shell field. F1 generic limits and policy are supplied by the trusted caller and are not extended by Rust. For a Rust CLI invocation the trusted request has `context="call"`; for a bridge invocation it has `context="bridge"`. The adapter receives that trusted context and does not invent, widen, or modify F1's generic API. F1's existing `CandidateProcessRequest` validator owns the CLI 64/70/75 precedence and all generic malformed-request rejection.

The lossless conversion is fixed:

```text
RustCliInvocation + trusted_context(call|bridge) + trusted staging_root/profile/policy
  -> CandidateCommand(
       argv=(resolved executable, *argv_tail),
       cwd=cwd_rel,
       environment=validated exact map)
  -> CandidateProcessRequest(
       schema_version="1.0",
       request_id=trusted 32-lowercase-hex ID,
       context=trusted_context,
       command=CandidateCommand,
       limits=SubprocessLimits(
         timeout_sec=profile.cli_timeout_sec,
         cpu_sec=min(profile.cli_timeout_sec, trusted_cpu_cap),
         max_stdin_bytes=profile.stdin_max_bytes,
         max_output_bytes=profile.max_output_bytes,
         max_file_bytes=trusted file cap,
         max_open_files=trusted FD cap,
         uid=10001, gid=10001, max_processes=64),
       policy=CandidateProcessPolicy(
         task_id=trusted task ID,
         staging_root=trusted absolute root,
         read_only_roots=trusted tuple,
         write_root=trusted UID-owned root,
         allowed_executable_roots=trusted candidate bin roots,
         allowed_environment_names=trusted allowlist,
         require_no_new_privs=true,
         require_empty_capabilities=true),
       stdin_base64=invocation.stdin_base64)
```

The adapter resolves `executable_rel`, `cwd_rel`, and `tempdir_rel` under trusted staging roots, rejects absolute components, `..`, symlink components, special files, and path escape, and validates every argv item as bounded UTF-8 without shell interpolation. It validates decoded stdin against `stdin_max_bytes` before the F1 call. `CandidateProcessRequest.context` is not invented or modified by Rust; the trusted F1 request context is exactly `call` for CLI or `bridge` for bridge execution. F1 owns spawn, UID, cgroup, process group, cleanup and transport.

F1 returns the unchanged generic result schema:

```text
SubprocessResult = {
  schema_version: "1.0",
  request_id: same as request,
  returncode: integer,
  stdout_base64: canonical RFC4648 base64,
  stderr_base64: canonical RFC4648 base64,
  timed_out: bool,
  output_limit_exceeded: bool,
  cleanup_complete: bool,
  spawn_error: ProcessError|null,
  cleanup_error: ProcessError|null
}
```

Rust maps `output_limit_exceeded` (never `output_limited`) and `cleanup_complete`/`cleanup_error` (never `cleanup_ok`) without renaming or guessing. `spawn_error` and `cleanup_error` are preserved as typed bounded records. Rust expected exit codes and tempdir policy remain adapter-side assertions after this result: returncode in the profile set plus exact stdout/stderr/tempdir assertions produces a passed CLI leaf; mismatch, `timed_out`, `output_limit_exceeded`, or spawn error produces a failed candidate leaf; `cleanup_complete=false` or non-null cleanup error produces verifier-invalid/infrastructure classification under the generic F1 precedence. F1 CLI 64/70/75 precedence, request/result schema validation and `context=call` are applied before any Rust assertion.

The adapter emits a canonical `CliObservation` only after F1 validation:

```text
CliObservation = {
  return_code: integer,
  stdout_base64: canonical RFC4648 base64,
  stderr_base64: canonical RFC4648 base64,
  timed_out: bool,
  output_limit_exceeded: bool,
  cleanup_complete: bool,
  spawn_error: ProcessError|null,
  cleanup_error: ProcessError|null,
  tempdir_entries: sorted [{relative_path: SafePath,
    kind: file|directory, size_bytes: integer, sha256: lowercase hex}]
}
```

A tempdir policy of `none` requires null/empty tempdir and zero entries; `empty` requires a fresh empty directory after cleanup; `fresh-writable` and `fresh-readonly` require the corresponding trusted setup and enforce the profile entry/byte/file limits. The adapter never lets candidate output claim a tempdir digest. Profile fields, invocation, converted F1 request, F1 result, observation, and assertion outcome are included in build/execution identities and receipts.

### 10B. Byte-exact bridge generator and state contract

`state_types` 使用以下严格 `StateDescriptor` schema，字段顺序为 canonical JSON 的 UTF-8 byte order：

```text
StateDescriptor = {
  state_id: SafeId,
  rust_type: TypeRef,
  create_api_id: SafeId,
  methods: [{api_id: SafeId, receiver: &self|&mut self,
             args: [{name: SafeId, type: TypeRef}],
             returns: TypeRef, error: TypeRef|null, state_type: TypeRef|null,
             leaf_ids: [SafeId]}],
  drop_api_id: SafeId|null
}
```

`state_id`、`create_api_id`、method IDs 和 leaf IDs 必须在相应 plan 表中存在且唯一; every method has the same required `returns`, `error`, and `state_type` fields as a function descriptor；`rust_type` 必须是非递归 named struct/enum `TypeRef`；create 的返回类型必须正好是该 state type，method 的 receiver 必须与 source signature 相同。`drop_api_id` 为 null 表示生成器使用 Rust `Drop`，非 null 时它必须是 `fn(&mut StateType)` 形式的 reviewed public operation。state descriptor 不允许 async method、associated receiver、generic type、borrowed argument/return、raw pointer 或 callback。

Generator version is `rust-bridge-generator-v1`; its exact template input is the UTF-8 LF file `tests/fixtures/rust-bridge-template-v1.rs.in`, final LF included, whose canonical bytes SHA-256 is `7e7191156c92d19c80da7160f29802fe3cf7cc36aae38388995871269cdfdb2d` (the file consists of the exact single line `// rust-bridge-template-v1\n`). The template is a marker-free fixed prelude contract: implementations must copy this byte sequence into the generated-source prelude before deterministic expansion and must reject any other template bytes. The exact generated Cargo manifest is the UTF-8 LF file `tests/fixtures/rust-bridge-golden/Cargo.toml`, with canonical content:

```toml
[package]
name = "nl2repo-bridge"
version = "0.0.0"
edition = "2021"

[features]
candidate_std = ["candidate/std"]

[dependencies]
pollster = "=0.4.0"
serde = { version = "=1.0.228", features = ["derive"], default-features = false }
serde_json = "=1.0.145"

[dependencies.candidate]
package = "<candidate-package-name>"
path = "/candidate"
default-features = false
```

The `<candidate-package-name>` token is replaced with the exact frozen package name after validating `[A-Za-z0-9_-]+`. The resulting bytes use LF, no trailing spaces, one final LF, and TOML keys/sections exactly as shown. The fixed synthetic golden package name `rust_cargo_fixture_candidate` yields manifest SHA-256 `7cd84b7485bf393f074abd03bf8ce9d5f5204f793a1565d1b6a34ed63fed561c`; production substitution yields a separately recorded digest. `serde`, `serde_json`, and `pollster` are verifier-owned frozen dependencies; candidate does not receive them as direct dependencies. Candidate feature names are never passed directly to the bridge root: each enabled candidate feature is represented by a generated root forwarding feature `candidate_<safe-feature> = ["candidate/<safe-feature>"]`, sorted by UTF-8 bytes. Thus async-channel's candidate command is `--no-default-features --features std`, while its bridge command is exactly `--no-default-features --features candidate_std`. Missing forwarding entries, unknown root features, or a bridge feature that is not forwarded is a hard failure. The manifest digest is calculated after substitution and included in the golden fixture for each candidate.

The exact generated Rust expansion uses these expressions, with `arg0`...`argN` in descriptor order and `candidate` the generated dependency crate name:

```text
free sync:       candidate::module::function(arg0, ..., argN)
free async:      pollster::block_on(candidate::module::function(arg0, ..., argN))
associated:      candidate::Type::function(arg0, ..., argN)
instance &self:  StateTable::get_ref::<Type>(&table, handle)?.function(arg0, ..., argN)
instance &mut:   StateTable::get_mut::<Type>(&mut table, handle)?.function(arg0, ..., argN)
state create:    Box::new(candidate::Type::create(arg0, ..., argN))
state drop:      StateTable::remove::<Type>(&mut table, handle)?
custom drop:     candidate::Type::drop_method(&mut *StateTable::get_mut::<Type>(
                   &mut table, handle)?)
```

`module::function`, `Type`, and method names are emitted from validated path components, never interpolated from a request. The generator emits no `unsafe` expression except the reviewed unsafe API call itself, which uses the same free/associated expression inside the single-operation unsafe leaf. It emits `StateTable` as a typed enum containing one variant per sorted `StateDescriptor`; ownership is `HashMap<String, StateSlot>` with handles allocated monotonically as `s0`..`s31`, and no handle is reused within a process. `StateTable::get_ref/get_mut` verify slot type and live status; `remove` takes ownership and drops the slot before returning. The table and every slot are owned by the bridge process, never by Python or the candidate caller.

Every generated call expression is wrapped exactly as `std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| { EXPR }))`. `Ok(Ok(value))` becomes `status=ok` with encoded return value. For a declared `Result<T,E>`, `Ok(Err(error))` becomes `status=declared-error`, `value=encode(error)`, `error_type=E`'s descriptor ID, and `message=null`; non-Result APIs cannot emit declared-error. `Err(payload)` from `catch_unwind` becomes `status=panic`, `value=null`, `error_type="panic"`, and a bounded canonical message: `&str`/`String` payload bytes if UTF-8, otherwise `"non-string panic payload"`, truncated to 4096 bytes. Panic does not cross the process or mutate the response schema.

Async expressions use `pollster::block_on` inside the same `catch_unwind` closure. There is no second executor and no internal retry. A future that completes returns `ok` or `declared-error`; a panic maps to `panic`; F1 wall timeout kills the process group and maps the leaf to `failed` with `timed_out=true`; a nonzero/abort maps to `failed`, and a malformed bridge line maps to trusted `error`. A future is not allowed to spawn a background task or thread. F1 timeout and cleanup receipts are authoritative; the bridge cannot self-report completion after timeout.

Operations execute strictly in request array order. The bridge appends one result after each completed operation. A protocol error, panic, timeout, or process abort ends the batch; later operations are not executed. A state panic/abort discards the whole table. State create/call/drop are thus deterministic ownership transitions: create inserts one owned slot, call borrows only for the duration of `EXPR`, drop removes and destroys it. The bridge assigns handles and response IDs; request handles are accepted only when they name a live slot of the expected descriptor type.

Generator canonicalization is exact: template bytes are copied first; generated sections follow the order `imports`, `type adapters`, `StateTable`, `operation dispatch`, `JSON main`; each section and item is sorted by canonical UTF-8 ID, indentation is four ASCII spaces, line endings are LF, there are no trailing spaces, and the file ends with one LF. The generator then runs the pinned rustfmt binary with `--edition 2021 --emit stdout`; rustfmt output must be UTF-8, LF-only, and is the final generated-source byte stream. Golden tests compare generated `Cargo.toml` and Rust source bytes and SHA-256, parse the same bytes with Rust and Python, and reject any digest not listed in the candidate's frozen golden fixture. `tests/test_rust_bridge.py` contains fixtures for free, associated, instance, state create/call/drop, declared-error, panic, async completion/timeout, ordering, and canonicalization.

### 10C. Candidate stdout isolation and bridge protocol channel

The generated bridge has two physically distinct output channels. Bridge-owned stdout is reserved exclusively for one canonical `RustBridgeResponse` line. Before each candidate operation expression is evaluated, the trusted generated runtime installs a bounded candidate-output channel by saving the bridge stdout descriptor, redirecting the process stdout descriptor to a dedicated pipe, and restoring the descriptor in an unconditional guard before serializing the bridge response. Candidate `println!` and `std::io::Write` to stdout are permitted; they cannot write into the bridge protocol pipe.

The channel contract is fixed: a trusted reader drains the pipe concurrently, retains at most `candidate_stdout_max_bytes = 1048576` bytes, computes SHA-256 over all retained bytes, and continues draining after the cap only to prevent blocking. `candidate_stdout_overflow=true` is set when any byte beyond the cap is observed. The bridge response is emitted only after stdout is restored. Candidate stdout is never parsed as JSON, never treated as a response line, and never causes trusted transport invalidity. A candidate stdout overflow maps the affected leaf to `failed`, detail `candidate-call-failed:output-limit`, with the candidate-output receipt retained; subsequent batch leaves receive `candidate-call-aborted:aborted-before-execution`.

Candidate stderr is not redirected: it remains the candidate process's stderr and is captured by unchanged F1 aggregate stdout/stderr accounting. F1's `output_limit_exceeded` has precedence for aggregate overflow and maps to the candidate failure row. The adapter records both channels separately: `candidate_stdout_bytes`, `candidate_stdout_sha256`, `candidate_stdout_overflow`, `candidate_stderr_bytes/sha256` as available from F1, and the bridge response bytes/sha256. Only the bridge response is parsed by the Rust normalizer.

The stdout guard is installed inside the exact `catch_unwind(std::panic::AssertUnwindSafe(...))` operation wrapper and restored on `ok`, declared error, panic, serializer failure and every Rust return path. A panic after candidate output therefore produces `status=panic` and a bounded candidate-output receipt; it cannot corrupt bridge stdout. A process abort, signal, F1 timeout, F1 output limit or candidate cgroup OOM prevents restoration in that process and is handled by unchanged F1 result mapping as candidate failure; missing bridge response in that case is not a trusted transport error. A trusted bridge invariant failure while installing/restoring the channel is instead `valid-bridge-invariant`, invalidates the report, and records a collection error. The helper never exposes pipe descriptors, bridge stdout descriptors, or output-channel handles through the API plan or candidate values.

The output-flood control fixture prints more than 1048576 bytes from an otherwise terminating candidate operation and must produce a valid report with one failed leaf and the later-leaf aborted mapping. A fixture that prints a normal line followed by a valid bridge response must still parse as one valid response and must not produce `trusted-transport-schema`. Receipts include channel setup/restore result, retained size, overflow flag, retained-byte digest, bridge-response line count/digest, F1 result fields, process exit, panic/abort status, timeout, cleanup and cgroup events.

### 10D. Normative operation, protocol and LeafReport contract

Every bridge operation and every CLI invocation carries exactly one `leaf_id` from the frozen private leaf inventory. `operation_id` is a trusted, per-request correlation identifier, unique within the request and distinct from `leaf_id`; it is never used as a leaf identifier. A state batch's private `operation_plan` maps each ordered operation ID to one leaf ID, and no leaf ID may occur twice in a batch. CLI `RustCliInvocation.leaf_id` is mandatory. The trusted runner independently enumerates all frozen leaf IDs in canonical UTF-8 order and emits exactly one `LeafCase` for each, regardless of response order or process termination.

Hidden expectations are private verifier-owned records:

```text
ExpectedLeafAssertion = {
  leaf_id: SafeId,
  expected: value-match(RustValue)
          | declared-error(error_type: TypeRef, value: RustValue)
          | cli(stdout_base64, stderr_base64, exit_code, tempdir_inventory)
          | no-assertion,
  initial_status: null|skipped|todo|xfail
}
```

There is exactly one assertion for every frozen leaf ID. Expected values and expected declared-error values are private test/verifier bytes. The public API plan exposes only frozen leaf IDs; `assertion_id` and `assertion_digest` are rejected as public extra fields. The private inventory is the sole binding from leaf_id to ExpectedLeafAssertion and is canonicalized as UTF-8 JSON with sorted object keys, leaf records sorted by leaf_id, expected structures recursively canonicalized, exactly one final LF, and SHA-256 `private_assertion_inventory_digest`. It is private verifier-only, is never mounted in candidate/model/bridge namespaces, and its digest plus visibility=`private` and record count are bound into `rust_execution_identity` and receipts; neither expected value enters candidate source, generated bridge source, bridge request, or model namespace. `collected == frozen_total > 0`; candidate output cannot create, remove, reorder, rename, or claim a leaf.

The closed protocol taxonomy is:

```text
trusted-transport-schema:
  request or response line missing/multiple; JSON/base64/canonical encoding error;
  unknown/duplicate field; request_id mismatch; response count mismatch;
  operation_id/leaf_id mismatch; duplicate operation or leaf; invalid operation plan;
  invalid RustValue/type/variant/map order; candidate response contains forbidden field.
valid-bridge-invariant:
  trusted generated bridge detects an impossible internal state-table, type-table,
  ownership, serializer, or dispatch invariant after a valid request;
  this is never emitted as a candidate operation status.
candidate-operation-failure:
  the selected public candidate function returns a declared error, panics inside
  catch_unwind, exits/aborts, times out, exceeds output, or is killed by candidate
  cgroup OOM; this is represented by the operation result or F1 result, never by a
  bridge-produced protocol-error status.
```

The bridge is never allowed to emit `status=protocol-error`. Its closed operation-result status is only `ok|declared-error|panic`; a valid operation cannot masquerade as a protocol error. A wrong handle, wrong type, duplicate operation, malformed request, serialization failure, or impossible bridge invariant is reported through trusted runner diagnostics/exit and classified by the taxonomy above. Thus no “candidate-produced protocol-error” row exists.

`LeafReport` remains the unchanged structure with exactly `framework`, `report_format`, `collected`, `leaves`, `collection_errors`, `trusted_runner_exit_code`, and `frozen_total`; `LeafCase` has `leaf_id`, one allowed status `passed|failed|error|skipped|todo|xfail`, duration, and bounded details. `LeafReport` has no `valid` field. The unchanged evaluator returns `EvaluationResult.valid`, which is the only validity field used for grading.

| condition | leaf/assertion result | LeafCase.status | details and failure class | EvaluationResult.valid | collection_errors | later leaves |
| --- | --- | --- | --- | --- | --- | --- |
| operation `ok`; exact value match, or CLI exact stdout/stderr/exit/tempdir match | expected match | `passed` | `ok` | true | none | execute normally |
| operation `ok`; value/CLI assertion mismatch | expected mismatch | `failed` | `candidate-call-failed`, `expected-value-mismatch` | true | none | execute normally |
| operation `declared-error`; private expected error type and value match | expected declared error | `passed` | `declared-error-expected` | true | none | execute normally |
| operation `declared-error`; wrong type/value, or expected error but `ok` | unexpected declared error | `failed` | `candidate-call-failed`, `unexpected-declared-error` | true | none | execute normally |
| `no-assertion` and operation `ok` | no comparison | `passed` | `no-assertion` | true | none | execute normally |
| `no-assertion` and operation `declared-error` | unexpected error | `failed` | `candidate-call-failed`, `unexpected-declared-error` | true | none | execute normally |
| bridge `panic` from exact `catch_unwind` | any executable assertion | `failed` | `candidate-call-failed`, `panic` | true | none | later operations abort |
| candidate F1 nonzero/abort, timeout, `output_limit_exceeded`, or candidate cgroup OOM | any executable assertion | `failed` | `candidate-call-failed`, `exit|abort|timeout|output-limit|oom` | true | none | later operations abort |
| a batch stops after candidate panic, F1 failure, timeout, output limit, abort, or OOM | every later frozen leaf | `failed` | `candidate-call-aborted`, `aborted-before-execution` | true | none | none |
| frozen `initial_status=skipped|todo|xfail` | explicit private status | exact initial status | `frozen-leaf-status` | true | none | execute other batches |
| trusted transport/schema taxonomy | no candidate assertion | `error` for every frozen leaf | `verifier-internal-error`, `trusted-transport-schema` | false | exactly one bounded error | stop trial |
| valid-bridge-invariant taxonomy | no candidate assertion | `error` for every frozen leaf | `verifier-internal-error`, `valid-bridge-invariant` | false | exactly one bounded error | stop trial |
| F1 `cleanup_complete=false`, non-null `cleanup_error`, UID residue, or trusted cleanup failure | no candidate assertion | `error` for every frozen leaf | `verifier-internal-error`, `cleanup-failed` | false | exactly one bounded error | stop trial |
| trusted bridge/verifier/Miri runner OOM or abnormal exit without valid report | no candidate assertion | `error` for every frozen leaf | `runner-abnormal-exit` | false | exactly one bounded error | stop trial |
| outer Harbor/verifier deadline before trusted result | no candidate assertion | `error` for every frozen leaf | `verifier-timeout` | false | exactly one bounded error | stop trial |

For all valid candidate-operation failures, the directly affected leaf receives the observed failure and every later unexecuted frozen leaf receives `candidate-call-aborted`; the report keeps the positive fixed denominator and is usable by the ordinary metric. For any trusted taxonomy, the runner emits one `error` case per frozen ID plus exactly one bounded collection error, sets `trusted_runner_exit_code` to the trusted failure code, and passes an invalid report to the unchanged evaluator; it never converts trusted failure to candidate failed leaves or a model reward of zero. Candidate cannot provide `valid`, reward, collection count, JUnit, expected values, or failure class. `tests/test_rust_normalizer.py` and `tests/test_rust_bridge.py` must assert every table row, one-to-one leaf binding, operation/leaf distinction, batch-abort behavior, and cross-language canonical fixtures.

### 10E. Exact unchanged evaluator field mapping

The Rust adapter uses only the existing enums `FailureClass.SOURCE|SPEC|ENVIRONMENT|VERIFIER|MODEL|INFRASTRUCTURE` and `VerificationReason` values `CANDIDATE_WORKSPACE_REJECTED|CANDIDATE_INSTALLATION_FAILED|CANDIDATE_CALL_FAILED|COLLECTION_ERROR|COLLECTION_MISMATCH|REPORT_COUNT_MISMATCH|RUNNER_ABNORMAL_EXIT|REPORT_EXIT_MISMATCH|VERIFIER_TIMEOUT|VERIFIER_INTERNAL_ERROR|INTEGRITY_FAILURE`; the closed labels `trusted-transport-schema`, `valid-bridge-invariant`, `cleanup-failed`, `candidate-call-aborted`, `panic`, `timeout`, `output-limit`, and `oom` are details strings only, never enum values.

The normalizer constructs the unchanged `LeafReport` with exact fields `framework`, `report_format`, `collected`, `leaves`, `collection_errors`, `trusted_runner_exit_code`, and `frozen_total`. Each `LeafCase` has `leaf_id`, allowed `status`, `duration_ms`, and bounded `details`. Each `LeafCollectionError` has exactly `message` and optional `leaf_id`. The normalizer never adds `valid`, `failure_class`, `failure_reason`, `reward`, or `runner_exit_code` to `LeafReport`; those belong only to the evaluator's `EvaluationResult` (`metric_contract`, `valid`, `reward`, `frozen_total`, `counts`, `report`, `runner_exit_code`, `failure_class`, `failure_reason`, `details`).

The exact evaluator-facing rows are:

| closed condition | LeafReport fields | EvaluationResult fields after unchanged `evaluate_leaf_report` | taxonomy/details |
| --- | --- | --- | --- |
| normal success, all expected values match | `collected=frozen_total`; all leaves `passed` or frozen `skipped|todo|xfail`; `collection_errors=()`; `trusted_runner_exit_code=0` | `valid=true`; `runner_exit_code=0`; `failure_class=None`; `failure_reason=None`; `details=()`; `reward=passed/frozen_total` | leaf details `ok` or `frozen-leaf-status` |
| candidate value/CLI mismatch, unexpected declared error, panic, candidate nonzero/abort, timeout, output limit or candidate OOM | one `failed` leaf per affected/aborted frozen ID as §10D; `collection_errors=()`; `trusted_runner_exit_code=1` | `valid=true`; `runner_exit_code=1`; `failure_class=None`; `failure_reason=None`; `details=()`; reward from failed/passed leaf counts | `VerificationReason.CANDIDATE_CALL_FAILED` is an adapter-side classification detail only when emitting gate evidence; it is not inserted into `EvaluationResult` for a valid report. Leaf details carry `candidate-call-failed:<panic|exit|abort|timeout|output-limit|oom>` or `candidate-call-aborted:aborted-before-execution`. |
| trusted transport/schema failure | one `error` leaf per frozen ID; exactly one `LeafCollectionError(message="trusted-transport-schema:<bounded reason>", leaf_id=null)`; `collected=frozen_total`; `trusted_runner_exit_code=1` | evaluator first accepts exit 1, then collection error yields `valid=false`, `runner_exit_code=1`, `failure_class=FailureClass.VERIFIER`, `failure_reason=VerificationReason.COLLECTION_ERROR`, `details=(same error message,)`, `reward=0.0` | no candidate leaf taxonomy; stop trial |
| valid-bridge-invariant failure | same report shape, message `valid-bridge-invariant:<bounded reason>` | `valid=false`; `runner_exit_code=1`; `failure_class=FailureClass.VERIFIER`; `failure_reason=VerificationReason.COLLECTION_ERROR`; `details=(same message,)`; `reward=0.0` | stop trial |
| F1 cleanup incomplete, `cleanup_error`, UID residue, trusted cleanup failure | same report shape, message `cleanup-failed:<bounded reason>` | `valid=false`; `runner_exit_code=1`; `failure_class=FailureClass.VERIFIER`; `failure_reason=VerificationReason.COLLECTION_ERROR`; `details=(same message,)`; `reward=0.0` | stop trial |
| trusted verifier/bridge/Miri runner OOM or abnormal exit without valid report | same report shape, message `runner-abnormal-exit:<bounded reason>` | `valid=false`; `runner_exit_code=1`; `failure_class=FailureClass.VERIFIER`; `failure_reason=VerificationReason.COLLECTION_ERROR`; `details=(same message,)`; `reward=0.0` | stop trial; infrastructure root cause is recorded in receipt, not invented as evaluator enum |
| outer Harbor/verifier deadline before trusted result | same report shape, message `verifier-timeout:<bounded reason>` | `valid=false`; `runner_exit_code=1`; `failure_class=FailureClass.VERIFIER`; `failure_reason=VerificationReason.COLLECTION_ERROR`; `details=(same message,)`; `reward=0.0` | stop trial |
| report count/exit mismatch or malformed normalizer output after a report exists | `collection_errors` has one bounded message, `trusted_runner_exit_code=1` | `valid=false`; `runner_exit_code=1`; `failure_class=FailureClass.VERIFIER`; `failure_reason=VerificationReason.COLLECTION_ERROR` for collection error, or `REPORT_COUNT_MISMATCH`/`REPORT_EXIT_MISMATCH` when the corresponding unchanged evaluator branch is reached; `details` exactly evaluator-generated bounded details | stop trial |

For valid candidate reports the evaluator intentionally leaves `failure_class` and `failure_reason` null; candidate attribution is carried by leaf `details` and the run receipt. For trusted invalid reports the adapter chooses `trusted_runner_exit_code=1`, never 2/64/70/75 in the canonical LeafReport path, so the unchanged evaluator reaches the stated collection-error branch; F1's own 64/70/75 transport exit remains in its unchanged subprocess receipt and is converted to the trusted collection message before normalization. This is the only Rust mapping and uses no invented enum member. `tests/test_rust_normalizer.py` must assert the exact Pydantic field values and enum members for every row.

## 11. Frozen dependency build-time isolation与resources

Frozen dependency build.rs/proc macro视为untrusted。它们以F1 install UID10001、no private mounts、no network、cleared environment、read-only source/vendor、writable target/temp、no_new_privs、zero caps、process cleanup执行。完整build member/package/checksum/command/result进入receipt；未inventory member拒绝。任何native/link directive或external executable需求拒绝。

Cgroup v2 fixed policy：verifier root memory.max=2147483648、swap=0、pids=64、cpu.max=`100000 100000`；install=1610612736 bytes/64 pids；bridge=268435456/64；CLI=536870912/64；Miri=536870912/64；all swap=0。F1 hard limits同时覆盖timeout/cpu/stdin/output/file/FD/process。每context记录memory.max/swap/pids/cpu/memory.events/OOM/cleanup。Candidate OOM是structured model failure；trusted verifier OOM或missing receipt为verifier/infrastructure failure。

Malicious control扫描/tests/private、verifier/logs/CAS/Oracle/provider env/proc/mounts，必须全部不可读且cleanup complete。

## 12. Miri offline sysroot与Oracle gate

### 12.1 Image-baked Miri sysroot

Miri component、rust-src、cargo-miri 和 target standard library 均来自第5节同一 provisional tuple。唯一允许生成 sysroot 的动作是 image build 中的 `MIRI_SETUP_ARGV`；Harbor trial 不运行 setup，不联网，不调用 rustup，也不重建 component/sysroot。

在 setup 前，image builder 必须先把已通过 F0.5 lock/store/inventory 校验的 private harness vendor root materialize 到 `/opt/nl2repobench-miri-harness/vendor`，并将其 manifest 放在 `/opt/nl2repobench-miri-harness/Cargo.toml`。setup image layer 已安装且已校验 miri-preview、rust-src、cargo-miri 和 target std archive；它使用 pristine empty `CARGO_HOME`、empty registry/index hierarchy 和 BuildKit `--network=none`。以下是唯一 canonical setup argv；12.4、Dockerfile、release gate 和 receipt 必须逐 token 使用它，不能省略 config 或换 path：

```text
MIRI_SETUP_ARGV = [
  "/opt/rust/bin/cargo", "miri", "setup",
  "--target", "x86_64-unknown-linux-gnu",
  "--config", "net.offline=true",
  "--config", "source.crates-io.replace-with=vendored-sources",
  "--config", "source.vendored-sources.directory=/opt/nl2repobench-miri-harness/vendor"
]
MIRI_PRINT_SYSROOT_ARGV = [
  "/opt/rust/bin/cargo", "miri", "setup", "--print-sysroot",
  "--target", "x86_64-unknown-linux-gnu",
  "--config", "net.offline=true",
  "--config", "source.crates-io.replace-with=vendored-sources",
  "--config", "source.vendored-sources.directory=/opt/nl2repobench-miri-harness/vendor"
]
MIRI_SETUP_ENV = {
  PATH="/opt/rust/bin:/usr/local/bin:/usr/bin:/bin",
  HOME="/tmp/miri-setup-home", CARGO_HOME="/tmp/miri-setup-home",
  CARGO_NET_OFFLINE="true", CARGO_INCREMENTAL="0",
  CARGO_TERM_COLOR="never", LC_ALL="C.UTF-8", TZ="UTC",
  TMPDIR="/tmp/miri-setup-tmp"
}
```

The image build executes exactly:

```bash
RUN --network=none env -i \
  PATH=/opt/rust/bin:/usr/local/bin:/usr/bin:/bin \
  HOME=/tmp/miri-setup-home CARGO_HOME=/tmp/miri-setup-home \
  CARGO_NET_OFFLINE=true CARGO_INCREMENTAL=0 CARGO_TERM_COLOR=never \
  LC_ALL=C.UTF-8 TZ=UTC TMPDIR=/tmp/miri-setup-tmp \
  /opt/rust/bin/cargo miri setup --target x86_64-unknown-linux-gnu \
  --config net.offline=true \
  --config source.crates-io.replace-with=vendored-sources \
  --config source.vendored-sources.directory=/opt/nl2repobench-miri-harness/vendor
RUN --network=none env -i \
  PATH=/opt/rust/bin:/usr/local/bin:/usr/bin:/bin \
  HOME=/tmp/miri-setup-home CARGO_HOME=/tmp/miri-setup-home \
  CARGO_NET_OFFLINE=true CARGO_INCREMENTAL=0 CARGO_TERM_COLOR=never \
  LC_ALL=C.UTF-8 TZ=UTC TMPDIR=/tmp/miri-setup-tmp \
  /opt/rust/bin/cargo miri setup --print-sysroot --target x86_64-unknown-linux-gnu \
  --config net.offline=true \
  --config source.crates-io.replace-with=vendored-sources \
  --config source.vendored-sources.directory=/opt/nl2repobench-miri-harness/vendor
```

The builder captures the print command stdout, requires one absolute path, and safely copies that tree to `/opt/nl2repobench-miri-sysroot/x86_64-unknown-linux-gnu`; the final path is root-owned and read-only. It records canonical tree digest in the locked toolchain. The final verifier image contains the fixed path, staged harness vendor root, component inventory, and no writable rustup/Cargo registry cache.

The final-image probe executes the same `MIRI_PRINT_SYSROOT_ARGV` and `MIRI_SETUP_ENV` with `--network=none`, then requires stdout to identify the fixed path and exact locked sysroot tree digest. This is a probe, not setup. Setup/probe receipts contain the exact argv arrays above, environment digest, stdout/stderr paths and hashes, exit code, network=false, component/archive/executable hashes, harness manifest/lock/vendor/inventory hashes, sysroot path/tree digest, and cgroup/cleanup results. Any missing staged vendor root, registry access, setup in a trial, path/tree mismatch, unsupported component, nonzero exit, or network observation keeps the toolchain `provisional-unlocked` and blocks Oracle.

### 12.2 Miri harness/vendor root

Oracle-only Miri harness位于private verifier bundle：

```text
miri/Cargo.toml
miri/Cargo.lock
miri/vendor/**
miri/tests/nl2repo_miri.rs
```

其vendor root由相同closure preparation/vendorization流程生成，lock/store/inventory和API/leaf list digest进入execution identity。Miri candidate source、trusted harness和vendor materialize到Oracle-only staging；model/candidate/verifier-normal namespaces看不到Miri assertions。

### 12.3 Exact Miri invocation

对每个frozen unsafe leaf单独运行，feature args由第6.3节函数生成：

```bash
env -i \
  PATH=/opt/rust/bin:/usr/local/bin:/usr/bin:/bin \
  HOME=/tmp/miri-run-home CARGO_HOME=/tmp/miri-run-home \
  CARGO_NET_OFFLINE=true CARGO_INCREMENTAL=0 CARGO_TERM_COLOR=never \
  LC_ALL=C.UTF-8 TZ=UTC TMPDIR=/tmp/miri-tmp \
  MIRI_SYSROOT=/opt/nl2repobench-miri-sysroot/x86_64-unknown-linux-gnu \
  MIRIFLAGS='' \
  /opt/rust/bin/cargo miri test \
    --manifest-path /opt/nl2repobench-miri-harness/Cargo.toml \
    --locked --offline --frozen --target x86_64-unknown-linux-gnu \
    --config net.offline=true \
    --config source.crates-io.replace-with="vendored-sources" \
    --config source.vendored-sources.directory="/opt/nl2repobench-miri-harness/vendor" \
    <profile-feature-argv> --test nl2repo_miri -- \
    --exact <frozen-unsafe-leaf-id> --nocapture
```

尖括号项由trusted typed argv builder从frozen profile/leaf inventory展开，不能由user/model提供。Receipt schema固定包含：execution identity、leaf ID、feature args digest、full argv、environment/config digest、MIRI_SYSROOT path/tree digest、cargo/cargo-miri/miri/rustc executable digests、`cargo -Vv`/`rustc -Vv` hashes、component/rust-src archive digests、harness manifest/lock/vendor/inventory digests、target、start/end、exit code、timeout、stdout/stderr/log paths+SHA、network=false、cgroup values/events、unsupported diagnostics、cleanup result。

每unsafe leaf必须exit0、无UB/unsupported diagnostic、network=false、cleanup true。Unsupported、missing sysroot、setup drift、UB、timeout或nonzero均是Oracle authoring blocker，不能转换为reward或memory-safety结论。Candidate Miri可以保存diagnostic但不评分。


### 12.4 Miri component and offline provisioning invariant

The toolchain image install is the only place allowed to obtain `miri-preview`, `rust-src`, `cargo-miri`, and the target standard library. The installer downloads the exact archive URLs named by the channel manifest in a networked build step, verifies each archive hash before installation, and writes a component inventory containing component name, channel manifest hash, archive hash, installed tree digest, and executable hashes. It then runs the Miri setup step in a separate BuildKit `--network=none` step with the already-installed component and a staged Miri sysroot; this step may not invoke rustup, cargo install, git, or an index fetch.

The setup step must use a pristine `CARGO_HOME`, an image-baked empty registry hierarchy, the exact target, and the same trusted source-replacement `--config` arguments used by consumption. The harness vendor root is copied into `/opt/nl2repobench-miri-harness/vendor` before setup. The final verifier image contains the resulting sysroot at the exact locked path, owned by root and read-only, plus the component inventory. It does not run setup during a Harbor trial. The trial only performs a network-none `--print-sysroot` probe and compares canonical path and tree digest to the lock.

The Miri harness is a private, task-scoped Cargo package. Its `Cargo.lock`, vendor root, source inventory, and all transitive registry archives are materialized by F0.5 authorization under the Oracle-only run context. Every Miri command includes `--locked --offline --frozen`, the selected target, `--config net.offline=true`, `source.crates-io.replace-with="vendored-sources"`, and `source.vendored-sources.directory` pointing at that harness vendor root. No command may depend on a host Cargo registry, ambient `CARGO_HOME`, rustup cache, network, or an unpinned `miri` binary. A missing component, missing vendor member, setup attempt during a run, sysroot path/tree mismatch, nonempty ambient Cargo hierarchy, or network observation is a hard toolchain/Oracle blocker, never a candidate result.

## 13. Identities与strict receipts

`rust_build_identity`包含：verified locked toolchain digest、full cargo/rustc output hashes和executable hashes、target、rust profile、完整CLI profile（含`cli_timeout_sec`和`expected_exit_codes`）、feature tuple、candidate manifest/dependency set、lock/store/inventory、selected target deps。CLI timeout和expected exit code不得从descriptor或命令覆盖。

`rust_execution_identity`在build identity基础上包含：verifier/test/commands/oracle categorized refs、verifier+harness+Miri closure、API plan、bridge generator/source/binary、normalizer/runner/grader、scanner policy/binary、Cargo env/config、Miri sysroot/component、images、cgroup/network policy、public Oracle bootstrap digest、run wrapper source digest。

Strict receipt字段：receipt ID/stage/mode/task/execution identity、完整CLI profile（`cli_timeout_sec`、`expected_exit_codes`）、argv/cwd/environment/config/mount/cgroup digests、toolchain/images、input refs/digests、exit/timeout/OOM/cleanup、stdout/stderr/log/report paths和SHA、network、start/end、failure class/reason。Paths repo-relative or run-root-relative、regular/non-symlink；gate重新hash所有bytes并拒绝missing/mutable/cross-task/execution mismatch。

## 14. Committed refs-only projection与public Oracle bootstrap

Committed task layout：

```text
catalog/tasks/<task-id>/
  task.toml
  instruction.md
  README.md
  rust-profile.json
  bundle.manifest.json
  private-artifact-refs.json
  environment/Dockerfile
  tests/Dockerfile
  tests/docker-compose.yaml
  tests/test.sh
  tests/runtime/nl2repobench/**
  solution/solve.sh
  controls/**
```

禁止Cargo.lock/vendor/.crate/index/private tests/verifier/API plan/reference source/CAS/.nl2repo/output进入Git。Manifest只记录refs、tree/inventory digest、build/execution identity和public file inventory。

`solution/solve.sh`是explicit public non-sensitive bootstrap，固定内容：

```sh
#!/bin/sh
set -eu
exec /opt/nl2repobench-oracle/run
```

它不含reference implementation、source URL、commit、digest、host、private value、credential、test assertion或reward。模型可见该bootstrap不获得Oracle能力。

Oracle bundle保持private CAS，包含root-owned executable`run`、source-fetch/verify metadata和reference delivery bytes。只有`rust_harbor_run.py oracle`的scoped authorization包含oracle digest，并materialize到run-specific`oracle-private/`，mount到Oracle agent namespace的`/opt/nl2repobench-oracle`。该mount在model、candidate、normal verifier和control namespaces中不存在。Oracle mode只授权exact source host，private `run`断言revision和source digest；model/control不继承host authorization。Control view以public compiler-owned control bootstrap替换solution bootstrap，不mount private Oracle。

该方案满足existing compiler要求generated task存在`solution/solve.sh`，同时保持Oracle bytes私有。

## 15. Repository-owned Harbor run wrapper

Stock Harbor 0.21不解析`artifact://` refs、不构造authorization、不materializeprivate context。本仓库唯一Rust run入口是：

```text
scripts/rust_harbor_run.py
```

### 15.1 API

```text
RustHarborRunRequest(strict):
  mode: model | oracle | control
  task_root: committed catalog/tasks/<id>
  artifact_root: .nl2repo/artifacts
  toolchain_lock: toolchain.rust.lock.toml
  run_id: safe unique ID
  output_root: .nl2repo/runs/<run-id>
  campaign_manifest: required only model
  model_index: 0|1 only model
  attempt: 1|2 only model
  control_kind: enum only control

RustHarborRunResult(strict):
  execution_identity
  materialized_task_path
  harbor_command
  harbor_version
  exit_code
  evidence_manifest_path/digest
  grading/network/process/cgroup/mount receipt paths/digests
  retention_status
  cleanup_status
```

### 15.2 Materialization algorithm

1. Resolve task_root under repository、reject symlink/dirty generated files、parse`bundle.manifest.json`和`private-artifact-refs.json`、recompute public inventory和execution identity。
2. Require locked toolchain and exact Harbor0.21/runner lock。
3. Build scoped authorization from categorized refs only：model=dependency+test+verifier，oracle=model set+oracle，control=dependency+test+verifier+selected public control；never acceptdigest/path from CLI。
4. Invoke`RustHarborCompiler.materialize_run_context(task_root, authorization, mode, run_id)`，which usesF0.5 materializer to sibling temp thenatomic rename：

```text
.nl2repo/compiled/<task-id>/<execution-identity>/harbor-context/<run-id>/task
```

5. Copy public projection intocontext；materialize candidate lock/store、verifier/test bundle；oracle mode materializesprivate solution toseparate`oracle-private`mount；model excludesoracle；control createsselected control view。Verify all tree digests/read-only modes/mount policy。
6. Pass the exact materialized `/.../<run-id>/task` path, not committed refs-only path, to stock Harbor。
7. Record execution identity、authorization digest、materialized tree digest、exact Harbor command/version、receipts。
8. After Harbor returns, verifygrading/reward/network/process/cgroup/mount/evidence hashes and archive run。Only whenevidence manifest isverified andretention status=`retained` may wrapper destroyrun-specific staging。Failure/missing evidence movesstaging to`.nl2repo/compiled-quarantine/<run-id>`；never destroy beforeverified evidence。

### 15.3 Exact commands

Oracle：

```bash
uv run python scripts/rust_harbor_run.py oracle \
  --task-root catalog/tasks/rust-cargo-synthetic \
  --artifact-root .nl2repo/artifacts \
  --toolchain-lock toolchain.rust.lock.toml \
  --run-id rust-cargo-synthetic-oracle-r6 \
  --output-root .nl2repo/runs/rust-cargo-synthetic-oracle-r6
```

Wrapper内部固定调用：

```bash
uv run --frozen --project harbor-runner harbor run \
  -p .nl2repo/compiled/rust-cargo-synthetic/<execution-identity>/harbor-context/rust-cargo-synthetic-oracle-r6/task \
  -a oracle --job-name rust-cargo-synthetic-oracle-r6 \
  -o .nl2repo/runs/rust-cargo-synthetic-oracle-r6 \
  --n-concurrent 1 --yes
```

Control：

```bash
uv run python scripts/rust_harbor_run.py control \
  --task-root catalog/tasks/rust-cargo-synthetic \
  --artifact-root .nl2repo/artifacts \
  --toolchain-lock toolchain.rust.lock.toml \
  --control-kind stub \
  --run-id rust-cargo-synthetic-stub-r6 \
  --output-root .nl2repo/runs/rust-cargo-synthetic-stub-r6
```

Wrapper materializesstub view and invokes stock Harbor with`-a oracle`againstmaterialized control task；private Oracle excluded。

Model campaign manifest固定包含exact two agents/models、attempts_per_model=2、budget/provider host runtime authorization、task/version/execution identity。单attempt：

```bash
uv run python scripts/rust_harbor_run.py model \
  --task-root catalog/tasks/<promoted-task-id> \
  --artifact-root .nl2repo/artifacts \
  --toolchain-lock toolchain.rust.lock.toml \
  --campaign-manifest reports/rust-model-campaign-r6.json \
  --model-index 0 --attempt 1 \
  --run-id <campaign-derived-run-id> \
  --output-root .nl2repo/runs/<campaign-derived-run-id>
```

Wrapper从campaign读取agent/model并调用stock Harbor materialized task；执行model indices0,1和attempts1,2共4次。CLI不能覆盖execution identity、private refs、materialized path、provider host或Harbor command。


### 15.4 Concrete Harbor 0.21.0 execution seam

The wrapper does not depend on an undefined Harbor hook. It imports the pinned runner API from the lock recorded in `harbor-runner/pyproject.toml`, asserts `harbor.__version__ == "0.21.0"`, and uses `Job` and `JobConfig` from `harbor`, and trial-level `AgentConfig`, `EnvironmentConfig`, and `TaskConfig` from `harbor.models.trial.config`. The executable Rust path is:

```python
from harbor import Job, JobConfig
from harbor.models.trial.config import AgentConfig, EnvironmentConfig, TaskConfig

config = JobConfig(
    job_name=run_id,
    jobs_dir=output_root / "jobs",
    n_attempts=1,
    n_concurrent_trials=1,
    quiet=True,
    tasks=[TaskConfig(path=materialized_task_path)],
    agents=[AgentConfig(name=agent_name, model_name=model_name, extra_allowed_hosts=effective_provider_hosts)],
    environment=EnvironmentConfig(
        type="docker",
        mounts=oracle_mounts,
        extra_docker_compose=[],
        extra_allowed_hosts=[],
    ),
)
job = await Job.create(config)
result = await job.run()
```

`agent_name` is exactly `"oracle"` for Oracle and control modes; model mode takes the model entry from the signed campaign manifest. Control mode uses the repository control agent and never carries provider credentials. The wrapper passes no unrecognized kwargs and does not monkey-patch Harbor classes. CLI `harbor run` remains a supported diagnostic invocation for a fully public task; it is not the production Rust run path because it cannot construct the scoped private authorization.

For Oracle mode, `oracle_mounts` contains exactly one additional entry, constructed only after the private bundle digest has been authorized and materialized:

```python
{
    "type": "bind",
    "source": str(oracle_private_dir.resolve()),
    "target": "/opt/nl2repobench-oracle",
    "read_only": True,
    "bind": {"create_host_path": False},
}
```

This is the Harbor 0.21.0 `EnvironmentConfig.mounts` contract. The source is a run-specific root-owned directory containing only the private executable `run` and its verified delivery metadata; it is never the CAS root. Harbor's `Trial._agent_env_mounts` adds configured mounts to the agent environment, while `Trial._verifier_env_mounts` constructs the separate verifier environment from the verifier directory only. The wrapper asserts the resulting agent mount manifest has this exact target and the separate verifier mount manifest does not. The public committed `solution/solve.sh` remains `exec /opt/nl2repobench-oracle/run`; it contains no private bytes.

Model and control `oracle_mounts` are the empty list. Their materialized task contexts contain no Oracle bundle, private Oracle digest authorization, source-fetch host authorization, provider secret, or Oracle target path. Dependency, test, and verifier refs are materialized into the task context or the role-specific build context according to the existing F0.5 contract; they are not made visible through an unrestricted host mount. All bind entries are absolute, regular, non-symlink sources, `read_only=true`, and `create_host_path=false`; the wrapper rejects any task-provided mount, volume, image mount, extra compose overlay, `network_mode`, or `networks` override.

The exact async entry point is `scripts/rust_harbor_run.py:async_main`, and the only calls that start Harbor are `await Job.create(config)` followed by `await job.run()`. A subprocess call is permitted only for the wrapper's preflight CAS/hash checks and for the pinned `harbor` process in diagnostic mode; production model/Oracle/control execution does not shell out to an unpinned command. The wrapper captures `job_dir`, each trial `result.json`, `reward.json`, grading/network/process/cgroup/mount receipts, the serialized redacted JobConfig, Harbor version, and all hashes into `RustHarborRunResult`. It verifies the evidence before deleting staging; on any missing or mismatched receipt it renames staging to the quarantine path and returns a typed failure.

### 15.5 Wrapper tests and authorization assertions

`tests/test_rust_harbor_run.py` must instantiate the wrapper with a fake pinned Harbor API and assert exact `JobConfig` values for all three modes. Its pinned-0.21.0 construction test must import `AgentConfig`, `EnvironmentConfig`, and `TaskConfig` from `harbor.models.trial.config`, import only `Job` and `JobConfig` from `harbor`, construct `TaskConfig(path=Path("/run/task"))`, `AgentConfig(name="oracle", model_name=None)` for Oracle, and `EnvironmentConfig(type="docker", mounts=[{"type":"bind","source":"/run/oracle-private","target":"/opt/nl2repobench-oracle","read_only":True,"bind":{"create_host_path":False}}])`; it must assert the exact task path, agent name/model, mount target/source/read-only/create_host_path and reach `Job.create` without validation error. Model/control cases must assert their exact agent/model and empty Oracle mount list. The pinned network-policy test must set the task agent baseline to `network_mode="no-network", allowed_hosts=[]`, set `EnvironmentConfig.extra_allowed_hosts=[]`, set only `AgentConfig.extra_allowed_hosts=["api.example.test"]`, and assert the resolved agent-phase policy allows exactly `api.example.test` while the environment baseline remains no-network; a second invocation with the agent list empty must deny the provider host. No other host, environment extra, wildcard, or generic public access may be enabled. The integration fixture then runs the real pinned API against a local Docker environment: committed refs-only projection plus approved CAS, Oracle read-only agent mount, no Oracle mount in verifier/model/control, `create_host_path=false`, and cleanup/quarantine behavior. A test must fail if `artifact://` reaches Harbor, if the private source is mounted at the CAS root, if a model config contains `oracle_mounts`, if a verifier receives the Oracle target, or if `Job.create`/`Job.run` is bypassed.

The wrapper's authorization input is a signed/canonical `private-artifact-refs.json` selected by mode; CLI values can select only an existing task, run ID grammar, model index/attempt, and control kind. They cannot select a digest, source path, mount target, compose path, provider host, toolchain, execution identity, or Harbor command. The wrapper recomputes every digest and serializes a mount authorization receipt with `mode`, categories, source tree digest, target, read-only flag, owner UID/GID, and cleanup result.

## 16. Synthetic proof

Task ID固定`rust-cargo-synthetic`，development-only，不进dataset。Single package含library+CLI；candidate direct dependency固定`itoa = =1.0.15`，harness有frozen serde_json/pollster；default_features=false、enabled=[]。

API固定：summarize(Payload)->Summary、normalize_async(Vec<String>)->Vec<String>、Counter state operations、unsafe bounded_xor(Vec<u8>,u8)->Vec<u8。20 leaves覆盖scalar/float/string/bytes/list/map/struct/enum/sync/error/async/state/unsafe/CLI。Unsafe两leaf不同PID、single operation。

Controls：normal Oracle20/20 reward1；panic/abort/crash trusted verifier存活；hang/output flood/setsid/double-fork bounded cleanup；empty structured0；installable stub<=0.20；forgery不能写trusted result；offline network=false；candidate-build.rs/proc macro/config/linker/rustflags/native拒绝；dependency build code隔离；private mount probe不可读；Miri setup/sysroot/vendor drift fail closed。

Synthetic Done还要求wrapper从committed refs-only task+approved CAS成功materialize并跑Oracle和全部controls；直接`harbor run -p catalog/tasks/...`不是valid Rust command/evidence。

## 17. Fixed real candidate funnel

Order1 async-channel2.5.0 commit`35a63c456aaa1906015f5a825e7e35505a749afa` source digest`e9509cf809eecc599dd0cea93e783fde9dd54fef72884dc6d2237342119df9ec` Apache-2.0 OR MIT，features false+[std]。

Order2 lexopt0.3.2 commit`f52c6a620b59dcadb01701c039cd4b270e2d5966` digest`9e106f75d6ce4cb77bcb14e7120100e5c8173b991913d1563f8208f7bf9b36d5` MIT，features false+[]。

Order6 humantime2.4.0 peeled commit`fc092817fa8689298eaac28ff49bd8bede4ff605` digest`18d6bf281ba67827602727cee729fd1af793fb360c4195b420e38ab043464776` MIT OR Apache-2.0，features false+[]；annotated tag object`d7963521a64ae1782e0ea72952943e84a62ee714`必须peel正确。

semver1.0.28因root build.rs拒绝。

三个candidate无tracked Cargo.lock。Gate order固定：freeze+license；closure preparation/vendorization；frozen metadata target list；3个fresh baseline；offline verifier；spec/traceability；Oracle/controls；two reviews。Baseline targets仅metadata中nonempty lib和explicit bins，不使用tests/examples。每个baseline argv由同一feature function构造；async-channel receipt必须含`--no-default-features --features std`。

Funnel receipt strict绑定source/license/toolchain full outputs/executables/channel manifest/index/crates/lock/store/inventory/target deps/feature tuple/argv/env/image/cgroup/log hashes。前一full pass立即promote；三者全fail写no-promotable-candidate，不自行扩候选。

## 18. Exact files

### 18.1 Foundation modified

```text
AGENTS.md
readme.md
docs/task-authoring-guide.zh-CN.md
docs/benchmark-operations-guide.zh-CN.md
docs/authoring-agent-remediation-guide.zh-CN.md
docs/authoring-pilot-retrospective-20260824.zh-CN.md
docs/node-foundation-status.v1.md
src/nl2repobench/cli.py
scripts/run_authoring_loop.py
scripts/authoring_supervisor.py
scripts/check_f0_runtime_contract.py
tests/test_f0_runtime_gate.py
```

### 18.2 Rust new

```text
toolchain.rust.dev.lock.toml
toolchain.rust.lock.toml
docker/rust/Dockerfile.toolchain
docker/rust/Dockerfile.agent
docker/rust/Dockerfile.verifier
src/nl2repobench/package_managers/cargo.py
src/nl2repobench/runtimes/rust.py
src/nl2repobench/authoring/runtime_asset_registry.py
src/nl2repobench/harbor/rust_compiler.py
src/nl2repobench/harbor/rust_toolchain.py
src/nl2repobench/verification/rust_models.py
src/nl2repobench/verification/rust_profile.py
src/nl2repobench/verification/rust_workspace.py
src/nl2repobench/verification/rust_bridge.py
src/nl2repobench/verification/rust_candidate_client.py
src/nl2repobench/verification/rust_contract_runner.py
src/nl2repobench/verification/rust_grader.py
src/nl2repobench/verification/normalize/rust_bridge_json.py
src/nl2repobench/verification/rust_source_scan/**
scripts/rust_harbor_run.py
scripts/check_rust_release_gate.py
reports/rust-cargo-candidate-funnel.v1.json
reports/rust-model-campaign-r6.json
tests/fixtures/rust-cargo-synthetic/**
tests/fixtures/rust-cargo-malicious/**
tests/test_cargo_package_manager.py
tests/test_rust_runtime.py
tests/test_rust_profile.py
tests/test_rust_workspace.py
tests/test_rust_bridge.py
tests/test_rust_normalizer.py
tests/test_rust_compiler.py
tests/test_rust_harbor_run.py
tests/test_rust_miri_offline.py
tests/test_rust_target_dependencies.py
tests/test_rust_feature_argv.py
tests/test_rust_security_controls.py
tests/test_rust_funnel_receipts.py
tests/test_r0_rust_seam_gate.py
```

### 18.3 Rust modified

```text
src/nl2repobench/domain/canonical_contract.py
src/nl2repobench/domain/runtime.py
src/nl2repobench/package_managers/__init__.py
src/nl2repobench/package_managers/registry.py
src/nl2repobench/authoring/catalog.py
src/nl2repobench/cli.py
src/nl2repobench/harbor/registry.py
src/nl2repobench/verification/__init__.py
src/nl2repobench/verification/cli.py
src/nl2repobench/verification/registry.py
src/nl2repobench/verification/normalize/__init__.py
schemas/v1/declarative-task-source.schema.json
schemas/v1/task-manifest.schema.json
schemas/v1/dataset-manifest.schema.json
docs/runtime-adapter-architecture.zh-CN.md
docs/network-policy.md
```

不修改evaluator、F1 API/models/supervisor/CLI、generic task writer、generic DependencyBundle/CAS/materializer业务逻辑。

## 19. Implementation phases与executable gates

P0 integrate F0 docs/flag+canonical atomic migration；P0.5 private staging；P1 F1。记录rust_base。

R0.1 domain/Cargo/profile/feature/target deps/source validator；R0.2 provisional toolchain fetch、Miri setup、images/probe、locked toolchain；R0.3 bridge/verifier/compiler/wrapper；R0.4 synthetic; R1 funnel/real reviewed；R2 only after Java pilot publication。

Core gates：

```bash
uv run nl2repo schema --check
uv run pytest -q --no-cov tests/test_cargo_package_manager.py tests/test_rust_runtime.py tests/test_rust_profile.py tests/test_rust_feature_argv.py tests/test_rust_target_dependencies.py tests/test_rust_workspace.py tests/test_rust_bridge.py tests/test_rust_normalizer.py tests/test_rust_compiler.py tests/test_rust_harbor_run.py tests/test_rust_miri_offline.py tests/test_rust_security_controls.py tests/test_rust_funnel_receipts.py tests/test_r0_rust_seam_gate.py
uv run ruff check src tests scripts
uv run mypy src/nl2repobench
uv run nl2repo task lint-network --include-generated
uv run python scripts/check_candidate_spawn_boundary.py --include-generated
```

Toolchain/Miri：

```bash
uv run python scripts/check_rust_release_gate.py toolchain --provisional toolchain.rust.dev.lock.toml --locked-output toolchain.rust.lock.toml
docker run --rm --network none nl2repobench/rust-verifier:<verified-image-id> /opt/nl2repobench/bin/rust-offline-probe
uv run pytest -q --no-cov tests/test_rust_miri_offline.py
```

Compile x2 only throughauthoritative scoped flag：

```bash
uv run nl2repo harbor compile tests/fixtures/rust-cargo-synthetic/source --output .nl2repo/rust-proof/compile-a --toolchain toolchain.rust.lock.toml --artifact-root .nl2repo/artifacts --authorize-task-private-artifacts
uv run nl2repo harbor compile tests/fixtures/rust-cargo-synthetic/source --output .nl2repo/rust-proof/compile-b --toolchain toolchain.rust.lock.toml --artifact-root .nl2repo/artifacts --authorize-task-private-artifacts
diff -qr .nl2repo/rust-proof/compile-a .nl2repo/rust-proof/compile-b
```

Run仅用第15节wrapper。Funnel：

```bash
uv run python scripts/check_rust_release_gate.py funnel --input reports/rust-cargo-candidate-funnel.v1.json --toolchain toolchain.rust.lock.toml --baseline-repetitions 3
```

R0：

```bash
uv run python scripts/check_rust_release_gate.py r0-seams --base <recorded-rust-base> --head HEAD
git diff --exit-code <recorded-rust-base>...HEAD -- src/nl2repobench/verification/evaluator.py src/nl2repobench/verification/subprocess_supervisor.py src/nl2repobench/verification/candidate_process_cli.py src/nl2repobench/harbor/task_writer.py
git diff --check
```

尖括号只表示由locked manifest、campaign或recorded commit解析的typed runtime value，不是human choice。Parser拒绝literal placeholder和CLI override。

## 20. Release semantics、residual risks与Definition of Done

Synthetic只在F0/F0.5/F1、locked toolchain/images/Miri sysroot、candidate+verifier closures、20 leaves、Miri、controls、wrapper materialization、network/mount/cgroup receipts、compile x2、private scan和R0 audit全部实际通过后称Rust Proof。Unit或Spec不是proof。

Real publication必须Java pilot通过、funnel first full pass、positive denominator、Oracle valid/reward>=0.80、controls、two reviews、campaign exact2 models x2 attempts、deterministic compile、private scan、wrapper receipts、archive、source+generated task commit和new dataset/release identity。Intermediate lifecycle不等于published。

Residual risks：foundation integration可能改变paths，必须在actualrust_base重跑；provisional toolchain tuple可能probe mismatch，mismatch只block不fallback；dependency build code仍不可信；Miri只覆盖frozen leaves；三候选可能均不符合narrow surface；Harbor/provider/Docker failures必须分类infrastructure；unverified evidence不得清理staging或解释model zero。

### Review findings retained as design blockers

- blocker：当前AGENTS/CLI仍是旧private flag，F0 atomic migration未完成。
- blocker：F0.5/F1和Rust images/Miri sysroot/run wrapper receipts不存在。
- blocker：stock Harbor不解析private refs，只有implemented/tested repository wrapper才能运行refs-only Rust task。
- major：Cargo/Rust expected tuple尚未actual probe；所有identity保持provisional-unlocked。
- major：三个candidate无tracked lock，closure必须受控生成和freeze。
- major：Miri unsupported、sysroot drift、offline/vendor failure均阻塞Oracle。

Definition of Done要求上述blocker被实际commands/evidence解除；R9不宣称它们已解除。

<!-- END OF NORMATIVE R9 SPEC -->

Non-attesting provenance note: R9 was produced from the R8 final gate artifact and inspection of the current `LeafReport` model. This transport envelope attests only delivery of this external document; it is outside the normative body and claims no implementation, test, toolchain, Miri, Harbor, Oracle, controls, or publication result.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Concrete severity-labelled findings and residual risks are recorded in Sections 1 and 20, including AGENTS.md:224, src/nl2repobench/cli.py:231, src/nl2repobench/verification/candidate_runner.py:36, src/nl2repobench/verification/leaf_report.py, and absent F1/Rust wrapper paths."
    }
  ],
  "changedFiles": [
    "/root/.pi/agent/sessions/--data-NL2RepoBench--/subagent-artifacts/outputs/12d5fe80-75b4-440d-98f4-a94a093cf04f/spec/rust-cargo-harbor-integration-final-r9.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "read R8 final gate artifact and current src/nl2repobench/verification/leaf_report.py",
      "result": "passed",
      "summary": "Confirmed all five R8 P1 findings and that LeafReport has no valid field."
    },
    {
      "command": "inspect current Rust/F1 symbols and Harbor 0.21 references",
      "result": "passed",
      "summary": "Confirmed the review-only repository context and existing evaluator/report contracts."
    },
    {
      "command": "run project implementation or release tests",
      "result": "not-run",
      "summary": "No implementation or release evidence was requested or claimed for this design-only replacement."
    }
  ],
  "validationOutput": [
    "R9 is a complete replacement specification, not a delta.",
    "All five R8 P1 blockers have explicit normative resolutions.",
    "The normative body ends before this non-attesting delivery envelope.",
    "No project files were edited or staged."
  ],
  "residualRisks": [
    "F0/F0.5/F1 integration, Rust images, exact toolchain probe, Miri sysroot, Harbor wrapper, controls and Oracle receipts remain unexecuted design blockers.",
    "The generated Rust golden source digest must be frozen from exact fixture bytes before implementation can be locked; no future digest is presented as executed evidence.",
    "The fixed three-candidate funnel may produce no promotable real candidate."
  ],
  "noStagedFiles": true,
  "diffSummary": "Created only the external R9 specification artifact; no project files were modified.",
  "reviewFindings": [
    "blocker: R8 feature forwarding - async-channel std was not forwarded to a bridge root feature; R9 defines generated forwarding features and exact bridge argv.",
    "blocker: R8 API-plan identity - assertion identity was claimed but absent from the strict schema; R9 uses private frozen leaf_id binding and rejects alternate fields.",
    "blocker: R8 transport attribution - malformed transport had conflicting trusted-invalid and candidate-protocol mappings; R9 separates them.",
    "blocker: R8 no-assertion mapping - successful no-assertion and failure outcomes were incomplete; R9 defines every row.",
    "blocker: R8 LeafReport.valid mismatch - current src/nl2repobench/verification/leaf_report.py has no valid field; R9 uses EvaluationResult.valid.",
    "blocker: current checkout is pre-F0/F0.5/F1 and lacks executable Rust/Miri/Harbor evidence; R9 preserves this as an explicit unexecuted blocker."
  ],
  "manualNotes": "Design-only artifact. This delivery record is outside the normative specification and is not implementation or release attestation."
}
```
