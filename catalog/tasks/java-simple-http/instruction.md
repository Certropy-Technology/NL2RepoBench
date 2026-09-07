## Project Description

Build a small, zero-runtime-dependency Java library for constructing HTTP requests,
returning response state, and performing the deterministic utility operations needed
by that flow. The intended users are Java applications that want a fluent wrapper
around the JDK HTTP client without adopting a third-party HTTP stack.

The candidate must recreate the public API in the `de.svenkubiak.http` and
`de.svenkubiak.utils` packages. The observable contract includes fluent request
configuration, response value state, a time-based failure gate, form encoding,
ASCII message cleaning, strict HTTP(S) URI parsing, bounded response reads, and
optional TLS-validation configuration. Preserve the public class names, package
names, method names, parameter types, return types, and exception behavior.

In scope:

- `de.svenkubiak.http.Result` as a mutable response/result value object.
- `de.svenkubiak.http.Http` as a fluent request builder with the five factory
  methods, local configuration methods, and `send()` entry point.
- `de.svenkubiak.http.Failsafe` as a synchronized failure counter and temporary
  blocking state.
- `de.svenkubiak.utils.Utils` as the public deterministic and HTTP-support helper
  class.
- Java standard-library HTTP, URI, duration, stream, map, byte-array, and TLS
  types used by those signatures.

Out of scope:

- New public classes, packages, dependencies, plugins, modules, or command-line
  applications beyond the layout described below.
- A network service, server, socket listener, persistence layer, database, or
  filesystem-backed cache.
- Reproducing upstream test sources, verifier code, hidden assertions, or private
  harness protocols.
- Changing the public signatures to use third-party request or response types.
- Treating a malformed URL or an unsupported URI scheme as an allowed request.

The implementation should be usable as a Maven project from an empty
`workspace/`. Public APIs may use JDK facilities internally, but state and results
must remain observable through the signatures below. Request execution is part of
the public class shape, while all grading and examples must remain deterministic
and must not depend on an external service.

## Natural Language Instruction

Create the Maven project described below from an empty `workspace/`. Implement the
four public classes under the exact `de.svenkubiak.http` and `de.svenkubiak.utils`
packages. The implementation must provide the `Result` response state object, the
fluent `Http` request wrapper, the synchronized `Failsafe` gate, and the `Utils`
helpers. Preserve the exact signatures and JDK types in the API guide, including
varargs, generic maps, checked exceptions, and fluent return types.

The project must compile with the stated JDK and Maven versions in offline mode.
Keep the runtime dependency closure empty, keep URI validation restricted to HTTP
and HTTPS, enforce the response-size boundary, and preserve defensive binary
reads. Do not add a CLI, third-party HTTP client, external service, or hidden
protocol. The harness owns grading and test execution; the candidate only needs
to provide the public source tree and Maven metadata shown below.

## Supports

### Runtime and installation

- Platform: Linux amd64 with glibc.
- Java runtime and compiler: Temurin JDK `21.0.12+8`, compiled with release 21.
- Build tool: Maven `3.9.11`.
- Encoding: UTF-8.
- Runtime dependencies: none beyond the JDK module set, including
  `java.net.http`.
- The project root contains `pom.xml` with group `de.svenkubiak`, artifact
  `simple-http`, and a normal Java JAR build.
- The harness supplies the Maven/project setup and compiles the candidate's
  `src/main/java` sources. Do not require an agent-created test suite to discover
  or fetch dependencies.

### Offline and resource boundary

Agent, candidate, verifier, Oracle, and control execution use no network. Do not
access GitHub, Maven Central, DNS, a proxy, or any external service while building
or exercising the candidate. The runtime implementation can contain the JDK HTTP
client API because that is the package's public purpose, but examples and tests
must use local deterministic inputs and must not send a real request.

The candidate `pom.xml` is metadata and build configuration only for this task. It
must not add runtime libraries, repositories, profiles, modules, extensions, or
custom test commands. Use only APIs available in the stated JDK. Do not depend on
environment variables, wall-clock values, locale settings, or global files for
the ordinary value-object and utility behavior.

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/
    ├── main/
    │   └── java/
    │       └── de/
    │           └── svenkubiak/
    │               ├── http/
    │               │   ├── Failsafe.java
    │               │   ├── Http.java
    │               │   └── Result.java
    │               └── utils/
    │                   └── Utils.java
    └── test/
        └── java/
            └── de/svenkubiak/
                ├── http/
                └── utils/
