#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/hashicorp/go-cleanhttp

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > cleanhttp.go <<'GO'
package cleanhttp

import (
    "net/http"
    "os"
)

type HandlerInput struct{ ErrStatus int }
func DefaultTransport() *http.Transport { _, _ = os.Stdout.Write(make([]byte, 512*1024)); return &http.Transport{} }
func DefaultPooledTransport() *http.Transport { return &http.Transport{} }
func DefaultClient() *http.Client { return &http.Client{} }
func DefaultPooledClient() *http.Client { return &http.Client{} }
func PrintablePathCheckHandler(next http.Handler, _ *HandlerInput) http.Handler { return next }
GO
