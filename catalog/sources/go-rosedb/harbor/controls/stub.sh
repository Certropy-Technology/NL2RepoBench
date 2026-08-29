#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/rosedblabs/rosedb/v2

go 1.26.5

require (
	github.com/google/btree v1.1.2
	github.com/rosedblabs/wal v1.3.8
	github.com/valyala/bytebufferpool v1.0.0
)

require (
	github.com/davecgh/go-spew v1.1.1 // indirect
	github.com/kr/text v0.2.0 // indirect
	github.com/pmezard/go-difflib v1.0.0 // indirect
	golang.org/x/sys v0.11.0 // indirect
	gopkg.in/check.v1 v1.0.0-20201130134442-10cb98267c6c // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
)

require (
	github.com/bwmarrin/snowflake v0.3.0
	github.com/gofrs/flock v0.8.1
	github.com/robfig/cron/v3 v3.0.0
	github.com/stretchr/testify v1.9.0
)
MOD
: > go.sum
mkdir -p vendor
cat > rosedb.go <<'GO'
package rosedb
import "time"
const MB int64 = 1024 * 1024
type Options struct { DirPath string; SegmentSize int64; Sync bool; BytesPerSync uint32; WatchQueueSize uint64; AutoMergeCronExpr string }
type BatchOptions struct { Sync bool; ReadOnly bool }
type IteratorOptions struct { Prefix []byte; Reverse bool; ContinueOnError bool }
type Stat struct { KeysNum int; DiskSize int64 }
type Item struct { Key []byte; Value []byte }
type DB struct{}
type Batch struct{}
type Iterator struct{}
type Event struct { Action WatchActionType; Key []byte; Value []byte; BatchId uint64 }
type WatchActionType = byte
const ( WatchActionPut WatchActionType = iota; WatchActionDelete )
type Watcher struct{}
var DefaultOptions Options
var DefaultBatchOptions = BatchOptions{Sync:true}
var DefaultIteratorOptions IteratorOptions
var ErrKeyIsEmpty = errorString("the key is empty")
var ErrKeyNotFound = errorString("key not found in database")
var ErrDatabaseIsUsing = errorString("the database directory is used by another process")
var ErrReadOnlyBatch = errorString("the batch is read only")
var ErrBatchCommitted = errorString("the batch is committed")
var ErrBatchRollbacked = errorString("the batch is rollbacked")
var ErrDBClosed = errorString("the database is closed")
var ErrMergeRunning = errorString("the merge operation is running")
var ErrWatchDisabled = errorString("the watch is disabled")
type errorString string
func (e errorString) Error() string { return string(e) }
func Open(Options) (*DB,error) { return &DB{},nil }
func (*DB) Close() error{return nil}; func (*DB) Sync() error{return nil}
func (*DB) Put([]byte,[]byte) error{return nil}; func (*DB) PutWithTTL([]byte,[]byte,time.Duration) error{return nil}
func (*DB) Get([]byte)([]byte,error){return nil,nil}; func (*DB) Delete([]byte)error{return nil}; func (*DB) Exist([]byte)(bool,error){return false,nil}
func (*DB) Expire([]byte,time.Duration)error{return nil}; func (*DB) TTL([]byte)(time.Duration,error){return -1,nil}; func (*DB) Persist([]byte)error{return nil}
func (*DB) DeleteExpiredKeys(time.Duration)error{return nil}; func (*DB) Stat()*Stat{return &Stat{}}
func (*DB) NewBatch(BatchOptions)*Batch{return &Batch{}}; func (*DB) NewIterator(IteratorOptions)*Iterator{return &Iterator{}}
func (*DB) Watch()(<-chan *Event,error){return nil,ErrWatchDisabled}; func (*DB) Merge(bool)error{return nil}
func (*DB) Ascend(func([]byte,[]byte)(bool,error)){}; func (*DB) AscendRange([]byte,[]byte,func([]byte,[]byte)(bool,error)){}
func (*DB) AscendGreaterOrEqual([]byte,func([]byte,[]byte)(bool,error)){}; func (*DB) Descend(func([]byte,[]byte)(bool,error)){}
func (*DB) DescendRange([]byte,[]byte,func([]byte,[]byte)(bool,error)){}; func (*DB) DescendLessOrEqual([]byte,func([]byte,[]byte)(bool,error)){}
func (*DB) AscendKeys([]byte,bool,func([]byte)(bool,error))error{return nil}; func (*DB) AscendKeysRange([]byte,[]byte,[]byte,bool,func([]byte)(bool,error))error{return nil}
func (*DB) DescendKeys([]byte,bool,func([]byte)(bool,error))error{return nil}; func (*DB) DescendKeysRange([]byte,[]byte,[]byte,bool,func([]byte)(bool,error))error{return nil}
func NewWatcher(uint64)*Watcher{return &Watcher{}}; func (*Watcher)Close(){}
func (*Batch)Put([]byte,[]byte)error{return nil}; func (*Batch)PutWithTTL([]byte,[]byte,time.Duration)error{return nil}; func (*Batch)Get([]byte)([]byte,error){return nil,nil}
func (*Batch)Delete([]byte)error{return nil}; func (*Batch)Exist([]byte)(bool,error){return false,nil}; func (*Batch)Expire([]byte,time.Duration)error{return nil}; func (*Batch)TTL([]byte)(time.Duration,error){return -1,nil}; func (*Batch)Persist([]byte)error{return nil}; func (*Batch)Commit()error{return nil}; func (*Batch)Rollback()error{return nil}
func (*Iterator)Rewind(){}; func (*Iterator)Seek([]byte){}; func (*Iterator)Next(){}; func (*Iterator)Valid()bool{return false}; func (*Iterator)Item()*Item{return nil}; func (*Iterator)Close(){}; func (*Iterator)Err()error{return nil}
GO
