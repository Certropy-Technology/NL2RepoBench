package main

import (
	"bufio"
	"bytes"
	"compress/flate"
	"compress/gzip"
	"encoding/json"
	"fmt"
	"io"
	"os"

	brotli "github.com/andybalholm/brotli"
	brotliflate "github.com/andybalholm/brotli/flate"
	"github.com/andybalholm/brotli/matchfinder"
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

func invalid(message string) response { return response{ErrorType: "InvalidInput", Message: message} }

func result(value any) response {
	payload, err := json.Marshal(value)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: payload}
}

func decode(args []json.RawMessage, values ...any) error {
	if len(args) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for i, value := range values {
		if err := json.Unmarshal(args[i], value); err != nil {
			return fmt.Errorf("argument %d: %w", i, err)
		}
	}
	return nil
}

func compressBrotli(input string, level int, v2 bool) ([]byte, error) {
	var encoded bytes.Buffer
	var writer io.WriteCloser
	if v2 {
		writer = brotli.NewWriterV2(&encoded, level)
	} else {
		writer = brotli.NewWriterLevel(&encoded, level)
	}
	if _, err := writer.Write([]byte(input)); err != nil {
		return nil, err
	}
	if err := writer.Close(); err != nil {
		return nil, err
	}
	return encoded.Bytes(), nil
}

func decompressBrotli(encoded []byte) (string, error) {
	reader := brotli.NewReader(bytes.NewReader(encoded))
	decoded, err := io.ReadAll(reader)
	return string(decoded), err
}

func brotliRoundtrip(input string, level int, v2 bool) (map[string]any, error) {
	encoded, err := compressBrotli(input, level, v2)
	if err != nil {
		return nil, err
	}
	decoded, err := decompressBrotli(encoded)
	if err != nil {
		return nil, err
	}
	return map[string]any{"decoded": decoded, "encoded_len": len(encoded), "level": level, "v2": v2}, nil
}

func readAllWithSmallBuffer(reader io.Reader) (string, error) {
	var decoded bytes.Buffer
	buffer := make([]byte, 3)
	for {
		n, err := reader.Read(buffer)
		if n > 0 {
			_, _ = decoded.Write(buffer[:n])
		}
		if err == io.EOF {
			return decoded.String(), nil
		}
		if err != nil {
			return decoded.String(), err
		}
	}
}

func streamRoundtrip(chunks []string, level int) (map[string]any, error) {
	var encoded bytes.Buffer
	writer := brotli.NewWriterLevel(&encoded, level)
	for _, chunk := range chunks {
		if _, err := writer.Write([]byte(chunk)); err != nil {
			return nil, err
		}
		if err := writer.Flush(); err != nil {
			return nil, err
		}
	}
	if err := writer.Close(); err != nil {
		return nil, err
	}
	decoded, err := readAllWithSmallBuffer(brotli.NewReader(bytes.NewReader(encoded.Bytes())))
	if err != nil {
		return nil, err
	}
	return map[string]any{"decoded": decoded, "encoded_len": encoded.Len(), "chunks": len(chunks)}, nil
}

func writerReset(first, second string) (map[string]any, error) {
	var firstEncoded, secondEncoded bytes.Buffer
	writer := brotli.NewWriter(&firstEncoded)
	if _, err := writer.Write([]byte(first)); err != nil {
		return nil, err
	}
	if err := writer.Close(); err != nil {
		return nil, err
	}
	writer.Reset(&secondEncoded)
	if _, err := writer.Write([]byte(second)); err != nil {
		return nil, err
	}
	if err := writer.Close(); err != nil {
		return nil, err
	}
	decodedFirst, err := decompressBrotli(firstEncoded.Bytes())
	if err != nil {
		return nil, err
	}
	decodedSecond, err := decompressBrotli(secondEncoded.Bytes())
	if err != nil {
		return nil, err
	}
	return map[string]any{"first": decodedFirst, "second": decodedSecond}, nil
}

func readerReset(first, second string) (map[string]any, error) {
	firstEncoded, err := compressBrotli(first, 6, false)
	if err != nil {
		return nil, err
	}
	secondEncoded, err := compressBrotli(second, 6, false)
	if err != nil {
		return nil, err
	}
	reader := brotli.NewReader(bytes.NewReader(firstEncoded))
	decodedFirst, err := io.ReadAll(reader)
	if err != nil {
		return nil, err
	}
	if err := reader.Reset(bytes.NewReader(secondEncoded)); err != nil {
		return nil, err
	}
	decodedSecond, err := io.ReadAll(reader)
	if err != nil {
		return nil, err
	}
	return map[string]any{"first": string(decodedFirst), "second": string(decodedSecond)}, nil
}

