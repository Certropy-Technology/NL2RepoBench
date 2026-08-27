# boto3 authoring audit

- Frozen upstream revision: `722e01b074c67db38ad226ac1a2dab5c36c1577c`.
- License: Apache-2.0, verified from the upstream `LICENSE` and `setup.py`.
- Source archive: SHA-256
  `2b56d8a2d4193499e3c3ed6685622e5c75af11c0cfa1e6173d59f10090be3208`.
- Deterministic unit inventory: 552 collected nodes under `tests/unit`; the
  frozen Oracle run recorded 539 pass and 13 optional CRT skips.
- The private verifier executes the frozen unit suite only in a candidate-owned
  subprocess and emits a bounded custom-json-v1 leaf report. The verifier never
  imports candidate code in the trusted process.
- AWS/network behavior is adapted to fake credentials and Botocore stubs; no
  remote AWS integration tests are included in the denominator.
- Official Harbor 0.21.0 Oracle smoke on the compiled bundle passed 539/552,
  skipped 13 optional CRT nodes, and returned reward/test pass rate
  `0.9764492753623188`. Evidence is under
  `.nl2repo/authoring-work/python-author-next-20260826-r1/boto3/provenance/harbor-results/oracle-final/`.
- Empty, stub, and forgery controls each returned reward `0.0`; every verifier
  network probe reported no public network. These are task-local control
  receipts, not model-agent results.
