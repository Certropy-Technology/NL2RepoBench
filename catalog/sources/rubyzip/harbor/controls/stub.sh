#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib/zip
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock
cat > lib/zip.rb <<'RUBY'
module Zip
  class Entry
    STORED = 0
    DEFLATED = 8
    def name = ""
    def size = 0
    def crc = 0
    def compression_method = 0
  end
  class File
    def self.open_buffer(*) = nil
    def entries = []
    def read(*) = "stub"
  end
  class OutputStream
    def self.write_buffer(io = nil) = io
  end
end
RUBY
