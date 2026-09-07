require "json"

candidate = ARGV.fetch(0)
bundle_path = ARGV.fetch(1)
ENV["BUNDLE_GEMFILE"] = File.join(candidate, "Gemfile")
ENV["BUNDLE_PATH"] = bundle_path
require "bundler/setup"
$LOAD_PATH.unshift(File.join(candidate, "lib"))
require "textx"

STDIN.each_line do |line|
  request = JSON.parse(line)
  if request["operation"] != "normalize" || request["args"]&.length != 1
    puts JSON.generate("error_type" => "InvalidInput", "message" => "unknown operation")
    next
  end
  value = Textx.normalize(request["args"].fetch(0))
  puts JSON.generate("value" => value)
rescue StandardError => error
  puts JSON.generate("error_type" => "CallFailed", "message" => error.message)
end
