# Offline Revalidation Policy

The Harbor 0.21.0 control registry in this checkout supports `empty`, `stub`,
`forgery`, `install-hang`, `workspace-invalid`, and `call-hang` for this Python
task. It has no standalone `offline` control kind; attempting
`harbor prepare-control ... offline` fails closed with `unsupported control kind:
offline`, so no hand-written or manually copied control bundle was used.

Every fresh Oracle and supported-control run generated a verifier-owned
`network.json`. The `pypi.org:443` and `1.1.1.1:443` probes were false and
`public_network_available` was false in all seven runs. This is the durable
offline evidence for the current registry contract.
