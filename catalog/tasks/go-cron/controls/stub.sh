#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/robfig/cron/v3

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > cron.go <<'GO'
package cron
import ("context"; "time")
type ParseOption int
const (Second ParseOption = 1<<iota; SecondOptional; Minute; Hour; Dom; Month; Dow; DowOptional; Descriptor)
type Schedule interface { Next(time.Time) time.Time }
type SpecSchedule struct { Second,Minute,Hour,Dom,Month,Dow uint64; Location *time.Location }
func (*SpecSchedule) Next(time.Time) time.Time { return time.Time{} }
type ConstantDelaySchedule struct { Delay time.Duration }
func Every(time.Duration) ConstantDelaySchedule { return ConstantDelaySchedule{} }
func (ConstantDelaySchedule) Next(time.Time) time.Time { return time.Time{} }
type Parser struct{}
func NewParser(ParseOption) Parser { return Parser{} }
func (Parser) Parse(string) (Schedule,error) { return &SpecSchedule{},nil }
func ParseStandard(string) (Schedule,error) { return &SpecSchedule{},nil }
type Job interface { Run() }
type FuncJob func()
func (f FuncJob) Run() { f() }
type JobWrapper func(Job) Job
type Chain struct{}
func NewChain(...JobWrapper) Chain { return Chain{} }
func (Chain) Then(j Job) Job { return j }
type Logger interface { Info(string,...interface{}); Error(error,string,...interface{}) }
type discardLogger struct{}
func (discardLogger) Info(string,...interface{}) {}
func (discardLogger) Error(error,string,...interface{}) {}
var DefaultLogger Logger = discardLogger{}
var DiscardLogger Logger = discardLogger{}
func Recover(Logger) JobWrapper { return func(j Job) Job{return j} }
func DelayIfStillRunning(Logger) JobWrapper { return func(j Job) Job{return j} }
func SkipIfStillRunning(Logger) JobWrapper { return func(j Job) Job{return j} }
func PrintfLogger(interface{Printf(string,...interface{})}) Logger { return discardLogger{} }
func VerbosePrintfLogger(interface{Printf(string,...interface{})}) Logger { return discardLogger{} }
type EntryID int
type Entry struct { ID EntryID; Schedule Schedule; Next,Prev time.Time; WrappedJob,Job Job }
func (e Entry) Valid() bool { return e.ID != 0 }
type Option func(*Cron)
func WithLocation(*time.Location) Option { return func(*Cron){} }
func WithSeconds() Option { return func(*Cron){} }
func WithParser(ScheduleParser) Option { return func(*Cron){} }
func WithChain(...JobWrapper) Option { return func(*Cron){} }
func WithLogger(Logger) Option { return func(*Cron){} }
type ScheduleParser interface { Parse(string) (Schedule,error) }
type Cron struct { entries []Entry; next EntryID; location *time.Location }
func New(...Option) *Cron { return &Cron{location:time.UTC} }
func (c *Cron) AddFunc(string,func()) (EntryID,error) { c.next++; c.entries=append(c.entries,Entry{ID:c.next}); return c.next,nil }
func (c *Cron) AddJob(string,Job) (EntryID,error) { c.next++; c.entries=append(c.entries,Entry{ID:c.next}); return c.next,nil }
func (c *Cron) Schedule(Schedule,Job) EntryID { c.next++; c.entries=append(c.entries,Entry{ID:c.next}); return c.next }
func (c *Cron) Entries() []Entry { return append([]Entry(nil),c.entries...) }
func (c *Cron) Location() *time.Location { return c.location }
func (c *Cron) Entry(id EntryID) Entry { for _,e:=range c.entries {if e.ID==id{return e}}; return Entry{} }
func (c *Cron) Remove(id EntryID) { out:=c.entries[:0]; for _,e:=range c.entries {if e.ID!=id {out=append(out,e)}}; c.entries=out }
func (*Cron) Start() {}
func (*Cron) Run() {}
func (*Cron) Stop() context.Context { return context.Background() }
GO
