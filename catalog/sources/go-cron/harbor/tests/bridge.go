package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sync"
	"time"

	cron "github.com/robfig/cron/v3"
)

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     json.RawMessage `json:"value,omitempty"`
	ErrorType string          `json:"error_type,omitempty"`
	Message   string          `json:"message,omitempty"`
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func decode[T any](args []json.RawMessage, index int, target *T) *response {
	if index >= len(args) {
		r := invalid("missing argument")
		return &r
	}
	if err := json.Unmarshal(args[index], target); err != nil {
		r := invalid(err.Error())
		return &r
	}
	return nil
}

func encode(value any) response {
	data, err := json.Marshal(value)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: data}
}

func locationFor(name string) (*time.Location, *response) {
	if name == "" {
		return time.UTC, nil
	}
	loc, err := time.LoadLocation(name)
	if err != nil {
		r := response{ErrorType: "InvalidInput", Message: err.Error()}
		return nil, &r
	}
	return loc, nil
}

func parseOptions(names []string) (cron.ParseOption, *response) {
	options := map[string]cron.ParseOption{
		"Second": cron.Second, "SecondOptional": cron.SecondOptional,
		"Minute": cron.Minute, "Hour": cron.Hour, "Dom": cron.Dom,
		"Month": cron.Month, "Dow": cron.Dow, "DowOptional": cron.DowOptional,
		"Descriptor": cron.Descriptor,
	}
	var result cron.ParseOption
	for _, name := range names {
		option, ok := options[name]
		if !ok {
			r := invalid("unknown parser option")
			return 0, &r
		}
		result |= option
	}
	return result, nil
}

type scheduleView struct {
	Kind     string   `json:"kind"`
	Next     string   `json:"next"`
	Fields   []uint64 `json:"fields,omitempty"`
	Location string   `json:"location,omitempty"`
	DelayNS  int64    `json:"delay_ns,omitempty"`
}

func inspectSchedule(schedule cron.Schedule, start time.Time) scheduleView {
	view := scheduleView{Kind: "unknown", Next: schedule.Next(start).Format(time.RFC3339Nano)}
	switch value := schedule.(type) {
	case *cron.SpecSchedule:
		view.Kind = "spec"
		view.Fields = []uint64{value.Second, value.Minute, value.Hour, value.Dom, value.Month, value.Dow}
		if value.Location != nil {
			view.Location = value.Location.String()
		}
	case cron.ConstantDelaySchedule:
		view.Kind = "constant-delay"
		view.DelayNS = int64(value.Delay)
	}
	return view
}

func parseNext(args []json.RawMessage) response {
	if len(args) != 4 {
		return invalid("parse_next expects spec, start, options, and location")
	}
	var spec, startText, location string
	var optionNames []string
	for i, target := range []any{&spec, &startText, &optionNames, &location} {
		if err := json.Unmarshal(args[i], target); err != nil {
			return invalid(err.Error())
		}
	}
	loc, errResponse := locationFor(location)
	if errResponse != nil {
		return *errResponse
	}
	start, err := time.Parse(time.RFC3339Nano, startText)
	if err != nil {
		return invalid(err.Error())
	}
	start = start.In(loc)
	options, errResponse := parseOptions(optionNames)
	if errResponse != nil {
		return *errResponse
	}
	oldLocal := time.Local
	time.Local = loc
	defer func() { time.Local = oldLocal }()
	var schedule cron.Schedule
	if len(optionNames) == 0 {
		schedule, err = cron.ParseStandard(spec)
	} else {
		defer func() {
			if recover() != nil {
				err = fmt.Errorf("parser construction panicked")
			}
		}()
		parser := cron.NewParser(options)
		schedule, err = parser.Parse(spec)
	}
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return encode(inspectSchedule(schedule, start))
}

func everyNext(args []json.RawMessage) response {
	if len(args) != 2 {
		return invalid("every_next expects duration and start")
	}
	var durationText, startText string
	if err := json.Unmarshal(args[0], &durationText); err != nil {
		return invalid(err.Error())
	}
	if err := json.Unmarshal(args[1], &startText); err != nil {
		return invalid(err.Error())
	}
	duration, err := time.ParseDuration(durationText)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	start, err := time.Parse(time.RFC3339Nano, startText)
	if err != nil {
		return invalid(err.Error())
	}
	schedule := cron.Every(duration)
	return encode(inspectSchedule(schedule, start))
}

