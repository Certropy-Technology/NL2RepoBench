# Candidate boundary for the chronic_duration contract: one JSON request per
# stdin line, one JSON response per stdout line. Module-level knobs are restored
# before every request, so no leaf can observe a previous leaf's state.
require "json"

candidate = ARGV.fetch(0)
bundle_path = ARGV.fetch(1)
ENV["BUNDLE_GEMFILE"] = File.join(candidate, "Gemfile")
ENV["BUNDLE_PATH"] = bundle_path
require "bundler/setup"
$LOAD_PATH.unshift(File.join(candidate, "lib"))
require "chronic_duration"

DEFAULT_HOURS_PER_DAY = 24
DEFAULT_DAYS_PER_WEEK = 7

def restore_defaults
  ChronicDuration.raise_exceptions = false
  ChronicDuration.hours_per_day = DEFAULT_HOURS_PER_DAY
  ChronicDuration.days_per_week = DEFAULT_DAYS_PER_WEEK
end

def parse_operation(request)
  case request.fetch("operation")
  when "parse_unit_arithmetic"
    { "mins_secs" => ChronicDuration.parse("3 mins 4 sec"),
      "hrs_mins" => ChronicDuration.parse("2 hrs 20 min"),
      "mos_days" => ChronicDuration.parse("6 mos 1 day"),
      "yrs_mos_days" => ChronicDuration.parse("47 yrs 6 mos and 4.5d") }
  when "parse_chrono_string"
    { "minutes_seconds" => ChronicDuration.parse("1:20"),
      "hours_minutes_seconds" => ChronicDuration.parse("4:01:01"),
      "fractional_seconds" => ChronicDuration.parse("1:20.51") }
  when "parse_spelled_numerals"
    { "hours_minutes" => ChronicDuration.parse("two hours and twenty minutes"),
      "mins_secs" => ChronicDuration.parse("three mins four sec") }
  when "parse_implicit_unit_and_precision"
    fractional = ChronicDuration.parse("2.5 hrs")
    whole = ChronicDuration.parse("12 mins 3 seconds")
    { "bare_number" => ChronicDuration.parse("5"),
      "default_minutes" => ChronicDuration.parse("5", default_unit: "minutes"),
      "default_hours" => ChronicDuration.parse("5", default_unit: "hours"),
      "fractional_hours" => fractional,
      "fractional_is_float" => fractional.is_a?(Float),
      "whole_seconds" => whole,
      "whole_is_integer" => whole.is_a?(Integer) }
  when "parse_unit_scaling"
    restore_defaults
    ChronicDuration.hours_per_day = 8
    ChronicDuration.days_per_week = 5
    scaled = { "work_days" => ChronicDuration.parse("5d"),
               "work_hours" => ChronicDuration.parse("40h"),
               "work_week" => ChronicDuration.parse("1w"),
               "work_month" => ChronicDuration.parse("1mo"),
               "scaled_year" => ChronicDuration.parse("1y") }
    restore_defaults
    scaled.merge("restored_day" => ChronicDuration.parse("1d"),
                 "restored_week" => ChronicDuration.parse("1w"),
                 "restored_month" => ChronicDuration.parse("1mo"))
  when "parse_invalid_input"
    { "unrecognized" => ChronicDuration.parse("gobblygoo"),
      "zero" => ChronicDuration.parse("0"),
      "keep_zero" => ChronicDuration.parse("0", keep_zero: true),
      "partial_match" => ChronicDuration.parse("23 gobblygoos") }
  when "parse_raise_exceptions"
    default_disabled = ChronicDuration.raise_exceptions == false
    error_class = "no-error"
    begin
      ChronicDuration.raise_exceptions = true
      ChronicDuration.parse("23 gobblygoos")
    rescue StandardError => error
      error_class = error.class.name
    end
    enabled = ChronicDuration.raise_exceptions == true
    restore_defaults
    { "default_disabled" => default_disabled,
      "enabled" => enabled,
      "error_class" => error_class,
      "after_reset" => ChronicDuration.parse("23 gobblygoos") }
  when "output_format_matrix"
    { "default_14461" => ChronicDuration.output(14461, format: :default),
      "micro_14461" => ChronicDuration.output(14461, format: :micro),
      "short_14461" => ChronicDuration.output(14461, format: :short),
      "long_14461" => ChronicDuration.output(14461, format: :long),
      "chrono_14461" => ChronicDuration.output(14461, format: :chrono),
      "chrono_8400" => ChronicDuration.output(8400, format: :chrono),
      "no_option_8400" => ChronicDuration.output(8400) }
  when "output_options"
    { "units_2" => ChronicDuration.output(14461, units: 2),
      "units_1" => ChronicDuration.output(14461, units: 1),
      "units_3_long" => ChronicDuration.output(15642061, units: 3, format: :long),
      "joiner" => ChronicDuration.output(8400, joiner: ", "),
      "limit_to_hours" => ChronicDuration.output(34128900, limit_to_hours: true),
      "weeks_enabled" => ChronicDuration.output(3888000, weeks: true),
      "weeks_disabled" => ChronicDuration.output(3888000),
      "units_0" => ChronicDuration.output(14461, units: 0) }
  when "output_zero_and_roundtrip"
    { "zero" => ChronicDuration.output(0),
      "zero_keep_zero" => ChronicDuration.output(0, keep_zero: true),
      "zero_micro_keep_zero" => ChronicDuration.output(0, format: :micro, keep_zero: true),
      "zero_chrono" => ChronicDuration.output(0, format: :chrono),
      "roundtrip_default" => ChronicDuration.parse(ChronicDuration.output(8400)),
      "roundtrip_short" => ChronicDuration.parse(ChronicDuration.output(15638400, format: :short)),
      "roundtrip_chrono" => ChronicDuration.parse(ChronicDuration.output(47109600, format: :chrono)) }
  else
    nil
  end
end

STDIN.each_line do |line|
  begin
    request = JSON.parse(line)
    restore_defaults
    value = parse_operation(request)
    if value.nil?
      puts JSON.generate("error_type" => "InvalidInput", "message" => "unknown operation")
    else
      puts JSON.generate("value" => value)
    end
  rescue StandardError => error
    puts JSON.generate("error_type" => "CallFailed", "message" => error.message)
  ensure
    begin
      restore_defaults
    rescue StandardError
      nil
    end
  end
end
