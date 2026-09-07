## Project Description

Sinatra is a Ruby domain-specific language for building web applications as
Rack endpoints. A modular application subclasses `Sinatra::Base`, registers
routes with HTTP verb and path patterns, reads request parameters, controls the
response status, headers, and body, and runs `before`/`after` filters around
each dispatch. Registered handlers are matched against the request verb and
path; the first match runs and its return value becomes the response body.

This task is a bounded, deterministic, pure-Ruby reimplementation of the
documented Sinatra DSL suitable for offline evaluation without a live web
server. It must load through `require "sinatra/base"` on Ruby 3.4 and must not
contact network services, bind sockets, start an HTTP server, spawn
subprocesses, or depend on native extensions. Requests are driven by the
verifier through the documented Rack contract `App.call(env)` inside the
candidate process.

## Natural Language Instruction (Prompt)

Please create a Ruby project named `sinatra` that implements the documented
Sinatra-compatible request DSL. The project should include the following
functions:

1. Modular application base: `Sinatra::Base` is a class that can be subclassed.
   Subclasses register routes at the class level, and each subclass inherits a
   `.call(env)` class method returning a Rack response triple
   `[status, headers, body]`.
2. Route registration: the class methods `get`, `post`, `put`, `patch`,
   `delete`, and `head` each take a path pattern string and a block. A path is
   either a literal (for example `"/"`) or contains exactly one `:name` capture
   segment (for example `"/hello/:name"`). When the pattern matches the request
   the block runs in the context of a fresh application instance. A literal
   pattern matches the whole path exactly; a capture pattern matches a path with
   the same number of `/`-separated segments and binds the `:name` segment. A
   route is considered only for its own verb.
3. Request parameters: within a handler or filter, `params` returns a Hash of
   String keys to String values (or `nil` for a bare flag key) merged from, in
   increasing precedence: the
   parsed `QUERY_STRING`, the named path captures, and the parsed
   `application/x-www-form-urlencoded` body read from `rack.input`. Values are
   percent-decoded (`+` becomes a space); a key that appears several times
   keeps its last value; a bare flag key with no `=` maps to `nil`.
4. Response control: within a handler, `status(code)` sets and returns the
   response status Integer; `headers(hash)` merges String header values and
   returns the merged Hash; the handler's String return value (or a value
   assigned with `body=`) becomes the single-element Rack body array. The
   default status is 200 and the default `Content-Type` header is
   `text/html;charset=utf-8`. A request matching no route yields status 404.
5. Filters: class-level `before { }` blocks run before the matching handler in
   registration order; class-level `after { }` blocks run after dispatch in
   registration order and may mutate response headers. Calling `halt(status)`
   inside a `before` filter ends the request immediately with that status and an
   empty body `[""]`, skipping the handler, while `after` filters still run and
   can still contribute their headers.
6. Core file requirements: provide a valid `Gemfile`, a matching `Gemfile.lock`
   with no external gem dependencies, and `lib/sinatra/base.rb` defining the
   `Sinatra` module and `Sinatra::Base` class. The package must load with
   `require "sinatra/base"` on Ruby 3.4. Do not copy the upstream repository,
   upstream tests, verifier files, or reference source into the generated
   project.

## Environment Configuration

### Ruby Version

The project is evaluated on MRI Ruby `3.4.10` with Bundler `2.6.9` on
Linux/amd64.

### Core Dependency Library Versions

```plain
ruby    3.4.10
bundler 2.6.9
```

The required implementation is pure Ruby and declares no runtime gem
dependencies; the candidate `Gemfile.lock` must therefore contain no `GEM`
specs and an empty `DEPENDENCIES` section. The Ruby standard library may be used,
but standard-library modules are not Gem dependencies and must not be declared
as external packages. The verifier installs the candidate using Bundler in
offline mode. Do not use a `GIT`, `PATH`, or plugin dependency source, native
extensions, the `rack`/`mustermann`/`tilt`/`sinatra` gems, or runtime network
access.

## Sinatra Project Architecture

### Project Directory Structure

Create an installable project with this public structure or an equivalent
standard Ruby Gem layout:

```plain
workspace/
├── Gemfile
├── Gemfile.lock
└── lib/
    └── sinatra/
        └── base.rb
```

`lib/sinatra/base.rb` defines the `Sinatra` module and the `Sinatra::Base`
class. Supporting Ruby files are allowed when they are loaded by this entry
point. Keep runtime files inside the project; do not read from an external
checkout or write outside application-requested paths.

## API Usage Guide

### Core API Imports

```ruby
require "sinatra/base"

Sinatra
Sinatra::Base
```

### 1. `Sinatra::Base` - Modular Application

**Function**: Base class for a Rack-callable modular web application.

```ruby
require "sinatra/base"

class App < Sinatra::Base
  before { headers "X-Before" => "1" }

  get "/" do
    "index"
  end

  get "/hello/:name" do
    status 201
    headers "Content-Type" => "text/plain"
    "Hello #{params["name"]}"
  end

  post "/echo" do
    params["value"].to_s
  end

  after { headers "X-After" => "1" }
end
```

#### 1.1 `get`/`post`/`put`/`patch`/`delete`/`head` - Register a Route

```ruby
App.get(path) { ... } -> nil
App.post(path) { ... } -> nil
```

**Parameters**:

- `path` (`String`): a literal path such as `"/"`, or a path with exactly one
  `:name` capture segment such as `"/hello/:name"`.
- block: the handler, executed with no arguments in the context of a fresh
  application instance for a matching request.

