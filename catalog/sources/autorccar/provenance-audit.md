# AutoRCCar provenance and blocker audit

## Provenance

- Upstream repository: `https://github.com/hamuchiwa/AutoRCCar`
- Frozen revision: `c5776aebff517361fb5473c36fd9918ae90a1a0b`
- License: BSD-2-Clause, evidenced by upstream `LICENSE.md` (SHA-256
  `d17410657e9d1316719057548552af9008e6059941f29fada92a0735702959a8`).
- Deterministic source archive: `git archive <revision>`; SHA-256
  `730b441114359e818cd90349868c1a23550c8afc2a8522aaaba71b5d919fb9d9`.
- Pinned verifier image:
  `ghcr.io/multimodal-art-projection/nl2repobench/autorccar@sha256:fe7beae3a27817f6140f0129202cbb127cf687a1dd288a72318647edec12a72e`.
- The registry manifest and config were fetched for inspection; config digest:
  `sha256:22e2c47f03515f5efe1b659d68af5ac158935ae57f7d0ac0af9c80c8742913aa`.
- The image's dependency layer is `sha256:e807afbdc33fd5b07527f71766a1b9df795c185cf1bb71d9291789daf5a3fbf2`.
- The image's test fixture layer is
  `sha256:163014ca2cdf51b195d28166bec418eb301772d42831d03c1913eba80e89e429`.

## Legacy contract

- `test_case_count.txt`: `13` (SHA-256
  `3fdba35f04dc8c462986c992bcf875546257113072a909c162f7e470e581e278`).
- `test_commands.json`: `pip install -e .`; `pytest --continue-on-collection-errors test`
  (SHA-256 `69c951a45d31bb01099b9f222f19e8682b19c94407e0436fe85ece8248ca92b7`).
- `test_files.json`: `test` (SHA-256
  `ecfd160805b1b0481fd0793c745be3b45d2054582de1c4df5d9b8fa4d78e7fbc`).
- Legacy instruction SHA-256:
  `5889b68892c91afe558271bd308f93916aa760bea85e39c8c1087ad96f64ada3`.

## Collection mismatch

The pinned image fixture is not the upstream repository's original `test/`
directory. It contains 8 Python source files, 15 test functions, and 22
parametrized pytest items according to AST inventory. The legacy denominator
is 13. The fixture inventory is recorded below without copying hidden test or
binary bytes into this public catalog.

| image fixture path | bytes | SHA-256 |
| --- | ---: | --- |
| `test/rc_control_test.py` | 850 | `f24ca7bd291269471e1892bcd3624a1311383bc28f2b666fe26f62e7dc0e05c7` |
| `test/rc_control_test_mock.py` | 2052 | `ca68ce6826fad6e0cef8f295de3afd470615cc109c47b8b54da061692514d935` |
| `test/stream_client_test_mock.py` | 2384 | `867c14a8fb409bd3169d7219a69ac42cc82c162883a12fd93eeb92e61ac308cd` |
| `test/stream_server_test.py` | 3254 | `49182b73d498d56227ec927ba0e645ccce422da89fbc1657f1f9906fc596856b` |
| `test/test_rc_driver.py` | 3327 | `2439d43cfb52b24a5b56affbfff4820184162e10b88c992b792be68a94105ebe` |
| `test/ultrasonic_client_test_mock.py` | 1458 | `8e168842fc03662ba20d1a54eb9dc3a3ca36616164ee651cdc05a59b02373fba` |
| `test/ultrasonic_server_test.py` | 2580 | `99a14659c9b4efc464a6258177686fd2cf3faedf7dfd7f0a744743dee5e286de` |
| `test/model_train_test/train_predict_test.py` | 2555 | `53bd01e3df33b85a5374c4de72c0b67a2ff7cf887215d9394a13e70e7b899799` |
| `test/model_train_test/data_test.npz` | 6144800 | `8c1589e96353052f7294160b388bf71fb535aa4a62f99a4b33c5fa3bc5adca01` |
| `test/model_train_test/model_test.xml` | 61345693 | `e739303c083b243c96f5e6953cf109ac24fe9ab14112b0b84bd2b6e958b68b5b` |
| `test/model_train_test/test_image.png` | 105802 | `0146eaadd425ca2188b4e51f9343aabac0362ffd1542b93188363ac1e7c6b800` |
| `test/model_train_test/train_predict_test.ipynb` | 62997 | `8483544466b73e8106dc76729f116cb84adfbaccbcb1aabe0c15c8dcb32e7c63` |

## Additional source/test blockers

Static comparison against the pinned checkout found further reasons not to
claim an Oracle baseline:

- The checkout has no `pyproject.toml`, `setup.py`, or other PEP 517 build
  metadata, although the legacy command requires `pip install -e .`.
- The fixture imports `computer.rc_driver.RCTest`, but that symbol is absent
  from the pinned checkout.
- `computer.rc_driver` constructs a model and serial controller at module
  scope, while the fixture imports it before applying mocks; collection can
  therefore touch `saved_model/nn_model.xml` and `/dev/tty.usbmodem1421`.
- The upstream checkout does not contain the image-generated mock fixture
  files, so the image layer alone is not an auditable upstream test bundle.

## Decision

This task is `blocked`. No Harbor bundle, private test artifact, Oracle
bundle, dependency wheelhouse, or frozen collection record is published from
this conversion. Do not run Docker or Oracle for this task until the test
fixture is reconciled with the legacy denominator, packaging/source behavior
is resolved, and the missing private artifacts are produced and reviewed. The
dataset and all shared indexes remain unchanged.
