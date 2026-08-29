package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"strings"

	bytebufferpool "github.com/valyala/bytebufferpool"
)

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     json.RawMessage `json:"value,omitempty"`
	ErrorType string          `json:"error_type,omitempty"`
	Message   string          `json:"message,omitempty"`
}

type step struct {
	Operation string `json:"operation"`
	Text      string `json:"text,omitempty"`
	Byte      uint8  `json:"byte,omitempty"`
}

type errorReader struct {
	data []byte
}

func (r *errorReader) Read(p []byte) (int, error) {
	n := copy(p, r.data)
	r.data = r.data[n:]
	return n, errors.New("reader error")
}

type limitedWriter struct {
	limit int
	data  bytes.Buffer
}

func (w *limitedWriter) Write(p []byte) (int, error) {
	n := w.limit
	if n > len(p) {
		n = len(p)
	}
	_, _ = w.data.Write(p[:n])
	return n, errors.New("writer error")
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func marshal(value interface{}) response {
	encoded, err := json.Marshal(value)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: encoded}
}

func call(req request) response {
	switch req.Operation {
	case "buffer_sequence":
		if len(req.Args) != 1 {
			return invalid("expected one argument")
		}
		var steps []step
		if err := json.Unmarshal(req.Args[0], &steps); err != nil {
			return invalid(err.Error())
		}
		var buffer bytebufferpool.ByteBuffer
		for _, item := range steps {
			switch item.Operation {
			case "write":
				_, _ = buffer.Write([]byte(item.Text))
			case "write_string":
				_, _ = buffer.WriteString(item.Text)
			case "write_byte":
				if err := buffer.WriteByte(item.Byte); err != nil {
					return response{ErrorType: "CallFailed", Message: err.Error()}
				}
			case "set":
				buffer.Set([]byte(item.Text))
			case "set_string":
				buffer.SetString(item.Text)
			case "reset":
				buffer.Reset()
			case "noop":
			default:
				return invalid("unknown buffer step")
			}
		}
		return marshal(map[string]interface{}{"bytes": string(buffer.Bytes()), "len": buffer.Len(), "string": buffer.String()})
	case "set_copy":
		if len(req.Args) != 1 {
			return invalid("expected one argument")
		}
		var text string
		if err := json.Unmarshal(req.Args[0], &text); err != nil {
			return invalid(err.Error())
		}
		input := []byte(text)
		var buffer bytebufferpool.ByteBuffer
		buffer.Set(input)
		if len(input) > 0 {
			input[0] = 'X'
		}
		return marshal(buffer.String())
	case "read_from":
		if len(req.Args) != 1 {
			return invalid("expected one argument")
		}
		var text string
		if err := json.Unmarshal(req.Args[0], &text); err != nil {
			return invalid(err.Error())
		}
		var buffer bytebufferpool.ByteBuffer
		n, err := buffer.ReadFrom(strings.NewReader(text))
		return marshal(map[string]interface{}{"error": errorString(err), "len": buffer.Len(), "n": n, "string": buffer.String()})
	case "write_to":
		if len(req.Args) != 1 {
			return invalid("expected one argument")
		}
		var text string
		if err := json.Unmarshal(req.Args[0], &text); err != nil {
			return invalid(err.Error())
		}
		var buffer bytebufferpool.ByteBuffer
		buffer.SetString(text)
		var output bytes.Buffer
		n, err := buffer.WriteTo(&output)
		return marshal(map[string]interface{}{"error": errorString(err), "n": n, "output": output.String()})
	case "read_from_error":
		if len(req.Args) != 1 {
			return invalid("expected one argument")
		}
		var text string
		if err := json.Unmarshal(req.Args[0], &text); err != nil {
			return invalid(err.Error())
		}
		var buffer bytebufferpool.ByteBuffer
		n, err := buffer.ReadFrom(&errorReader{data: []byte(text)})
		return marshal(map[string]interface{}{"error": errorString(err), "len": buffer.Len(), "n": n, "string": buffer.String()})
	case "write_to_error":
		if len(req.Args) != 2 {
			return invalid("expected two arguments")
		}
		var text string
		var limit int
		if err := json.Unmarshal(req.Args[0], &text); err != nil {
			return invalid(err.Error())
		}
		if err := json.Unmarshal(req.Args[1], &limit); err != nil || limit < 0 {
			return invalid("invalid writer limit")
		}
		var buffer bytebufferpool.ByteBuffer
		buffer.SetString(text)
		writer := &limitedWriter{limit: limit}
		n, err := buffer.WriteTo(writer)
		return marshal(map[string]interface{}{"error": errorString(err), "n": n, "output": writer.data.String()})
	case "pool_roundtrip":
		if len(req.Args) != 1 {
			return invalid("expected one argument")
		}
		var text string
		if err := json.Unmarshal(req.Args[0], &text); err != nil {
			return invalid(err.Error())
		}
		buffer := bytebufferpool.Get()
		if buffer == nil || buffer.Len() != 0 {
			return response{ErrorType: "CallFailed", Message: "pool returned a non-empty buffer"}
		}
		buffer.SetString(text)
		bytebufferpool.Put(buffer)
		again := bytebufferpool.Get()
		if again == nil {
			return response{ErrorType: "CallFailed", Message: "pool returned nil"}
		}
		result := map[string]interface{}{"len": again.Len(), "string": again.String()}
		bytebufferpool.Put(again)
		return marshal(result)
	case "custom_pool_roundtrip":
		if len(req.Args) != 1 {
			return invalid("expected one argument")
		}
		var text string
		if err := json.Unmarshal(req.Args[0], &text); err != nil {
			return invalid(err.Error())
		}
		var pool bytebufferpool.Pool
		buffer := pool.Get()
		buffer.SetString(text)
		pool.Put(buffer)
		again := pool.Get()
		result := map[string]interface{}{"len": again.Len(), "string": again.String()}
		pool.Put(again)
		return marshal(result)
	case "invalid":
		return invalid("known bridge operation has invalid request")
	default:
		return invalid("unknown operation")
	}
}

func errorString(err error) string {
	if err == nil || err == io.EOF {
		return ""
	}
	return err.Error()
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var req request
		if err := json.Unmarshal(scanner.Bytes(), &req); err != nil {
			_ = encoder.Encode(response{ErrorType: "InvalidInput", Message: err.Error()})
			continue
		}
		if err := encoder.Encode(call(req)); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
