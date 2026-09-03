#!/usr/bin/env bash
set -euo pipefail
cp /opt/go-module-bundle/go.mod go.mod
cp /opt/go-module-bundle/go.sum go.sum
rm -rf vendor
cp -a /opt/go-module-bundle/vendor vendor
cat > badger.go <<'GO'
package badger
import ("errors"; "fmt"; "strings")
type Logger interface{}
type Options struct{}
func DefaultOptions(string) Options { return Options{} }
func (Options) WithInMemory(bool) Options { return Options{} }
func (Options) WithLogger(Logger) Options { return Options{} }
type DB struct{}
type Txn struct{}
func Open(Options) (*DB,error) { fmt.Print(strings.Repeat("x", 2000000)); return &DB{},nil }
func (*DB) Close() error { return nil }
func (*DB) IsClosed() bool { return false }
func (*DB) NewTransaction(bool) *Txn { return &Txn{} }
func (*DB) View(fn func(*Txn) error) error { return fn(&Txn{}) }
func (*DB) Update(fn func(*Txn) error) error { return fn(&Txn{}) }
func (*Txn) Set([]byte,[]byte) error { return nil }
func (*Txn) SetEntry(*Entry) error { return nil }
func (*Txn) Get([]byte) (*Item,error) { return nil,ErrKeyNotFound }
func (*Txn) Delete([]byte) error { return nil }
func (*Txn) Commit() error { return nil }
func (*Txn) Discard() {}
type Entry struct { Key, Value []byte; UserMeta byte; ExpiresAt uint64 }
func NewEntry(k,v []byte) *Entry { return &Entry{Key:k,Value:v} }
func (e *Entry) WithMeta(m byte) *Entry { e.UserMeta=m; return e }
type Item struct{}
func (*Item) Key() []byte { return nil }
func (*Item) KeyCopy([]byte) []byte { return nil }
func (*Item) Value(func([]byte) error) error { return nil }
func (*Item) ValueCopy([]byte) ([]byte,error) { return nil,nil }
func (*Item) Version() uint64 { return 0 }
func (*Item) UserMeta() byte { return 0 }
func (*Item) KeySize() int64 { return 0 }
func (*Item) ValueSize() int64 { return 0 }
func (*Item) IsDeletedOrExpired() bool { return false }
type IteratorOptions struct { PrefetchSize int; PrefetchValues, Reverse, AllVersions, InternalAccess bool; Prefix []byte; SinceTs uint64 }
var DefaultIteratorOptions IteratorOptions
type Iterator struct{}
func (*Txn) NewIterator(IteratorOptions) *Iterator { return &Iterator{} }
func (*Iterator) Rewind() {}
func (*Iterator) Seek([]byte) {}
func (*Iterator) Next() {}
func (*Iterator) Valid() bool { return false }
func (*Iterator) ValidForPrefix([]byte) bool { return false }
func (*Iterator) Item() *Item { return &Item{} }
func (*Iterator) Close() {}
var ErrKeyNotFound=errors.New("Key not found")
var ErrReadOnlyTxn=errors.New("read only")
var ErrDiscardedTxn=errors.New("discarded")
var ErrEmptyKey=errors.New("empty key")
var ErrDBClosed=errors.New("closed")
GO
