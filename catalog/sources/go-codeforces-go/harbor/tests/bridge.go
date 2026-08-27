package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	"github.com/EndlessCheng/codeforces-go/copypasta"
)

const maxWords = 16

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     json.RawMessage `json:"value,omitempty"`
	ErrorType string          `json:"error_type,omitempty"`
	Message   string          `json:"message,omitempty"`
}

type setup struct {
	Words     int   `json:"words"`
	Positions []int `json:"positions"`
}

type rangeAction struct {
	Kind string `json:"kind"`
	From int    `json:"from"`
	To   int    `json:"to"`
}

type snapshot struct {
	Bits     []int  `json:"bits"`
	Count    int    `json:"count"`
	Text     string `json:"text"`
	Len      int    `json:"len"`
	First0   int    `json:"first_zero"`
	First1   int    `json:"first_one"`
	Last1    int    `json:"last_one"`
	Trailing int    `json:"trailing_zeros"`
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func decode[T any](args []json.RawMessage, index int, target *T) *response {
	if index >= len(args) {
		result := invalid("missing argument")
		return &result
	}
	if err := json.Unmarshal(args[index], target); err != nil {
		result := invalid(err.Error())
		return &result
	}
	return nil
}

func capacity(words int) int {
	return words * 64
}

func makeBitset(input setup) (copypasta.Bitset, *response) {
	if input.Words < 1 || input.Words > maxWords {
		result := invalid("words must be within 1..16")
		return nil, &result
	}
	b := copypasta.NewBitset(capacity(input.Words))
	for _, position := range input.Positions {
		if position < 0 || position >= capacity(input.Words) {
			result := invalid("position outside capacity")
			return nil, &result
		}
		b.Set(position)
	}
	return b, nil
}

func summarize(b copypasta.Bitset) snapshot {
	return snapshot{
		Bits:     b.AllIndex1(),
		Count:    b.OnesCount(),
		Text:     b.String(),
		Len:      b.Len(),
		First0:   b.Index0(),
		First1:   b.Index1(),
		Last1:    b.LastIndex1(),
		Trailing: b.TrailingZeros(),
	}
}

func encode(value any) response {
	payload, err := json.Marshal(value)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: payload}
}

func decodeSetup(args []json.RawMessage) (copypasta.Bitset, *response) {
	if len(args) < 1 {
		result := invalid("expected setup argument")
		return nil, &result
	}
	var input setup
	if err := decode(args, 0, &input); err != nil {
		return nil, err
	}
	return makeBitset(input)
}

func checkIndex(position, words int) *response {
	if position < 0 || position >= capacity(words) {
		result := invalid("index outside capacity")
		return &result
	}
	return nil
}

