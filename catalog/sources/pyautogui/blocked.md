# `pyautogui` Blocked Conversion Audit

Status: **blocked**. This directory is an audit record only. It contains no
Harbor task, Oracle solution, verifier Dockerfile, grader, hidden test bytes,
or copied upstream source. No dataset, shared index, conversion-loop state, or
legacy task file is changed by this audit.

## Decision

Do not emit a Harbor 1.4 bundle from the current legacy contract. The source,
image, test bytes, and declared denominator are internally coherent, but the
frozen test suite has seven interactive keyboard tests that call `input()` from
worker threads and explicitly require a focused terminal window. `xvfb-run`
provides an X display only; it does not provide a terminal, interactive stdin,
or a focused terminal application. In a separate Harbor verifier these tests
will either receive EOF immediately or wait for stdin until the verifier
timeout. Supplying scripted stdin or adding a terminal emulator would change
the frozen test contract and would no longer be an image-backed conversion of
the legacy task.

The task can be reopened only after an owner-approved replacement test
contract (for example, a deterministic X11/PTY adapter) is authored and its
denominator is separately frozen. Do not lower the denominator or silently
skip the interactive methods to bypass this blocker.

## Legacy Contract

The four legacy artifacts were read without modification:

| File | Bytes | SHA-256 | Evidence |
| --- | ---: | --- | --- |
| `test_files/pyautogui/start.md` | 41,870 | `f10b25e0752d7be902fa372453b9c04dbfdabb273e9e1e5837d6489a50aac173` | Public specification |
| `test_files/pyautogui/test_case_count.txt` | 2 | `59e19706d51d39f66711c2653cd7eb1291c94d9b55eb14bda74ce4dc636d015a` | Declares `28` |
| `test_files/pyautogui/test_commands.json` | 77 | `a66262100dcc498c176a8efc3370f0266166213b7c9a88f2a82d61662e4e7552` | `pip install .`; `xvfb-run -a pytest --continue-on-collection-errors tests` |
| `test_files/pyautogui/test_files.json` | 9 | `af7f0b2bd3428222f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The legacy command and count are syntactically coherent. The count file has
no trailing newline and contains exactly `28`.

## Pinned Verifier Image

The conversion-loop state recorded this immutable image reference:

```text
ghcr.io/multimodal-art-projection/nl2repobench/pyautogui@sha256:806aaeb2ed7a61abbdff6d1a9b6ba2dedd146bb6b345842b8c8d61ae75732259
```

Static registry inspection of that digest reported:

- manifest media type: Docker distribution manifest v2;
- platform: `linux/amd64`;
- config digest: `sha256:233107036c1435b208f1a01890f535c4c55ff6618d8f81e9fc55687d76e02f58`;
- runtime: CPython `3.9.23`, Debian trixie base, user `appuser`;
- working directory: `/workspace`;
- final command: `tail -f /dev/null`;
- image creation time: `2025-09-03T08:15:15.4692647Z`;
- GUI packages installed in image history: `libxtst6`, `scrot`, `xvfb`,
  `xauth`, and `python3-tk`.

Relevant image history/layers are:

| Purpose | Compressed layer digest | Size |
| --- | --- | ---: |
| Install X11/Xvfb runtime packages | `sha256:8b9a42611fdf46024457c7bfe6df05b808c0a6bf208fdcb33a6b981aa8df74a1` | 106,177,173 |
| Copy frozen `tests/` and PNG fixtures | `sha256:a13c086eaf2ae524dcbf0760bc6ccea76b23a879e19feebb56a1b9963f534c5f` | 22,339 |
| Copy frozen `setup.py` | `sha256:56d001a9ab90d0d57440129788d6266a29b96881773e6b1c00f23be34ca91ffe` | 1,091 |
| Remove preinstalled PyAutoGUI package | `sha256:79a417dfee11c3f689f607b7a57c0cf2eda2227fa29a557b6ef1ac9a7c4a5c5d` | 319 |

The final image contains the test fixture and `setup.py`, not a candidate
source tree. The image history records the test/setup copy and then
`pip uninstall -y pyautogui`; the verifier must therefore import the
candidate from `/workspace` while retaining the image-provided dependencies.

## Upstream Source And License

The frozen test and setup bytes identify the following exact upstream revision
in `https://github.com/asweigart/pyautogui`:

- full commit: `5fee761f90e69f47dd3af6439f3a1a6b4ac806d8`;
- subject: `Updates.`;
- parent: `b6b2c4c4f94471bcef0785e236dda0046ff190b0`;
- tree: `02cfbcdd6b998a3fef631a86ad825cf0095539ee`;
- author/committer date: `2023-05-24T22:11:12+02:00`;
- deterministic archive command:
  `git archive --format=tar 5fee761f90e69f47dd3af6439f3a1a6b4ac806d8`;
- unprefixed archive size: 532,480 bytes;
- archive SHA-256:
  `e0ec59dff155bf12f40f44b2d4acf3fc6dcb6173976f9b1f5f818c5ffed9dd8a`.

