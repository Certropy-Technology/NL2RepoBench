# coxeter: deterministic computational geometry

## Project Description

Build an installable Python package named `coxeter` for creating and inspecting
idealized two- and three-dimensional shapes. Its users are researchers and
engineers who need convenient geometry construction, numerical measurements,
serialization, and mesh export rather than a general-purpose CAD editor. The
package boundary is the public API below: analytic circles, ellipses, spheres,
and ellipsoids; planar and convex polygons; polyhedra and convex polyhedra;
rounded convex polygons and polyhedra; shape families; GSD shape conversion;
Conway shape moves; and file exporters.

Create the package and packaging metadata from an empty workspace. It must
import as `coxeter`, expose the documented names, and preserve mutable shape
state: changing a center, vertex array, radius, area, perimeter, volume, or
surface area must be reflected by later reads. Inertia uses constant unit
density. Numeric results are Python scalars or NumPy arrays with the stated
shapes; JSON-facing results contain only JSON-compatible values.

This is not a renderer, mesh repairer, arbitrary-dimensional solver, web
service, or remote resource. Do not add network access, a database, or an
unlisted CLI. Plotting and Plato are optional adapters; ordinary construction,
measurement, containment, conversion, and text export must not require them.
The source revision is `9056679b197f0e835c04dd317cc1049359a0ee7c`, distribution
version `0.10.0`, and these identities must be preserved.

## Supports

### Runtime and installation contract

- Use Python `>=3.9` and `setuptools.build_meta`, with `setuptools` and `wheel`
  as build requirements.
- Declare runtime dependencies `numpy>=1.19.0`, `rowan>=1.2.0`, and
  `scipy>1.0.0`. The harness provides the scientific dependencies offline; an
  equivalent local install is `uv pip install --offline --no-deps -e .`.
- The run environment is `no-network`: agent, candidate, verifier, Oracle, and
  controls must not contact GitHub, PyPI, DNS, numeric IP addresses, or any
  external service. Family JSON is local package data.
- `miniball` is optional for minimal bounding circles/spheres of polygonal and
  polyhedral shapes. `matplotlib` and `plato-draw` are optional plotting
  adapters. Missing optional packages must produce the documented import or
  backend error, not break ordinary imports.
- There is no required CLI. The entry point is the installed `coxeter` import;
  exporters are Python functions writing to caller-supplied paths.

### Project Directory Structure

```text
workspace/
├── pyproject.toml
├── LICENSE
└── coxeter/
    ├── __init__.py
    ├── io.py
    ├── shapemoves.py
    ├── shape_getters.py
    ├── shape_utils.py
    ├── shapes/
    │   ├── __init__.py
    │   ├── base_classes.py
    │   ├── circle.py
    │   ├── ellipse.py
    │   ├── sphere.py
    │   ├── ellipsoid.py
    │   ├── polygon.py
    │   ├── convex_polygon.py
    │   ├── polyhedron.py
    │   ├── convex_polyhedron.py
    │   ├── convex_spheropolygon.py
    │   ├── convex_spheropolyhedron.py
    │   └── utils.py
    ├── families/
    │   ├── __init__.py
    │   ├── common.py
    │   ├── shape_family.py
    │   ├── tabulated_shape_family.py
    │   ├── plane_shape_families.py
    │   ├── doi_data_repositories.py
    │   └── data/
    │       ├── archimedean.json
    │       ├── catalan.json
    │       ├── johnson.json
    │       ├── platonic.json
    │       ├── prism_antiprism.json
    │       ├── pyramid_dipyramid.json
    │       └── science1220869.json
    └── extern/
        ├── bentley_ottmann/
        └── polytri/
```

The two `extern` directories are implementation dependencies and must retain
their license notices. The exact documentation and test checkout is not part
of the runtime contract.

## API Usage Guide

### Package exports and shared shape contract

`import coxeter` exposes `coxeter.families`, `coxeter.shapes`,
`coxeter.shapemoves`, `coxeter.io`, and
`coxeter.from_gsd_type_shapes(params, dimensions=3)`. Root `__all__` is
`["families", "shapes", "from_gsd_type_shapes", "io"]` and
`coxeter.__version__ == "0.10.0"`.

All concrete shapes implement `coxeter.shapes.base_classes.Shape`. The shared
contract is:

- `centroid` and alias `center` are gettable/settable `(3,)` NumPy arrays.
  Setting either translates the shape without changing its dimensions.
  `gsd_shape_spec` returns a JSON-serializable dictionary.
