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
cat > lib/haml.rb <<'RB'
module Haml
  class Error < StandardError; end

  class Template
    def initialize(*_args, **_kwargs, &_block)
    end

    def render(*)
      ""
    end
  end
end
RB
