# get-stream revalidation blocker

- The canonical catalog digest is `sha256:17fa3bfe51aca11ca201365650403d988f077178d721dda2c4e13f49cd1f89af`, matching the delegated expected digest.
- The immutable source archive digest remains `sha256:85c68c24e1216863eb41e79754b10b50dcdbf94137b2f0b7821f802fd7ec2a06`; all four declared private CAS objects were present and size/hash verified.
- Two production Node/npm compiles were successful and byte-identical: 95 bundle files, raw manifest `sha256:efe4342ee49299ef8d78ac3af9a379c9c45683b5cd4570567d4a312ece43b565`, canonical digest `sha256:0d874a48966ef431f8e0fbaf68f139867e46d6ec59d5d967274300b8c42d5139`.
- The Oracle tar contains `solve.sh`, which performs a runtime `git fetch` from `github.com` for the pinned revision. No Oracle or control run was started because all runtime source-host authorization is forbidden under NoNetwork.
- This is an artifact/verifier blocker for revalidation. Lifecycle, denominator, historical `production-evidence.json`, and generated projection were not changed. Revalidation can resume after the Oracle payload is rebuilt to use an offline local source archive while preserving the pinned revision and archive digest.