- `is_inside(points)` accepts one point or an `(N,3)` array and returns an
  `(N,)` boolean array; boundary points are inside. `inertia_tensor` is a
  `(3,3)` float array. `distance_to_surface(angles)` returns one distance per
  angular sample where implemented.
- `compute_form_factor_amplitude(q)` is complex-valued where implemented;
  unsupported classes raise `NotImplementedError`. `plot()` is optional.
- `to_json(attributes: list)` returns a dictionary containing every requested
  attribute. An unknown name raises `AttributeError`.
- `to_plato_scene(backend="matplotlib", scene=None, scene_kwargs=None)` returns
  or updates a Plato scene. It raises `ImportError` for an unavailable backend,
  and may raise `NotImplementedError` or `AttributeError` for an unsupported
  primitive.
- `Shape2D` adds `area`, `perimeter`, `planar_moments_inertia` (a three-value
  `(I_x,I_y,I_xy)` result), `polar_moment_inertia`, `iq`, and bounding-circle
  properties. `Shape3D` adds `volume`, `surface_area`, `iq`, and the analogous
  bounding-sphere properties. Unsupported concrete calculations retain
  `NotImplementedError` rather than returning fake values.

Example: `Sphere(1).is_inside([[0,0,0],[2,0,0]])` returns
`array([True, False])`; an empty `(0,3)` input returns an empty boolean array.

### Analytic shapes

#### `coxeter.shapes.Circle`

`Circle(radius, center=(0, 0, 0))` requires a strictly positive radius.
Public state and properties are `radius`, `centroid`, `center`, `area`,
`perimeter`, `circumference` (alias), `eccentricity` (always `0`), `iq`
(always `1`), `planar_moments_inertia`, `polar_moment_inertia`,
`gsd_shape_spec`, and the four bounding-circle properties. Area, perimeter,
circumference, and radius setters uniformly rescale or update the circle and
reject non-positive values with `ValueError`. `is_inside(points)` returns
`(N,)` booleans and requires z approximately zero; `distance_to_surface`
returns an array filled with the radius. `repr` is package-qualified.

Ordinary: `Circle(2).area == 4*pi` and its GSD spec is
`{"type":"Sphere","diameter":4}`. Edge: `Circle(0)` raises `ValueError`.

#### `coxeter.shapes.Ellipse`

`Ellipse(a, b, center=(0, 0, 0))` requires positive semi-axes. Public state is
`a`, `b`, `centroid`, and `center`; measurements are `area`, `perimeter`,
`circumference`, `eccentricity`, `iq`, `planar_moments_inertia`,
`polar_moment_inertia`, `distance_to_surface`, `is_inside`,
`minimal_bounding_circle`, `minimal_centered_bounding_circle`, their radius
properties, and `gsd_shape_spec`. Positive area/perimeter setters uniformly
rescale both axes; invalid axes or measures raise `ValueError`.

Ordinary: `Ellipse(1,2).area == 2*pi`, and its spec has type `Ellipsoid` with
`a=1,b=2`. Edge: `Ellipse(0,1)` raises `ValueError`; equal axes have
eccentricity zero.

#### `coxeter.shapes.Sphere`

`Sphere(radius, center=(0, 0, 0))` requires a positive radius. Public state is
`radius`, `diameter`, `centroid`, and `center`; measurements are `volume`,
`surface_area`, `iq`, `inertia_tensor`, the four bounding-sphere properties,
and `gsd_shape_spec`. Setters for radius, diameter, volume, and surface area
reject non-positive values. `is_inside` returns one boolean per point.
`compute_form_factor_amplitude(q, density=1.0)` accepts one or more 3-vector
wavevectors and returns a complex array of length `N`; zero q returns volume
times density. `to_hoomd()` returns a JSON-safe dictionary with diameter,
origin centroid, volume, and moment inertia, and restores the original center.

Ordinary: `Sphere(1).volume == 4*pi/3`; the zero wavevector form factor is its
volume. Edge: `Sphere(-1)` and assigning `diameter=0` raise `ValueError`.

#### `coxeter.shapes.Ellipsoid`

`Ellipsoid(a, b, c, center=(0, 0, 0))` requires three positive semi-axes.
Public state is `a`, `b`, `c`, `centroid`, and `center`; public operations are
`volume`, `surface_area`, `iq`, `inertia_tensor`, `is_inside`, four bounding-
sphere properties, `gsd_shape_spec`, and `to_hoomd()`. Positive volume and
surface-area setters uniformly rescale all axes. Invalid axes or measures
raise `ValueError`. `is_inside` accepts one or more 3-vectors. `to_hoomd()`
contains `a`, `b`, `c`, origin centroid, volume, and inertia and restores state.

