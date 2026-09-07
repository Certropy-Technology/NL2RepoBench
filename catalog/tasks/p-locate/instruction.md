# p-locate

## Project Description

Build an installable `p-locate` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `p-locate`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `pLocate`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `p-locate`: preserve the documented object or module behavior, including state and side effects.
3. `root exports`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `core classes`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `p-locate`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- Declared build/runtime packages are supplied by the frozen evaluation image: `p-limit==7.3.1`, `yocto-queue==1.2.2`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

### `pLocate`

```ts
export type Options = {
  readonly concurrency?: number;
  readonly preserveOrder?: boolean;
};

export default function pLocate<ValueType>(
  input: Iterable<PromiseLike<ValueType> | ValueType>,
  tester: (element: ValueType) => PromiseLike<boolean> | boolean,
  options?: Options,
): Promise<ValueType | undefined>;

export default function pLocate<ValueType>(
  input: AsyncIterable<PromiseLike<ValueType> | ValueType>,
  tester: (element: ValueType) => PromiseLike<boolean> | boolean,
): Promise<ValueType | undefined>;
```

For a synchronous iterable, resolve every input value before passing it as the
sole argument to `tester`. Adopt both synchronous and PromiseLike tester
results. A value matches only when the fulfilled tester result is the boolean
`true`; other truthy values do not match. Fulfill with the matching resolved
input value, or with `undefined` when the iterable ends without a match.

`options.concurrency` bounds the number of pending tester calls. It defaults
to `Number.POSITIVE_INFINITY` and accepts positive integers or positive
infinity. Invalid values, including zero, negative numbers, fractions, and
`NaN`, reject with the `TypeError` produced by the limiter.

`options.preserveOrder` defaults to `true`. In that mode, testers may execute
concurrently, but matching is resolved in input order: a later value that
finishes first does not overtake an earlier matching value. With
`preserveOrder: false`, return the first matching value by tester completion.
The first observed terminal outcome ends the search; a tester or input
rejection observed before a match rejects the returned promise.

When `input` implements `Symbol.asyncIterator`, consume it serially with
`for await`. Await each yielded value and its tester result before requesting
the next value, stop requesting values after a match, and ignore the
synchronous-iterable `concurrency` and `preserveOrder` options. If an object
implements both iterator protocols, use its asynchronous iterator.

Preserve exception constructor names and messages from rejected input values,
tester throws or rejections, and iterator failures. The package has no global
mutable state and does not mutate input values.

Example:

```js
import pLocate from 'p-locate';

const result = await pLocate(
  [Promise.resolve('alpha'), 'beta', 'gamma'],
  async value => value.startsWith('b'),
  {concurrency: 2},
);

// result is 'beta'
```

Completion-order example:

```js
const result = await pLocate(jobs, runCheck, {preserveOrder: false});
```

Here the first job whose `runCheck` promise fulfills to `true` wins, even when
it appears later in `jobs`.


Keep synchronous-iterable scheduling deterministic under bounded concurrency,
and keep asynchronous-iterable consumption serial. Do not coerce tester
results to booleans. Do not swallow input, tester, or iterator failures merely
to continue searching. The generated repository should contain the package
metadata, implementation, declarations, license, and any original tests you
choose to write, but it must not contain the hidden verifier or forged grading
files.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

### Example 2: ordinary usage
```text
export type Options = {
  readonly concurrency?: number;
  readonly preserveOrder?: boolean;
};

export default function pLocate<ValueType>(
  input: Iterable<PromiseLike<ValueType> | ValueType>,
  tester: (element: ValueType) => PromiseLike<boolean> | boolean,
  options?: Options,
): Promise<ValueType | undefined>;

export default function pLocate<ValueType>(
  input: AsyncIterable<PromiseLike<ValueType> | ValueType>,
  tester: (element: ValueType) => PromiseLike<boolean> | boolean,
): Promise<ValueType | undefined>;
```

### Example 3: boundary or error behavior
```text
import pLocate from 'p-locate';

const result = await pLocate(
  [Promise.resolve('alpha'), 'beta', 'gamma'],
  async value => value.startsWith('b'),
  {concurrency: 2},
);

// result is 'beta'
```

### Example 4: boundary or error behavior
```text
const result = await pLocate(jobs, runCheck, {preserveOrder: false});
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
