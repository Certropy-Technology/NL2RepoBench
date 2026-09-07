# Project Name: excon

## Project Description

Excon is a simple, fast, and reasonably complete HTTP client library for Ruby.
Agents build reusable code for it; tests almost never need to be written again.
This task asks you to recreate the pure-Ruby request/response core of the excon
library (version 1.7.1): a module-level stubbed transport, connection objects
that merge defaults with per-request options, a response object exposing status,
headers and body, a middleware stack that runs in declaration order, and the
error hierarchy used when a stub or an expectation is not satisfied.

The goal is to make the library usable exactly as the public API guide below
describes. Every behavior that the fixed verifier contract exercises is
documented here, including defaults, ordering, casing, and error contracts.

The library must run with no network access at all. The graded surface is the
mock/stub transport: when `Excon.defaults[:mock]` is `true`, requests never open
a socket; they are matched against registered stubs and answered from them.
Real-socket transport, TLS handshakes, and HTTP parsing from a live server are
outside the graded contract and may be implemented as minimal or inert
placeholders, as long as requiring the library and using the documented subset
works.

## Natural Language Instruction (Prompt)

Implement the `excon` Ruby library under `lib/` so that `require "excon"` loads
the whole public surface described in the API Usage Guide. Follow these
guidelines for the overall logic:

1. Implement module-level configuration and the stub registry in `lib/excon.rb`:
   `Excon.defaults`, `Excon.stub`, `Excon.stubs`, `Excon.unstub`,
   `Excon.stub_for`, and the verb shortcuts such as `Excon.get`. The registry is
   emptied with `Excon.stubs.clear`; there is no module-level `Excon.clear` or
   `Excon.reset`.
   Stubs are stored as `[request_params, response]` pairs and new stubs are
   added to the front of the list, so the most recently defined matching stub
   wins.
2. Implement request-parameter matching in the stub lookup. A stub request hash
   matches a live request when every key present in the stub equals (or, for a
   `Regexp` stub value, matches with `=~`) the corresponding request value. The
   `:method` key is compared symbol-wise, so a live `:get` symbol matches the
   stub `:get`. A `String` request value never matches a `Regexp` stub value by
   equality; it matches only through the regexp match. On a match the request
   params receive a `:captures` entry whose `:headers` sub-hash comes first and
   which then holds one entry per matched non-header key, each being the array
   of `Regexp` capture groups in group order.
3. Implement `Excon::Connection`, created through `Excon.new(url, params)`.
   `Excon.new` parses the URL into `scheme`, `host`, `hostname`, `port`, `path`
   and `query` params, keeps the caller's extra params, raises `ArgumentError`
   for a URL without a scheme, and returns a connection whose `data` hash is the
   merge of `Excon.defaults` with those params. `Excon.defaults[:mock]` defaults
   to `false` and `Excon.defaults[:retry_limit]` defaults to `4`.
4. Implement request dispatch in `Excon::Connection#request` and the verb
   wrappers (`#get`, `#post`, and siblings). The request params merge onto the
   connection data, with per-request `:headers` merged over the connection
   headers rather than replacing them, so both connection-level and
   request-level header keys are visible to the middleware stack. The request
   `:method` is a symbol and the request `:path` keeps the leading slash; when
   the connection was built from a URL that already has a path, a later request
   `:path` replaces it. The verb methods must also work when the connection URL
   carries the path.
5. Implement the middleware stack. Each middleware is constructed with the next
   object in the stack, holds it as `@stack`, and exposes
   `#request_call(datum)`, `#response_call(datum)` and `#error_call(datum)`.
   The first entry of the list is the outermost object, so both `request_call`
   and `response_call` enter at the first entry and delegate inward to
   `@stack`, reaching the connection last. Each default implementation just
   forwards to `@stack`, and the mock middleware short-circuits the socket
   layer by pre-filling `datum[:response]` before delegating. The default stack is, in order,
   `Excon::Middleware::ResponseParser`, `Decompress`, `Expects`, `Idempotent`,
   `Instrumentor`, `Mock`. The mock middleware is last, so it short-circuits the
   socket layer while the earlier middleware still get to post-process the
   stubbed response.
