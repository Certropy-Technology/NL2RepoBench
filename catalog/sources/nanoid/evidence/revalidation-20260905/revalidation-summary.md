# Nanoid Wave 9 provider-failure retry

- Source digest was validated before mutation: `sha256:737e307703cef3a301a532a95e23919d06e87774ba2ce8704c7ff8ae9aab3290`.
- The exact private CAS payloads were present locally. The Oracle payload is a self-contained `solve.sh` (23,677 bytes; SHA-256 `d644f1540cc8b3323d28441829617fefb40b0863eecbcc3fb70451b391bcb7f6`) and contains no runtime fetch operation. No external service was contacted.
- Two NoNetwork Node/npm compiles completed with identical manifest SHA-256 `cb1f3850addc0165c268e9d9a1502473d899b582101613b2d141eff82eec56ae` and canonical digest `sha256:34e2fd444f0f983df5a4c63fa7935ad2f0a8c5c3fbef799177992d478cc3d2e0`.
- Fresh Harbor 0.21.0 Oracle: `valid=true`, `28/28`, reward `1.0`.
- Fresh controls: empty `0/0` installation exception; stub `1/28`; offline `1/28`; hang `1/28`; forgery, install-script, and loader-hook each ended as the recorded `candidate-installation-failed` result with `0` collected. All network receipts reported `public_network_available=false` and both probes false.
- The forgery/install-script/loader-hook installation failures mean controls are recorded but not claimed as a complete production-controls pass. Existing production evidence was intentionally left unchanged.

Detailed machine-readable results are in `compile-summary.json`, `oracle-grading.json`, `oracle-network.json`, and `control-summary.json`.
