# Authoring Audit

The candidate is pure Python with a small runtime closure. The source tests are
executable and passed in the frozen checkout. The verifier uses a separate
custom-json-v1 subprocess and writes all grading data outside the candidate
workspace. No task-local compose declares `network_mode` or `networks`.

The development-server and browser-debugger portions of upstream Werkzeug are
not part of the deterministic denominator. Their omission is an explicit
bounded adaptation, not a weakened assertion: the fixed suite retains core
data structure, HTTP, URL, security, WSGI, request/response, routing, and
test-client behavior.
