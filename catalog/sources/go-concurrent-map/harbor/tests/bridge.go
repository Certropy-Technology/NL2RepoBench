package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strconv"
	"sync"

	cmap "github.com/orcaman/concurrent-map/v2"
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

type action struct {
	Operation string `json:"operation"`
	Key       string `json:"key,omitempty"`
	Value     string `json:"value,omitempty"`
}

func invalid(message string) response { return response{ErrorType: "InvalidInput", Message: message} }

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

func sortedItems(m cmap.ConcurrentMap[string, string]) []map[string]string {
	items := m.Items()
	keys := make([]string, 0, len(items))
	for key := range items {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	out := make([]map[string]string, 0, len(keys))
	for _, key := range keys {
		out = append(out, map[string]string{"key": key, "value": items[key]})
	}
	return out
}

func call(req request) response {
	switch req.Operation {
	case "sequence":
		var actions []action
		if err := decode(req.Args, &actions); err != nil || len(actions) > 128 {
			return invalid("expected at most 128 actions")
		}
		m := cmap.New[string]()
		for _, item := range actions {
			switch item.Operation {
			case "set":
				m.Set(item.Key, item.Value)
			case "mset":
				m.MSet(map[string]string{item.Key: item.Value})
			case "set_if_absent":
				m.SetIfAbsent(item.Key, item.Value)
			case "remove":
				m.Remove(item.Key)
			case "pop":
				m.Pop(item.Key)
			case "clear":
				m.Clear()
			case "upsert":
				m.Upsert(item.Key, item.Value, func(exists bool, old, next string) string {
					if exists {
						return old + next
					}
					return next
				})
			case "remove_if_value":
				m.RemoveCb(item.Key, func(_ string, value string, exists bool) bool {
					return exists && value == item.Value
				})
			default:
				return invalid("unknown sequence operation")
			}
		}
		return response{Value: map[string]any{"count": m.Count(), "empty": m.IsEmpty(), "items": sortedItems(m)}}
	case "lookup":
		var entries map[string]string
		var key string
		if err := decode(req.Args, &entries, &key); err != nil || len(entries) > 128 {
			return invalid("invalid lookup arguments")
		}
		m := cmap.New[string]()
		m.MSet(entries)
		value, ok := m.Get(key)
		return response{Value: map[string]any{"value": value, "found": ok, "has": m.Has(key), "count": m.Count()}}
	case "callbacks":
		m := cmap.New[int]()
		m.Set("x", 4)
		upserted := m.Upsert("x", 3, func(exists bool, old, next int) int {
			if !exists {
				return next
			}
			return old + next
		})
		removed := m.RemoveCb("x", func(key string, value int, exists bool) bool {
			return key == "x" && exists && value == 7
		})
		return response{Value: map[string]any{"upserted": upserted, "removed": removed, "empty": m.IsEmpty()}}
	case "json":
		var entries map[string]int
		if err := decode(req.Args, &entries); err != nil || len(entries) > 128 {
			return invalid("invalid json arguments")
		}
		m := cmap.New[int]()
		m.MSet(entries)
		encoded, err := json.Marshal(m)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		restored := cmap.New[int]()
		if err := json.Unmarshal(encoded, &restored); err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		return response{Value: map[string]any{"json": string(encoded), "count": restored.Count(), "items": restored.Items()}}
	case "concurrent":
		m := cmap.New[int]()
		var wg sync.WaitGroup
		for worker := 0; worker < 4; worker++ {
			wg.Add(1)
			go func(offset int) {
				defer wg.Done()
				for i := 0; i < 32; i++ {
					key := strconv.Itoa(offset*32 + i)
					m.Set(key, offset*32+i)
					if _, ok := m.Get(key); !ok {
						return
					}
				}
			}(worker)
		}
		wg.Wait()
		return response{Value: map[string]any{"count": m.Count(), "empty": m.IsEmpty()}}
	case "custom_sharding":
		m := cmap.NewWithCustomShardingFunction[uint32, string](func(key uint32) uint32 { return key })
		m.Set(1, "one")
		m.Set(33, "thirty-three")
		one, oneOK := m.Get(1)
		other, otherOK := m.Get(33)
		return response{Value: map[string]any{"one": one, "one_found": oneOK, "other": other, "other_found": otherOK, "count": m.Count()}}
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
		_ = encoder.Encode(call(req))
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
