# Test traceability

| Leaves | Public behavior | Frozen upstream basis |
|---|---|---|
| public-surface, signatures | imports, version and exact call signatures | `tests/test_base_detection.py`, `tests/test_cli.py` |
| empty/ascii/utf8/UTF BOM/isolated/excluded/invalid | detection, ordering and input errors | `tests/test_base_detection.py`, `tests/test_edge_case.py` |
| from-fp/from-path/is-binary | local stream/path and binary handling | `tests/test_isbinary.py`, `tests/test_full_detection.py` |
| legacy-detect and invalid | compatibility result dictionary and type errors | `tests/test_detect_legacy.py` |
| matches and match-properties/output | container, candidate metadata, decoding and re-encoding | `tests/test_base_detection.py`, `tests/test_full_detection.py` |
| iana/declaration/BOM/Unicode helpers | deterministic standard-library utility behavior | `tests/test_utils.py`, `tests/test_mess_detection.py` |
| CLI leaves | version and minimal path operation | `tests/test_cli.py` |

Every hidden leaf is represented by a behavior in `instruction.md`; no hidden leaf requires private names or source-specific helper layout.
