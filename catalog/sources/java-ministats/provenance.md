# Java/Maven E2E Provenance

This is a synthetic vertical slice used to verify the Java/Maven authoring and
Harbor runtime path. The Maven lock, verifier harness, and Oracle are private
CAS artifacts. The Agent receives only the public instruction and its runtime
toolchain; verifier assets are mounted in the separate verifier image.
