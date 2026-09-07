# Commons BCEL Authoring Evidence

The source archive and revision were frozen before this task was authored.
This task uses the bounded public `ByteSequence` API, not the upstream test
suite. The static inventory found 7,106 public symbols in the complete source
tree; the verifier contract intentionally covers eight deterministic leaves
for the selected class.

The parent integrator must register the refs in
`.nl2repo/authoring-work/java-commons-bcel/staging-refs.json` into the
task-scoped private CAS before changing this source from `inventoried` to
`packaged`. No Oracle, controls, or Harbor runtime result is claimed here.