6. Implement `Excon::Middleware::Mock` so that in mock mode it looks up a stub
   for the request. A matching stub whose response is a `Hash` is duplicated; a
   matching stub whose response is a `Proc` is called with the request params.
   The resulting response hash is merged onto the base response
   `{ body: "", headers: {}, status: 200, remote_ip: "127.0.0.1" }`, meaning an
   unspecified `:status`, `:body`, or `:headers` keeps that base value. When no
   stub matches, raise `Excon::Errors::StubNotFound` unless the request or
   default `:allow_unstubbed_requests` is truthy.
7. Implement `Excon::Middleware::Expects`. When the request carries
   `:expects`, compare it against the response status; `:expects` may be a
   single status or an array of statuses. On mismatch raise the mapped status
   error, whose message's first line is exactly
   `Expected(<expects>) <=> Actual(<status> <reason>)` where `<expects>` is the
   `inspect` of the expectation value and `<reason>` is the status reason. The
   raised error must expose `#request` (the request params without the response)
   and `#response` (an `Excon::Response` for the actual status/body/headers).
8. Implement `Excon::Response`, `Excon::Headers`, and the error hierarchy.
   `Excon::Response#status`, `#body`, `#headers`, `#remote_ip` and `#data`
   return the stubbed values, `#[]` indexes into the same data hash, and
   `#data[:headers]` is the response header collection. `Excon::Headers` is a
   `Hash` subclass that keeps every key under the spelling it was assigned while
   maintaining a downcased index: `[]`, `[]=`, `key?`, `has_key?`, `member?`,
   `values_at` and `fetch` accept any casing and read the most recently assigned
   value for that name, whereas `include?` and `keys` stay literal. A
   differently-cased assignment therefore adds a second stored spelling instead
   of replacing the first. `Excon::Error` inherits from `StandardError`;
   `Excon::Errors::StubNotFound`, `Excon::Errors::InvalidStub` and
   `Excon::Errors::NotFound` are the very same classes as their
   `Excon::Error::StubNotFound`, `Excon::Error::InvalidStub` and
   `Excon::Error::NotFound` names, while the legacy `Excon::Errors::ClientError`,
   `Excon::Errors::ServerError` and `Excon::Errors::HTTPStatusError` names alias
   `Excon::Error::Client`, `Excon::Error::Server` and `Excon::Error::HTTPStatus`
   (which have no `...Error` spelling under `Excon::Error`).
9. Implement `Excon::Errors.status_error(request_params, response)` returning
   the mapped error instance rather than raising: a status in the published
   status table maps to its own class (`404` to `Excon::Errors::NotFound`, a
   `ClientError` subclass; `500` to `Excon::Errors::InternalServerError`, a
   `ServerError` subclass), and any status absent from that table maps to
   `Excon::Errors::HTTPStatusError`.
10. Build the `StubNotFound` message so its first line is exactly
    `no stubs matched`, followed by the pretty-printed request datum on later
    lines; the contract pins only that first line, and no extra public helper is
    required to produce it.
11. Do not copy upstream source, upstream tests, private verifier files, or any
    reference solution into the repository. Do not add native extensions. Do
    not perform network access, DNS resolution, or subprocess spawning while
    requiring the library or serving the documented subset. Do not use the
    `test/` or `spec/` harness of the original project as the graded surface.

## Environment Configuration

- Language: Ruby, MRI `3.4.10` (parsed by `gem` as `ruby 3.4.10 (build ...)`),
  Linux `amd64`.
- Package manager: Bundler `2.6.9`, with `BUNDLE_GEMFILE` pointing at the
  project `Gemfile` and an offline cache installed by
  `bundle install --local`.
