# Instruction Revalidation Blocker

The migrated catalog source validates at:

```text
sha256:63bd822f89beae1c759a1c8b67ca2da3a66ad52ff4f506111a58b710e837bdb2
```

The frozen upstream revision is
`e239bdc5cc1eb1f0db08d4046ad531f805dbea71`, with upstream source archive
digest `sha256:4846e586d01120fcea41d4a60b8d287d28e59b3060f46476f6844b83b3eb86cf`.

Parent-side NoNetwork CAS inspection confirmed that all three private artifacts
declared by `task.toml` are absent:

```text
dependency lock: sha256:5d0ca04e334f7260a4cae5b961c5661a26b8e55c42002e58e661426135618c5c
Oracle bundle:   sha256:74f4b338b55edbe51e0885d5a23fdcaf97ce1bff8cb59d88e0e33d18a823a3c3
verifier bundle: sha256:fe872ebb92147ea21c6c471ba49619365b2967296e24bbdb13fa53fb1d7ac84d
```

Compile and Harbor execution were not attempted because they cannot resolve
their immutable inputs. No network authorization was granted and no historical
receipt was reused. This is an artifact/infrastructure revalidation blocker,
not evidence that the task is unsupported; lifecycle and production evidence
remain unchanged.

The next step is to restore the exact artifacts from an authorized frozen
backup, verify size and SHA-256, compile twice with the locked Python toolchain,
inspect the Oracle payload for runtime network access, and run the complete
NoNetwork Oracle/empty/stub/forgery/offline matrix.
