# Control plan

The source package contains only control scripts; private tests, verifier code,
and the Oracle solution are stored as content-addressed private artifacts.

- `empty`: removes the workspace before installation; observed reward 0.
- `stub`: provides packaging plus functions that raise; observed reward 0.
- `forgery`: attempts to write fake reward files; trusted grading must ignore them.
- `install-hang`: sleeps in `setup.py`; observed reward 0 after install timeout.
- `workspace-invalid`: creates an escaping symlink; observed reward 0 after workspace rejection.
- `call-hang`: sleeps in an API call; observed reward 0 after call timeout.
