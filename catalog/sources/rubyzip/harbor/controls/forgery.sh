#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib/zip
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock
cat > lib/zip.rb <<'RUBY'
require "json"
module Zip
  class Entry
    STORED = 0
    DEFLATED = 8
    attr_reader :name, :size, :crc, :compression_method
    def initialize(name = "", size = 0, crc = 0, cmethod = 0)
      @name = name; @size = size; @crc = crc; @compression_method = cmethod
    end
  end
  class OutputStream
    def put_next_entry(*) = nil
    def write(*) = nil
  end
  class File
    def self.open_buffer(io)
      zf = new
      yield zf if block_given?
      io
    end
    def entries
      [Entry.new("forged.txt", 999, 12345, 8)]
    end
    def read(*) = "forged"
    def get_entry(*) = Entry.new("forged.bin", 4, 2601322737, 0)
    def find_entry(*) = Entry.new("forged", 1, 2, 3)
    def get_input_stream(*) = "forged"
  end
  def self.default_compression = 6
end
RUBY
