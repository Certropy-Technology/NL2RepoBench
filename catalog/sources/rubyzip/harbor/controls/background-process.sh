#!/usr/bin/env bash
set -euo pipefail
(sleep 600) &
mkdir -p lib/zip
printf 'source "https://rubygems.org"\n' > Gemfile
printf 'GEM\n  remote: https://rubygems.org/\n\nPLATFORMS\n  ruby\n\nDEPENDENCIES\n\nBUNDLED WITH\n   2.6.9\n' > Gemfile.lock
printf 'module Zip\nend\n' > lib/zip.rb