Ordinary: `Ellipsoid(1,2,3).gsd_shape_spec` includes all three axes. Edge:
`Ellipsoid(1,1,1).iq == 1`; a non-positive axis raises `ValueError`.

### Planar polygon shapes

#### `coxeter.shapes.Polygon`

`Polygon(vertices, normal=None, planar_tolerance=1e-5, test_simple=True)`
accepts an `(N,2)` or `(N,3)` numeric array with at least three distinct,
coplanar points; stored vertices are `(N,3)` floats. A supplied nonzero normal
must be orthogonal to the polygon. Public properties/methods are `vertices`,
`normal`, `num_vertices`, `centroid`/`center`, `edges`, `edge_vectors`,
`edge_lengths`, `area`, `signed_area`, `perimeter`,
`planar_moments_inertia`, `polar_moment_inertia`, `inertia_tensor`,
`gsd_shape_spec`, `is_inside`, `distance_to_surface`,
`minimal_bounding_circle`, `circumcircle`, `circumcircle_radius`, `incircle`,
`incircle_radius`, `compute_form_factor_amplitude(q, density=1.0)`, and
`plot(ax=None, center=False, plot_verts=False, label_verts=False)`. Edges are
consecutive vertex pairs. Center assignment translates vertices; positive area
and perimeter assignments rescale them. Duplicate, too-short, non-coplanar,
or self-intersecting input raises `ValueError`; a missing `miniball` raises
`ImportError` for the minimal circle; absent circum/inscribed circles raise
`RuntimeError`.

Ordinary: `Polygon([[-1,0],[0,1],[1,0]]).area == 1`, with `(3,3)` stored
vertices. Edge: duplicate vertices raise `ValueError`; an empty point query
returns an empty boolean array.

#### `coxeter.shapes.ConvexPolygon`

`ConvexPolygon(vertices, normal=None, planar_tolerance=1e-5)` accepts an
unsorted set of full-dimensional convex coplanar points and orders its hull.
All `Polygon` properties apply, with implemented centered bounding circles and
convex `distance_to_surface`. Non-convex, degenerate, wrong-dimensional, or
Qhull-invalid input raises `ValueError` or the underlying SciPy error; do not
silently retain interior points. Its ordering helper
`_reorder_verts(clockwise=False, ref_index=0, increasing_length=True)` is an
internal method, not a required root export.

Ordinary: four square corners in any order produce four vertices and positive
area. Edge: adding a point strictly inside those corners is rejected.

#### `coxeter.shapes.ConvexSpheropolygon`

`ConvexSpheropolygon(vertices, radius, normal=None)` wraps a `ConvexPolygon`
in `polygon` and adds non-negative `radius`. Public members are `polygon`,
`vertices`, `normal`, `num_vertices`, `radius`, `signed_area`, `area`,
`perimeter`, centroid/center through the core polygon, `gsd_shape_spec`,
`is_inside`, `distance_to_surface`, `to_hoomd()`, and `to_plato_scene(...)`.
The core vertices remain visible; area and perimeter include the rounding.
Radius zero is valid, negative radius raises `ValueError`, and polygon errors
are propagated. `to_hoomd()` returns JSON-safe core vertices, sweep radius,
area, and origin centroid.

Ordinary: rounding a triangle by `0.1` increases its area and adds
`rounding_radius` to its GSD spec. Edge: radius `0` is valid; `-0.1` is not.

### Polyhedral shapes

#### `coxeter.shapes.Polyhedron`

`Polyhedron(vertices, faces, faces_are_convex=None)` requires `(N,3)` vertices
and faces made of vertex indices. Public members are `vertices`, `faces`,
`edges`, `edge_vectors`, `edge_lengths`, `num_vertices`, `num_faces`,
`num_edges`, `neighbors`, `normals`, `equations`, `centroid`/`center`,
`volume`, `surface_area`, `inertia_tensor`, `gsd_shape_spec`, `is_inside`,
`get_face_area(faces=None)`, `get_dihedral(a,b)`,
`merge_faces(atol=1e-8, rtol=1e-5)`, `sort_faces()`, minimal bounding sphere,
`circumsphere`, `circumsphere_radius`, `insphere`, `insphere_radius`, and
`plot(ax=None, plot_verts=False, label_verts=False)`. Edges are unique pairs
with smaller index first; neighbors are arrays of adjacent face indices.
`get_face_area` accepts `None`, an integer, or a sequence and returns one area
per selected face. `get_dihedral` rejects non-neighboring faces with
`ValueError`; face merging is destructive and requires convex faces.

