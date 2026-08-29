package fastjson

import (
	"errors"
	"strings"
	"time"
)

const MaxDepth = 300

type Type int

const (
	TypeNull Type = iota
	TypeObject
	TypeArray
	TypeString
	TypeNumber
	TypeTrue
	TypeFalse
)

func (t Type) String() string {
	values := []string{"null", "object", "array", "string", "number", "true", "false"}
	if int(t) < 0 || int(t) >= len(values) {
		return "unknown"
	}
	return values[t]
}

type Value struct {
	typeValue Type
}

type Object struct{}
type Parser struct{}
type ParserPool struct{}
type Scanner struct{}
type Arena struct{}
type ArenaPool struct{}

func controlledValue() *Value {
	switch controlMode {
	case "panic":
		panic("control panic")
	case "hang":
		time.Sleep(60 * time.Second)
	}
	return &Value{typeValue: TypeString}
}

func Parse(string) (*Value, error)                { return controlledValue(), nil }
func ParseBytes([]byte) (*Value, error)           { return controlledValue(), nil }
func MustParse(string) *Value                     { return controlledValue() }
func MustParseBytes([]byte) *Value                { return controlledValue() }
func Validate(string) error                       { return nil }
func ValidateBytes([]byte) error                  { return nil }
func Exists([]byte, ...string) bool               { return true }
func GetString([]byte, ...string) string          { return "forged" }
func GetBytes([]byte, ...string) []byte           { return []byte("forged") }
func GetInt([]byte, ...string) int                { return 999 }
func GetFloat64([]byte, ...string) float64        { return 999 }
func GetBool([]byte, ...string) bool              { return true }
func (*Parser) Parse(string) (*Value, error)      { return controlledValue(), nil }
func (*Parser) ParseBytes([]byte) (*Value, error) { return controlledValue(), nil }
func (*ParserPool) Get() *Parser                  { return &Parser{} }
func (*ParserPool) Put(*Parser)                   {}
func (*Scanner) Init(string)                      {}
func (*Scanner) InitBytes([]byte)                 {}
func (*Scanner) Next() bool                       { return false }
func (*Scanner) Value() *Value                    { return controlledValue() }
func (*Scanner) Error() error                     { return nil }
func (v *Value) Type() Type                       { return v.typeValue }
func (*Value) String() string                     { return "forged" }
func (*Value) StringBytes() ([]byte, error) {
	if controlMode == "oversized" {
		return []byte(strings.Repeat("x", 2*1024*1024)), nil
	}
	return []byte("forged"), nil
}
func (*Value) Bool() (bool, error)       { return true, nil }
func (*Value) Int() (int, error)         { return 999, nil }
func (*Value) Int64() (int64, error)     { return 999, nil }
func (*Value) Uint() (uint, error)       { return 999, nil }
func (*Value) Uint64() (uint64, error)   { return 999, nil }
func (*Value) Float64() (float64, error) { return 999, nil }
func (*Value) Object() (*Object, error)  { return &Object{}, nil }
func (*Value) Array() ([]*Value, error)  { return []*Value{}, nil }
func (*Value) MarshalTo(dst []byte) []byte {
	if controlMode == "oversized" {
		return append(dst, strings.Repeat("x", 2*1024*1024)...)
	}
	return append(dst, `"forged"`...)
}
func (*Value) Get(...string) *Value            { return nil }
func (*Value) Exists(...string) bool           { return true }
func (*Value) GetStringBytes(...string) []byte { return []byte("forged") }
func (*Value) GetInt(...string) int            { return 999 }
func (*Value) GetInt64(...string) int64        { return 999 }
func (*Value) GetUint(...string) uint          { return 999 }
func (*Value) GetUint64(...string) uint64      { return 999 }
func (*Value) GetFloat64(...string) float64    { return 999 }
func (*Value) GetBool(...string) bool          { return true }
func (*Value) GetObject(...string) *Object     { return &Object{} }
func (*Value) GetArray(...string) []*Value     { return []*Value{} }
func (*Value) Set(string, *Value)              {}
func (*Value) SetArrayItem(int, *Value)        {}
func (*Value) Del(string)                      {}
func (*Object) Get(string) *Value              { return nil }
func (*Object) Len() int                       { return 0 }
func (*Object) Visit(func([]byte, *Value))     {}
func (*Object) Set(string, *Value)             {}
func (*Object) Del(string)                     {}
func (*Object) MarshalTo(dst []byte) []byte    { return append(dst, `{}`...) }
func (*Object) String() string                 { return "{}" }
func (*Arena) NewObject() *Value               { return &Value{typeValue: TypeObject} }
func (*Arena) NewArray() *Value                { return &Value{typeValue: TypeArray} }
func (*Arena) NewString(string) *Value         { return &Value{typeValue: TypeString} }
func (*Arena) NewStringBytes([]byte) *Value    { return &Value{typeValue: TypeString} }
func (*Arena) NewNumberFloat64(float64) *Value { return &Value{typeValue: TypeNumber} }
func (*Arena) NewNumberInt(int) *Value         { return &Value{typeValue: TypeNumber} }
func (*Arena) NewNumberString(string) *Value   { return &Value{typeValue: TypeNumber} }
func (*Arena) NewNull() *Value                 { return &Value{typeValue: TypeNull} }
func (*Arena) NewTrue() *Value                 { return &Value{typeValue: TypeTrue} }
func (*Arena) NewFalse() *Value                { return &Value{typeValue: TypeFalse} }
func (*Arena) Reset()                          {}
func (*ArenaPool) Get() *Arena                 { return &Arena{} }
func (*ArenaPool) Put(*Arena)                  {}

var _ = errors.New
