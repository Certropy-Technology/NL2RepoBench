# Project Description

Build the pinned ESM npm package `emittery` from an empty `workspace/`. It is an
asynchronous event emitter with direct and any-event listeners, one-shot
subscriptions, serial/parallel emission, and buffered async iterators.

# Natural Language Instruction

Create the package root and implement the `Emittery` default export plus every
static and instance member documented below. Preserve listener order, event
payload shape, iterator buffering, lifecycle cleanup, and deterministic errors.

# Supports or Environment Configuration

- Use Node.js 24.19.0 and npm 11.17.0 with the exact ESM package metadata in
  `task.toml`; install the closed npm lockfile offline.
- Do not use lifecycle downloads, workspaces, native addons, or runtime
  services. Agent, candidate, verifier, Oracle, and controls use no network.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

# API Usage Guide

The API Usage Guide below is authoritative for the constructor, static exports,
subscription/emission methods, iterator contracts, and listener lifecycle.

# Implementation Notes

Preserve registration order and remove listeners exactly once. Async iteration
must be bounded and deterministic without timers or external services.

# Examples

```js
import Emittery from 'emittery';
const emitter = new Emittery();
const stop = emitter.on('ready', value => value);
await emitter.emit('ready', {ok: true});
stop();
```

```js
const events = emitter.events('message');
await emitter.emit('message', 'hello');
```

# Error Handling and Boundary Conditions

```js
await emitter.emitSerial('empty', undefined);
```

```js
emitter.off('missing', () => {}); // retain documented no-op behavior
```

# Build `emittery`

## Project Description

Create an installable npm package named `emittery`, version `2.0.0`, from an
empty workspace. It must provide a small, fully asynchronous event emitter for
string, number, and symbol event names. Listeners can be subscribed directly or
through an any-event channel; events can also be consumed through buffered async
iterators. The implementation must preserve listener ordering, event-data shape,
subscription cleanup, lifecycle hooks, reserved meta events, and deterministic
error behavior.

The package is evaluated as a complete repository, not as a patch to a supplied
implementation. Do not copy upstream source or tests into the generated
repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- Use ESM with `"type": "module"`.
- `package.json` must expose the root default entry `./index.js` and declaration
  entry `./index.d.ts`, with no runtime dependencies and no `scripts` entries.
- The package must pass clean installation with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not require browser globals, native addons, custom loaders, workspaces,
  network access, random state, or wall-clock timing for event behavior.

## API Usage Guide

### `Emittery`

Import the default export from `emittery`:

```ts
new Emittery<EventData = Record<PropertyKey, unknown>>(options?: Options): Emittery
```

The optional `options.debug` object accepts `name?: string`, `enabled?: boolean`,
and `logger?: (type, debugName?, eventName?, eventData?) => void`. The instance
has a mutable `debug` property. `Emittery.isDebugEnabled` is a static boolean;
the default logger is enabled when it or the instance setting is enabled.

The documented instance methods form the complete public method surface. Each
method is available as a non-enumerable bound own property, so detached method
calls keep their instance receiver. Do not expose additional prototype methods.
When a custom debug logger is enabled, subscription, emission, removal, and
clearing call it with operation types `subscribe`, `emit`, `unsubscribe`, and
`clear`, respectively, followed by the configured debug name, event name, and
event data when that operation has data.

### Event names and event objects

Event names are strings, numbers, or symbols. Other values throw `TypeError`.
An emitted event object always has `name`; it has an own `data` property only
when `emit` or `emitSerial` was called with a second argument, including an
explicit `undefined`. Each listener receives its own event object.

### Subscriptions

```ts
on(eventName: EventName | readonly EventName[], listener: Listener, options?: {signal?: AbortSignal}): UnsubscribeFunction
off(eventName: EventName | readonly EventName[], listener: Listener): void
onAny(listener: Listener, options?: {signal?: AbortSignal}): UnsubscribeFunction
offAny(listener: Listener): void
```

`on` subscribes one listener to one or more event names and deduplicates the
same listener for the same name. It returns an idempotent callable unsubscribe
function that also implements `Disposable`. `off` and `offAny` remove matching
subscriptions and are safe when no matching subscription exists. An abort signal
removes the subscription; an already-aborted signal does not leave it installed.

`onAny` receives ordinary events from every name, but not the reserved meta
events. Listener invocation is asynchronous. `emit` snapshots listeners at
invocation time, starts the snapshot concurrently, awaits all of them, and if
any reject or throw, rejects with `AggregateError` whose `errors` contains every
reason while still allowing every listener to run.

### Emission

```ts
emit(eventName: EventName, eventData?: unknown): Promise<void>
emitSerial(eventName: EventName, eventData?: unknown): Promise<void>
```

Both methods validate the event name. `emitSerial` invokes the snapshot in
registration order and stops at the first thrown or rejected listener error,
propagating that error directly. User code cannot emit `Emittery.listenerAdded`
or `Emittery.listenerRemoved`; doing so throws `TypeError`.

### One-shot and iterator APIs

```ts
once(eventNames: EventName | readonly EventName[], predicateOrOptions?): EmitteryOncePromise<Event>
events(eventNames: EventName | readonly EventName[], options?: {signal?: AbortSignal}): AsyncIterableIterator<Event> & AsyncDisposable
anyEvent(options?: {signal?: AbortSignal}): AsyncIterableIterator<Event> & AsyncDisposable
```

`once` resolves with the first matching event, optionally using a predicate or
an options object containing `predicate` and/or `signal`. Its promise has an
idempotent `off()` method. A signal rejection uses its reason and removes every
subscription. `events` buffers matching event objects in emission order;
`anyEvent` buffers all ordinary events. Calling `return(value)` stops buffering,
awaits `value`, and returns `{done: true, value}`; aborting also finishes the
iterator. Both iterators implement `Symbol.asyncDispose`.

### Listener management and lifecycle

```ts
clearListeners(eventNames?: EventName | readonly EventName[]): void
listenerCount(eventNames?: EventName | readonly EventName[]): number
init(eventName: EventName, initFn: () => (() => void) | void): UnsubscribeFunction
bindMethods(target: object, methodNames?: readonly string[]): void
```

`clearListeners` clears only the named events when names are supplied and all
listeners/iterators otherwise. `listenerCount` counts matching direct, any, and
iterator subscriptions according to the requested scope. `init` runs when the
first direct listener for an event is added and its returned cleanup runs when
the last is removed or cleared. Registering the same hook twice, using a meta
event, or passing a non-function throws.

`bindMethods` installs selected, or all, Emittery methods as non-enumerable
bound properties on an object; it validates the target, names, and conflicts.
`Emittery.mixin(propertyName, methodNames?)` returns a class decorator that
lazily creates an Emittery instance on each object and forwards the selected
methods. It validates class targets, names, and conflicts.

`Emittery.listenerAdded` and `Emittery.listenerRemoved` are public symbol
constants. They report subscription changes through the normal event object and
are not user-emittable.

## Implementation Notes

Keep the package root importable without a build step and keep declarations
consistent with runtime exports. Async iterators must clean up when returned or
aborted, and lifecycle cleanup must not leak listeners. Preserve ordinary JSON-
serializable event values in examples and deterministic behavior in tests.
