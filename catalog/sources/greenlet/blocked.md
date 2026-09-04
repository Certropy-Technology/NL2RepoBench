# `greenlet` blocked status

The assigned source is frozen at commit `6aaf3af698aa7789075a904e5bbb70e24df06553`
from `https://github.com/python-greenlet/greenlet`. The archive and both license files
were recorded before runtime. A CPython 3.12 native build succeeds with the available
C/C++ toolchain and produces a platform-specific wheel.

Publication is blocked for two connected reasons:

- `greenlet` is a C++ extension whose core contract switches Python stacks and thread
  state. Its upstream tests include C-API calls, deliberate crash probes, interpreter
  shutdown, cross-thread ownership, leak, frame, tracing, and exception-propagation
  behavior. The current separate verifier contract has no reviewed child-side adapter
  that can represent these operations without importing candidate code in the trusted
  process or changing their semantics.
- The trusted Oracle needs a digest-bound native reference wheel, while the checked-in
  Python Harbor projection must not vendor wheels. The current compiler therefore lacks
  an approved private Oracle payload path for this task.

The task must remain `blocked` until a reviewed bounded JSON scenario adapter, a complete
hash-locked build/test closure, and a private out-of-projection Oracle wheel path exist.
After that work, collect a positive frozen denominator and rerun the final compiled
manifest's Oracle, empty, installable stub, forgery, and offline controls under
`network_mode=no-network`. Do not create `catalog/tasks/greenlet` while blocked.
