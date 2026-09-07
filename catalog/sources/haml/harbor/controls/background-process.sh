#!/usr/bin/env bash
set -euo pipefail
mkdir -p lib
printf %s\\n source\ \"https://rubygems.org\" > Gemfile
cat > Gemfile.lock <<'LOCK'
GEM
  remote: https://rubygems.org/

PLATFORMS
  ruby

DEPENDENCIES

BUNDLED WITH
   2.6.9
LOCK
(sleep 600) &
cat > lib/haml.rb <<'RB'
module Haml
end
RB