License evidence is the revision's `LICENSE.txt`:

- SPDX: `BSD-3-Clause`;
- Git blob: `105aea99a1778ddd3eb45212fc2064ac44c6e758`;
- bytes: 1,482;
- SHA-256: `48f16390e9d5559e2aaacfe3a009666af686187bea7175a4503201da942331ac`.

GitHub's repository/license metadata also identifies the project as BSD 3
Clause. The source lock and license are therefore acceptable; provenance is
not the blocker.

## Frozen Tests And Denominator

The image's final test layer contains these files (plus a generated
`__pycache__` entry):

| Path | Bytes | Image SHA-256 | Upstream blob at `5fee761f...` |
| --- | ---: | --- | --- |
| `tests/100x100blueimage.png` | 204 | `2384d44b4843be550fdba8edc4e6cfe3cfcbdd294c5f0297ef2ef082ae1bf4af` | `8944ea51e1467ed46008430fd61ef313960bc060` |
| `tests/100x100redimage.png` | 205 | `df11cafb69d99094e6be163461b19fca77c759c4455f012f869e809e33ee4297` | `37cc2efaf39bb30a6ac94b503f3ec26eb0445997` |
| `tests/25x25blueimage.png` | 93 | `d9b9741daa942e7dafcd8d11491dfab427d58b54bcb3c0df15a9cf1b15522cba` | `482fb078d2bd976b0cb2d3f9a9b3543dc4f1902c` |
| `tests/test_pyautogui.py` | 35,143 | `f2a0e5efe127bbeaa66177289dd21df025fa0fd659de643c3657bf97336d1fb8` | `9e94dbec9f626e5199bdf8375c6f413a5377b30e` |
| `setup.py` | 2,588 | `fcc3f91638cf892450b6f70acf7d3743395da4405f8b90cb8955043b41439a89` | `b3d2f9caf9da2bfa1855218c3ec67cd020c04e48` |

The image test, setup, and three fixture files are byte-identical to the
corresponding upstream revision. No behavioral test overlay was found. The
generated `__pycache__/test_pyautogui.cpython-311-pytest-8.4.0.pyc` is a build
artifact, not a test source overlay. Hidden test bytes therefore could have
remained in the pinned image; none are copied into this repository.

Static AST inventory of `/workspace/tests/test_pyautogui.py` finds 28 ordinary
`test_*` methods, with no parametrization, skip, or xfail marker. The methods
are:

```text
TestGeneral: 5
TestHelperFunctions: 1
TestDoctests: 1
TestMouse: 6
TestRun: 5
TestKeyboard: 8
TestFailSafe: 1
TestPyScreezeFunctions: 1
```

Thus the image-derived raw collection and the legacy denominator both resolve
to 28, subject to a real collection run that is intentionally not performed
in this lane.

## GUI/Xvfb Blocker

The seven methods below call `input()` while a worker thread generates
keyboard events through PyAutoGUI:

```text
TestKeyboard.test_typewrite
TestKeyboard.test_typewrite_slow
TestKeyboard.test_typewrite_editable
TestKeyboard.test_press
TestKeyboard.test_hold
TestKeyboard.test_press_during_hold
TestKeyboard.test_typewrite_space
```

The test module also documents both constraints directly: the terminal window
must be in focus, and the test cannot run as a scheduled task or remotely.
`xvfb-run -a` creates a virtual X server for X11 mouse/keyboard and screenshot
calls, but it does not create a terminal emulator, connect `input()` to an X11
window, or guarantee a focused terminal. A Harbor verifier's `runuser`/shell
process has no guaranteed interactive TTY. The resulting behavior is either:

1. closed/non-interactive stdin causes `EOFError` in the main test thread; or
2. an open pipe waits for input that the Xvfb event stream cannot provide,
   leading to a verifier timeout.

Other static environment sensitivities reinforce the blocker: the suite moves
the real X pointer through all fail-safe corners, depends on Xvfb screen
geometry, and asserts narrow elapsed-time windows (`1.0 < elapsed < 1.1` for
the pause test and `1.0 < elapsed < 2.0` for slow typing). These are not
appropriate to reinterpret as deterministic headless tests without changing
the verifier contract.

## Static Validation

No Docker, Harbor, Xvfb, pytest, Oracle, or candidate behavior was run. The
audit used only static and registry/source operations:

- SHA-256 and byte-size checks for all four legacy artifacts;
- conversion-loop state inspection for the immutable image reference;
- registry manifest/config/layer inspection for the pinned digest;
- extraction of only the image's test/setup layers under `/tmp`;
- GitHub repository/license metadata lookup;
- full-SHA Git fetch, tree/blob comparison, and `git archive` hashing;
- Python AST inventory and source inspection of the frozen test module;
- clean worktree/diff inspection.

The correct terminal recommendation is **blocked**, with no Harbor 1.4 assets
created.