- The base image is the pinned `docker.io/library/ruby` MRI image recorded in the
  task metadata; the image digest is environment-side and is not part of this
  contract.
- Runtime dependencies: none beyond the Ruby standard library. The published gem
  declares an unpinned `logger` runtime dependency, used only by
  `Excon::Instrumentors::LoggingInstrumentor`; the graded subset must not
  require it, and the verifier installs with a `Gemfile.lock` that resolves only
  the library itself.
- Required standard library modules available in the image: `uri`, `json`,
  `stringio`, `pp`, `digest`, `openssl`, `socket`, `resolv`, `timeout`,
  `ipaddr`, `forwardable`, `cgi/escape`, `zlib`, `rbconfig`.
- Network policy: `no-network`. Both the agent container and the verifier
  container run detached from any network; any attempt to reach the public
  internet must fail closed rather than fall back to a real HTTP request.
- Time, locale, random seed, current directory, and environment variables other
  than those listed above must not change any documented return value. The
  contract runs in a single process, in the documented order, and calls
  `Excon.stubs.clear` between operations.

## Excon Project Architecture

The recreate-the-repository contract is a pure Ruby contract: no native
extension, no database, no server, no external service, and no filesystem state
outside the process. The module is loaded once and every documented value is
derived from the request params plus the registered stubs, so identical inputs
give byte-identical JSON output.

### Project Directory Structure

Recommended layout (any equivalent internal layout is accepted, as long as
`require "excon"` and the documented public constants work):

```text
workspace/
├── Gemfile
├── Gemfile.lock
├── excon.gemspec
└── lib/
    ├── excon.rb                    # Excon.defaults, stub registry, verb shortcuts, Excon.new
    └── excon/
        ├── constants.rb            # DEFAULTS, HTTP_VERBS, status reason map
        ├── errors.rb               # Excon::Error / Excon::Errors hierarchy
        ├── headers.rb              # Excon::Headers case-insensitive hash
        ├── response.rb             # Excon::Response
        ├── connection.rb           # Excon::Connection + middleware stack wiring
        ├── middleware.rb           # Excon::Middleware namespace
        ├── middlewares/
        │   ├── base.rb             # request_call/response_call/error_call forwarding
        │   ├── response_parser.rb
        │   ├── decompress.rb
        │   ├── expects.rb          # :expects comparison + status error
        │   ├── idempotent.rb
        │   ├── instrumentor.rb
        │   └── mock.rb             # stub matching, base response merge
        ├── test/server.rb          # optional, may be inert
        └── utils.rb
```

Public entry points and the file that must define them:

```text
Excon.defaults            lib/excon.rb
Excon.stub                lib/excon.rb
Excon.stubs               lib/excon.rb
Excon.unstub              lib/excon.rb
Excon.stub_for            lib/excon.rb
Excon.get/post/...        lib/excon.rb
Excon.new                 lib/excon.rb
Excon::Connection         lib/excon/connection.rb
Excon::Response           lib/excon/response.rb
Excon::Headers            lib/excon/headers.rb
Excon::Error / Errors     lib/excon/errors.rb
Excon::Middleware::*      lib/excon/middleware*.rb
```

Determinism rules that the contract depends on:

- One Ruby process handles all operations in order; nothing is cached between
  operations except `Excon.defaults`, which the harness resets by clearing
  stubs only.
- The `:status` reported for a stubbed response is an `Integer`; `:body` is a
  `String`; `:headers` values are `String`s indexed by their original spelling.
- Errors are reported by class name, and the first line of the message is
  pinned exactly; later message lines are not part of the contract.
- No output depends on wall-clock time, locale, `RUBY_OPT`, or terminal width.
  The pretty-printed remainder of a `StubNotFound` message must never be
  compared.

## API Usage Guide

### Core API Imports

