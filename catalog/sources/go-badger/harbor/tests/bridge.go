package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"os"

	badger "github.com/dgraph-io/badger/v4"
)

const (
	maxRecords = 64
	maxField   = 4096
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

type record struct {
	Key   string `json:"key"`
	Value string `json:"value"`
	Meta  byte   `json:"meta"`
}

type itemView struct {
	Key     string `json:"key"`
	Value   string `json:"value"`
	Meta    byte   `json:"meta"`
	Version uint64 `json:"version"`
	KeySize int64  `json:"key_size"`
	ValSize int64  `json:"value_size"`
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 512*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			write(encoder, response{ErrorType: "InvalidInput", Message: err.Error()})
			continue
		}
		write(encoder, safeCall(input))
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func safeCall(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = response{ErrorType: "CallFailed", Message: fmt.Sprint(recovered)}
		}
	}()
	return call(input)
}

func call(input request) response {
	switch input.Operation {
	case "put_get":
		var records []record
		var key string
		if err := decodeArgs(input.Args, &records, &key); err != nil {
			return invalid(err)
		}
		if err := validateRecords(records); err != nil || len(key) > maxField {
			return invalid(firstError(err, "key exceeds 4096 bytes"))
		}
		db, err := openMemory()
		if err != nil {
			return failed(err)
		}
		defer db.Close()
		if err := db.Update(func(txn *badger.Txn) error {
			for _, item := range records {
				if err := txn.SetEntry(badger.NewEntry([]byte(item.Key), []byte(item.Value)).WithMeta(item.Meta)); err != nil {
					return err
				}
			}
			return nil
		}); err != nil {
			return failed(err)
		}
		var view itemView
		err = db.View(func(txn *badger.Txn) error {
			item, getErr := txn.Get([]byte(key))
			if getErr != nil {
				return getErr
			}
			view, getErr = snapshot(item)
			return getErr
		})
		if err != nil {
			return failed(err)
		}
		return response{Value: view}
	case "scan":
		var records []record
		var prefix string
		var reverse bool
		if err := decodeArgs(input.Args, &records, &prefix, &reverse); err != nil {
			return invalid(err)
		}
		if err := validateRecords(records); err != nil {
			return invalid(err)
		}
		if len(prefix) > maxField {
			return invalid(errors.New("prefix exceeds 4096 bytes"))
		}
		db, err := openMemory()
		if err != nil {
			return failed(err)
		}
		defer db.Close()
		if err := db.Update(func(txn *badger.Txn) error {
			for _, item := range records {
				if err := txn.SetEntry(badger.NewEntry([]byte(item.Key), []byte(item.Value)).WithMeta(item.Meta)); err != nil {
					return err
				}
			}
			return nil
		}); err != nil {
			return failed(err)
		}
		var views []itemView
		err = db.View(func(txn *badger.Txn) error {
			options := badger.DefaultIteratorOptions
			options.Reverse = reverse
			options.Prefix = []byte(prefix)
			iterator := txn.NewIterator(options)
			defer iterator.Close()
			for iterator.Rewind(); iterator.Valid(); iterator.Next() {
				view, itemErr := snapshot(iterator.Item())
				if itemErr != nil {
					return itemErr
				}
				views = append(views, view)
			}
			return nil
		})
		if err != nil {
			return failed(err)
		}
		return response{Value: views}
	case "transaction":
		return transactionReport()
	case "errors":
		return errorReport()
	default:
		return invalid(errors.New("unknown operation"))
	}
}

func openMemory() (*badger.DB, error) {
	options := badger.DefaultOptions("").WithInMemory(true).WithLogger(nil)
	return badger.Open(options)
}

func snapshot(item *badger.Item) (itemView, error) {
	var callbackValue []byte
	if err := item.Value(func(value []byte) error {
		callbackValue = append([]byte(nil), value...)
		return nil
	}); err != nil {
		return itemView{}, err
	}
	value, err := item.ValueCopy(nil)
	if err != nil {
		return itemView{}, err
	}
	if string(callbackValue) != string(value) {
		return itemView{}, errors.New("Value callback and ValueCopy disagree")
	}
	return itemView{
		Key: string(item.KeyCopy(nil)), Value: string(value), Meta: item.UserMeta(),
		Version: item.Version(), KeySize: item.KeySize(), ValSize: item.ValueSize(),
	}, nil
}

