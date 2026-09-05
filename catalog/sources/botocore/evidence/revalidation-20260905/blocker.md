# Botocore instruction revalidation blocker

Status: revalidation blocked; the declared lifecycle and historical
`production-evidence.json` are unchanged.

## Frozen source check

- Expected catalog source digest: `sha256:1200fb4abc886c5fd4b3cd0132438ec9fb2e3942152f25d49acdd972944ed4fd`
- Source revision: `577f39f278bec5635ffdc7efd6d99f17687419e2`
- Frozen upstream archive digest: `sha256:13720b9e9a36c235c45535e1364ec7e5faddd47789b87cd27865b1ec9eafa9a3`
- `uv run nl2repo task validate-source catalog/sources/botocore`: exit `0`

## Artifact checks

The declared dependency lock and verifier bundle are present in the private
artifact store and match their declared size and SHA-256:

- Dependency lock: `sha256:3a91a7b8c6f6e932308c2d440feed9234f360588a02dc20f643366cb4b0c1cfd`, 2,003 bytes.
- Verifier bundle: `sha256:aabd6f2e85f20726f994330511d8cfa919bfcb2b12f5ddf635ef941cfc23e2f9`, 10,240 bytes.
- Oracle bundle: `sha256:08b8fb942831b48c3054eebee9a6198ef1a7447285620853b26d0c7c7b12d4b1`, 10,240 bytes.

The Oracle bundle contains only `solve.sh`. Its source-acquisition step runs
`git fetch` from `https://github.com/boto/botocore` before checking out the
frozen revision. This violates the required no-network Oracle/runtime policy.
The task-local source does not contain a proven hash-equivalent Oracle source
archive, so the bundle was not modified or executed.

## Revalidation disposition

No compile, Oracle, empty, stub, forgery, or offline run was started. Existing
production receipts were not reused because the instruction migration changed
the source digest. A follow-up may proceed only after a local Oracle payload is
provided and proven against the frozen source revision and archive digest; it
must then compile twice and run the full control matrix under no-network.