Ordinary: a cube with eight corners and six faces has six faces, twelve edges,
and positive volume. Edge: `get_dihedral(0,0)` raises `ValueError`.

#### `coxeter.shapes.ConvexPolyhedron`

`ConvexPolyhedron(vertices)` requires an `(N,3)` set in which every point is a
full-dimensional hull vertex. It derives and orders faces and provides every
applicable `Polyhedron` member plus `simplices`, `face_centroids`,
`mean_curvature`, `tau`, `asphericity`, `diagonalize_inertia()`, centered
bounding spheres, and convex containment. `get_face_area(face=None)` also
accepts `"total"` and returns a scalar or list according to the selection.
Wrong shape, coplanar/insufficient points, interior points, or Qhull failure
raises explicitly. It must not fall back to a non-convex object.

Ordinary: corners at `+/-1` produce eight vertices, six faces, volume `8`, and
surface area `24`. Edge: an `(N,2)` array or interior point is rejected.

#### `coxeter.shapes.ConvexSpheropolyhedron`

`ConvexSpheropolyhedron(vertices, radius)` wraps a `ConvexPolyhedron` as
`polyhedron` and adds non-negative `radius`. Public members are `polyhedron`,
`vertices`, `radius`, `volume`, `surface_area`, `mean_curvature`,
centroid/center through the wrapped object, `gsd_shape_spec`, `is_inside`,
`to_hoomd()`, and `to_plato_scene(...)`. Setting positive aggregate measures
rescales the whole rounded shape. Radius zero is valid; negative radius raises
`ValueError`; core faces and neighbors remain accessible.

Ordinary: rounding a cube by `0.5` increases volume and surface area. Edge:
radius `0` is valid and `-0.1` raises `ValueError`.

### GSD conversion

`coxeter.from_gsd_type_shapes(params, dimensions=3)` requires a dictionary with
`type`. `Sphere` uses `diameter` and returns `Sphere`, or `Circle` when
`dimensions=2`; `Ellipsoid` uses `a,b,c`, or `a,b` in two dimensions;
`Polygon` uses `vertices` and optionally `rounding_radius`; `ConvexPolyhedron`
uses `vertices` and optionally `rounding_radius`; and `Mesh` uses `vertices`
and `indices` to construct `Polyhedron`. Missing type raises `ValueError`; an
unsupported type raises `ValueError`; missing required keys raise the normal
key error. A shape's `gsd_shape_spec` should round-trip through this function.

Ordinary: diameter `2` yields a unit sphere, or a unit circle with
`dimensions=2`. Edge: `{}` and an unknown type both raise `ValueError`.

### Shape families

`coxeter.families.ShapeFamily` is an abstract factory whose concrete classes
provide class-level `get_shape(...)`. `TabulatedGSDShapeFamily(data)` accepts
a mapping of names to GSD dictionaries; `data` and alphabetical `names` are
readable, `get_shape(name)` returns a shape, and iteration yields `(name,
shape)` in name order. Unknown names raise `KeyError`.
`TabulatedGSDShapeFamily._from_json_file(filename, classname=None,
docstring=None)` reads a local JSON mapping and optionally changes the class
name/docstring.

Public analytic family callables are:

- `RegularNGonFamily.get_shape(n)` and `.make_vertices(n)` create an `n`-gon
  of unit area, for `n >= 3`.
- `UniformPrismFamily.get_shape(n)`/`.make_vertices(n)` create a unit-volume
  right prism, and `UniformAntiprismFamily.get_shape(n)`/`.make_vertices(n)` a
  unit-volume right antiprism, each for `n >= 3`.
- `UniformPyramidFamily.get_shape(n)`/`.make_vertices(n)` and
  `UniformDipyramidFamily.get_shape(n)`/`.make_vertices(n)` create unit-volume
  solids for `3 <= n <= 5`.
- `CanonicalTrapezohedronFamily.get_shape(n)`/`.make_vertices(n)` creates a
  unit-volume canonical trapezohedron for `n >= 3`.
- `TetragonalDisphenoidFamily.get_shape(a,b,c)`/`.make_vertices(a,b,c)`
  creates a normalized disphenoid from positive extents.
- `Family323Plus.get_shape(a,c)`, `Family423.get_shape(a,c)`, and
  `Family523.get_shape(a,c)` create convex polyhedra in their bounded domains:
  `[1,3]` for both parameters in 323+; `a in [1,2]`, `c in [2,3]` in 423;
  and `a in [1,s*sqrt(5)]`, `c in [S**2,3]` in 523, where `S` is the golden
  ratio and `s=1/S`. Their `get_planes()`, `get_plane_types()`, and
  `make_vertices(a,b,c)` methods return the local plane/vertex arrays.
