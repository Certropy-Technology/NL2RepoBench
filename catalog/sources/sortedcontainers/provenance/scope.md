# Bounded Assertion Scope

The frozen upstream revision has coverage and stress modules for
`SortedList`, `SortedKeyList`, `SortedSet`, and `SortedDict`. The production
contract retains deterministic semantics from those modules and adapts them to
a 30-leaf task-specific subprocess protocol.

The retained behavior families are:

- sorted-list duplicate ordering, sequence access, mutation, bisect, index,
  positional slicing, value ranges, arithmetic operators, and copy behavior;
- sorted-key-list stable equal-key ordering, key bisect/ranges, and exact-value
  membership/removal;
- sorted-set uniqueness, sequence access, mutation, value/key ranges, set
  algebra, and in-place operations;
- sorted-dictionary key ordering, mapping mutation, positional pop/peek,
  value/key ranges, live sequence views, view set operations, and dictionary
  union;
- documented exception contracts for missing values and invalid positions.

The adapter constructs every stateful container and key callable inside a
fresh unprivileged child. The trusted parent imports no candidate module and
accepts only one allowlisted scenario name and one JSON verdict. Each child has
a 12-second wall-clock bound, and no scenario processes more than 100 scalar
values.

Stress repetition, benchmarks, complexity/timing thresholds, private
`_reset`/`_check`/index-tree state, recursive representation, pickle load-factor
details, CPython reference counting, Python 2 compatibility, docs, and test
tooling are excluded. These exclusions define the versioned denominator and
are not hidden requirements.