```ruby
require "excon"

Excon                       # module with defaults, stub registry, verb shortcuts
Excon::Connection           # connection object returned by Excon.new
Excon::Response             # response object returned by #request and verbs
Excon::Headers              # case-insensitive Hash subclass
Excon::Error                # base error class (Excon::Errors is an alias module)
Excon::Middleware::Base     # superclass for middleware
```

### 1. `Excon.defaults`

```ruby
Excon.defaults[:mock]         # => false
Excon.defaults[:retry_limit]  # => 4
Excon.defaults[:stubs]        # => :global
```

`Excon.defaults` returns the mutable hash of connection defaults.
`:mock` selects the stubbed transport, `:retry_limit` is the idempotent retry
budget, and `:stubs` selects the `:global` (process-wide) versus `:local`
(per-thread) stub registry. The values shown are the shipped defaults.

```ruby
Excon.defaults[:mock] = true
```

Setting `:mock` to `true` makes every subsequent request that is not matched by
a stub raise `Excon::Errors::StubNotFound` instead of opening a socket. The
graded contract always enables mock mode first.

### 2. `Excon.stub(request_params = {}, response_params = nil, &block)`

```ruby
Excon.stub({ method: :get }, { status: 201, body: "created" })
# => [[{:method=>:get}, {:status=>201, :body=>"created"}]]

Excon.stub({ path: %r{^/items/(\d+)$} }) do |params|
  { status: 200, body: params[:captures][:path].first }
end
```

**Parameters:**

- `request_params` (Hash): keys to match against the request, for example
  `:method`, `:path`, `:query`, `:host`, `:headers`. Omitted keys match
  anything. A `Regexp` value matches by `=~`; any other value matches by `==`.
- `response_params` (Hash or nil): the canned response. Exactly one of
  `response_params` or a block is required.

**Return Value:** `Excon.stub` returns the `Excon.stubs` array with the new
`[request_params, response]` pair prepended.

**Errors:** raises `ArgumentError` when both `response_params` and a block are
given, or when neither is given.

**Deterministic behavior:** the newest matching stub wins, because stubs are
prepended. `Excon.stubs` returns the live array; `Excon.stubs.clear` removes all
stubs and is the only reset the contract performs between operations.

### 3. `Excon.unstub(request_params = {})`

```ruby
Excon.stub({ path: "/a" }, { status: 200 })
Excon.unstub({ method: :get, path: "/a" })
# => [{:path=>"/a"}, {:status=>200}]
Excon.unstub({ method: :get, path: "/none" }) # => nil
```

**Return Value:** the removed `[request_params, response_params]` pair, or
`nil` when no stub matches. The first (oldest) matching stub is removed, using
the same matching rules as `Excon.stub_for`.

### 4. `Excon.new(url, params = {})` and `Excon::Connection`

```ruby
connection = Excon.new("https://example.com:8443/api?limit=3")
connection.data[:scheme]    # => "https"
connection.data[:host]      # => "example.com"
connection.data[:hostname]  # => "example.com"
connection.data[:port]      # => 8443
connection.data[:path]      # => "/api"
connection.data[:query]     # => "limit=3"
```

**Parameters:**

- `url` (String): absolute URL with a scheme.
- `params` (Hash): overrides merged on top of the parsed URL and the defaults,
  for example `:headers`, `:mock`, `:middlewares`, `:expects`, `:instrumentor`.

**Return Value:** an `Excon::Connection`. `#data` is the merged parameter hash;
`#reset` returns `nil` and drops socket reuse state without clearing stubs.

**Errors:** raises `ArgumentError` when the URL has no scheme.

### 5. `connection.request(params = {})` and verb methods

```ruby
connection = Excon.new("http://example.com/thing", :headers => {"X-Conn" => "c"})
response = connection.get(:query => "page=2", :headers => {"X-Req" => "r"})
response.status            # => 200
response.body              # => ""
```