func call(req request) response {
	switch req.Operation {
	case "summary":
		if len(req.Args) != 4 {
			return invalid("summary expects setup and three position lists")
		}
		var input setup
		if err := decode(req.Args, 0, &input); err != nil {
			return *err
		}
		b, err := makeBitset(input)
		if err != nil {
			return *err
		}
		actions := []struct {
			kind  string
			index int
		}{
			{kind: "set", index: 1},
			{kind: "reset", index: 2},
			{kind: "flip", index: 3},
		}
		for _, action := range actions {
			var positions []int
			if decodeErr := decode(req.Args, action.index, &positions); decodeErr != nil {
				return *decodeErr
			}
			for _, position := range positions {
				if checkErr := checkIndex(position, input.Words); checkErr != nil {
					return *checkErr
				}
				switch action.kind {
				case "set":
					b.Set(position)
				case "reset":
					b.Reset(position)
				default:
					b.Flip(position)
				}
			}
		}
		return encode(summarize(b))
	case "ranges":
		if len(req.Args) != 2 {
			return invalid("ranges expects setup and actions")
		}
		var input setup
		var actions []rangeAction
		if err := decode(req.Args, 0, &input); err != nil {
			return *err
		}
		if err := decode(req.Args, 1, &actions); err != nil {
			return *err
		}
		b, err := makeBitset(input)
		if err != nil {
			return *err
		}
		for _, action := range actions {
			if action.From < 0 || action.To < action.From || action.To > capacity(input.Words) {
				return invalid("range outside capacity")
			}
			switch action.Kind {
			case "set":
				b.SetRange(action.From, action.To)
			case "reset":
				b.ResetRange(action.From, action.To)
			case "flip":
				b.FlipRange(action.From, action.To)
			case "reset_from":
				if action.To != capacity(input.Words) {
					return invalid("reset_from must end at capacity")
				}
				b.ResetFrom(action.From)
			default:
				return invalid("unknown range action")
			}
		}
		return encode(summarize(b))
	case "search":
		if len(req.Args) != 2 {
			return invalid("search expects setup and starts")
		}
		var input setup
		var starts []int
		if err := decode(req.Args, 0, &input); err != nil {
			return *err
		}
		if err := decode(req.Args, 1, &starts); err != nil {
			return *err
		}
		b, err := makeBitset(input)
		if err != nil {
			return *err
		}
		type item struct {
			Start int `json:"start"`
			Next0 int `json:"next_zero"`
			Next1 int `json:"next_one"`
		}
		items := make([]item, 0, len(starts))
		for _, start := range starts {
			if checkErr := checkIndex(start, input.Words); checkErr != nil {
				return *checkErr
			}
			items = append(items, item{Start: start, Next0: b.Next0(start), Next1: b.Next1(start)})
		}
		return encode(items)
	case "has":
		if len(req.Args) != 2 {
			return invalid("has expects setup and positions")
		}
		var input setup
		var positions []int
		if err := decode(req.Args, 0, &input); err != nil {
			return *err
		}
		if err := decode(req.Args, 1, &positions); err != nil {
			return *err
		}
		b, err := makeBitset(input)
		if err != nil {
			return *err
		}
		values := make([]bool, 0, len(positions))
		for _, position := range positions {
			if checkErr := checkIndex(position, input.Words); checkErr != nil {
				return *checkErr
			}
			values = append(values, b.Has(position))
		}
		return encode(values)
	case "shift":
		if len(req.Args) != 3 {
			return invalid("shift expects setup, direction, and amount")
		}
		b, err := decodeSetup(req.Args)
		if err != nil {
			return *err
		}
		var direction string
		var amount int
		if decodeErr := decode(req.Args, 1, &direction); decodeErr != nil {
			return *decodeErr
		}
		if decodeErr := decode(req.Args, 2, &amount); decodeErr != nil {
			return *decodeErr
		}
		if amount < 0 || amount > maxWords*64 {
			return invalid("invalid shift amount")
		}
		switch direction {
		case "left":
			b.Lsh(amount)
		case "right":
			b.Rsh(amount)
		default:
			return invalid("unknown shift direction")
		}
		return encode(summarize(b))
	case "arithmetic":
		if len(req.Args) != 3 {
			return invalid("arithmetic expects setup, kind, and index")
		}
		var input setup
		if decodeErr := decode(req.Args, 0, &input); decodeErr != nil {
			return *decodeErr
		}
		b, err := makeBitset(input)
		if err != nil {
			return *err
		}
		var kind string
		var index int
		if decodeErr := decode(req.Args, 1, &kind); decodeErr != nil {
			return *decodeErr
		}
		if decodeErr := decode(req.Args, 2, &index); decodeErr != nil {
			return *decodeErr
		}
		if checkErr := checkIndex(index, input.Words); checkErr != nil {
			return *checkErr
		}
		switch kind {
		case "add":
			b.Add(index)
		case "sub":
			b.Sub(index)
		default:
			return invalid("unknown arithmetic kind")
		}
		return encode(summarize(b))
	case "relation":
		if len(req.Args) != 3 {
			return invalid("relation expects left setup, right setup, and kind")
		}
		var leftInput, rightInput setup
		var kind string
		if decodeErr := decode(req.Args, 0, &leftInput); decodeErr != nil {
			return *decodeErr
		}
		if decodeErr := decode(req.Args, 1, &rightInput); decodeErr != nil {
			return *decodeErr
		}
		if decodeErr := decode(req.Args, 2, &kind); decodeErr != nil {
			return *decodeErr
		}
		if leftInput.Words != rightInput.Words {
			return invalid("bitsets must have equal word counts")
		}
		left, err := makeBitset(leftInput)
		if err != nil {
			return *err
		}
		right, err := makeBitset(rightInput)
		if err != nil {
			return *err
		}
		switch kind {
		case "or":
			left.Or(right)
			return encode(summarize(left))
		case "and":
			left.And(right)
			return encode(summarize(left))
		case "xor":
			left.Xor(right)
			return encode(summarize(left))
		case "equals":
			return encode(left.Equals(right))
		case "has_subset":
			return encode(left.HasSubset(right))
		default:
			return invalid("unknown relation kind")
		}
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
