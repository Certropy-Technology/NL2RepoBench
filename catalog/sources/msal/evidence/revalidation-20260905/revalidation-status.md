# MSAL instruction revalidation status

- Expected current catalog source digest: `sha256:90777e23b4182524ea27d38b2a7ef59d77fda7f13d5f0469619f63926edf647a`.
- Frozen upstream revision: `1416438a14118949d05be634124ab5d1c94c1f99`.
- Frozen upstream archive digest: `sha256:8061a883f29af255e7b3ba4da8c8f2b61a16e767e2ab40557443ad24a295b71a`.
- `uv run nl2repo task validate-source catalog/sources/msal`: exit `0`.
- All three declared private artifacts were verified offline by exact size and SHA-256.
- Both production compiles completed with `--allow-private`, Harbor `0.21.0`, and the parent CAS. The output trees were byte-identical. The fresh bundle-manifest file SHA-256 was `sha256:0e8e2225143f0445fecb334241830571356c316ad6f0b87ed66708453dc1a269`; canonical manifest digest is recorded inside that manifest.
- The Oracle bundle contains only `solve.sh`; it performs a runtime `git fetch` from `github.com` before producing `/workspace`. No source archive is bundled.
- Bounded local recovery found no exact source archive matching the frozen digest in the existing generated task, local CAS, retained authoring archives, historical task evidence, or package caches.
- Oracle, empty, stub, forgery, timeout, invalid-workspace, and offline Harbor runs were **not** started because the only Oracle materializer violates the required NoNetwork contract. No receipt or reward is claimed.
- `task.toml`, lifecycle, generated projection, and historical `production-evidence.json` were left unchanged. The historical evidence contains old non-durable run paths and is not reused.

## Remediation

Restore trusted bytes for the frozen MSAL source archive, verify the revision and digest, and construct a replacement private Oracle bundle whose solve script materializes that archive without runtime network access. Parent integration must register the replacement in CAS, update the source reference, compile twice, inspect for path leaks, and run the complete Oracle/empty/stub/forgery/offline matrix before replacing production evidence.
