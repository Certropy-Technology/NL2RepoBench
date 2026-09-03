package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	isatty "github.com/mattn/go-isatty"
	"golang.org/x/sys/unix"
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

type descriptor struct {
	Name     string `json:"name"`
	Terminal bool   `json:"terminal"`
	Cygwin   bool   `json:"cygwin"`
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
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

func call(input request) response {
	switch input.Operation {
	case "probe_fds":
		if len(input.Args) != 0 {
			return invalid("probe_fds expects no arguments")
		}
		file, err := os.OpenFile("/dev/null", os.O_RDONLY, 0)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		defer file.Close()
		readPipe, writePipe, err := os.Pipe()
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		defer readPipe.Close()
		defer writePipe.Close()
		return response{Value: []descriptor{
			{Name: "stdin", Terminal: isatty.IsTerminal(os.Stdin.Fd()), Cygwin: isatty.IsCygwinTerminal(os.Stdin.Fd())},
			{Name: "dev_null", Terminal: isatty.IsTerminal(file.Fd()), Cygwin: isatty.IsCygwinTerminal(file.Fd())},
			{Name: "pipe", Terminal: isatty.IsTerminal(readPipe.Fd()), Cygwin: isatty.IsCygwinTerminal(readPipe.Fd())},
			{Name: "invalid", Terminal: isatty.IsTerminal(^uintptr(0)), Cygwin: isatty.IsCygwinTerminal(^uintptr(0))},
		}}
	case "probe_pty":
		if len(input.Args) != 0 {
			return invalid("probe_pty expects no arguments")
		}
		master, err := unix.Open("/dev/ptmx", unix.O_RDWR|unix.O_NOCTTY, 0)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		defer unix.Close(master)
		number, err := unix.IoctlGetInt(master, unix.TIOCGPTN)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		if err := unix.IoctlSetPointerInt(master, unix.TIOCSPTLCK, 0); err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		slave, err := unix.Open(fmt.Sprintf("/dev/pts/%d", number), unix.O_RDWR|unix.O_NOCTTY, 0)
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		defer unix.Close(slave)
		return response{Value: descriptor{
			Name: "pty-slave", Terminal: isatty.IsTerminal(uintptr(slave)), Cygwin: isatty.IsCygwinTerminal(uintptr(slave)),
		}}
	case "probe_fd":
		var fd uint64
		if err := decode(input.Args, &fd); err != nil {
			return invalid(err.Error())
		}
		if fd > uint64(^uintptr(0)) {
			return invalid("fd is outside uintptr range")
		}
		value := descriptor{
			Name:     "custom",
			Terminal: isatty.IsTerminal(uintptr(fd)),
			Cygwin:   isatty.IsCygwinTerminal(uintptr(fd)),
		}
		return response{Value: value}
	case "probe_cygwin":
		var fd uint64
		if err := decode(input.Args, &fd); err != nil {
			return invalid(err.Error())
		}
		if fd > uint64(^uintptr(0)) {
			return invalid("fd is outside uintptr range")
		}
		return response{Value: isatty.IsCygwinTerminal(uintptr(fd))}
	default:
		return invalid("unknown operation")
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 64*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
			continue
		}
		var output response
		func() {
			defer func() {
				if recovered := recover(); recovered != nil {
					output = response{ErrorType: "CallFailed", Message: fmt.Sprintf("panic: %v", recovered)}
				}
			}()
			output = call(input)
		}()
		if err := encoder.Encode(output); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
