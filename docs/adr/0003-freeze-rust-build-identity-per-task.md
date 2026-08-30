# Freeze Rust build identity per task

Every Rust task binds one release-wide `x86_64-unknown-linux-gnu` toolchain profile together with a task-specific Cargo feature profile and candidate dependency set. Generated candidates may use only that frozen closure, preventing ambient Cargo caches, feature drift, or newly selected crates from changing the evaluated repository after publication.
