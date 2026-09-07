#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock
cat > lib/rainbow.rb <<'RUBY'
# Packaging-only stub: it loads and answers the documented entry points, but
# returns the text unchanged so no frozen leaf can pass.
def Rainbow(string)
  string.to_s
end

module Rainbow
  VERSION = "0.0.0"

  class Presenter < ::String
    def color(*_values); self; end
    def background(*_values); self; end
    def reset; self; end
    def bright; self; end
    def faint; self; end
    def italic; self; end
    def underline; self; end
    def blink; self; end
    def inverse; self; end
    def hide; self; end
    def cross_out; self; end
  end

  class Wrapper
    attr_accessor :enabled

    def initialize(enabled = true)
      @enabled = enabled
    end

    def wrap(string)
      Presenter.new(string.to_s)
    end
  end

  def self.global
    @global ||= Wrapper.new
  end

  def self.enabled
    global.enabled
  end

  def self.enabled=(value)
    global.enabled = value
  end

  def self.new
    Wrapper.new(true)
  end

  def self.uncolor(string)
    string
  end
end
RUBY