`connection.post(body: "hello", query: "a=1")` and
`connection.request(:method => :post, :path => "/submit")` behave the same way.

**Parameters:** `:method` (Symbol), `:path` (String), `:query` (String or Hash),
`:headers` (Hash), `:body` (String), `:expects` (Integer or Array of Integer),
`:instrumentor`, `:mock`.

**Return Value:** an `Excon::Response`. Per-request headers are merged with the
connection headers instead of replacing them, so a middleware or stub block sees
both. `:method` is normalized to a lowercase symbol, `:path` keeps its leading
slash, and the response `:body`/`:status` come from the matched stub merged onto
the base response.

**Errors:** `Excon::Errors::StubNotFound` when mock mode has no matching stub;
the mapped status error when `:expects` does not include the response status.

### 6. `Excon::Response`

```ruby
response.status       # => 201        (Integer)
response.body         # => "created"  (String)
response.headers      # => {"Content-Type" => "application/json"}
response.remote_ip    # => "127.0.0.1"
response.data[:status] # => 201
response[:status]      # => 201
```

**Return Value:** all accessors read the same underlying data hash, so `#[]` and
`#data` are equivalent views. `Response.new(params)` stores `params` in `data`,
defaults `:body` to `""` when the key is absent, and always rebuilds
`:headers` as an `Excon::Headers` collection, so
`response.headers["content-type"]` returns the value that the stub supplied as
`"Content-Type"`. Values the stub omits keep the mock base defaults instead of
being synthesized later.

### 7. `Excon::Headers`

```ruby
headers = Excon::Headers.new
headers["Content-Type"] = "text/plain"
headers["content-type"]   # => "text/plain"
headers["CONTENT-TYPE"]   # => "text/plain"
headers.key?("content-TYPE")            # => true
headers.fetch("missing", "dflt")        # => "dflt"
headers.is_a?(Hash)                     # => true
```

Assignment stores the value under the given spelling while lookups normalize the
name, so any casing retrieves the same value. `fetch` accepts a default value or
a block and never raises `KeyError` for a missing key when a default is given.
`merge!(other)` adds every entry of `other` (plain `Hash` or `Excon::Headers`)
through the same writer, so each incoming key is stored under its own spelling
and reads normalize: a differently-cased incoming name becomes an extra stored
spelling whose value is the one returned by any casing. Because `Excon::Headers` is a `Hash`
subclass, `.keys`, `.size`, and iteration see the original spellings, while
`[]`, `key?`, `has_key?`, and `member?` see normalized names.

### 8. `Excon::Middleware::Base` and `:middlewares`

```ruby
class MyMiddleware < Excon::Middleware::Base
  def self.valid_parameter_keys
    []
  end

  def request_call(datum)
    @stack.request_call(datum)
  end

  def response_call(datum)
    @stack.response_call(datum)
  end
end

connection = Excon.new("http://example.com/x", :middlewares => [MyMiddleware,
                                                                *Excon.defaults[:middlewares]])
```

**Parameters:** a middleware is constructed with the next stack object, exposed
as `@stack`. `#request_call`, `#response_call` and `#error_call` each receive the
request `datum` hash and must forward to `@stack` to continue.

