# Oracle provenance

The trusted Oracle bundle initializes a temporary Git repository, fetches only revision `502b2b445b89b753cd468df979b71503f8f99425` from `https://github.com/langchain-ai/langchain`, asserts the resolved commit, and verifies the SHA-256 of `git archive --format=tar <revision> libs/langchain_v1` as `324411670c256bcbdf4dfab75a1b099910b6fc8880a4e9722270288c5a1e4ccd` before copying that package subtree into `/workspace`.

The source-host authorization is required only for the trusted Oracle run. The model Agent and verifier remain offline and receive no source-host authorization.