func flateRoundtrip(input string, level int, gzipMode bool) (map[string]any, error) {
	var encoded bytes.Buffer
	var writer *matchfinder.Writer
	if gzipMode {
		writer = brotliflate.NewGZIPWriter(&encoded, level)
	} else {
		writer = brotliflate.NewWriter(&encoded, level)
	}
	if _, err := writer.Write([]byte(input)); err != nil {
		return nil, err
	}
	if err := writer.Close(); err != nil {
		return nil, err
	}
	var decoded []byte
	var err error
	if gzipMode {
		var reader *gzip.Reader
		reader, err = gzip.NewReader(bytes.NewReader(encoded.Bytes()))
		if err == nil {
			decoded, err = io.ReadAll(reader)
			_ = reader.Close()
		}
	} else {
		reader := flate.NewReader(bytes.NewReader(encoded.Bytes()))
		decoded, err = io.ReadAll(reader)
		_ = reader.Close()
	}
	if err != nil {
		return nil, err
	}
	return map[string]any{"decoded": string(decoded), "encoded_len": encoded.Len(), "gzip": gzipMode}, nil
}

func finder(name string) (matchfinder.MatchFinder, error) {
	switch name {
	case "none":
		return matchfinder.NoMatchFinder{}, nil
	case "m0":
		return matchfinder.M0{MaxDistance: 64, MaxLength: 64}, nil
	case "m4":
		return &matchfinder.M4{MaxDistance: 64, HashLen: 5, ChainLength: 8}, nil
	case "pathfinder":
		return &matchfinder.Pathfinder{MaxDistance: 64, HashLen: 5, ChainLength: 8}, nil
	case "trio":
		return &matchfinder.Trio{MaxDistance: 64}, nil
	case "zfast":
		return &matchfinder.ZFast{MaxDistance: 64}, nil
	case "zdfast":
		return &matchfinder.ZDFast{MaxDistance: 64}, nil
	case "zm":
		return &matchfinder.ZM{MaxDistance: 64}, nil
	case "bargain1":
		return &matchfinder.Bargain1{MaxDistance: 64}, nil
	case "bargain2":
		return &matchfinder.Bargain2{MaxDistance: 64}, nil
	case "bargain3":
		return &matchfinder.Bargain3{MaxDistance: 64}, nil
	default:
		return nil, fmt.Errorf("unknown finder %q", name)
	}
}

func matchfinderOutput(name, input string) (map[string]any, error) {
	if len(input) > 65536 {
		return nil, fmt.Errorf("input exceeds bounded matchfinder size")
	}
	mf, err := finder(name)
	if err != nil {
		return nil, err
	}
	matches := mf.FindMatches(nil, []byte(input))
	text := matchfinder.TextEncoder{}.Encode(nil, []byte(input), matches, true)
	return map[string]any{"matches": matches, "text": string(text), "finder": name}, nil
}

func call(req request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = response{ErrorType: "CallFailed", Message: fmt.Sprintf("candidate panic: %v", recovered)}
		}
	}()
	switch req.Operation {
	case "brotli_roundtrip":
		var input string
		var level int
		if err := decode(req.Args, &input, &level); err != nil {
			return invalid(err.Error())
		}
		value, err := brotliRoundtrip(input, level, false)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		return result(value)
	case "brotli_v2_roundtrip":
		var input string
		var level int
		if err := decode(req.Args, &input, &level); err != nil {
			return invalid(err.Error())
		}
		value, err := brotliRoundtrip(input, level, true)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		return result(value)
	case "stream_roundtrip":
		var chunks []string
		var level int
		if err := decode(req.Args, &chunks, &level); err != nil {
			return invalid(err.Error())
		}
		if len(chunks) > 128 {
			return invalid("too many chunks")
		}
		value, err := streamRoundtrip(chunks, level)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		return result(value)
	case "writer_reset":
		var first, second string
		if err := decode(req.Args, &first, &second); err != nil {
			return invalid(err.Error())
		}
		value, err := writerReset(first, second)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		return result(value)
	case "reader_reset":
		var first, second string
		if err := decode(req.Args, &first, &second); err != nil {
			return invalid(err.Error())
		}
		value, err := readerReset(first, second)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		return result(value)
	case "flate_roundtrip", "gzip_roundtrip":
		var input string
		var level int
		if err := decode(req.Args, &input, &level); err != nil {
			return invalid(err.Error())
		}
		value, err := flateRoundtrip(input, level, req.Operation == "gzip_roundtrip")
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		return result(value)
	case "matchfinder_output":
		var name, input string
		if err := decode(req.Args, &name, &input); err != nil {
			return invalid(err.Error())
		}
		value, err := matchfinderOutput(name, input)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		return result(value)
	default:
		return invalid("unknown operation")
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var req request
		if err := json.Unmarshal(scanner.Bytes(), &req); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
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
