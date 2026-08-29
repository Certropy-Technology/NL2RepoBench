# Build `gitpython`

Create an installable Python distribution named `GitPython` whose import package is `git`.
Start from an empty workspace. The implementation must work with Python 3.12 and the
preinstalled `gitdb==4.0.12` and `smmap==5.0.2` dependencies, without downloading anything
during the agent or verifier run.

## Project Description

GitPython is a Python interface to local Git repositories. The scored contract is a bounded,
deterministic local repository API: create repositories, stage and commit files, inspect Git
objects and history, manage local branches and tags, read configuration, compute local status
and diffs, and expose the documented exception and actor utilities. Operations that contact a
remote service are outside this task.

## Supports

- Install with `pip install .` from the workspace and import `git`.
- Expose the package metadata constants, `Repo`, `Git`, `Actor`, the core object/reference
  classes, and exception classes from their normal `git` modules.
- Use the local `git` executable for repository operations. The executable is available in the
  evaluation image; do not replace GitPython with a fake in-memory implementation.
- Keep repository creation, commit ordering, object lookup, branch/tag order, config values,
  status, and diff output deterministic for fixed files and explicit configuration.
- Keep candidate code and its dependency installation local. Do not clone, download, or
  install packages at evaluation time.

## API Usage Guide

### `git.Repo`

Import path: `from git import Repo`.

Signatures used by this task include `Repo(path, odbt="git", search_parent_directories=False,
expand_vars=True)`, `Repo.init(path, mkdir=True, odbt="git", bare=False, initial_branch=None)`,
`Repo.clone_from(url, to_path, progress=None, **kwargs)`, `repo.index.add(paths)`,
`repo.index.commit(message, **kwargs)`, `repo.commit(rev="HEAD")`, `repo.tree(rev="HEAD")`,
`repo.iter_commits(rev="HEAD", paths=None, **kwargs)`, `repo.create_head(path, commit=None,
force=False)`, `repo.create_tag(path, ref="HEAD", message=None, force=False, **kwargs)`,
`repo.merge_base(*rev, **kwargs)`, and `repo.is_ancestor(ancestor_rev, rev)`.

`Repo.init` returns a repository rooted at the requested path; `bare=True` creates a bare
repository. `Repo.clone_from` is only exercised with a local filesystem path. `index.add`
stages existing files, and `index.commit` creates a commit using the repository's explicit
`user.name` and `user.email` configuration. `commit()` accepts common revision expressions such
as `HEAD`, `HEAD~1`, and `HEAD^{commit}` and returns a `Commit`; `tree()` returns a `Tree`.

The repository exposes `working_tree_dir`, `git_dir`, `bare`, `head`, `heads`, `branches`,
`tags`, `remotes`, `active_branch`, `is_dirty()`, `index`, and `git`. `repo.git` dynamically
dispatches local Git commands and returns decoded text for ordinary commands. File paths,
branch names, and revision strings must be passed as arguments rather than interpolated into a
shell command.

### Git objects and references

`Commit` exposes `hexsha`, `message`, `author`, `committer`, `parents`, `tree`, `stats`, and
`diff()`. `Tree` is iterable and supports path lookup such as `repo.tree("HEAD") / "src" /
"module.py"`; `Blob` exposes `hexsha`, `path`, `size`, `type`, and `data_stream.read()`.
`Head` and `TagReference` expose their names and resolved commits. Fixed local operations must
preserve Git's object IDs and history order.

### Configuration, actors, and errors

Use `with repo.config_writer() as writer:` followed by `writer.set_value(section, option,
value)`, then `repo.config_reader().get(section, option)`. In this frozen revision,
`Actor._from_string("Name <email@example.com>")` returns an actor with `name` and `email`
fields; direct `Actor(name, email)` construction is also supported.

Provide `git.exc.GitError`, `InvalidGitRepositoryError`, `NoSuchPathError`, `GitCommandError`,
`GitCommandNotFound`, and `UnsafeOptionError` with their normal inheritance and operation
behavior. Invalid repository paths must fail instead of silently creating unrelated state.

## Implementation Notes

Use the package's normal setuptools layout and include package data needed by `git`. The runtime
depends on `gitdb` and `smmap`; keep those imports working in a candidate-owned site directory.
The public contract intentionally excludes remote fetch/push, SSH credentials, network
authentication, submodules, daemon/server behavior, platform-specific shell quirks, and
performance-only tests. Do not add a network fallback or contact the frozen reference source.
Avoid hard-coded object IDs: IDs must be produced by the local Git executable from the exact
files, author identity, timestamps, and commit messages supplied by each caller.
