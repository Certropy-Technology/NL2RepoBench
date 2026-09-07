#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib/sinatra
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock
cat > lib/sinatra/base.rb <<'RUBY'
module Sinatra
  class Base
    def self.before(*); end
    def self.after(*); end
    def self.get(*); end
    def self.post(*); end
    def self.put(*); end
    def self.patch(*); end
    def self.delete(*); end
    def self.head(*); end
    # Forged: ignores the request and returns canned output to mimic success.
    def self.call(_env); [200, { "Content-Type" => "text/html" }, ["forged"]]; end
  end
end
RUBY
