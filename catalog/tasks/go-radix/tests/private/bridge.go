package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	radix "github.com/armon/go-radix"
)

const (
	maxRequestBytes = 256 * 1024
	maxItems        = 64
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

type entry struct {
	Key   string `json:"key"`
	Value any    `json:"value"`
}

type snapshotRequest struct {
	Entries  []entry  `json:"entries"`
	Lookups  []string `json:"lookups"`
	Longest  []string `json:"longest"`
	Prefixes []string `json:"prefixes"`
	Paths    []string `json:"paths"`
}

type mutationRequest struct {
	Entries        []entry  `json:"entries"`
	Inserts        []entry  `json:"inserts"`
	Deletes        []string `json:"deletes"`
	DeletePrefixes []string `json:"delete_prefixes"`
}

type pair struct {
	Key   string `json:"key"`
	Value any    `json:"value"`
}

type foundValue struct {
	Value any  `json:"value"`
	Found bool `json:"found"`
}

type prefixValue struct {
	Key   string `json:"key"`
	Value any    `json:"value"`
	Found bool   `json:"found"`
}

type walkResult struct {
	Keys   []string `json:"keys"`
	Values []any    `json:"values"`
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func failed(err error) response {
	return response{ErrorType: "CallFailed", Message: err.Error()}
}

func encode(value any) response {
	payload, err := json.Marshal(value)
	if err != nil {
		return failed(err)
	}
	return response{Value: payload}
}

func decode(args []json.RawMessage, index int, target any) error {
	if index >= len(args) {
		return fmt.Errorf("missing argument %d", index)
	}
	return json.Unmarshal(args[index], target)
}

func checkItems(items ...int) error {
	for _, count := range items {
		if count > maxItems {
			return fmt.Errorf("request exceeds %d item limit", maxItems)
		}
	}
	return nil
}

func build(entries []entry, fromMap bool) *radix.Tree {
	if fromMap {
		values := make(map[string]interface{}, len(entries))
		for _, item := range entries {
			values[item.Key] = item.Value
		}
		return radix.NewFromMap(values)
	}
	tree := radix.New()
	for _, item := range entries {
		tree.Insert(item.Key, item.Value)
	}
	return tree
}

func collect(fn func(radix.WalkFn)) walkResult {
	result := walkResult{Keys: []string{}, Values: []any{}}
	fn(func(key string, value interface{}) bool {
		result.Keys = append(result.Keys, key)
		result.Values = append(result.Values, value)
		return false
	})
	return result
}

func snapshotCall(args []json.RawMessage) response {
	if len(args) != 1 {
		return invalid("snapshot expects one request")
	}
	var input snapshotRequest
	if err := decode(args, 0, &input); err != nil {
		return invalid(err.Error())
	}
	if err := checkItems(len(input.Entries), len(input.Lookups), len(input.Longest), len(input.Prefixes), len(input.Paths)); err != nil {
		return invalid(err.Error())
	}
	tree := build(input.Entries, true)
	lookups := make([]foundValue, 0, len(input.Lookups))
	for _, key := range input.Lookups {
		value, found := tree.Get(key)
		lookups = append(lookups, foundValue{Value: value, Found: found})
	}
	longest := make([]prefixValue, 0, len(input.Longest))
	for _, query := range input.Longest {
		key, value, found := tree.LongestPrefix(query)
		longest = append(longest, prefixValue{Key: key, Value: value, Found: found})
	}
	prefixes := make([]walkResult, 0, len(input.Prefixes))
	for _, prefix := range input.Prefixes {
		prefix := prefix
		prefixes = append(prefixes, collect(func(fn radix.WalkFn) { tree.WalkPrefix(prefix, fn) }))
	}
	paths := make([]walkResult, 0, len(input.Paths))
	for _, path := range input.Paths {
		path := path
		paths = append(paths, collect(func(fn radix.WalkFn) { tree.WalkPath(path, fn) }))
	}
	minimumKey, minimumValue, minimumFound := tree.Minimum()
	maximumKey, maximumValue, maximumFound := tree.Maximum()
	return encode(map[string]any{
		"len": tree.Len(), "lookups": lookups, "longest": longest,
		"minimum":  prefixValue{Key: minimumKey, Value: minimumValue, Found: minimumFound},
		"maximum":  prefixValue{Key: maximumKey, Value: maximumValue, Found: maximumFound},
		"walk":     collect(func(fn radix.WalkFn) { tree.Walk(fn) }),
		"prefixes": prefixes, "paths": paths, "map": tree.ToMap(),
	})
}

func mutationCall(args []json.RawMessage) response {
	if len(args) != 1 {
		return invalid("mutate expects one request")
	}
	var input mutationRequest
	if err := decode(args, 0, &input); err != nil {
		return invalid(err.Error())
	}
	if err := checkItems(len(input.Entries), len(input.Inserts), len(input.Deletes), len(input.DeletePrefixes)); err != nil {
		return invalid(err.Error())
	}
	tree := build(input.Entries, false)
	type insertResult struct {
		Old     any  `json:"old"`
		Updated bool `json:"updated"`
	}
	inserts := make([]insertResult, 0, len(input.Inserts))
	for _, item := range input.Inserts {
		old, updated := tree.Insert(item.Key, item.Value)
		inserts = append(inserts, insertResult{Old: old, Updated: updated})
	}
	deletes := make([]foundValue, 0, len(input.Deletes))
	for _, key := range input.Deletes {
		value, found := tree.Delete(key)
		deletes = append(deletes, foundValue{Value: value, Found: found})
	}
	prefixDeletes := make([]int, 0, len(input.DeletePrefixes))
	for _, prefix := range input.DeletePrefixes {
		prefixDeletes = append(prefixDeletes, tree.DeletePrefix(prefix))
	}
	return encode(map[string]any{
		"inserts": inserts, "deletes": deletes, "prefix_deletes": prefixDeletes,
		"len": tree.Len(), "walk": collect(func(fn radix.WalkFn) { tree.Walk(fn) }), "map": tree.ToMap(),
	})
}

func callbackCall(args []json.RawMessage) response {
	if len(args) != 1 {
		return invalid("callbacks expects one request")
	}
	var input struct {
		Entries   []entry `json:"entries"`
		StopAfter int     `json:"stop_after"`
	}
	if err := decode(args, 0, &input); err != nil {
		return invalid(err.Error())
	}
	if err := checkItems(len(input.Entries)); err != nil || input.StopAfter < 0 || input.StopAfter > maxItems {
		return invalid("invalid callback bounds")
	}
	tree := build(input.Entries, false)
	seen := []string{}
	tree.Walk(func(key string, _ interface{}) bool {
		seen = append(seen, key)
		return input.StopAfter > 0 && len(seen) >= input.StopAfter
	})
	return encode(map[string]any{"seen": seen, "len": tree.Len()})
}

func call(input request) response {
	switch input.Operation {
	case "snapshot":
		return snapshotCall(input.Args)
	case "mutate":
		return mutationCall(input.Args)
	case "callbacks":
		return callbackCall(input.Args)
	default:
		return invalid("unknown operation")
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), maxRequestBytes)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		if len(scanner.Bytes()) > maxRequestBytes {
			_ = encoder.Encode(invalid("request is too large"))
			continue
		}
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
			continue
		}
		if err := encoder.Encode(call(input)); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
