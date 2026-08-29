package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	rosedb "github.com/rosedblabs/rosedb/v2"
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

func invalid(message string) response { return response{ErrorType: "InvalidInput", Message: message} }
func failed(message string) response  { return response{ErrorType: "CallFailed", Message: message} }

func newDB(watch uint64) (*rosedb.DB, string, error) {
	dir, err := os.MkdirTemp("", "rosedb-contract-")
	if err != nil {
		return nil, "", err
	}
	opts := rosedb.DefaultOptions
	opts.DirPath = filepath.Join(dir, "db")
	opts.SegmentSize = 1 * rosedb.MB
	opts.WatchQueueSize = watch
	db, err := rosedb.Open(opts)
	if err != nil {
		_ = os.RemoveAll(dir)
		return nil, "", err
	}
	return db, dir, nil
}

func closeDB(db *rosedb.DB, dir string) {
	if db != nil {
		_ = db.Close()
	}
	_ = os.RemoveAll(dir)
}

func require(condition bool, message string) error {
	if !condition {
		return errors.New(message)
	}
	return nil
}

func basic() error {
	db, dir, err := newDB(0)
	if err != nil {
		return err
	}
	defer closeDB(db, dir)
	if err = db.Put([]byte("alpha"), []byte("one")); err != nil {
		return err
	}
	if err = db.Put([]byte("beta"), []byte("two")); err != nil {
		return err
	}
	value, err := db.Get([]byte("alpha"))
	if err != nil || string(value) != "one" {
		return fmt.Errorf("get alpha: %v %q", err, value)
	}
	exists, err := db.Exist([]byte("beta"))
	if err != nil || !exists {
		return fmt.Errorf("exist beta: %v %v", err, exists)
	}
	if err = db.Delete([]byte("beta")); err != nil {
		return err
	}
	if _, err = db.Get([]byte("beta")); !errors.Is(err, rosedb.ErrKeyNotFound) {
		return fmt.Errorf("deleted key error: %v", err)
	}
	if err = db.Sync(); err != nil {
		return err
	}
	if err = db.Close(); err != nil {
		return err
	}
	db = nil
	opts := rosedb.DefaultOptions
	opts.DirPath = filepath.Join(dir, "db")
	opts.SegmentSize = 1 * rosedb.MB
	db, err = rosedb.Open(opts)
	if err != nil {
		return err
	}
	defer func() { closeDB(db, dir) }()
	value, err = db.Get([]byte("alpha"))
	if err != nil || string(value) != "one" {
		return fmt.Errorf("reopen alpha: %v %q", err, value)
	}
	stat := db.Stat()
	return require(stat.KeysNum == 1, fmt.Sprintf("unexpected key count %d", stat.KeysNum))
}

func batch() error {
	db, dir, err := newDB(0)
	if err != nil {
		return err
	}
	defer closeDB(db, dir)
	b := db.NewBatch(rosedb.DefaultBatchOptions)
	if err = b.Put([]byte("b:2"), []byte("two")); err != nil {
		return err
	}
	if err = b.Put([]byte("b:1"), []byte("one")); err != nil {
		return err
	}
	value, err := b.Get([]byte("b:1"))
	if err != nil || string(value) != "one" {
		return fmt.Errorf("pending read: %v %q", err, value)
	}
	if err = b.Delete([]byte("b:2")); err != nil {
		return err
	}
	if err = b.Commit(); err != nil {
		return err
	}
	exists, err := db.Exist([]byte("b:1"))
	if err != nil || !exists {
		return fmt.Errorf("committed key: %v %v", err, exists)
	}
	exists, err = db.Exist([]byte("b:2"))
	if err != nil || exists {
		return fmt.Errorf("deleted key: %v %v", err, exists)
	}
	rollback := db.NewBatch(rosedb.DefaultBatchOptions)
	if err = rollback.Put([]byte("transient"), []byte("value")); err != nil {
		return err
	}
	if err = rollback.Rollback(); err != nil {
		return err
	}
	_, err = db.Get([]byte("transient"))
	return require(errors.Is(err, rosedb.ErrKeyNotFound), fmt.Sprintf("rollback error: %v", err))
}

