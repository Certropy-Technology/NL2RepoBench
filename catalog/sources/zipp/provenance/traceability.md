# Public Contract Traceability

| Public instruction area | Frozen authority | Private verifier coverage |
| --- | --- | --- |
| Distribution metadata, no runtime dependencies, and root exports | `pyproject.toml`, `zipp/__init__.py` | metadata, requirements, exports, and compatibility-import leaves |
| Construction, root state, iteration, and implied directories | `Path`, `CompleteDirs`, `test_iterdir_and_types`, `test_subdir_is_dir` | construction, iteration order/types, and implied-directory leaves |
| Text/binary reads, writes, and error contracts | `Path.open`, `read_text`, `read_bytes`, upstream open/read tests | read, encoding, write, directory, missing, and binary-argument leaves |
| Composition, parents, path-like inputs, mutation, and subclassing | `joinpath`, `parent`, `_next`, upstream traversal tests | join/division, path-like, parent/at, mutation, repeat-read, and subclass leaves |
| Filename, string, repr, suffix, stem, and unnamed roots | `_base`, `filename`, `__str__`, `__repr__`, upstream metadata tests | string/repr, filename/root-parent, suffix/stem, and unnamed-root leaves |
| Match, glob, recursive glob, directory and character-set behavior | `zipp.glob.Translator`, `Path.glob`, upstream glob tests | basic, recursive, directory, character-set, invalid-pattern, and match leaves |
| Equality, hashing, symlink mode, relative paths, pickle, and Traversable | corresponding `Path` methods and upstream tests | equality/hash, symlink, relative, pickle, and interface leaves |
| Complete directory lookup and materialization | `CompleteDirs.namelist`, `resolve_dir`, `getinfo`, `inject` | synthetic getinfo and injection leaves |
| Malformed/special ZIP names and compatibility overlay | upstream malformed/name tests, `zipp.compat.overlay` | malformed path, special/backslash name, and overlay leaves |

Every verifier leaf belongs to one row above and every row is described in
`instruction.md`. A root-owned entrypoint sends one trusted scenario to a
UID-10001 child through `nl2repobench.verification.candidate_client`; only that
child imports `zipp`. The child creates bounded in-memory or temporary ZIP
fixtures and returns JSON-safe leaf outcomes. Candidate code cannot write the
trusted collection, JUnit, grading, network, or reward files.
