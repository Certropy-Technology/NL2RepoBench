# `wrap-ansi` source contract

This directory is the declarative authoring source for the `wrap-ansi` Harbor
task. It freezes `wrap-ansi@10.0.1` and binds the public behavior contract to an
exact private npm cache, a 44-leaf separate verifier, a digest-checked Oracle,
and adversarial controls.

The Node compiler generates runtime files under `catalog/tasks/wrap-ansi/`.
Do not edit generated runtime files by hand.