func iterator() error {
	db, dir, err := newDB(0)
	if err != nil {
		return err
	}
	defer closeDB(db, dir)
	for _, entry := range [][2]string{{"a:2", "two"}, {"b:1", "b"}, {"a:1", "one"}, {"a:3", "three"}} {
		if err = db.Put([]byte(entry[0]), []byte(entry[1])); err != nil {
			return err
		}
	}
	it := db.NewIterator(rosedb.IteratorOptions{Prefix: []byte("a:")})
	defer it.Close()
	var keys []string
	for it.Rewind(); it.Valid(); it.Next() {
		keys = append(keys, string(it.Item().Key))
	}
	if err = require(strings.Join(keys, ",") == "a:1,a:2,a:3", fmt.Sprintf("prefix order %v", keys)); err != nil {
		return err
	}
	it.Close()
	reverse := db.NewIterator(rosedb.IteratorOptions{Reverse: true})
	defer reverse.Close()
	reverse.Seek([]byte("a:2"))
	if err = require(reverse.Valid() && string(reverse.Item().Key) == "a:2", "reverse seek"); err != nil {
		return err
	}
	reverse.Next()
	return require(reverse.Valid() && string(reverse.Item().Key) == "a:1", "reverse next")
}

func ttl() error {
	db, dir, err := newDB(0)
	if err != nil {
		return err
	}
	defer closeDB(db, dir)
	if err = db.PutWithTTL([]byte("short"), []byte("value"), 25*time.Millisecond); err != nil {
		return err
	}
	remaining, err := db.TTL([]byte("short"))
	if err != nil || remaining <= 0 || remaining > 25*time.Millisecond {
		return fmt.Errorf("ttl %v %v", remaining, err)
	}
	time.Sleep(45 * time.Millisecond)
	if _, err = db.Get([]byte("short")); !errors.Is(err, rosedb.ErrKeyNotFound) {
		return fmt.Errorf("expired get: %v", err)
	}
	if err = db.PutWithTTL([]byte("persistent"), []byte("value"), time.Second); err != nil {
		return err
	}
	if err = db.Persist([]byte("persistent")); err != nil {
		return err
	}
	remaining, err = db.TTL([]byte("persistent"))
	return require(err == nil && remaining == -1, fmt.Sprintf("persist ttl %v %v", remaining, err))
}

func scans() error {
	db, dir, err := newDB(0)
	if err != nil {
		return err
	}
	defer closeDB(db, dir)
	for _, key := range []string{"apple", "banana", "cherry", "date", "grape"} {
		if err = db.Put([]byte(key), []byte("v-"+key)); err != nil {
			return err
		}
	}
	var asc []string
	db.Ascend(func(key, value []byte) (bool, error) { asc = append(asc, string(key)); return true, nil })
	if err = require(strings.Join(asc, ",") == "apple,banana,cherry,date,grape", fmt.Sprintf("asc %v", asc)); err != nil {
		return err
	}
	var desc []string
	db.DescendRange([]byte("grape"), []byte("cherry"), func(key, value []byte) (bool, error) { desc = append(desc, string(key)); return true, nil })
	if err = require(strings.Join(desc, ",") == "grape,date", fmt.Sprintf("desc range %v", desc)); err != nil {
		return err
	}
	var matched []string
	err = db.AscendKeys([]byte(`^b`), false, func(key []byte) (bool, error) { matched = append(matched, string(key)); return true, nil })
	return require(err == nil && strings.Join(matched, ",") == "banana", fmt.Sprintf("keys %v %v", matched, err))
}

func watch() error {
	db, dir, err := newDB(8)
	if err != nil {
		return err
	}
	defer closeDB(db, dir)
	channel, err := db.Watch()
	if err != nil {
		return err
	}
	if err = db.Put([]byte("watched"), []byte("value")); err != nil {
		return err
	}
	select {
	case event := <-channel:
		if event.Action != rosedb.WatchActionPut || string(event.Key) != "watched" || string(event.Value) != "value" {
			return fmt.Errorf("put event %#v", event)
		}
	case <-time.After(2 * time.Second):
		return errors.New("put watch timeout")
	}
	if err = db.Delete([]byte("watched")); err != nil {
		return err
	}
	select {
	case event := <-channel:
		if event.Action != rosedb.WatchActionDelete || string(event.Key) != "watched" || len(event.Value) != 0 {
			return fmt.Errorf("delete event %#v", event)
		}
	case <-time.After(2 * time.Second):
		return errors.New("delete watch timeout")
	}
	return nil
}

func run(operation string) error {
	switch operation {
	case "basic":
		return basic()
	case "batch":
		return batch()
	case "iterator":
		return iterator()
	case "ttl":
		return ttl()
	case "scans":
		return scans()
	case "watch":
		return watch()
	default:
		return fmt.Errorf("unknown operation %q", operation)
	}
}

func handle(input request) (result response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			result = failed(fmt.Sprintf("panic: %v", recovered))
		}
	}()
	if len(input.Args) != 0 {
		return invalid("suite operations take no arguments")
	}
	if err := run(input.Operation); err != nil {
		return failed(err.Error())
	}
	return response{Value: input.Operation + "-ok"}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 1024), 16*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
			continue
		}
		if err := encoder.Encode(handle(input)); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
