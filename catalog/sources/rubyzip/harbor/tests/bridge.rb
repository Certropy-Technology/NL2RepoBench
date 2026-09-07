require "json"
require "stringio"

CANDIDATE = File.expand_path(ARGV.fetch(0))
$LOAD_PATH.unshift File.join(CANDIDATE, "lib")
require "zip"

def write_archive
  buffer = StringIO.new
  archive_io = Zip::OutputStream.write_buffer(buffer) { |zos| yield zos }
  archive_io.respond_to?(:string) ? archive_io.string : buffer.string
end

def with_archive(archive)
  result = nil
  Zip::File.open_buffer(StringIO.new(archive)) { |zf| result = yield zf }
  result
end

def invoke(request)
  operation = request.fetch("operation")
  case operation
  when "create-and-list"
    archive = write_archive do |zos|
      zos.put_next_entry("dir/a.txt")
      zos.write "hello"
      zos.put_next_entry("b.bin")
      zos.write "xyz"
    end
    names = with_archive(archive) { |zf| zf.entries.map(&:name) }
    { "value" => names.sort }
  when "entry-count"
    archive = write_archive do |zos|
      zos.put_next_entry("dir/a.txt")
      zos.write "hello"
      zos.put_next_entry("b.bin")
      zos.write "xyz"
    end
    { "value" => with_archive(archive) { |zf| zf.entries.size } }
  when "read-entry"
    archive = write_archive do |zos|
      zos.put_next_entry("dir/a.txt")
      zos.write "hello"
    end
    { "value" => with_archive(archive) { |zf| zf.read("dir/a.txt") } }
  when "stored-metadata"
    archive = write_archive do |zos|
      zos.put_next_entry("stored.bin", "", nil, Zip::Entry::STORED)
      zos.write "AAAA"
    end
    with_archive(archive) do |zf|
      e = zf.get_entry("stored.bin")
      { "value" => [e.name, e.size, e.crc, e.compression_method] }
    end
  when "deflated-metadata"
    archive = write_archive do |zos|
      zos.put_next_entry("b.bin")
      zos.write "xyz"
    end
    with_archive(archive) do |zf|
      e = zf.get_entry("b.bin")
      { "value" => [e.name, e.size, e.crc, e.compression_method] }
    end
  when "directory-entry"
    archive = write_archive do |zos|
      zos.put_next_entry("folder/", "", nil, Zip::Entry::STORED)
      zos.put_next_entry("folder/x")
      zos.write "q"
    end
    { "value" => with_archive(archive) { |zf| zf.entries.map(&:name) } }
  when "stream-read"
    archive = write_archive do |zos|
      zos.put_next_entry("b.bin")
      zos.write "xyz"
    end
    { "value" => with_archive(archive) { |zf| zf.get_input_stream("b.bin") { |is| is.read } } }
  when "missing-entry"
    archive = write_archive do |zos|
      zos.put_next_entry("dir/a.txt")
      zos.write "hello"
    end
    with_archive(archive) do |zf|
      find_nil = zf.find_entry("nope").nil?
      raises =
        begin
          zf.get_entry("nope")
          false
        rescue Errno::ENOENT
          true
        end
      { "value" => [find_nil, raises] }
    end
  else
    { "error_type" => "InvalidInput", "message" => "unknown operation" }
  end
end

STDIN.each_line do |line|
  next if line.strip.empty?

  begin
    request = JSON.parse(line)
    puts JSON.generate(invoke(request))
  rescue StandardError => e
    puts JSON.generate("error_type" => e.class.name, "message" => e.message)
  end
end
