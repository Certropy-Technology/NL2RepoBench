#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib
cat > Gemfile <<'GEMFILE'
source "https://rubygems.org"
GEMFILE
cat > Gemfile.lock <<'LOCK'
GEM
  remote: https://rubygems.org/

PLATFORMS
  ruby

DEPENDENCIES

BUNDLED WITH
   2.6.9
LOCK
cat > lib/textx.rb <<'RUBY'
module Textx
  def self.normalize(value)
    value.gsub(/\A[ \t\n\r\f\v]+|[ \t\n\r\f\v]+\z/, "")
  end
end
RUBY