- `TruncatedTetrahedronFamily.get_shape(truncation)` accepts `[0,1]`.
- `PlatonicFamily`, `ArchimedeanFamily`, `CatalanFamily`, `JohnsonFamily`,
  `PyramidDipyramidFamily`, and `PrismAntiprismFamily` are tabulated instances
  with `names`, `data`, `get_shape(name)`, and iteration. The last two are
  compatibility exports and issue `DeprecationWarning` on `get_shape`.

`coxeter.families.DOI_SHAPE_REPOSITORIES` lazily maps the supported keys
`10.1126/science.1220869`, `10.1103/PhysRevX.4.011024`, and
`10.1021/nn204012y` to shape-family lists. An unknown key raises `KeyError`.
Known data loads locally from the family JSON files.

Ordinary: `RegularNGonFamily.get_shape(6).num_vertices == 6` and
`list(PlatonicFamily)` yields name/shape pairs. Edge: `RegularNGonFamily` with
`n=2` and an out-of-range `Family423.get_shape(0,2)` raise `ValueError`; an
empty user tabulation iterates to no items.

### Shape moves

`coxeter.shapemoves.vertex_truncate(poly: ConvexPolyhedron, t: float,
degrees=None)`, `dual(poly: ConvexPolyhedron)`, and
`kis(poly: ConvexPolyhedron, k: float, degrees=ArrayLike)` each return a new
`ConvexPolyhedron` and do not mutate the input. Truncation/height fractions
must be in `[0,0.5]`; `degrees=None` applies to all relevant vertices/faces.
Invalid convex geometry and numeric hull/intersection failures are explicit.
Outputs follow the package behavior of preserving the input volume.

Ordinary: `vertex_truncate(cube,0.1)` returns a distinct convex object. Edge:
an invalid negative fraction raises and leaves `cube` unchanged; `dual(cube)`
has no filesystem or network side effect.

### File exporters

`coxeter.io.to_obj(shape, filename)`, `to_off(shape, filename)`,
`to_stl(shape, filename)`, `to_ply(shape, filename)`, `to_x3d(shape, filename)`,
`to_vtk(shape, filename)`, and `to_html(shape, filename)` each accept a
polyhedron/subclass plus a `str`, `pathlib.Path`, or `os.PathLike` and return
`None` after writing the named format. OBJ face indices are one-based;
OFF/PLY/VTK use zero-based indices; STL is ASCII; X3D is UTF-8 XML; VTK is
legacy ASCII POLYDATA; HTML embeds generated X3D. `to_stl` must not mutate its
input. Unwritable paths raise `OSError`; analytic shapes are outside this
exporter contract and must fail explicitly.

Ordinary: `to_obj(cube, tmp_path / "cube.obj")` creates vertex and face records.
Edge: a missing parent directory raises `OSError`.

## Implementation Notes

Keep module names, import paths, signatures, and return shapes stable. Use
NumPy arrays for geometry, return new arrays or shape objects for derived
values, and preserve defined vertex/face ordering. The same input and explicit
arguments must produce the same family geometry and export ordering; do not
use process-global randomness to choose an ordinary result.

Setters must maintain dependent state. Translating a polyhedron must update
vertices and plane equations; scaling must keep lengths, areas, volumes, and
inertia mutually consistent. Exporters may use temporary copies but must never
leave caller-owned shapes modified. Keep optional imports lazy. Preserve the
BSD package license and the notices for both vendored implementations.

Verifiable behavior examples are: a unit sphere has volume `4*pi/3`, surface
area `4*pi`, `iq == 1`, and contains its center but not `(2,0,0)`; a square
`ConvexPolygon` with corners `+/-1` has area `4`, four edges, and centered
bounding radius `sqrt(2)`; a cube with corners `+/-1` has eight vertices, six
faces, twelve unique edges, volume `8`, and surface area `24`; and GSD sphere
conversion with diameter `2` yields a unit sphere in 3D and a unit circle in
2D.

Reject invalid dimensions, negative lengths/radii, duplicate or non-coplanar
geometry, invalid family domains, unknown GSD types, non-neighboring face
pairs, unavailable optional backends, and filesystem failures. Do not catch
broad exceptions to return zeros, empty geometry, or plausible files. No CLI,
network protocol, hidden-test data, verifier report, Oracle result, reward, or
publication status is part of this instruction.
