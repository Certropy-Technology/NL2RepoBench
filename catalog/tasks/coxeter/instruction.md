# `coxeter` static authoring pilot (blocked)

This directory is a task-local public authoring record for the `coxeter`
computational-geometry library at the immutable revision recorded in
`task.toml`. It is **not** a runnable benchmark task and does not contain the
upstream test suite, hidden assertions, a verifier, an Oracle solution, a
Docker image, or private command artifacts. The audit and blockers are in
[`audit.md`](audit.md).

## Project Description

The eventual repository-generation task would recreate an installable Python
package for mutable two- and three-dimensional geometric shapes. The library
covers analytic shapes (circles, ellipses, spheres, and ellipsoids), planar
polygons, convex polygons, polyhedra, convex polyhedra, and rounded
(spheropolygon/spheropolyhedron) variants. It also provides shape-family
constructors for common solids, geometric transformations, GSD-style shape
conversion, and file exporters for common mesh formats.

## Supports

- Use the package name and import namespace `coxeter` from the revision lock.
- The source metadata declares Python `>=3.9` and runtime dependencies
  `numpy>=1.19.0`, `rowan>=1.2.0`, and `scipy>1.0.0`.
- Preserve the package-root layout and the JSON shape-family data needed by
  `coxeter.families`.
- Ordinary calculations must not require network access. Plotting backends,
  `matplotlib`, `plato-draw`, and the optional `miniball` dependency are
  separate environment decisions, not silently assumed runtime guarantees.

## Provisional API Scope

The public surface to inventory and specify before unblocking includes:

- root exports `families`, `shapes`, `from_gsd_type_shapes`, and `io`;
- the shape classes exported by `coxeter.shapes`, including their mutable
  centers/parameters, area/volume/perimeter/surface-area properties, inertia,
  containment, bounding-shape, form-factor, and serialization behavior;
- the family classes and `DOI_SHAPE_REPOSITORIES` exported by
  `coxeter.families`;
- `vertex_truncate`, `dual`, and `kis` in `coxeter.shapemoves`;
- the `to_obj`, `to_off`, `to_stl`, `to_ply`, `to_x3d`, `to_vtk`, and `to_html`
  exporters in `coxeter.io`; and
- array shapes/dtypes, mutation rules, invalid/degenerate geometry errors,
  ordering, numerical tolerances, and optional-backend failures.

These bullets are a scope outline, not a substitute for the final
behavior-level instruction. Hidden assertions and exact verifier policy must be
added only after the blockers in `audit.md` are resolved.

## Current Status

Keep this pilot blocked. In particular, do not infer a production denominator
from the provisional collect-only count, do not run an Oracle from this
catalog, and do not use a trusted pytest process that imports candidate code
directly. A future task needs a pinned numerical environment, a reviewed
runtime/test dependency closure, an explicit treatment of skipped and xfailed
geometry cases, and a child-side adapter that can marshal NumPy arrays and
maintain mutable shape state across candidate operations.
