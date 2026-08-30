# NL2RepoBench

NL2RepoBench defines reproducible repository-generation evaluations and the evidence required to publish them.

## Language

**Authoring Truth**:
The human-owned declaration from which immutable benchmark artifacts are compiled.
_Avoid_: Published task, generated task

**Published Task Projection**:
A compiler-owned Harbor task included in a dataset release. It is never edited by hand.
_Avoid_: Authoring truth, source task

**Rust Platform Support**:
The shared ability to author and evaluate Rust packages through the benchmark's common contracts, rather than through a crate-specific harness.
_Avoid_: Rust task special case

**Rust Proof**:
A non-production synthetic evaluation that demonstrates the Rust and Cargo adapters compose with unchanged shared evaluation boundaries.
_Avoid_: Rust pilot, Rust production task

**Rust Production Lane**:
The published candidate-to-task pipeline for real Rust packages after its shared foundation, proof, and pilot gates pass.
_Avoid_: Rust proof

**Frozen Cargo Closure**:
The complete, immutable dependency set authorized for one Rust task, including checksums and any dependency-owned build-time code.
_Avoid_: Cargo cache, local registry

**Candidate Build-Time Code**:
Build scripts or procedural macros supplied by the generated candidate rather than by its frozen dependency closure.
_Avoid_: Frozen dependency build-time code

**Rust Verifier Harness**:
A verifier-owned executable that exercises a candidate crate or CLI across the subprocess boundary without exposing hidden test sources.
_Avoid_: Candidate test suite, libtest output

**Rust Toolchain Profile**:
The exact Rust compiler, Cargo, target, and runtime image shared by every Rust task in one dataset release.
_Avoid_: Latest stable, host Rust

**Rust Candidate Funnel**:
The fixed set of frozen upstream candidates evaluated by the same source, license, baseline, offline, specification, and verifier gates before one is promoted.
_Avoid_: Published Rust task

**Serializable Rust API**:
The Rust library surface representable by the common candidate bridge, including bounded values, async operations, and opaque state handles.
_Avoid_: Arbitrary Rust API

**Bounded Unsafe API**:
An unsafe function whose inputs and outputs remain serializable and whose invocation is isolated to a fresh candidate process.
_Avoid_: FFI, raw-pointer bridge, memory-safety proof

**Rust CLI Surface**:
The command behavior observable through arguments, standard streams, exit status, and a task-scoped temporary directory.
_Avoid_: Daemon, interactive terminal, host process control

**Rust Feature Profile**:
The exact default-feature setting and named Cargo features evaluated for one task and bound into its immutable identity.
_Avoid_: All features, ambient features

**Rust Candidate Dependency Set**:
The subset of a frozen Cargo closure that generated candidate code is publicly authorized to reference.
_Avoid_: Shared Cargo cache, arbitrary crates.io dependency

**Rust Pilot**:
The multi-model, multi-attempt evaluation of validated real Rust tasks used to judge difficulty, stability, and failure attribution before enabling the production lane.
_Avoid_: Rust proof, Oracle control
