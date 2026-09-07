#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib/excon
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock
cat > lib/excon.rb <<'RUBY'
module Excon
  VERSION = "0.0.0"

  class Error < StandardError; end
  class Headers < Hash; end
  module Middleware; end
  module Errors; end

  def self.defaults
    @defaults ||= {}
  end

  def self.stubs
    @stubs ||= []
  end

  def self.stub(*)
    []
  end

  def self.unstub(*)
    nil
  end

  def self.stub_for(*)
    nil
  end

  def self.new(*)
    raise Error, "stub implementation"
  end
end
RUBY