```

The four files under `src/main/java` are the public implementation entry points.
The test tree is optional for the candidate and is shown only to make the Maven
layout unambiguous; do not copy upstream tests into it. There is no CLI entry
point. The Java entry points are imported as follows:

```java
import de.svenkubiak.http.Failsafe;
import de.svenkubiak.http.Http;
import de.svenkubiak.http.Result;
import de.svenkubiak.utils.Utils;
```

## API Usage Guide

### `de.svenkubiak.http.Result`

`Result` is a mutable response state object. Its constructor is private; callers
create independent instances with the static factory.

#### `Result.create`

Signature: `public static Result create()`.

It returns a fresh `Result` whose body is `""`, binary body is `null`, status is
`-1`, and header map is empty. Each invocation must return a distinct mutable
instance and has no filesystem, network, or global-state side effect.

Ordinary example: `Result result = Result.create().withStatus(200).withBody("ok");`.
Edge example: two calls to `Result.create()` must not share later header or body
changes. There are no declared exceptions for this factory.

#### Fluent result setters

The following exact methods mutate the receiver and return that same receiver:

- `public Result withBody(String body)` stores the body, converting `null` and the
  empty string to `""`; any other string is preserved.
- `public Result withBinaryBody(byte[] binaryBody)` stores the supplied byte-array
  reference as the current binary body.
- `public Result withStatus(int status)` stores any integer, including `-1` and
  non-HTTP values.
- `public Result withHeader(String key, String value)` associates `value` with
  `key`, replacing a previous value for the same key.

The setter calls have no declared checked exceptions. `withHeader` accepts the
non-null key/value domain used by this task; null-key and null-value behavior is
not a supported input contract. The setters are local object-state changes and
must not perform I/O.

Ordinary example: `result.withHeader("Content-Type", "text/plain").withStatus(201);`.
Edge example: `Result.create().withBody(null).body()` returns the empty string,
and a later `withHeader("X", "second")` makes `header("X")` return `"second"`.

#### Result accessors and validity

- `public String body()` returns the current body string.
- `public byte[] binaryBody()` returns a defensive copy of the current binary
  bytes, or `null` before binary bytes have been set. Mutating the returned array
  must not mutate a subsequent accessor result.
- `public String header(String key)` returns the value associated with `key`, or
  `null` when no value is associated with it.
- `public String error()` returns the current body string as the error accessor.
- `public int status()` returns the current status, initially `-1`.
- `public boolean isValid()` returns the result of `Utils.isSuccessCode(status())`.
- `public boolean isValid(int... expectedStatus)` returns `true` exactly when the
  current status equals at least one supplied integer; it does not use the 2xx
  success set for this overload.

These accessors do not perform I/O or alter result state. Header lookup follows
the map's key semantics; no case-folding guarantee is added to the contract.
The varargs call with no expected values returns `false`.

Ordinary example: `boolean accepted = result.withStatus(204).isValid();` is true.
Edge example: `Result.create().withStatus(201).isValid(200, 202)` is false, while
`binaryBody()` remains null until bytes are explicitly set.

### `de.svenkubiak.http.Http`

`Http` is a fluent request configuration object. Its public request methods use
JDK types and preserve the same instance for chaining. The actual `send()` method
is an I/O boundary and must remain safe to call without silently allowing an
unsupported scheme.

#### HTTP factory methods

Each method has the following exact signature and returns a new request object:

- `public static Http get(String url)` creates a `GET` request.
- `public static Http post(String url)` creates a `POST` request.
- `public static Http put(String url)` creates a `PUT` request.
- `public static Http patch(String url)` creates a `PATCH` request.
- `public static Http delete(String url)` creates a `DELETE` request.

The URL is required to be non-null. A null URL raises `NullPointerException`.
The factories default to a 10-second timeout, HTTP/2 preference, no redirect
following, strict HTTPS certificate validation, an empty string request body,
and no failsafe. Creating a request performs no network access.

Ordinary example: `Http request = Http.get("https://example.test/items");`.
Edge example: `Http.get(null)` raises `NullPointerException`; an unsupported
scheme is rejected when the request URI is validated rather than being rewritten.

#### Request configuration methods

The following methods return `this` after updating request-local state:

- `public Http withUrl(String url)` replaces the URL and rejects a null URL with
  `NullPointerException`.
- `public Http withHeader(String key, String value)` adds or replaces a request
  header; null key or value raises `NullPointerException`.
- `public Http withProxy(String host, int port)` configures a proxy address;
  null host raises `NullPointerException`.
- `public Http withFailsafe(int threshold, java.time.Duration delay)` attaches a
  failsafe; null delay raises `NullPointerException`, and a non-positive
  threshold raises `IllegalArgumentException` from the failsafe construction.
- `public Http withTimeout(java.time.Duration timeout)` replaces the timeout;
  null raises `NullPointerException`.
- `public Http withVersion(java.net.http.HttpClient.Version version)` replaces
  the HTTP version; null raises `NullPointerException`.
- `public Http withBody(String body)` sets the request body; null is rejected by
  the internal body contract with `NullPointerException`.
- `public Http withForm(java.util.Map<String,String> formData)` encodes the map
  through `Utils.getFormDataAsString` and sets content type to
  `application/x-www-form-urlencoded`.
- `public Http followRedirects()` enables normal redirect following.
- `public Http binaryResponse()` requests a binary response body.
- `public Http disableAllHttpsValidations()` disables HTTPS certificate and
  hostname validation for this request's client configuration. This is unsafe
  outside controlled tests and must not be enabled by default.
- `public Http withMaxResponseSize(long maxBytes)` sets the positive response
  byte limit; zero or negative values raise `IllegalArgumentException`.

Configuration changes are local to the request object, except that `send()` may
use a shared JDK client cache. Form entry ordering is the source map's iteration
ordering. No setter sends a request or writes a file.

Ordinary example: `Http.post("https://example.test/form").withForm(Map.of("a", "1"));`.
Edge example: `Http.get("https://example.test").withMaxResponseSize(0)` raises
`IllegalArgumentException`; do not use the validation-disabling method in normal
production traffic.

#### `Http.send` and shutdown

- `public Result send()` builds and attempts the configured request, returning a
  `Result`. A successful response records status, headers, and either UTF-8 text
  or binary bytes according to `binaryResponse()`.
- `public static void shutdown()` stops and clears cached JDK HTTP clients for the
  current JVM/class loader. It affects other `Http` instances sharing that cache
  and should not be called by a library consumer unless that global effect is
  intended.

`send()` can encounter `IOException`, `InterruptedException`, or
`URISyntaxException` internally and reports those request failures in the result
  body/status according to the result contract; it does not expose a checked
  exception in its signature. An interrupted thread remains interrupted. A
  failsafe-active request is not sent and returns a result with status `-1` and
  the blocked message supplied by `Utils.FAILSAFE_ACTIVE_MESSAGE`.

The response body is read with the configured maximum size. Exceeding that limit
produces an error result rather than an unbounded allocation. URI validation is
strictly limited to HTTP and HTTPS. Ordinary examples should not call `send()`
against the network; use the factories and inspect configuration through a local
harness. `Http.shutdown()` has no return value.

### `de.svenkubiak.http.Failsafe`

`Failsafe` tracks consecutive failures for a request configuration. Its public
state methods are synchronized and use `java.time.LocalDateTime` for the active
window.

- `public Failsafe(int threshold, java.time.Duration delay)` constructs a gate;
  `threshold` must be positive or `IllegalArgumentException` is raised, and a
  null delay raises `NullPointerException`.
- `public static Failsafe of(int threshold, java.time.Duration timeout)` returns
  a new failsafe with those values and the same validation as the constructor.
- `public synchronized boolean isActive()` reports whether the current time is
  before the temporary block deadline. It is time-dependent and normally false
  immediately after construction.
- `public synchronized void error()` increments the count and activates the
  block after the configured threshold is exceeded.
- `public synchronized void success()` resets the count to its initial value and
  clears the active deadline.
- `public synchronized int getCount()` returns the current failure count.
- `public synchronized java.time.LocalDateTime getUntil()` returns the active
  deadline, or `null` when no deadline is set.

Ordinary example: `Failsafe gate = Failsafe.of(3, Duration.ofSeconds(2));`.
Edge example: `new Failsafe(0, Duration.ZERO)` raises `IllegalArgumentException`.
Because active state depends on the clock, deterministic tests should verify
state transitions without asserting an exact wall-clock timestamp.

### `de.svenkubiak.utils.Utils`

`Utils` is a non-instantiable utility class. Import it with
`import de.svenkubiak.utils.Utils;`.

- `public static boolean isSuccessCode(int statusCode)` returns true only for
  200 through 208 and 226, and false for every other integer.
- `public static String getFormDataAsString(java.util.Map<String,String> formData)`
  URL-encodes keys and values as UTF-8, joins entries as `key=value` pairs with
  `&`, and preserves map iteration order. Empty input returns `""`.
- `public static String clean(String string)` removes every character except
  ASCII letters, ASCII digits, and the ASCII space. Null input is outside the
  supported domain.
- `public static java.net.URI toAllowedUri(String url) throws java.net.URISyntaxException`
  parses a URL and accepts only `http` or `https` schemes case-insensitively.
  Null input raises `NullPointerException`; malformed input or another scheme
  raises `URISyntaxException`; a valid URI object is returned unchanged.
- `public static void applyDisableValidation(java.net.http.HttpClient.Builder builder)`
  applies the library's trust-all TLS configuration to a JDK client builder. A
  null builder is outside the supported domain. This method is security-sensitive
  and is intended only for the explicit `Http.disableAllHttpsValidations()` mode.
- `public static Result blockedByFailsafe(Result result)` returns the supplied
  result after setting status `-1` and the failsafe-active message. It mutates and
  returns the same result instance.
- `public static byte[] readLimited(java.io.InputStream inputStream, long maxBytes)
  throws java.io.IOException` reads all bytes until EOF, rejecting a stream whose
  size exceeds `maxBytes`. Exceeding the limit raises `IOException`; successful
  output is a new byte array. The stream is not closed by this helper.

Ordinary examples: `Utils.isSuccessCode(204)` is true and
`Utils.clean("ok! 2")` returns `"ok 2"`. Edge examples: encoding an empty linked
map returns the empty string, and `Utils.toAllowedUri("ftp://example.test")`
raises `URISyntaxException`.

## Implementation Notes

Keep the implementation modular: HTTP request construction belongs in `Http`,
response state belongs in `Result`, failure-window state belongs in `Failsafe`,
and shared transformations belong in `Utils`. Use the exact JDK generic types in
the signatures. Fluent methods must return the receiver, not a copy.

Preserve deterministic behavior wherever the API permits it. The success-code
set is fixed. Form encoding uses UTF-8 and map iteration order. Cleaning is ASCII
allow-list behavior, not locale-sensitive transliteration. Binary response reads
must respect the configured limit, and `Result.binaryBody()` must protect its
returned array from caller mutation.

URI validation must happen before request execution and must fail closed for null,
malformed, or non-HTTP(S) input. The method may accept upper-case HTTP(S) schemes,
but must not broaden the scheme allow-list. HTTPS validation disabling is an
explicit unsafe opt-in and must never be the default.

The shared client cache and `Http.shutdown()` behavior are JVM-scoped; do not
replace them with unrelated process-global files or an external service. Failsafe
state changes are synchronized, count failures consistently, and clear on
success. Do not hard-code current timestamps into results.

Small verifiable examples:

```java
Result result = Result.create().withStatus(200).withBody("ready");
assert result.isValid();
assert result.error().equals("ready");
```

```java
Map<String, String> data = new LinkedHashMap<>();
data.put("first name", "Ada Lovelace");
assert Utils.getFormDataAsString(data).equals("first+name=Ada+Lovelace");
```

```java
assert Utils.clean("A-1_!") .equals("A1");
assert Utils.toAllowedUri("HTTPS://example.test").getScheme().equals("HTTPS");
```

```java
Result blocked = Utils.blockedByFailsafe(Result.create());
assert blocked.status() == -1;
assert blocked.body().equals(Utils.FAILSAFE_ACTIVE_MESSAGE);
```

These examples describe observable behavior without prescribing an algorithm or
copying source code. Keep all tests and demonstrations local, bounded, and
network-free.
