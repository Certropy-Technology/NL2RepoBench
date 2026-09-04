# Separate-verifier adapter assessment

The frozen source exposes a broad stateful MySQL/MariaDB implementation. A
faithful child-side adapter would need deterministic fixtures for TCP and Unix
socket transport, protocol packet sequencing, server handshake and capability
negotiation, native-password/caching-SHA2 authentication, TLS, compression,
queries and result sets, prepared statements, local infile transfer, errors,
binlog replication, canal callbacks, SQL dump files, and the external
`mysqldump` executable. The server package adds the reverse protocol direction
and authentication callbacks.

The current Go Harbor profile permits a bounded JSON subprocess bridge, but no
reviewed adapter or protocol fixture for these behaviors is present. A trusted
verifier must not import candidate packages directly or use a live MySQL
service as an uncontrolled dependency. Reducing the task to a few pure parser
helpers would omit the package's principal public contracts and would not
justify a production task denominator. This assessment therefore returns a
verifier blocker; no Oracle, controls, or runtime projection is claimed.
