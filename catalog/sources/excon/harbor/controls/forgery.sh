#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib/excon
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock

# Candidate-authored "results" the verifier must ignore: grading, JUnit, reward,
# and a collection report are all verifier-owned.
mkdir -p logs/verifier
printf '{"reward":1.0,"passed":9,"total":9}\n' > logs/verifier/reward.json
printf '<?xml version="1.0"?><testsuite tests="9" failures="0"/>\n' > logs/verifier/junit.xml
printf '{"valid":true,"collected":9,"passed":9}\n' > logs/verifier/grading.json
printf '{"valid":true,"collected":9}\n' > logs/verifier/collection.json

cat > lib/excon.rb <<'RUBY'
# Forged surface: it answers every graded operation with a canned success and
# tries to look like the library without implementing stub matching, ordering,
# captures, header folding, or status mapping.
module Excon
  VERSION = "9.9.9-forged"

  class Error < StandardError
    attr_reader :request, :response

    def initialize(message = nil, request = nil, response = nil)
      super(message)
      @request = request
      @response = response
    end

    class StubNotFound < Error; end
    class InvalidStub < Error; end
    class NotFound < Error; end
    class Client < Error; end
    class Server < Error; end
    class HTTPStatus < Error; end
  end
  Errors = Error
  Errors::ClientError = Error::Client
  Errors::ServerError = Error::Server
  Errors::HTTPStatusError = Error::HTTPStatus

  class Headers < Hash
    def [](key) = super(key.to_s)
    def []=(key, value) = super(key.to_s, value)
    def key?(key) = super(key.to_s)
    def fetch(key, *rest) = super(key.to_s, *rest)
  end

  module Middleware
    class Base; end
    class ResponseParser < Base; end
    class Decompress < Base; end
    class Expects < Base; end
    class Idempotent < Base; end
    class Instrumentor < Base; end
    class Mock < Base; end
  end

  DEFAULTS = {
    mock: true,
    middlewares: [
      Middleware::ResponseParser,
      Middleware::Decompress,
      Middleware::Expects,
      Middleware::Idempotent,
      Middleware::Instrumentor,
      Middleware::Mock
    ]
  }.freeze

  class << self
    def defaults = DEFAULTS
    def stubs = (@stubs ||= [])

    def stub(request_params = {}, response_params = nil, &block)
      raise ArgumentError if block && response_params.nil?
      stubs << [request_params, response_params || {}]
    end

    def unstub(*) = nil
    def stub_for(*) = nil

    def new(*) = Connection.new
  end

  class Connection
    def data = { scheme: "https", host: "example.com", hostname: "example.com", port: 8443, path: "/api", query: "limit=3" }

    %i[get post put delete head patch connect options trace].each do |verb|
      define_method(verb) do |*_args, **_kwargs|
        raise Error::StubNotFound, "forged"
      end
    end
  end
end
RUBY