func transactionReport() response {
	db, err := openMemory()
	if err != nil {
		return failed(err)
	}
	defer db.Close()
	report := map[string]bool{}
	txn := db.NewTransaction(true)
	if err := txn.Set([]byte("staged"), []byte("discarded")); err != nil {
		return failed(err)
	}
	item, err := txn.Get([]byte("staged"))
	report["read_your_write"] = err == nil && item != nil
	txn.Discard()
	report["discard_hides_write"] = errors.Is(db.View(func(view *badger.Txn) error {
		_, getErr := view.Get([]byte("staged"))
		return getErr
	}), badger.ErrKeyNotFound)
	callbackErr := errors.New("rollback")
	report["update_propagates_error"] = errors.Is(db.Update(func(update *badger.Txn) error {
		if setErr := update.Set([]byte("rolled-back"), []byte("value")); setErr != nil {
			return setErr
		}
		return callbackErr
	}), callbackErr)
	report["rollback_hides_write"] = errors.Is(db.View(func(view *badger.Txn) error {
		_, getErr := view.Get([]byte("rolled-back"))
		return getErr
	}), badger.ErrKeyNotFound)
	if err := db.Update(func(update *badger.Txn) error {
		return update.Set([]byte("committed"), []byte("value"))
	}); err != nil {
		return failed(err)
	}
	report["commit_visible"] = db.View(func(view *badger.Txn) error {
		_, getErr := view.Get([]byte("committed"))
		return getErr
	}) == nil
	if err := db.Update(func(update *badger.Txn) error {
		return update.Delete([]byte("committed"))
	}); err != nil {
		return failed(err)
	}
	report["delete_hides_write"] = errors.Is(db.View(func(view *badger.Txn) error {
		_, getErr := view.Get([]byte("committed"))
		return getErr
	}), badger.ErrKeyNotFound)
	return response{Value: report}
}

func errorReport() response {
	db, err := openMemory()
	if err != nil {
		return failed(err)
	}
	defer db.Close()
	report := map[string]bool{}
	report["empty_key"] = errors.Is(db.Update(func(txn *badger.Txn) error {
		return txn.Set(nil, []byte("value"))
	}), badger.ErrEmptyKey)
	report["missing_key"] = errors.Is(db.View(func(txn *badger.Txn) error {
		_, getErr := txn.Get([]byte("missing"))
		return getErr
	}), badger.ErrKeyNotFound)
	report["read_only_write"] = errors.Is(db.View(func(txn *badger.Txn) error {
		return txn.Set([]byte("key"), []byte("value"))
	}), badger.ErrReadOnlyTxn)
	txn := db.NewTransaction(true)
	txn.Discard()
	report["discarded_txn"] = errors.Is(txn.Set([]byte("key"), []byte("value")), badger.ErrDiscardedTxn)
	return response{Value: report}
}

func validateRecords(records []record) error {
	if len(records) > maxRecords {
		return errors.New("too many records")
	}
	for _, item := range records {
		if len(item.Key) == 0 {
			return errors.New("record key is empty")
		}
		if len(item.Key) > maxField || len(item.Value) > maxField {
			return errors.New("record field exceeds 4096 bytes")
		}
	}
	return nil
}

func decodeArgs(raw []json.RawMessage, values ...any) error {
	if len(raw) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for index, value := range values {
		if err := json.Unmarshal(raw[index], value); err != nil {
			return fmt.Errorf("argument %d: %w", index, err)
		}
	}
	return nil
}

func firstError(err error, fallback string) error {
	if err != nil {
		return err
	}
	return errors.New(fallback)
}

func invalid(err error) response { return response{ErrorType: "InvalidInput", Message: err.Error()} }
func failed(err error) response  { return response{ErrorType: "CallFailed", Message: err.Error()} }

func write(encoder *json.Encoder, value response) {
	if err := encoder.Encode(value); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
