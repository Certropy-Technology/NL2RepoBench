#!/usr/bin/env bash
set -euo pipefail
(sleep 600) &
mkdir -p lib/excon
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock
cat > lib/excon.rb <<'RUBY'
module Excon
  VERSION = "0.0.0"
  class Error < StandardError; end
  def self.defaults
    @defaults ||= {}
  end
  def self.stubs
    @stubs ||= []
  end
end
RUBY
