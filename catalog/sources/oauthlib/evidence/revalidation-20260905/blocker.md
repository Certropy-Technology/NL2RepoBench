# OAuthLib instruction revalidation blocker

The queue entry for `oauthlib` expects source content digest
`sha256:849fa31fb29d2cde54e217eef5711ce62eea0a55105d42495f5c31e686bb`.
The source archive authority remains known and is separately recorded as
`sha256:7d459f401eb8595ad42c7a77edfb0ee17b67acf27213812d1c13a1ed505d7c2b`
for revision `40b0ab56da3682c2484a4b78bbff309f8025d950`.

All three declared private CAS objects were found and verified by exact size and
SHA-256. The Oracle object is only a 10,240-byte bundle containing `solve.sh`.
It does not contain the required source archive. Its solve script clones and
fetches GitHub at runtime, which is forbidden by the current NoNetwork contract.
The bounded local recovery search found no exact 1,935,360-byte archive and no
other trusted payload matching the frozen archive digest.

This is an artifact/verifier revalidation blocker, not a source-authority
failure. No runtime Oracle, compile, or control receipt was generated. The
historical production evidence points to deleted run paths and therefore cannot
be reused as current evidence.

Required remediation: recover an exact archive-matching local source payload,
construct a NoNetwork Oracle bundle, register it in the parent-owned CAS, update
the source artifact reference, compile twice, and rerun Oracle plus every
supported control. Keep the existing lifecycle and historical production
evidence unchanged until that complete matrix is durable.
