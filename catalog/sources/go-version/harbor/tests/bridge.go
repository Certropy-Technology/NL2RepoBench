package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"

	version "github.com/hashicorp/go-version"
)

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     any    `json:"value,omitempty"`
	ErrorType string `json:"error_type,omitempty"`
	Message   string `json:"message,omitempty"`
}

type snapshotValue struct {
	String     string  `json:"string"`
	Original   string  `json:"original"`
	Prefix     string  `json:"prefix"`
	Metadata   string  `json:"metadata"`
	Prerelease string  `json:"prerelease"`
	Segments   []int64 `json:"segments"`
}

func decode(args []json.RawMessage, values ...any) error {
	if len(args) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for i, value := range values {
		if err := json.Unmarshal(args[i], value); err != nil {
			return fmt.Errorf("argument %d: %w", i, err)
		}
	}
	return nil
}

func parse(text string, strict bool, prefix string) (*version.Version, error) {
	if strict {
		return version.NewSemver(text)
	}
	if prefix == "" {
		return version.NewVersion(text)
	}
	return version.NewVersion(text, version.WithPrefix(prefix))
}

func snap(v *version.Version) snapshotValue {
	return snapshotValue{String: v.String(), Original: v.Original(), Prefix: v.Prefix(), Metadata: v.Metadata(), Prerelease: v.Prerelease(), Segments: v.Segments64()}
}

func call(req request) response {
	switch req.Operation {
	case "parse":
		var text string
		var strict bool
		var prefix string
		if err := decode(req.Args, &text, &strict, &prefix); err != nil { return invalid(err) }
		v, err := parse(text, strict, prefix)
		if err != nil { return failed(err) }
		return response{Value: snap(v)}
	case "compare":
		var left, right string
		if err := decode(req.Args, &left, &right); err != nil { return invalid(err) }
		l, err := version.NewVersion(left); if err != nil { return failed(err) }
		r, err := version.NewVersion(right); if err != nil { return failed(err) }
		return response{Value: l.Compare(r)}
	case "core":
		var text string
		if err := decode(req.Args, &text); err != nil { return invalid(err) }
		v, err := version.NewVersion(text); if err != nil { return failed(err) }
		return response{Value: snap(v.Core())}
	case "constraint_check":
		var text, candidate string
		if err := decode(req.Args, &text, &candidate); err != nil { return invalid(err) }
		c, err := version.NewConstraint(text); if err != nil { return failed(err) }
		v, err := version.NewVersion(candidate); if err != nil { return failed(err) }
		return response{Value: c.Check(v)}
	case "constraint_string":
		var text string
		if err := decode(req.Args, &text); err != nil { return invalid(err) }
		c, err := version.NewConstraint(text); if err != nil { return failed(err) }
		return response{Value: c.String()}
	case "sort":
		var values []string
		if err := decode(req.Args, &values); err != nil { return invalid(err) }
		if len(values) > 64 { return invalid(fmt.Errorf("too many versions")) }
		collection := make(version.Collection, 0, len(values))
		for _, text := range values { v, err := version.NewVersion(text); if err != nil { return failed(err) }; collection = append(collection, v) }
		sort.Sort(collection)
		out := make([]string, len(collection)); for i, v := range collection { out[i] = v.String() }
		return response{Value: out}
	default:
		return invalid(fmt.Errorf("unknown operation"))
	}
}

func invalid(err error) response { return response{ErrorType: "InvalidInput", Message: err.Error()} }
func failed(err error) response { return response{ErrorType: "CallFailed", Message: err.Error()} }

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var req request
		if err := json.Unmarshal(scanner.Bytes(), &req); err != nil { _ = encoder.Encode(invalid(err)); continue }
		if err := encoder.Encode(call(req)); err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(1) }
	}
	if err := scanner.Err(); err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(1) }
}
