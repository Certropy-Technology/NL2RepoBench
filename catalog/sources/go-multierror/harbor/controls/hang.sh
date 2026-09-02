#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/hashicorp/go-multierror
go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > multierror.go <<'GO'
package multierror
import("errors";"time")
type Error struct{Errors []error;ErrorFormat ErrorFormatFunc};type ErrorFormatFunc func([]error)string
func(*Error)Error()string{time.Sleep(60*time.Second);return ""};func(*Error)ErrorOrNil()error{return nil};func(*Error)WrappedErrors()[]error{return nil};func(*Error)Unwrap()error{return nil};func(*Error)Len()int{return 0};func(Error)Swap(int,int){};func(Error)Less(int,int)bool{return false};func ListFormatFunc([]error)string{return ""};func Append(error,...error)*Error{return &Error{Errors:[]error{errors.New("x")}}};func Flatten(error)error{return &Error{}};func Prefix(error,string)error{return &Error{}};type Group struct{};func(*Group)Go(func()error){};func(*Group)Wait()*Error{return nil}
GO
