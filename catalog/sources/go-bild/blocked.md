# go-bild blocked authoring record

Status: **blocked**. This source-local record freezes the upstream revision and
documents the evidence-backed production blocker. It does not create a Harbor
runtime, private dependency bundle, Oracle, controls, or shared CAS object.

## Frozen source

- Upstream: `https://github.com/anthonynsimon/bild`
- Revision: `3bef4b08d12a23a2f8c87ac6b52901ec6492d09b`
- Git archive SHA-256: `f287180ea998e43c2ecd7cff6c26344638d64647fc27a27b6ca4ddfe7b3e628d`
- Git archive size: 4,546,560 bytes
- License: MIT
- LICENSE SHA-256: `0c5184b0a2ce22abc964669a76795398a9f34f234a09975621113f5fc9db05a5`
- LICENSE size: 1,075 bytes

The source tree contains 67 Go files, 26 Go test files, 20 Go packages, and 96
top-level test functions. The source package is a broad image library plus a
CLI, rather than a small stateless API.

## Offline dependency probe

The locked Linux/amd64 probe used Go 1.26.5, `CGO_ENABLED=0`, an empty module
cache, and `GOPROXY=off`. It exited 1 before collection for the root, `cmd`,
and `imgio` packages because the declared modules were unavailable. The pure
image-processing packages did run and pass in the same invocation, but that
does not establish a production dependency closure for the complete module.

Missing closure includes:

- `github.com/HugoSmits86/nativewebp@v1.3.0`
- `github.com/spf13/cobra@v1.10.2` and its transitive CLI modules
- `golang.org/x/image@v0.44.0`

## Adapter and verifier blocker

The public surface spans adjustment, blending, blur, channel extraction,
cloning, convolution, effects, histograms, codecs, noise, flood fill,
segmentation, transforms, and a Cobra CLI. `imgio.Open` reads arbitrary files;
the encoders write PNG, JPEG, BMP, and WebP; the CLI performs filesystem I/O;
noise uses process-global random state; and image values are native Go image
objects rather than JSON values. A separate verifier therefore needs a
reviewed typed image representation, bounded pixel limits, deterministic random
controls, codec fixtures, and filesystem/CLI adapters. No such adapter or
complete private module closure is available in this lane.

The upstream test suite is useful source health evidence but is not a frozen
public behavior denominator. It includes image fixture and codec behavior that
cannot be faithfully transported through the current generic Go JSON bridge.

## Remediation

1. Materialize and hash-lock the complete Go module closure, including nativewebp,
   Cobra, x/image, and transitive modules, in a private artifact.
2. Decide whether the task should be scoped to a documented pure image subset or
   cover the complete library and CLI.
3. If retained, approve a child-side typed image/codec adapter with bounded
   dimensions, deterministic fixtures, explicit filesystem paths, and controlled
   randomness.
4. Add public-behavior tests and freeze their collection before compiling a
   Harbor runtime, Oracle, and controls.

Until those artifacts and decisions exist, the task remains blocked. No
`catalog/tasks/go-bild` projection is permitted.
