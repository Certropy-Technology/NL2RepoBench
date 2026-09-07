#!/usr/bin/env bash
set -euo pipefail
(sleep 600) &
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
module ChronicDuration
end
RUBY
