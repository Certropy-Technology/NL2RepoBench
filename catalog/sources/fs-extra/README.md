# `fs-extra` Source Contract

This directory is the declarative authoring source for the `fs-extra` Harbor
task. It freezes `fs-extra@11.4.0`, documents the supported CommonJS and ESM
filesystem helper surface, and binds a private offline npm closure, separate
UID-isolated verifier, trusted Oracle, and verifier controls.

Generated runtime files belong under `catalog/tasks/fs-extra/` and must be
created by the Node compiler; they are not edited here.