**Return Value**: `nil`.

Routes are recorded in registration order and grouped by verb. A literal path
(with no `:capture`) matches only when `PATH_INFO` equals it exactly. A path with
one `:name` segment matches a request whose `PATH_INFO` has the same number of
`/`-separated segments, binding the segment aligned with `:name`. A route is
considered only when its verb equals the request `REQUEST_METHOD`. When several
registered routes match, the earliest registered match wins.

#### 1.2 `before`/`after` - Register Filters

```ruby
App.before { ... } -> nil
App.after  { ... } -> nil
```

**Parameters**: a block run around a matched dispatch (status 200-499), in
registration order.

**Return Value**: `nil`.

`before` filters run before the handler; `after` filters run after dispatch on
the same instance and may edit response headers. A `halt` inside a `before`
filter skips the handler, but the registered `after` filters still run.

#### 1.3 `call` - Rack Endpoint

```ruby
App.call(env) -> [Integer, Hash, Array]
```

**Parameters**:

- `env` (`Hash`): a Rack-style environment using String keys. The documented keys
  are `REQUEST_METHOD`, `PATH_INFO`, `QUERY_STRING`, `CONTENT_TYPE`,
  `CONTENT_LENGTH`, and `rack.input` (a rewindable object providing the request
  body).

**Return Value**: a Rack triple `[status, headers, body]` where `status` is an
Integer, `headers` is a Hash carrying the String header pairs the application
set, and `body` is an Array containing a single String. Header names are matched
case-insensitively when the response is inspected, so a plain `String`-keyed Hash
is sufficient.

`call` selects the first matching route for `REQUEST_METHOD` and `PATH_INFO`,
runs `before` filters, the handler, and `after` filters in order, and returns the
accumulated triple. A request that matches no route for its verb yields status
404. `env["rack.input"]` must be rewound before it is read by the form parser.

### 2. Request/Response Helpers (inside a handler or filter)

```ruby
params() -> Hash<String, String | nil>
status() -> Integer
status(value) -> Integer
headers() -> Hash<String, String>
headers(hash) -> Hash<String, String>
body() -> String | Array | nil
body=(value) -> value
halt(status) -> ends the request immediately
```

**`params`**: a String-keyed Hash merging query string, named path captures, and
the urlencoded body as described above, with percent-decoding, last-value-wins
for repeated keys, and bare flags mapped to `nil`.

**`status(value)`**: with an Integer argument sets the response status and
returns it; with no argument returns the current status (default `200`).

**`headers(hash)`**: merges the given String-valued header pairs into the
response headers and returns the full merged Hash; with no argument returns the
current Hash. A default `Content-Type` of `text/html;charset=utf-8` is present
unless a handler or filter overrides it.

**`body` / `body=`**: the handler's String return value is the response body;
assigning `body = value` overrides it. The Rack body is always `[string]`.

**`halt(status)`**: ends the request immediately with the given status, an empty
body `[""]`, and the headers accumulated so far, skipping the handler; the
registered `after` filters still run afterwards.

**Usage Example** (driven by the verifier through `App.call`):

```ruby
status, headers, body = App.call(
  "REQUEST_METHOD" => "GET",
  "PATH_INFO"      => "/hello/Ada",
  "QUERY_STRING"   => "x=1"
)
status   # => 201
body     # => ["Hello Ada"]
headers  # => includes X-Before => "1", X-After => "1",
         #    and Content-Type => "text/plain"
```
`X-After` is present because the `after` filter contributed a header to the same
response, and `Content-Type` reflects the handler override rather than the
`text/html;charset=utf-8` default.

The verifier exercises only the public behavior documented above through
`App.call(env)` in an isolated Ruby subprocess. Unrelated upstream Sinatra
features - ERB/`tilt` templates, multiple or splat named parameters, cookies,
sessions, static file serving, custom `error` handlers, `Rack::Builder`, `run!`,
and middleware - are outside the required boundary.

## Implementation Notes

- The contract drives the application in-process through Rack: `App.call(env)`
  returns the triple `[status, headers, body]`. No HTTP server, socket,
  subprocess, native extension, or network service is involved.
- The package must load with `require "sinatra/base"` on Ruby 3.4 from a
  `Gemfile`/`Gemfile.lock` pair with no external gem dependencies, and
  `lib/sinatra/base.rb` defines the `Sinatra` module and `Sinatra::Base`.
- Each subclass inherits a `.call` class method, and a matched pattern runs its
  block in a fresh application instance. A pattern is either a literal matched
  against the whole path or one with exactly one `:name` capture segment matched
  against a path with the same number of `/`-separated segments, and a route is
  considered only for the verb it was registered with.
- `params` merges, in increasing precedence, the parsed `QUERY_STRING`, the named
  path captures, and the parsed `application/x-www-form-urlencoded` body from
  `rack.input`; values are percent-decoded with `+` as a space, a repeated key
  keeps its last value, and a bare flag key with no `=` maps to `nil`.
- Defaults are status `200` and `Content-Type: text/html;charset=utf-8`; the
  handler's String return value (or a `body=` assignment) becomes the
  single-element body array, and a request matching no route yields `404`.
- `before` and `after` filters run in registration order around dispatch;
  `halt(status)` inside a `before` filter ends the request immediately with that
  status and the empty body `[""]`, skipping the handler, while `after` filters
  still run and can still contribute headers.
- Results are deterministic: no clock, locale, environment, or state left by a
  previous request may change a documented return value.
- Do not copy the upstream repository, upstream tests, verifier files, or
  reference source into the generated project.
