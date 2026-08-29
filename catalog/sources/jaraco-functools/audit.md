# Authoring Audit

- Frozen revision: `f7f4f3bcac8f70e01064dee9a8bde6cc8f997a17`.
- The revision is tag `v4.6.0`; its deterministic Git archive is 81,920 bytes
  with SHA-256 `7ef01289b53574ed426a959b34621ae611bf415d17b03bb9b807f5c81e1e53ff`.
- Source archive and license metadata were verified before task authoring.
- The source has a setuptools build backend and a single runtime dependency.
- Native Python 3.12.11 collection is 40 leaves; the frozen upstream baseline
  is 38 passed and two documented xfails.
- The upstream `coherent.licensed` build hook was removed only in the trusted
  Oracle metadata adaptation because it attempts a network fetch during build.
- Candidate and verifier runtime are separate; candidate imports occur only in
  a child process running as UID `10001`.
- The formatter-clean private verifier bundle is 30,720 bytes with SHA-256
  `d403e67383ad65627c91ef658e2043ea6a86d6ba05b3dc4362638e26392056ef`.
- No model Agent Run was started in this authoring lane.
