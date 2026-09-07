require "json"

candidate = ARGV.fetch(0)
bundle_path = ARGV.fetch(1)
ENV["BUNDLE_GEMFILE"] = File.join(candidate, "Gemfile")
ENV["BUNDLE_PATH"] = bundle_path
require "bundler/setup"
$LOAD_PATH.unshift(File.join(candidate, "lib"))
require "haml"

# Rendered-output entry point for this contract: Haml's public template API,
# constructed with an options Hash plus a block holding the template source and
# rendered against a scope object with optional locals.
def render(source, options = {})
  Haml::Template.new(options) { source }.render(Object.new)
end

def invoke(request)
  case request.fetch("operation")
  when "static_tag"
    { "value" => render("%span hello") }
  when "loud_script_sequence"
    { "value" => render("= 1 + 2\n%span= 3 * 4") }
  when "nested_tag"
    { "value" => render("%span\n  hello") }
  when "text_interpolation"
    { "value" => render('1#{ "2#{3}4" }5') }
  when "escaped_loud_script"
    { "value" => render(%q|%span&= '<nyaa>'|) }
  when "raw_loud_script"
    { "value" => render(%q|%p!= '<em>x</em>'|) }
  when "old_attributes"
    { "value" => render(%q|%span{ :class => 'foo', id: 'bar' } bar|) }
  when "silent_then_loud"
    { "value" => render("- foo = 3\n- bar = 2\n= foo + bar") }
  when "loop_block"
    { "value" => render("- 2.times do |i|\n  = i") }
  when "illegal_indent_error"
    begin
      render("%body\n  %div\n        %p")
      { "value" => "None" }
    rescue Haml::Error
      # The documented contract is that illegal indentation is rescuable
      # as Haml::Error. Engine subclasses (the reference raises
      # Haml::SyntaxError) satisfy it, so they are reported under the
      # documented class name.
      { "value" => "Haml::Error" }
    rescue StandardError => error
      { "value" => error.class.name }
    end
  else
    { "error_type" => "InvalidInput", "message" => "unknown operation" }
  end
end

STDIN.each_line do |line|
  request = JSON.parse(line)
  puts JSON.generate(invoke(request))
rescue StandardError => error
  puts JSON.generate("error_type" => "CallFailed", "message" => error.message)
end
