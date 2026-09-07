# p-map

## Project Description

Build an installable `p-map` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `p-map`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `pMap`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `pMapIterable`: preserve the documented object or module behavior, including state and side effects.
3. `pMapSkip`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `p-map`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `p-map`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- No third-party runtime package is declared by the local task metadata; standard-library support is sufficient unless the API section says otherwise.
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

### `pMap`

Import the default export from the package root:

```js
import pMap, {pMapSkip} from 'p-map';

const values = await pMap([1, 2, 3], async (value, index) => value + index, {
  concurrency: 2,
});
```

```ts
function pMap<Element, NewElement>(
  input: Iterable<Element | Promise<Element>> | AsyncIterable<Element | Promise<Element>>,
  mapper: (element: Element, index: number) => NewElement | Promise<NewElement | typeof pMapSkip>,
  options?: Options
): Promise<Array<Exclude<NewElement, typeof pMapSkip>>>;
```

`input` must be a synchronous or asynchronous iterable. Each input item is
awaited before the mapper receives it. The mapper receives the item and its
zero-based input index. Mapper results are returned in input order, regardless
of completion order. Synchronous mapper returns are accepted; thrown errors and
rejected promises reject the result.

`options.concurrency` defaults to `Infinity` and must be a safe integer at least
1 or positive infinity. With `stopOnError: true` (the default), the first
mapper error rejects the returned promise, while already-started work may still
settle. With `stopOnError: false`, all work is allowed to settle and mapper
errors are reported as an `AggregateError`. The `signal` option accepts an
`AbortSignal`; an already-aborted signal or a later abort rejects with its
reason, normally an `AbortError` DOMException.

Return the exported `pMapSkip` symbol from the mapper to omit that item from the
final array. Multiple skipped values are removed while the remaining values
retain their input order.

### `pMapIterable`

```ts
function pMapIterable<Element, NewElement>(
  input: Iterable<Element | Promise<Element>> | AsyncIterable<Element | Promise<Element>>,
  mapper: (element: Element, index: number) => NewElement | Promise<NewElement | typeof pMapSkip>,
  options?: IterableOptions
): AsyncIterable<Exclude<NewElement, typeof pMapSkip>>;
```

This validates the same iterable, mapper, and `concurrency` rules, then returns
an async iterable. Results are yielded in input order even when later mapper
promises settle first. `backpressure` defaults to `concurrency` and must be a
safe integer at least as large as `concurrency`, or positive infinity. It bounds
the number of produced-but-not-yet-collected results. Mapper and source errors
are raised when the consumer advances the result iterator.

### `pMapSkip`

`pMapSkip` is a named-export unique symbol. Returning it from either mapper
causes the corresponding item not to appear in the array or async iterable.


Keep the package self-contained and deterministic. Do not expose private helper
modules through the export map. Preserve source iteration order and mapper
indices for promise-valued inputs and async iterables. Validation errors should
be `TypeError` and should happen before invoking an invalid mapper. The scored
verifier uses a bounded JSON scenario adapter: callbacks, symbols, custom
objects, and arbitrary executable strings do not cross the trusted boundary,
but the adapter constructs controlled promises, async generators, and errors in
the candidate child process.

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
import pMap, {pMapSkip} from 'p-map';

const values = await pMap([1, 2, 3], async (value, index) => value + index, {
  concurrency: 2,
});
```

### Example 2: ordinary usage
```text
function pMap<Element, NewElement>(
  input: Iterable<Element | Promise<Element>> | AsyncIterable<Element | Promise<Element>>,
  mapper: (element: Element, index: number) => NewElement | Promise<NewElement | typeof pMapSkip>,
  options?: Options
): Promise<Array<Exclude<NewElement, typeof pMapSkip>>>;
```

### Example 3: boundary or error behavior
```text
function pMapIterable<Element, NewElement>(
  input: Iterable<Element | Promise<Element>> | AsyncIterable<Element | Promise<Element>>,
  mapper: (element: Element, index: number) => NewElement | Promise<NewElement | typeof pMapSkip>,
  options?: IterableOptions
): AsyncIterable<Exclude<NewElement, typeof pMapSkip>>;
```

### Example 4: boundary or error behavior
```text
import pMap, {pMapSkip} from 'p-map';

const values = await pMap([1, 2, 3], async (value, index) => value + index, {
  concurrency: 2,
});
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