func cronEntries(args []json.RawMessage) response {
	if len(args) != 3 {
		return invalid("cron_entries expects location, specs, and seconds")
	}
	var location string
	var specs []string
	var seconds bool
	if err := json.Unmarshal(args[0], &location); err != nil {
		return invalid(err.Error())
	}
	if err := json.Unmarshal(args[1], &specs); err != nil {
		return invalid(err.Error())
	}
	if err := json.Unmarshal(args[2], &seconds); err != nil {
		return invalid(err.Error())
	}
	loc, errResponse := locationFor(location)
	if errResponse != nil {
		return *errResponse
	}
	opts := []cron.Option{cron.WithLocation(loc), cron.WithLogger(cron.DiscardLogger)}
	if seconds {
		opts = append(opts, cron.WithSeconds())
	}
	c := cron.New(opts...)
	ids := make([]cron.EntryID, 0, len(specs))
	for _, spec := range specs {
		id, err := c.AddFunc(spec, func() {})
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		ids = append(ids, id)
	}
	before := c.Entries()
	lookupValid := make([]bool, 0, len(ids)+1)
	for _, id := range ids {
		lookupValid = append(lookupValid, c.Entry(id).Valid())
	}
	lookupValid = append(lookupValid, c.Entry(999999).Valid())
	removed := false
	if len(ids) > 0 {
		c.Remove(ids[0])
		removed = !c.Entry(ids[0]).Valid()
	}
	return encode(map[string]any{
		"location": c.Location().String(), "ids": ids, "before": len(before),
		"after_remove": len(c.Entries()), "lookup_valid": lookupValid,
		"removed": removed,
	})
}

type recordingLogger struct {
	mu     sync.Mutex
	infos  int
	errors int
}

func (l *recordingLogger) Info(string, ...interface{}) {
	l.mu.Lock()
	l.infos++
	l.mu.Unlock()
}

func (l *recordingLogger) Error(error, string, ...interface{}) {
	l.mu.Lock()
	l.errors++
	l.mu.Unlock()
}

func (l *recordingLogger) counts() (int, int) {
	l.mu.Lock()
	defer l.mu.Unlock()
	return l.infos, l.errors
}

func chainRecover() response {
	logger := &recordingLogger{}
	job := cron.NewChain(cron.Recover(logger)).Then(cron.FuncJob(func() { panic("boom") }))
	job.Run()
	infos, errors := logger.counts()
	return encode(map[string]int{"infos": infos, "errors": errors})
}

func chainSkip() response {
	logger := &recordingLogger{}
	started := make(chan struct{})
	release := make(chan struct{})
	count := 0
	var mu sync.Mutex
	job := cron.FuncJob(func() {
		mu.Lock()
		count++
		mu.Unlock()
		select {
		case <-started:
		default:
			close(started)
		}
		<-release
	})
	wrapped := cron.SkipIfStillRunning(logger)(job)
	var first sync.WaitGroup
	first.Add(1)
	go func() { defer first.Done(); wrapped.Run() }()
	<-started
	wrapped.Run()
	close(release)
	first.Wait()
	infos, errors := logger.counts()
	mu.Lock()
	defer mu.Unlock()
	return encode(map[string]int{"count": count, "infos": infos, "errors": errors})
}

func chainDelay() response {
	logger := &recordingLogger{}
	started := make(chan struct{})
	release := make(chan struct{})
	count := 0
	var mu sync.Mutex
	job := cron.FuncJob(func() {
		mu.Lock()
		count++
		mu.Unlock()
		select {
		case <-started:
		default:
			close(started)
		}
		<-release
	})
	wrapped := cron.DelayIfStillRunning(logger)(job)
	var runs sync.WaitGroup
	runs.Add(2)
	go func() { defer runs.Done(); wrapped.Run() }()
	<-started
	go func() { defer runs.Done(); wrapped.Run() }()
	close(release)
	runs.Wait()
	infos, errors := logger.counts()
	mu.Lock()
	defer mu.Unlock()
	return encode(map[string]int{"count": count, "infos": infos, "errors": errors})
}

func call(req request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = response{ErrorType: "CallFailed", Message: fmt.Sprintf("panic: %v", recovered)}
		}
	}()
	switch req.Operation {
	case "parse_next":
		return parseNext(req.Args)
	case "every_next":
		return everyNext(req.Args)
	case "cron_entries":
		return cronEntries(req.Args)
	case "chain_recover":
		if len(req.Args) != 0 {
			return invalid("chain_recover expects no arguments")
		}
		return chainRecover()
	case "chain_skip":
		if len(req.Args) != 0 {
			return invalid("chain_skip expects no arguments")
		}
		return chainSkip()
	case "chain_delay":
		if len(req.Args) != 0 {
			return invalid("chain_delay expects no arguments")
		}
		return chainDelay()
	default:
		return invalid("unknown operation")
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var req request
		if err := json.Unmarshal(scanner.Bytes(), &req); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
			continue
		}
		if err := encoder.Encode(call(req)); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
