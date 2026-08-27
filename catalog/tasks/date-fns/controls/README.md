# Control Matrix

The production verifier owns the fixed denominator and writes its own grading
files. The bounded controls are executed against the compiled bundle and are
kept separate from the private scored leaves:

- `empty.sh`: an empty workspace must receive a valid model zero.
- `stub.sh`: callable placeholders must not pass the behavior leaves.
- `forgery.sh`: candidate-written reward files must not influence grading.
- `offline.sh`: installation and verification must work with network disabled.
- `timeout.sh`: a candidate that does not terminate must be bounded.
