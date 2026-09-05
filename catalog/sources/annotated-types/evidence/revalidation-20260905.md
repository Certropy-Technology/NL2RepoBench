# annotated-types instruction-migration revalidation

- Current source digest: `sha256:21dc75bcb85e3a2dac6cd1c4d7dfb871b0987d7d612d6b82d9eeb7812cc59a0c`.
- Current instruction digest: `sha256:c6c4d1757f274a02a6a71504951f192054a84af06dbda201958e168f9d386467`.
- Harbor: `0.21.0`; runtime: Python `3.12`; network policy: `no-network`.
- Deterministic compile A/B: both completed successfully, 59 files each, byte-identical; fresh canonical manifest digest is `sha256:6213eef071df8289223ba4278ba9d5c56c4f71c0d6d183fb20147dd8098aa93d`.
- Oracle: valid, collected/passed `60/60`, reward `1.0`, public network unavailable.
- Empty: valid allowed `candidate-installation-failed` exception, collected `0`, reward `0.0`, public network unavailable.
- Stub: first attempt was infrastructure `OSError: [Errno 11]` before collection; bounded retry validly collected `60`, passed `1`, reward `0.016666666666666666`.
- Forgery: validly collected `60`, passed `2`, reward `0.03333333333333333`; candidate workspace fake grading claimed reward `1.0`, while verifier-owned grading remained authoritative.
- Offline: fresh Oracle verifier network probe completed with `public_network_available=false`.

Task-local receipt JSON files in `evidence/receipts/*-revalidation.json` contain the
structured summaries and SHA-256-bound grading/network artifacts. The generated
`catalog/tasks/annotated-types` projection must be regenerated and committed by the
parent before this evidence is used by the production catalog gate.
