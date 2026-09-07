require "json"
require "stringio"

candidate = ARGV.fetch(0)
$LOAD_PATH.unshift(File.join(candidate, "lib"))
require "excon"

# Captured before this bridge turns mock mode on: the contract pins the defaults
# a fresh candidate ships with, not the values mutated by the harness itself.
SHIPPED_DEFAULTS = {
  "version" => Excon::VERSION,
  "mock_default" => Excon.defaults[:mock],
  "retry_limit" => Excon.defaults[:retry_limit],
  "stubs_scope" => Excon.defaults[:stubs].to_s
}.freeze

Excon.defaults[:mock] = true

def invoke(request)
  Excon.stubs.clear
  case request.fetch("operation")
  when "version_defaults"
    {"value" => SHIPPED_DEFAULTS}
  when "stub_basic_response"
    Excon.stub({:method => :get, :host => "example.com"},
               {:status => 201, :body => "created", :headers => {"Content-Type" => "application/json"}})
    response = Excon.new("http://example.com/thing").get
    {"value" => {"status" => response.status, "body" => response.body,
                 "data_status" => response.data[:status], "index_body" => response[:body],
                 "remote_ip" => response.remote_ip}}
  when "stub_precedence"
    Excon.stub({:method => :get, :path => "/dup"}, {:status => 200, :body => "first"})
    Excon.stub({:method => :get, :path => "/dup"}, {:status => 202, :body => "second"})
    response = Excon.new("http://example.com/dup").get
    {"value" => {"status" => response.status, "body" => response.body}}
  when "stub_block_captures"
    Excon.stub({:method => :get, :path => %r{^/items/(\d+)$}}) do |params|
      {:status => 200, :body => params[:captures][:path].join(",")}
    end
    response = Excon.new("http://example.com/items/42").get
    {"value" => {"status" => response.status, "body" => response.body}}
  when "stub_not_found"
    begin
      Excon.new("http://example.com/absent").get
      {"value" => {"error" => "none"}}
    rescue Excon::Error::StubNotFound => error
      {"value" => {"error" => error.class.name,
                   "first_line" => error.message.lines.first.to_s.chomp,
                   "aliased" => (Excon::Errors::StubNotFound == Excon::Error::StubNotFound)}}
    end
  when "expects_mismatch"
    Excon.stub({:method => :get, :path => "/missing"}, {:status => 404, :body => "nope"})
    begin
      Excon.new("http://example.com").get(:path => "/missing", :expects => 200)
      {"value" => {"error" => "none"}}
    rescue Excon::Error => error
      {"value" => {"error" => error.class.name,
                   "response_status" => error.response.status,
                   "request_expects" => error.request[:expects]}}
    end
  when "connection_url_params"
    data = Excon.new("https://example.com:8443/api?limit=3").data
    {"value" => {"scheme" => data[:scheme], "host" => data[:host], "hostname" => data[:hostname],
                 "port" => data[:port], "path" => data[:path], "query" => data[:query]}}
  when "request_option_merge"
    seen = nil
    Excon.stub({:method => :post}) do |params|
      seen = params
      {:status => 200, :body => "ok"}
    end
    connection = Excon.new("http://example.com/submit", :headers => {"X-Conn" => "c"})
    response = connection.post(:headers => {"X-Req" => "r"}, :query => "a=1", :body => "hello")
    {"value" => {"status" => response.status, "method" => seen[:method].to_s, "path" => seen[:path],
                 "query" => seen[:query], "body" => seen[:body],
                 "conn_header" => seen[:headers]["X-Conn"], "req_header" => seen[:headers]["X-Req"],
                 "host_header" => seen[:headers]["Host"]}}
  when "headers_case_insensitive"
    headers = Excon::Headers.new
    headers["Content-Type"] = "text/plain"
    {"value" => {"lower" => headers["content-type"], "upper" => headers["CONTENT-TYPE"],
                 "key" => headers.key?("content-type"), "fetch" => headers.fetch("missing", "dflt"),
                 "is_hash" => headers.is_a?(Hash)}}
  else
    {"error_type" => "InvalidInput", "message" => "unknown operation"}
  end
ensure
  Excon.stubs.clear if defined?(Excon) && Excon.respond_to?(:stubs)
end

STDIN.each_line do |line|
  request = JSON.parse(line)
  puts JSON.generate(invoke(request))
rescue StandardError => error
  puts JSON.generate("error_type" => "CallFailed", "message" => error.message)
end
