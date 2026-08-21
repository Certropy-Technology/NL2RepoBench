# Build `AutoRCCar`

Create a complete, installable Python project from an empty `/workspace`.
AutoRCCar connects a Raspberry Pi camera and ultrasonic sensor to a computer
that performs image processing and steering decisions, then sends commands to
an Arduino-controlled remote-control car.

The project must be usable without physical hardware in unit tests: serial,
network, camera, OpenCV display, and model objects must be replaceable with
mocks. Keep hardware and network work behind the documented classes and avoid
opening devices merely by importing helper modules.

## Supports

- Python 3.11 or newer.
- An installable project that succeeds with `pip install -e .`.
- Runtime dependencies used by the implementation, including NumPy,
  OpenCV, scikit-learn, matplotlib, Jupyter, Cython, pygame, and pyserial.
- The import paths below must work from the repository root after installation.
- Keep the existing repository layout: `computer/` contains the host-side
  modules, `raspberryPi/` contains camera and sensor clients, and `arduino/`
  contains controller sketches and documentation.
- Include `environment.yml` describing the Python environment and the runtime
  libraries needed by the host and client programs.

## Host model API: `computer.model`

Implement `load_data(input_size, path)`. Treat `path` as a glob pattern for
NumPy `.npz` files. Each input file supplies `train` feature rows and
`train_labels` one-hot labels. Concatenate all matching files, normalize image
features to the `[0, 1]` range, and return a deterministic 70/30 training and
validation split as `(X_train, X_test, y_train, y_test)`. When no file matches,
terminate with a clear failure instead of returning fabricated data.

Implement `NeuralNetwork` with these methods:

- `create(layer_sizes)` creates an OpenCV multilayer perceptron with the given
  layer sizes, back-propagation training, sigmoid activation, and a finite
  training termination criterion.
- `train(X, y)` trains on row-sample floating-point feature and one-hot label
  arrays.
- `evaluate(X, y)` returns the fraction of rows whose largest predicted output
  class equals the largest target class.
- `save_model(path)` writes the trained model to the requested path and creates
  its parent directory when needed.
- `load_model(path)` loads a previously saved model and reports a missing path
  as an error.
- `predict(X)` returns the predicted class index for every input row.

## Hardware helper API: `computer.rc_driver_helper`

### `RCControl`

`RCControl(serial_port)` opens the supplied serial device at 115200 baud with a
one-second timeout and exposes the opened object as `serial_port`.

`steer(prediction)` sends one encoded command byte through that object. The
integer mapping is:

- `2`: forward, byte value `1`;
- `0`: left, byte value `7`;
- `1`: right, byte value `6`;
- every other value: stop, byte value `0`.

`stop()` always sends byte value `0`. Steering methods may log the selected
command, but command bytes and call order must be exact.

### `DistanceToCamera`

Constructing `DistanceToCamera` loads the fixed camera calibration constants
used by this project. `calculate(v, h, x_shift, image)` returns the estimated
positive distance in centimeters from the target's image coordinate `v` and
physical height `h`. For a positive distance, annotate `image` with the value
using the supplied horizontal offset; return the numeric distance even when no
annotation is drawn.

### `ObjectDetection`

Constructing `ObjectDetection` initializes `red_light`, `green_light`, and
`yellow_light` to `False`.

`detect(cascade_classifier, gray_image, image)` invokes the classifier's
multi-scale detector with scale factor `1.1`, five neighbors, and minimum size
`(30, 30)`. Draw a box for each detection on `image`, classify square detections
as stop signs, and inspect non-square detections for traffic-light state. Set
the corresponding light flag when a lit red, green, or yellow state is found.
Return the bottom image coordinate (the detection's y coordinate plus height,
using the project's five-pixel inset) for the last detection, or `0` when there
is no detection.

## Host streaming API: `computer.rc_driver`

Export `SensorDataHandler`, `VideoStreamHandler`, `Server`, and `RCTest`.
Importing the module must leave hardware and sockets unopened; constructors or
runtime methods perform those actions.

`SensorDataHandler` receives byte messages from a socket request, converts each
numeric message to a one-decimal-centimeter floating-point reading, and makes
the current reading available to the driving handler.

`VideoStreamHandler` consumes a byte stream containing JPEG frames delimited by
JPEG start and end markers. For each complete frame it must:

1. decode grayscale and color images with OpenCV;
2. use the lower half of the grayscale image as the neural-network region of
   interest;
3. run stop-sign and traffic-light detection and distance estimation;
4. reshape the region of interest into a floating-point model input and obtain
   a prediction from `NeuralNetwork`;
5. stop for an obstacle, a close stop sign, or a red light, otherwise forward
   the prediction to `RCControl.steer`;
6. display the color frame and poll the display for `q`; on `q`, stop the car
   and leave the loop.

Clean up the OpenCV windows in all exit paths and terminate the request cleanly
once the stream ends or the quit key is received. The handler must work with
mocked model, detector, controller, OpenCV, and request objects.

`Server(host, port1, port2)` stores the host and two TCP ports. `start()` runs
the sensor listener and video listener, using a background thread for the
sensor listener and serving video frames on the main thread. The standard
script entry point may use the project's documented default host and ports.

`RCTest` is a lightweight keyboard-control harness exposing `steer` and `stop`
for environments that want to exercise controller commands without starting
the network server.

## Raspberry Pi and controller programs

Provide camera and ultrasonic client programs under `raspberryPi/`. The camera
client sends JPEG frames over TCP and closes the stream cleanly. The ultrasonic
client measures distance in centimeters, sends readings periodically, and
cleans up GPIO and sockets on exit. Provide Arduino sketches and README files
that document the command bytes used by `RCControl`.

## Quality and boundaries

Use clear exceptions for missing model/data files, malformed sensor data,
failed image decoding, and unavailable hardware. Do not require a live camera,
serial device, GPIO board, GUI display, or remote server during import or unit
tests. Keep public behavior deterministic for identical inputs, and preserve
text and byte handling for the JPEG and serial protocols.
