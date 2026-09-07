# Reviewed candidate-facing adapter for the Rainbow contract.
#
# It loads only the candidate's public `rainbow` entry point, drives every
# operation through documented public API, and returns plain JSON data, so the
# trusted contract never imports the candidate in-process.
require "json"

candidate = ARGV.fetch(0)
$LOAD_PATH.unshift(File.join(candidate, "lib"))
require "rainbow"

# Records the class of the error raised by `block`, or "no-raise". The caller is
# responsible for the global `Rainbow.enabled` state, which this helper never
# changes.
def error_class
  yield
  "no-raise"
rescue Exception => error
  error.class.name
end

def invoke(request)
  case request.fetch("operation")
  when "named-color-methods"
    Rainbow.enabled = true
    source = "hello"
    presented = Rainbow(source).red
    {"value" => [
      Rainbow("hello").red,
      Rainbow("hello").green,
      Rainbow("hello").blue,
      Rainbow(123).red,
      source,
      presented.to_s,
      presented.equal?(source)
    ]}
  when "color-form-and-ground-equivalence"
    Rainbow.enabled = true
    {"value" => [
      Rainbow("hello").color(1),
      Rainbow("hello").color(:red),
      Rainbow("hello").fg(:red),
      Rainbow("hello").foreground(:red),
      Rainbow("hello").bg(:yellow),
      Rainbow("hello").background(0),
      Rainbow("hello").color(:default),
      Rainbow("hello").background(:default)
    ]}
  when "rgb-triplet-palette-code"
    Rainbow.enabled = true
    {"value" => [
      Rainbow("hello").color(115, 23, 98),
      Rainbow("hello").color(0, 0, 0),
      Rainbow("hello").color(255, 255, 255),
      Rainbow("hello").background(115, 23, 98)
    ]}
  when "hex-string-color-code"
    Rainbow.enabled = true
    {"value" => [
      Rainbow("hello").color("#FFC482"),
      Rainbow("hello").color("ffc482"),
      Rainbow("hello").color("#000000"),
      Rainbow("hello").color("#ffffff")
    ]}
  when "style-effect-code-table"
    Rainbow.enabled = true
    {"value" => [
      Rainbow("hello").bright.faint.italic.underline.blink.inverse.hide.cross_out,
      Rainbow("hello").bold,
      Rainbow("hello").dark,
      Rainbow("hello").strike,
      Rainbow("hello").reset
    ]}
  when "style-chain-order-significant"
    Rainbow.enabled = true
    {"value" => [
      Rainbow("hola!").blue.bright.underline,
      Rainbow("hola!").underline.bright.blue,
      Rainbow("hello").color(:red).bright
    ]}
  when "composition-leading-run-preservation"
    Rainbow.enabled = true
    {"value" => [
      Rainbow("\e[32mgreen\e[0m").red,
      Rainbow("x\e[0m").red,
      Rainbow("A\e[31mB").red,
      Rainbow("\e[1m\e[4mabc").red
    ]}
  when "nested-presenter-composition"
    Rainbow.enabled = true
    {"value" => [
      Rainbow(Rainbow("x").red).green,
      Rainbow(Rainbow("hello").bg(:yellow)).fg(:red)
    ]}
  when "uncolor-removes-only-sgr"
    {"value" => [
      Rainbow.uncolor("\e[1;31mA\e[0m B\e[K \e[38;5;90mC"),
      Rainbow.uncolor("plain"),
      Rainbow.uncolor("\e[0m"),
      Rainbow.uncolor(Rainbow.uncolor("\e[31mA\e[0m"))
    ]}
  when "disabled-null-presenter-output"
    Rainbow.enabled = false
    red = Rainbow("hello").red
    {"value" => [
      red,
      Rainbow("hello").red.bright.bg(:blue),
      red.include?("\e"),
      Rainbow("hello").reset,
      Rainbow("hello").cross_out,
      error_class { Rainbow("hello").not_a_color }
    ]}
  when "wrapper-instance-isolation"
    Rainbow.enabled = true
    first = Rainbow.new
    second = Rainbow.new
    first.enabled = false
    {"value" => [
      first.wrap("hello").red,
      second.wrap("hello").red,
      Rainbow("hello").red,
      first.enabled,
      second.enabled,
      Rainbow.enabled
    ]}
  when "color-argument-error-contract"
    Rainbow.enabled = true
    {"value" => [
      error_class { Rainbow("hello").color },
      error_class { Rainbow("hello").color(1, 2) },
      error_class { Rainbow("hello").color(1, 2, 3, 4) },
      error_class { Rainbow("hello").color(:snowbonk) },
      error_class { Rainbow("hello").color(300, 0, 0) },
      error_class { Rainbow("hello").color(0, -1, 0) },
      error_class { Rainbow("hello").color("zzzzzz") },
      error_class { Rainbow("hello").color("FFC48") },
      error_class { Rainbow("hello").not_a_color },
      error_class { Rainbow("hello").color(:red) }
    ]}
  else
    {"error_type" => "InvalidInput", "message" => "unknown operation"}
  end
end

STDIN.each_line do |line|
  request = JSON.parse(line)
  puts JSON.generate(invoke(request))
rescue StandardError => error
  puts JSON.generate("error_type" => "CallFailed", "message" => error.message)
end
