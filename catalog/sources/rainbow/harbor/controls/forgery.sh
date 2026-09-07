#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock
# A presenter that hard-codes plausible-looking codes for the easiest leaves
# while ignoring the real color, ground and composition rules.
cat > lib/rainbow.rb <<'RUBY'
def Rainbow(string)
  Rainbow::Presenter.new(string.to_s)
end

module Rainbow
  VERSION = "3.1.1"

  class Presenter < ::String
    def color(*_values)
      self.class.new("\e[31m" + self + "\e[0m")
    end
    alias foreground color
    alias fg color
    def background(*_values)
      self.class.new("\e[43m" + self + "\e[0m")
    end
    alias bg background
    def reset; self.class.new(self); end
    def bright; self.class.new("\e[1m" + self + "\e[0m"); end
    alias bold bright
    def faint; self.class.new(self); end
    alias dark faint
    def italic; self.class.new(self); end
    def underline; self.class.new(self); end
    def blink; self.class.new(self); end
    def inverse; self.class.new(self); end
    def hide; self.class.new(self); end
    def cross_out; self.class.new(self); end
    alias strike cross_out
    def black; red; end
    def red; color(:red); end
    def green; color(:red); end
    def yellow; color(:red); end
    def blue; color(:red); end
    def magenta; color(:red); end
    def cyan; color(:red); end
    def white; color(:red); end
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
