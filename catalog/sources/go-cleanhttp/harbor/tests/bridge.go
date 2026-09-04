package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"runtime"

	cleanhttp "github.com/hashicorp/go-cleanhttp"
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

type transportState struct {
	DisableKeepAlives     bool `json:"disable_keep_alives"`
	MaxIdleConns          int  `json:"max_idle_conns"`
	MaxIdleConnsPerHost   int  `json:"max_idle_conns_per_host"`
	IdleConnTimeoutMS     int  `json:"idle_conn_timeout_ms"`
	TLSHandshakeTimeoutMS int  `json:"tls_handshake_timeout_ms"`
	ExpectContinueMS      int  `json:"expect_continue_ms"`
	ForceAttemptHTTP2     bool `json:"force_attempt_http2"`
}

func invalid(err error) response {
	return response{ErrorType: "InvalidInput", Message: err.Error()}
}

func decode(args []json.RawMessage, values ...any) error {
	if len(args) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for index, value := range values {
		if err := json.Unmarshal(args[index], value); err != nil {
			return fmt.Errorf("argument %d: %w", index, err)
		}
	}
	return nil
}

func summarizeTransport(transport *http.Transport) transportState {
	return transportState{
		DisableKeepAlives:     transport.DisableKeepAlives,
		MaxIdleConns:          transport.MaxIdleConns,
		MaxIdleConnsPerHost:   transport.MaxIdleConnsPerHost,
		IdleConnTimeoutMS:     int(transport.IdleConnTimeout.Milliseconds()),
		TLSHandshakeTimeoutMS: int(transport.TLSHandshakeTimeout.Milliseconds()),
		ExpectContinueMS:      int(transport.ExpectContinueTimeout.Milliseconds()),
		ForceAttemptHTTP2:     transport.ForceAttemptHTTP2,
	}
}

func call(input request) response {
	switch input.Operation {
	case "transport_summary":
		if len(input.Args) != 0 {
			return invalid(fmt.Errorf("transport_summary expects no arguments"))
		}
		plainA, plainB := cleanhttp.DefaultTransport(), cleanhttp.DefaultTransport()
		pooledA, pooledB := cleanhttp.DefaultPooledTransport(), cleanhttp.DefaultPooledTransport()
		return response{Value: map[string]any{
			"default":                            summarizeTransport(plainA),
			"pooled":                             summarizeTransport(pooledA),
			"fresh":                              plainA != plainB && pooledA != pooledB && plainA != pooledA,
			"pooled_max_idle_matches_gomaxprocs": pooledA.MaxIdleConnsPerHost == runtime.GOMAXPROCS(0)+1,
		}}
	case "client_summary":
		if len(input.Args) != 0 {
			return invalid(fmt.Errorf("client_summary expects no arguments"))
		}
		plainA, plainB := cleanhttp.DefaultClient(), cleanhttp.DefaultClient()
		pooledA, pooledB := cleanhttp.DefaultPooledClient(), cleanhttp.DefaultPooledClient()
		plainTransport, plainOK := plainA.Transport.(*http.Transport)
		pooledTransport, pooledOK := pooledA.Transport.(*http.Transport)
		return response{Value: map[string]any{
			"default":                            summarizeTransport(plainTransport),
			"pooled":                             summarizeTransport(pooledTransport),
			"concrete":                           plainOK && pooledOK,
			"fresh_transports":                   plainA.Transport != plainB.Transport && pooledA.Transport != pooledB.Transport,
			"pooled_max_idle_matches_gomaxprocs": pooledTransport.MaxIdleConnsPerHost == runtime.GOMAXPROCS(0)+1,
		}}
	case "handler_status":
		var path string
		var inputConfig *cleanhttp.HandlerInput
		if err := decode(input.Args, &path, &inputConfig); err != nil {
			return invalid(err)
		}
		called := false
		next := http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
			called = true
			writer.WriteHeader(http.StatusNoContent)
		})
		recorder := httptest.NewRecorder()
		request := httptest.NewRequest(http.MethodGet, "http://example.test/", nil)
		request.URL.Path = path
		cleanhttp.PrintablePathCheckHandler(next, inputConfig).ServeHTTP(recorder, request)
		return response{Value: map[string]any{"status": recorder.Code, "next_called": called}}
	case "handler_nil_request":
		if len(input.Args) != 0 {
			return invalid(fmt.Errorf("handler_nil_request expects no arguments"))
		}
		called := false
		recorder := httptest.NewRecorder()
		cleanhttp.PrintablePathCheckHandler(http.HandlerFunc(func(http.ResponseWriter, *http.Request) {
			called = true
		}), nil).ServeHTTP(recorder, nil)
		return response{Value: map[string]any{"status": recorder.Code, "next_called": called}}
	default:
		return invalid(fmt.Errorf("unknown operation"))
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(invalid(err))
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
