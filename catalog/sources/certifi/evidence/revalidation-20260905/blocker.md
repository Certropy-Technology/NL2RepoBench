# Instruction Revalidation Blocker

The migrated catalog source validates at:

```text
sha256:356f41fcbeb5caaa07a8d8e91759da7eee96f822e309b30e060952c3199d787e
```

The declared dependency, verifier, and Oracle artifacts are present and
hash-valid. Two locked production compiles were byte-identical, with canonical
manifest digest
`sha256:c6984e3e1932301292f4ac4c5d4242d74ca78d15bd4a2ca9bb043a519a4dcefe`
and bundle-manifest file SHA-256
`sha256:de98518ccc61a7b821a50d070390eb2fc0820592e38a81e780afa981be0d8f7f`.

The private Oracle solver performs a runtime GitHub fetch, while the required
frozen source archive is absent from the local CAS:

```text
sha256:b3217053a0e844b3449c4f59b5c9c3537c90343203f2b05a92e96ab4a5d23095
```

No Oracle or control run was started because Agent, candidate, verifier,
Oracle, and controls must remain NoNetwork. This is an artifact/verifier
revalidation blocker, not evidence that the task is unsupported. Lifecycle and
historical production evidence remain unchanged.

The next step is to restore and hash-verify the exact local source archive,
rebuild the private Oracle payload without runtime fetches, compile the final
manifest twice, and run the complete Oracle/empty/stub/forgery/offline matrix.