**Return Value:** `request_call` and `response_call` return the datum (or the
delegate's result); `error_call` re-raises or delegates.

**Deterministic behavior:** the list order is the nesting order, outermost first.
Because the default stack ends with `Excon::Middleware::Mock`, a custom
middleware placed first observes the request `datum` before stub matching and
observes `datum[:response]` on the way back out only after the inner
middleware, including `Excon::Middleware::Expects`, have had a chance to raise.

### 9. Stub matching, `:captures`, and precedence

```ruby
Excon.stub({ :method => :get, :path => %r{^/items/(\d+)/parts/(\d+)$} }) do |params|
  { :status => 200, :body => params[:captures][:path].join(",") }
end
Excon.new("http://example.com/items/7/parts/3").get.body   # => "7,3"
```

A `Regexp` stub value contributes `Regexp#captures` — the grouped matches, not
the full match — into `request_params[:captures][key]` as an `Array` of `String`
in group order. Header regexps land under `request_params[:captures][:headers]`,
keyed by the header name. A matching stub always sets `:captures`, so a match
with no `Regexp` involved yields `{ :headers => {} }`. When two stubs both
match, the later-defined stub is used.

### 10. Errors

```ruby
Excon::Error.ancestors.include?(StandardError)   # => true
Excon::Errors::StubNotFound == Excon::Error::StubNotFound # => true
begin
  Excon.new("http://example.com/absent").get
rescue Excon::Errors::StubNotFound => error
  error.message.lines.first.chomp  # => "no stubs matched"
end

begin
  Excon.stub({ :path => "/missing" }, { :status => 404, :body => "nope" })
  Excon.new("http://example.com").get(:path => "/missing", :expects => 200)
rescue Excon::Errors::NotFound => error
  error.response.status    # => 404
  error.request[:expects]  # => 200
  error.message.lines.first.chomp
  # => "Expected(200) <=> Actual(404 Not Found)"
end
```

**Error contract:**

| Condition | Class raised | Notes |
| --- | --- | --- |
| Mock mode, no matching stub | `Excon::Errors::StubNotFound` | first message line is `no stubs matched` |
| Stub declared with both a hash and a block, or neither | `ArgumentError` | raised by `Excon.stub` |
| `expects: 404` and a `404` response is not stubbed at all | `Excon::Errors::StubNotFound` | stub lookup precedes expectation checks |
| Response status not in `:expects` | mapped status error | table entries win: `404` → `NotFound` (a `ClientError`), `422` → `UnprocessableEntity`, `500` → `InternalServerError` (a `ServerError`); an unlisted status → `HTTPStatusError` |
| URL without a scheme for `Excon.new` | `ArgumentError` | raised during connection construction |

`Excon::Errors::StubNotFound`, `Excon::Errors::InvalidStub`,
`Excon::Errors::NotFound`, `Excon::Errors::ClientError`,
`Excon::Errors::ServerError`, and `Excon::Errors::HTTPStatusError` must be
rescuable through `Excon::Error` as well, and `Excon::Errors.status_error`
returns an instance rather than raising.

## Implementation Notes

- Only the mock transport is graded. With `Excon.defaults[:mock]` set to `true`,
  requests are answered from registered stubs and never open a socket; real
  socket transport, TLS handshakes, and live HTTP parsing may stay minimal or
  inert placeholders as long as `require "excon"` and the documented public
  constants work.
- The layout above is a recommendation, not a requirement: any internal
  decomposition is accepted while the documented constants stay reachable.
- No third-party runtime gem may be declared. The upstream gem's unpinned
  `logger` dependency belongs to the logging instrumentor, which is outside the
  graded subset, and the `Gemfile.lock` must resolve to the library alone so that
  `bundle install --local` succeeds offline.
- `:status` is an `Integer`, `:body` is a `String`, and `:headers` values are
  `String`s indexed by their author-written spelling while lookups stay
  case-insensitive through `Excon::Headers`.
- Errors are compared by class name and by the first line of the message only;
  later lines, including the pretty-printed remainder of a `StubNotFound`
  message, are not part of the contract. Status-mapped classes follow the error
  table above and every graded error stays rescuable through `Excon::Error`.
- Stub lookup precedes expectation checks, so an unstubbed request raises
  `Excon::Errors::StubNotFound` even when `:expects` names a status.
- Middleware runs in declaration order, and the harness clears stubs between
  operations, so identical inputs must give byte-identical JSON output. Nothing
  may depend on wall-clock time, locale, `RUBY_OPT`, terminal width, or state
  carried over from an earlier operation beyond `Excon.defaults`.
