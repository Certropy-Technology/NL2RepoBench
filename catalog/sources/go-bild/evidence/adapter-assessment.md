# go-bild adapter assessment

## Result

Blocked. No reviewed deterministic child-side adapter exists for the native
Go image values and filesystem/codec behavior exposed by the revision.

## Public surface groups

- `adjust`, `blend`, `blur`, `channel`, `clone`, and `convolution` operate on
  `image.Image` and return native `*image.RGBA` values.
- `effect`, `histogram`, `noise`, `paint`, `segment`, and `transform` expose
  additional image operations, floating point parameters, random noise, and
  image-boundary behavior.
- `imgio.Open` reads filesystem paths and decodes registered formats.
- `imgio.PNGEncoder`, `JPEGEncoder`, `BMPEncoder`, and `WEBPEncoder` write
  format-specific bytes; WebP requires nativewebp and BMP requires x/image.
- `cmd` and the root executable expose Cobra commands that read and write files.

## Required boundary controls

A faithful adapter would need a typed image model with bounded width, height,
stride, color model, and pixel bytes; deterministic request-local random state;
golden codec fixtures; explicit workspace-relative file paths; and separate
child-side execution. Native image objects and callback/function values must
not cross the JSON boundary. The current generic bridge does not supply these
controls, and no task-specific bridge was approved in this lane.

## Environment finding

The full module cannot be tested under the required offline policy without a
private closure for nativewebp, Cobra, x/image, and transitive dependencies.
The pure packages passing from the same command do not remedy the missing
closure for the declared module and CLI.
