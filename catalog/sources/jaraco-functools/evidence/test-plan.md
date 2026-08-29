# Frozen Test Plan

The private `custom-json-v1` verifier freezes 35 unique leaf IDs. Each leaf
starts a candidate-UID child process and compares one JSON result with a
trusted expected value. The denominator is fixed at 35 and collection mismatch
is invalid.

Coverage groups:

- composition and identity: `compose`, `compose-empty`, `identity`, `splat`
- stateful decorators and metadata: `once`, `once-reset`, `method-cache`,
  `method-cache-clear`, `special-cache`, `decorators`, `metadata`,
  `save-method-args`
- invocation and rate limiting: `invoke`, `method-caller`, `first-invoke`,
  `throttler`, `throttler-descriptor`
- retry contracts: `retry-call`, `retry-failure`, `retry-infinite`,
  `retry-defaults`, `retry-decorator`
- value and exception helpers: `print-yielded`, `simple-helpers`,
  `assign-params`, `assign-missing`, `except-replace`, `except-use`,
  `except-untrapped`
- conditional and fluent helpers: `bypass-when`, `bypass-callable`,
  `bypass-unless`, `chainable`, `chainable-error`, `noop`

Native upstream collection at the frozen revision is 40 leaves: 21 doctests
and 19 test methods. The baseline is 38 passed and two documented xfails. The
upstream test file was inventoried but not copied into the public task. Its
timing-sensitive Throttler test is adapted to deterministic infinite-rate and
descriptor scenarios. The private contract also checks API areas not covered
by the short upstream test file.
