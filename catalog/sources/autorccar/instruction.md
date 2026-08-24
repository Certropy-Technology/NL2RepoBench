# Build the hardware-independent AutoRCCar model API

Create an installable Python project from an empty `/workspace` for the
documented machine-learning slice of AutoRCCar. This task is intentionally
bounded: it measures the host-side training-data and neural-network model API,
not the complete robot, and does not claim full upstream parity.

## Project layout and support

- Support Python 3.12 on Linux.
- `pip install -e .` must succeed without network access at runtime.
- Keep the import path `computer.model` and provide `computer/__init__.py`.
- Include `environment.yml` describing the project and its NumPy/OpenCV
  runtime libraries.
- The model module must be importable in a headless environment. Importing it
  must not open a camera, serial device, socket, GPIO device, or GUI window.
- The task covers only `computer.model`. Raspberry Pi clients, Arduino code,
  serial control, camera streaming, object detection, calibration, pygame,
  GUI behavior, and `RCTest` are explicitly outside this task's score.

## `computer.model.load_data`

Implement `load_data(input_size, path)`.

- Treat `path` as a glob pattern and read every matching NumPy `.npz` file in
  deterministic sorted path order.
- Each file must contain `train` and `train_labels`. Concatenate rows from all
  files. `train` is a two-dimensional feature array whose second dimension is
  `input_size`; labels are a two-dimensional one-hot array with the same row
  count.
- Convert features and labels to floating-point arrays. Normalize features by
  dividing by `255.0`, so image values are in the `[0, 1]` range for ordinary
  byte-valued inputs.
- Return `(X_train, X_valid, y_train, y_valid)`. Use a deterministic 70/30
  split with no shuffling; the first `floor(0.7 * n)` rows are training rows
  and the remaining rows are validation rows. Reject an empty dataset or a
  dataset too small to produce both non-empty partitions with a clear
  `ValueError`.
- If the glob matches no files, raise `FileNotFoundError` with the pattern in
  the message. Do not fabricate data and do not call process-exit helpers.
- Reject missing arrays, incompatible shapes, non-finite values, or a label
  row count different from the feature row count with a clear `ValueError`.

## `computer.model.NeuralNetwork`

Implement `NeuralNetwork` with `model` initially set to `None` and these
methods, using OpenCV's headless-compatible `cv2.ml.ANN_MLP` implementation:

- `create(layer_sizes)` builds an MLP with the supplied positive integer layer
  sizes, row-sample training, back-propagation, sigmoid-symmetric activation,
  and a finite count-based termination criterion. Store and return no extra
  result. Reject malformed layer sizes clearly.
- `train(X, y)` requires a created model and trains on row-sample floating
  feature and one-hot label arrays. Convert inputs to `float32` and reject
  incompatible or non-finite arrays.
- `evaluate(X, y)` returns the fraction of rows where the largest predicted
  output class equals the largest target class. Return a Python `float` and
  reject empty or incompatible inputs.
- `save_model(path)` requires a created model, creates the requested parent
  directory when needed, and writes the OpenCV model to that exact path.
- `load_model(path)` loads a saved OpenCV model. Raise `FileNotFoundError` for
  a missing path and leave a usable model in `model` on success.
- `predict(X)` requires a loaded or created model and returns a one-dimensional
  NumPy integer array containing one class index per input row.

Use clear exceptions for invalid inputs and missing model files. Identical
inputs and model files must produce deterministic shapes and classifications;
training itself may follow OpenCV's normal optimizer behavior.

## Scope boundary

The upstream AutoRCCar repository also contains hardware and streaming
programs. Those programs are deliberately not requested here because the
legacy task denominator and image fixture do not agree and the fixture refers
 to an absent `RCTest`. Do not infer requirements for those excluded modules,
and do not claim that satisfying this task implements the full upstream
robotics system.
