require "json"

candidate = ARGV.fetch(0)
$LOAD_PATH.unshift(File.join(candidate, "lib"))
require "tilt"
require "tilt/string"

def with_new_mapping
  mapping = Tilt::Mapping.new
  yield mapping
end

def invoke(request)
  case request.fetch("operation")
  when "render_literal"
    {"value" => Tilt::StringTemplate.new { |t| "Hello World!" }.render}
  when "render_locals"
    {"value" => Tilt::StringTemplate.new { "Hey #{name}!" }.render(Object.new, :name => "Joe")}
  when "render_scope"
    scope = Object.new
    scope.instance_variable_set(:@name, "Joe")
    {"value" => Tilt::StringTemplate.new { "Hey #{@name}!" }.render(scope)}
  when "render_yield"
    {"value" => Tilt::StringTemplate.new { "Hey #{yield}!" }.render { "Joe" }}
  when "render_multiline_bytes"
    {"value" => Tilt::StringTemplate.new { "Hello\nWorld!\n" }.render.bytes.length}
  when "render_twice_stable"
    template = Tilt::StringTemplate.new { |t| "Hello World!" }
    results = Array.new(3) { template.render }
    {"value" => results.all? { |r| r == "Hello World!" }}
  when "template_data_accessor"
    {"value" => Tilt::StringTemplate.new { "abc" }.data}
  when "mapping_registration"
    stub = Class.new
    ok = with_new_mapping do |mapping|
      mapping.register(stub, "foo", "bar")
      mapping["foo"].equal?(stub) &&
        mapping["hello.foo"].equal?(stub) &&
        mapping["foo.baz"].nil? &&
        mapping.registered?("bar") &&
        !mapping.registered?("baz")
    end
    {"value" => ok}
  when "template_cache_identity"
    template = Tilt::StringTemplate.new { "" }
    cache = begin
      verbose, $VERBOSE = $VERBOSE, nil
      Tilt::Cache.new
    ensure
      $VERBOSE = verbose
    end
    first = cache.fetch("k") { template }
    second = cache.fetch("k") { Object.new }
    {"value" => first.equal?(template) && second.equal?(template)}
  when "missing_source_error"
    begin
      Tilt::StringTemplate.new
      {"value" => "none"}
    rescue StandardError => error
      {"value" => error.class.name}
    end
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
