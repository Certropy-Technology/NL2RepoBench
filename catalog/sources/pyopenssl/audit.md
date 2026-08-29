# pyOpenSSL Static Authoring Audit

Status at authoring handoff: **controls-passed / awaiting-agent-run**.

The candidate is a hard, native-adaptation task. The frozen source is coherent,
Apache-2.0 licensed, and its core crypto tests pass in the selected CPython and
cryptography environment. The complete upstream suite is intentionally not the
production denominator because it exercises live socket handshakes, DTLS,
callbacks, current-time validity, host certificate stores, and CFFI pointers
that cannot cross the separate-verifier JSON boundary deterministically.

The public contract keeps high-value key, certificate, X.509 name,
cryptography bridge, store verification, TLS context, and memory-connection
behavior. The private verifier uses fresh UID 10001 child processes for every
scenario and writes trusted JUnit/collection/reward files through the generic
custom-json-v1 runner. Controls include empty, stub, forgery, and offline
inputs; receipts are created after production compilation.

The production compile, trusted Oracle, empty, stub, forgery, install-hang,
call-hang, and offline controls completed successfully. No model Agent Run is
performed in this lane. Publication, review, and dataset integration remain the
integrator's responsibility.
