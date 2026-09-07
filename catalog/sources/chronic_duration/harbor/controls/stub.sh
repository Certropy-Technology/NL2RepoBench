#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib
cat > Gemfile <<'GEMFILE'
source "https://rubygems.org"
gem "numerizer", "0.2.0"
GEMFILE
cat > Gemfile.lock <<'LOCK'
GEM
  remote: https://rubygems.org/
  specs:
    numerizer (0.2.0)

PLATFORMS
  ruby

DEPENDENCIES
  numerizer (= 0.2.0)

BUNDLED WITH
   2.6.9
LOCK
cat > lib/chronic_duration.rb <<'RUBY'
# Declares the documented surface so packaging and import succeed, while every
# behavior returns a placeholder. Expected result: frozen denominator, zero.
module ChronicDuration
  class DurationParseError < StandardError; end

  @state = { raise_exceptions: false, hours_per_day: 24, days_per_week: 7 }

  class << self
    def raise_exceptions = !!@state[:raise_exceptions]
    def raise_exceptions=(value) = @state[:raise_exceptions] = !!value
    def hours_per_day = @state[:hours_per_day]
    def hours_per_day=(value) = @state[:hours_per_day] = value
    def days_per_week = @state[:days_per_week]
    def days_per_week=(value) = @state[:days_per_week] = value
    def parse(_string, _opts = {}) = 0
    def output(_seconds, _opts = {}) = "0 secs"
  end
end
RUBY
