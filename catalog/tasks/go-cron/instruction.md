# Build a bounded cron scheduling library

## Project Description

Create the pure-Go module `github.com/robfig/cron/v3` at the repository root.
It parses cron expressions, computes deterministic next activation times, and
keeps an in-memory set of scheduled jobs. The task exercises the serializable
parts of the parser and scheduler API, plus the standard job wrappers. Actual
wall-clock service operation is not required by the bridge contract.

## Supports

- Linux/amd64 with Go `1.26.5`.
- Exactly one root `go.mod` declaring `module github.com/robfig/cron/v3`, a
  matching `go.sum`, and a complete `vendor/modules.txt` closure. The package
  has no third-party dependencies.
- Pure Go with `CGO_ENABLED=0`; build with
  `GOOS=linux GOARCH=amd64 GOWORK=off GOPROXY=off GOSUMDB=off
  GOTOOLCHAIN=local` and `go build -mod=vendor`.
- No cgo, plugins, `unsafe`, generated code, workspace files, network services,
  or external state.

## Natural Language Instruction

Create the pure-Go `github.com/robfig/cron/v3` module from an empty workspace.
Implement cron parsing, deterministic next-time calculation, scheduler
entries, and standard job wrappers listed below; live wall-clock service
operation is outside the evaluated bridge contract.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── parser.go
├── cron.go
├── chain.go
└── wrappers.go
```

Expose package `cron` at the exact module root. Do not add private verifier
files or external services.

## Examples

```go
schedule, err := ParseStandard("0 * * * *")
next := schedule.Next(time.Unix(0, 0))
```

```go
c := New(WithSeconds()); c.AddFunc("*/5 * * * * *", func() {})
```

## Error Handling and Boundary Conditions

Preserve malformed expression errors, field descriptors, timezone behavior,
next-time boundaries, job wrapper errors, and deterministic entry ordering.
Avoid requiring a running scheduler or network access.

## API Usage Guide

Implement package `cron` at import path `github.com/robfig/cron/v3` with these
public APIs:

```go
type ParseOption int
const (
    Second ParseOption = 1 << iota
    SecondOptional
    Minute
    Hour
    Dom
    Month
    Dow
    DowOptional
    Descriptor
)

type Parser struct { /* private representation */ }
func NewParser(options ParseOption) Parser
func (p Parser) Parse(spec string) (Schedule, error)
func ParseStandard(spec string) (Schedule, error)

type Schedule interface { Next(time.Time) time.Time }
type SpecSchedule struct {
    Second, Minute, Hour, Dom, Month, Dow uint64
    Location *time.Location
}
func (s *SpecSchedule) Next(t time.Time) time.Time

type ConstantDelaySchedule struct { Delay time.Duration }
func Every(duration time.Duration) ConstantDelaySchedule
func (s ConstantDelaySchedule) Next(t time.Time) time.Time

type Job interface { Run() }
type FuncJob func()
func (f FuncJob) Run()
type JobWrapper func(Job) Job
type Chain struct { /* private representation */ }
func NewChain(wrappers ...JobWrapper) Chain
func (c Chain) Then(j Job) Job
func Recover(logger Logger) JobWrapper
func DelayIfStillRunning(logger Logger) JobWrapper
func SkipIfStillRunning(logger Logger) JobWrapper

type Logger interface {
    Info(msg string, keysAndValues ...interface{})
    Error(err error, msg string, keysAndValues ...interface{})
}
var DefaultLogger Logger
var DiscardLogger Logger
func PrintfLogger(l interface{ Printf(string, ...interface{}) }) Logger
func VerbosePrintfLogger(l interface{ Printf(string, ...interface{}) }) Logger

type Cron struct { /* private representation */ }
type EntryID int
type Entry struct {
    ID EntryID
    Schedule Schedule
    Next time.Time
    Prev time.Time
    WrappedJob Job
    Job Job
}
func New(opts ...Option) *Cron
func (c *Cron) AddFunc(spec string, cmd func()) (EntryID, error)
func (c *Cron) AddJob(spec string, cmd Job) (EntryID, error)
func (c *Cron) Schedule(schedule Schedule, cmd Job) EntryID
func (c *Cron) Entries() []Entry
func (c *Cron) Location() *time.Location
func (c *Cron) Entry(id EntryID) Entry
func (c *Cron) Remove(id EntryID)
func (c *Cron) Start()
func (c *Cron) Run()
func (c *Cron) Stop() context.Context
func (e Entry) Valid() bool

type ScheduleParser interface { Parse(string) (Schedule, error) }
type Option func(*Cron)
func WithLocation(loc *time.Location) Option
func WithSeconds() Option
func WithParser(p ScheduleParser) Option
func WithChain(wrappers ...JobWrapper) Option
func WithLogger(logger Logger) Option
```

### Parsing and next times

`ParseStandard` accepts five whitespace-separated fields in minute, hour, day
of month, month, and day of week order. Fields support numbers, named months or
weekdays, lists, inclusive ranges, `/step`, `*`, and `?` in the two day fields.
Descriptors include `@yearly`, `@annually`, `@monthly`, `@weekly`, `@daily`,
`@midnight`, `@hourly`, and `@every <time.ParseDuration>`. A `TZ=Zone` or
`CRON_TZ=Zone` prefix overrides the schedule timezone. Invalid field counts,
names, ranges, steps, descriptors, and locations return an error.

`Parser` is configured with the `ParseOption` bit flags. `Second` adds a
required seconds field; `SecondOptional` permits either a six-field form or a
five-field form; `DowOptional` permits the day-of-week field to be omitted;
`Descriptor` enables descriptors. `NewParser` must reject two optional-field
flags by panicking, as in the upstream API. `SpecSchedule.Next` returns the
first matching time strictly after the input, preserving the input location
unless the schedule explicitly names a different location. If no match is
found within the implementation's bounded search horizon it returns the zero
time.

### Constant delay and entries

`Every` rounds durations below one second up to one second and truncates
sub-second precision. `Next` adds the delay after truncating the input's
nanoseconds. `Cron` assigns positive increasing entry IDs, applies its parser
and chain options, exposes snapshots through `Entries` and `Entry`, and removes
future entries through `Remove`. A new cron uses `time.Local` and the standard
five-field parser unless options change them. `Start`, `Run`, and `Stop` must
remain safe to call, but the bridge does not depend on wall-clock execution.

### Job wrappers

`NewChain` applies wrappers in the documented outer-to-inner order. `Recover`
swallows a panic from the wrapped job and reports it through `Logger.Error`.
`DelayIfStillRunning` serializes overlapping calls, while `SkipIfStillRunning`
skips an overlapping call and reports the skip through `Logger.Info`.

## Implementation Notes

The evaluator invokes the package through a newline-delimited JSON bridge. The
bridge uses only bounded strings and arrays and returns structured errors; it
must never print diagnostics to stdout or panic on malformed requests. Keep
ordinary parsing deterministic and free of package-global mutation. Do not
hard-code evaluator examples, fetch source during a candidate run, or add
third-party dependencies. Callbacks, goroutines, and contexts are exercised
only through bounded bridge-owned probes, not serialized as user input.
