# `mdast-util-find-and-replace` Traceability

The frozen upstream file contains one parent test and 24 behavioral subtests.
The private verifier uses 48 flat deterministic `node:test` leaves. Splitting
combined upstream checks gives each leaf one stable grading status while adding
documented boundary cases for callback metadata, UTF-16 indexes, ignore tests,
tree splicing, and package policy. No scored assertion targets a private helper.

| Public contract | Private coverage | Reverse traceability |
| --- | --- | --- |
| ESM package identity, named export, declarations, exact dependencies, no scripts/workspaces | Package inventory leaf | Package inventory maps only to **Supports** |
| Return `undefined`, mutate in place, reject invalid list values | Three invocation/error leaves | Invocation/error leaves map only to the API signature and exception paragraph |
| Literal strings, RegExp flags/global state, captures, match index/input/stack | Fourteen matching and callback leaves | Matching/callback leaves map to **API Usage Guide** match rules |
| Normalize omitted/null/undefined/empty/string/node/node-array/false results | Ten replacement leaves, shared with matching groups | Replacement leaves map to the replacement-result bullets |
| Apply pairs sequentially, skip same-pair recursion, process earlier output with later pairs | Five sequencing/recursion leaves | Sequencing leaves map to pair-order and recursion paragraphs |
| `ignore` supports type, object, array, and predicate tests over ancestors | Five ignore leaves | Ignore leaves map only to the `Options.ignore` paragraph |
| Search text nodes in preorder; do not cross nodes or process non-text values; require a parent for splicing | Five traversal/domain leaves | Traversal leaves map to the traversal input-domain paragraphs |
| Preserve unmatched order and fields; avoid empty split nodes; remove fully deleted text children | Seven splice and preservation leaves | Splice/preservation leaves map to implementation notes and replacement bullets |
| Deterministic pair order, per-node RegExp reset, UTF-16 index, optional captures, tuple/list forms | Eight ordering and edge leaves | Edge leaves map to the explicit deterministic ordering and bounded-input contract |

The coverage counts overlap where one leaf validates both matching and result
normalization, but the frozen denominator is the 48 unique flat test IDs in the
private bundle. Every private leaf is represented by one reverse-traceability
row above, and every public behavioral paragraph has at least one scored leaf.
