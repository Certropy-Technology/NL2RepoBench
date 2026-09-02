#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/DATA-DOG/go-sqlmock

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > sqlmock.go <<'GO'
package sqlmock

import "database/sql/driver"

type SqlMockOption func(*sqlmock) error
type sqlmock struct{}
type Argument interface{ Match(driver.Value) bool }
type anyArgument struct{}
func (anyArgument) Match(driver.Value) bool { return true }
func AnyArg() Argument { return anyArgument{} }
GO
