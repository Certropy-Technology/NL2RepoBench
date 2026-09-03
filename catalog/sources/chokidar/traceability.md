# `chokidar` Traceability

Frozen source revision: `0bc7bed37d6b018e5b11afcce329bbf797d6441f`.

| Leaves | Public contract | Evidence basis |
| --- | --- | --- |
| 1, 14, 18, 29 | npm metadata, ESM root, declaration, default object, named exports | package metadata and declarations |
| 2, 3, 15, 16, 17 | recursive initial scan, `ignoreInitial`, hierarchy, root directory event | README event contract and `FSWatcher` scan behavior |
| 4, 5, 6, 7, 19, 20 | add/change/unlink normalization and polling option | README event contract and fs.watch/fs.watchFile implementation |
| 8, 21 | ignored matcher behavior and excluded paths | README `ignored` option and anymatch behavior |
| 9, 22 | `cwd` relative paths and watched keys | README `cwd` option and `getWatched()` contract |
| 10, 23 | depth-limited recursive traversal | README `depth` option |
| 11, 24 | sorted `getWatched()` directory children | `getWatched()` declaration and implementation |
| 12, 25 | chainable `add`, dynamic watching, `unwatch` | `FSWatcher` public methods |
| 13, 26, 27 | asynchronous close, idempotency, listener cleanup | README close contract and implementation |
| 28 | invalid path type error | public `watch()` path validation |

The private adapter keeps native watcher handles, callback functions, temporary
filesystem mutation, and Stats objects inside the candidate process. It sorts
only initial-scan observations where filesystem enumeration order is not part of
the documented contract; mutation tests wait for the named event and assert the
normalized path. The fixed denominator is the 29 collected `node:test` leaves.
