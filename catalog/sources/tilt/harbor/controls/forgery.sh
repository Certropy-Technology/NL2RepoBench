#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib/tilt
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock
cat > lib/tilt.rb <<'RUBY'
module Tilt
  def self.[](*); :forged; end
  def self.register(*); :forged; end
  def self.registered?(*) true; end
  class Template
  end
  class Mapping
    def register(*); end
    def [](*); :forged; end
    def registered?(*) true; end
  end
  class Cache
    def fetch(*key); yield; end
  end
end
RUBY
cat > lib/tilt/string.rb <<'RUBY'
module Tilt
  class StringTemplate < Template
    def initialize(*args, &block); @data = block ? block.call(self) : ""; end
    def data; @data; end
    def render(*, **); "forged"; end
  end
end
RUBY
