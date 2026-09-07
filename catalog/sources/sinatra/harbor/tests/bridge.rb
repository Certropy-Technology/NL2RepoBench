# frozen_string_literal: true

require "json"
require "stringio"

candidate_root = ARGV.fetch(0)
ENV["BUNDLE_GEMFILE"] = File.join(candidate_root, "Gemfile")
ENV["BUNDLE_PATH"] = ARGV.fetch(1)
require "bundler/setup"
$LOAD_PATH.unshift File.join(candidate_root, "lib")
require "sinatra/base"

# Fixed modular application. Every operation exercises this one class so the
# private contract observes only behavior documented in instruction.md.
class App < Sinatra::Base
  before { headers "X-Before" => "1" }
  before { halt 403 if params["deny"] == "yes" }

  get "/" do
    "index"
  end

  get "/hello/:name" do
    status 201
    "Hello #{params["name"]}"
  end

  get "/search" do
    params.to_json
  end

  post "/echo" do
    params["value"].to_s
  end

  get "/status" do
    status 418
    "teapot"
  end

  after { headers "X-After" => "1" }
end

def call_app(method, path, query = "", body = nil)
  env = {
    "REQUEST_METHOD" => method,
    "PATH_INFO" => path,
    "QUERY_STRING" => query,
    "SCRIPT_NAME" => "",
    "SERVER_NAME" => "example.org",
    "SERVER_PORT" => "80",
    "rack.url_scheme" => "http",
    "rack.input" => StringIO.new(body.to_s),
  }
  if body
    env["CONTENT_TYPE"] = "application/x-www-form-urlencoded"
    env["CONTENT_LENGTH"] = body.to_s.bytesize.to_s
  end
  status, headers, io = App.call(env)
  text = io.respond_to?(:each) ? io.map { |part| part.to_s }.join : io.to_s
  lowered = headers.each_with_object({}) { |(k, v), o| o[k.to_s.downcase] = v }
  [status, lowered, text]
end

# A projection keeps only documented, deterministic fields so the comparison is
# stable across a faithful reimplementation and upstream behavior.
request = JSON.parse($stdin.read)
op = request["operation"]
case op
when "query_params"
  st, hd, text = call_app("GET", "/search", "q=hi%20there&flag&n=7")
  projection = { status: st, params: JSON.parse(text).sort.to_h }
when "form_params"
  st, hd, text = call_app("POST", "/echo", "", "value=deep%20thought")
  projection = { status: st, body: text }
when "not_found"
  st, hd, text = call_app("GET", "/missing")
  projection = { status: st }
when "method_isolation"
  st, hd, text = call_app("POST", "/")
  projection = { status: st }
when "capture_precedence"
  st, hd, text = call_app("GET", "/hello/Ada", "name=Bob")
  projection = { status: st, body: text }
when "halt_denied"
  st, hd, text = call_app("GET", "/", "deny=yes")
  projection = { status: st, after: hd["x-after"] }
when "capture"
  st, hd, text = call_app("GET", "/hello/Ada")
  projection = { status: st, body: text }
when "status_code"
  st, hd, text = call_app("GET", "/status")
  projection = { status: st, body: text }
when "filters_headers"
  st, hd, text = call_app("GET", "/")
  projection = { status: st, body: text, before: hd["x-before"], after: hd["x-after"] }
else
  projection = { status: 500, body: "unsupported" }
end
puts JSON.generate({ ok: true, projection: projection })
