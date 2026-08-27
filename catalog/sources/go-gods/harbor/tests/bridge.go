package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"

	"github.com/emirpasic/gods/v2/lists/arraylist"
	doublylinkedlist "github.com/emirpasic/gods/v2/lists/doublylinkedlist"
	singlylinkedlist "github.com/emirpasic/gods/v2/lists/singlylinkedlist"
	"github.com/emirpasic/gods/v2/maps/hashmap"
	"github.com/emirpasic/gods/v2/maps/linkedhashmap"
	"github.com/emirpasic/gods/v2/maps/treemap"
	"github.com/emirpasic/gods/v2/queues/arrayqueue"
	"github.com/emirpasic/gods/v2/queues/circularbuffer"
	"github.com/emirpasic/gods/v2/queues/linkedlistqueue"
	"github.com/emirpasic/gods/v2/sets/hashset"
	"github.com/emirpasic/gods/v2/sets/treeset"
	"github.com/emirpasic/gods/v2/stacks/arraystack"
	"github.com/emirpasic/gods/v2/stacks/linkedliststack"
	"github.com/emirpasic/gods/v2/trees/binaryheap"
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

type action struct {
	Name   string `json:"name"`
	Index  int    `json:"index"`
	Other  int    `json:"other"`
	Value  int    `json:"value"`
	Values []int  `json:"values"`
}

type pair struct {
	Key   string `json:"key"`
	Value int    `json:"value"`
}

type intPair struct {
	Key   int `json:"key"`
	Value int `json:"value"`
}

const maxItems = 64

func decode(args []json.RawMessage, index int, target any) error {
	if index >= len(args) {
		return fmt.Errorf("missing argument %d", index)
	}
	return json.Unmarshal(args[index], target)
}

func encode(value any) response {
	payload, err := json.Marshal(value)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: payload}
}

func invalid(err error) response {
	return response{ErrorType: "InvalidInput", Message: err.Error()}
}

func applyList(list interface {
	Add(...int)
	Remove(int)
	Insert(int, ...int)
	Set(int, int)
	Swap(int, int)
}, actions []action) {
	for _, item := range actions {
		switch item.Name {
		case "add":
			list.Add(item.Values...)
		case "remove":
			list.Remove(item.Index)
		case "insert":
			list.Insert(item.Index, item.Values...)
		case "set":
			list.Set(item.Index, item.Value)
		case "swap":
			list.Swap(item.Index, item.Other)
		}
	}
}

func applyLinkedList(list interface {
	Add(...int)
	Remove(int)
	Insert(int, ...int)
	Set(int, int)
	Swap(int, int)
	Append(...int)
	Prepend(...int)
}, actions []action) {
	for _, item := range actions {
		switch item.Name {
		case "add":
			list.Add(item.Values...)
		case "append":
			list.Append(item.Values...)
		case "prepend":
			list.Prepend(item.Values...)
		case "remove":
			list.Remove(item.Index)
		case "insert":
			list.Insert(item.Index, item.Values...)
		case "set":
			list.Set(item.Index, item.Value)
		case "swap":
			list.Swap(item.Index, item.Other)
		}
	}
}

type listView interface {
	Get(int) (int, bool)
	Contains(...int) bool
	Values() []int
	IndexOf(int) int
	Empty() bool
	Size() int
	String() string
}

func listResult(list listView) map[string]any {
	got, ok := list.Get(0)
	return map[string]any{
		"values": list.Values(), "size": list.Size(), "empty": list.Empty(),
		"contains_all": list.Contains(1, 2), "contains_empty": list.Contains(),
		"index_of_one": list.IndexOf(1), "first": got, "first_ok": ok,
		"string": list.String(),
	}
}

func listCall(args []json.RawMessage) response {
	var kind string
	var values []int
	var actions []action
	if err := decode(args, 0, &kind); err != nil {
		return invalid(err)
	}
	if err := decode(args, 1, &values); err != nil {
		return invalid(err)
	}
	if err := decode(args, 2, &actions); err != nil {
		return invalid(err)
	}
	if len(values) > maxItems || len(actions) > maxItems {
		return invalid(fmt.Errorf("list request exceeds item limit"))
	}
	switch kind {
	case "array":
		list := arraylist.New(values...)
		applyList(list, actions)
		for _, item := range actions {
			if item.Name == "sort" {
				list.Sort(func(a, b int) int { return a - b })
			}
		}
		return encode(listResult(list))
	case "singly":
		list := singlylinkedlist.New(values...)
		applyLinkedList(list, actions)
		return encode(listResult(list))
	case "doubly":
		list := doublylinkedlist.New(values...)
		applyLinkedList(list, actions)
		return encode(listResult(list))
	default:
		return invalid(fmt.Errorf("unknown list kind"))
	}
}

func stackCall(args []json.RawMessage) response {
	var kind string
	var values []int
	if err := decode(args, 0, &kind); err != nil {
		return invalid(err)
	}
	if err := decode(args, 1, &values); err != nil {
		return invalid(err)
	}
	if len(values) > maxItems {
		return invalid(fmt.Errorf("stack request exceeds item limit"))
	}
	var push func(int)
	var pop func() (int, bool)
	var peek func() (int, bool)
	var empty func() bool
	var size func() int
	var clear func()
	var snapshot func() []int
	switch kind {
	case "array":
		stack := arraystack.New[int]()
		push, pop, peek, empty, size, clear, snapshot = stack.Push, stack.Pop, stack.Peek, stack.Empty, stack.Size, stack.Clear, stack.Values
	case "linked":
		stack := linkedliststack.New[int]()
		push, pop, peek, empty, size, clear, snapshot = stack.Push, stack.Pop, stack.Peek, stack.Empty, stack.Size, stack.Clear, stack.Values
	default:
		return invalid(fmt.Errorf("unknown stack kind"))
	}
	for _, value := range values {
		push(value)
	}
	peekValue, peekOK := peek()
	popValue, popOK := pop()
	return encode(map[string]any{
		"peek": peekValue, "peek_ok": peekOK, "pop": popValue, "pop_ok": popOK,
		"values_after_pop": snapshot(), "size_after_pop": size(), "empty": empty(),
		"cleared_size": func() int { clear(); return size() }(),
	})
}

func queueCall(args []json.RawMessage) response {
	var kind string
	var values []int
	if err := decode(args, 0, &kind); err != nil {
		return invalid(err)
	}
	if err := decode(args, 1, &values); err != nil {
		return invalid(err)
	}
	if len(values) > maxItems {
		return invalid(fmt.Errorf("queue request exceeds item limit"))
	}
	var enqueue func(int)
	var dequeue func() (int, bool)
	var peek func() (int, bool)
	var empty func() bool
	var size func() int
	var clear func()
	var snapshot func() []int
	switch kind {
	case "array":
		queue := arrayqueue.New[int]()
		enqueue, dequeue, peek, empty, size, clear, snapshot = queue.Enqueue, queue.Dequeue, queue.Peek, queue.Empty, queue.Size, queue.Clear, queue.Values
	case "linked":
		queue := linkedlistqueue.New[int]()
		enqueue, dequeue, peek, empty, size, clear, snapshot = queue.Enqueue, queue.Dequeue, queue.Peek, queue.Empty, queue.Size, queue.Clear, queue.Values
	default:
		return invalid(fmt.Errorf("unknown queue kind"))
	}
	for _, value := range values {
		enqueue(value)
	}
	peekValue, peekOK := peek()
	dequeueValue, dequeueOK := dequeue()
	return encode(map[string]any{
		"peek": peekValue, "peek_ok": peekOK, "dequeue": dequeueValue, "dequeue_ok": dequeueOK,
		"values_after_dequeue": snapshot(), "size_after_dequeue": size(), "empty": empty(),
		"cleared_size": func() int { clear(); return size() }(),
	})
}

func circularCall(args []json.RawMessage) response {
	var capacity int
	var values []int
	if err := decode(args, 0, &capacity); err != nil {
		return invalid(err)
	}
	if err := decode(args, 1, &values); err != nil {
		return invalid(err)
	}
	if capacity < 1 || capacity > maxItems || len(values) > maxItems {
		return invalid(fmt.Errorf("circular request exceeds bounds"))
	}
	queue := circularbuffer.New[int](capacity)
	for _, value := range values {
		queue.Enqueue(value)
	}
	peek, peekOK := queue.Peek()
	dequeued, dequeueOK := queue.Dequeue()
	return encode(map[string]any{
		"values": queue.Values(), "full_before_dequeue": len(values) >= capacity,
		"full_after_dequeue": queue.Full(), "peek": peek, "peek_ok": peekOK,
		"dequeue": dequeued, "dequeue_ok": dequeueOK, "size": queue.Size(),
	})
}

func hashmapCall(args []json.RawMessage) response {
	var kind string
	var pairs []pair
	if err := decode(args, 0, &kind); err != nil {
		return invalid(err)
	}
	if err := decode(args, 1, &pairs); err != nil {
		return invalid(err)
	}
	if len(pairs) > maxItems {
		return invalid(fmt.Errorf("map request exceeds item limit"))
	}
	if kind == "hash" {
		m := hashmap.New[string, int]()
		for _, item := range pairs {
			m.Put(item.Key, item.Value)
		}
		m.Remove("missing")
		keys := m.Keys()
		sort.Strings(keys)
		values := make([]int, 0, len(keys))
		for _, key := range keys {
			value, _ := m.Get(key)
			values = append(values, value)
		}
		return encode(map[string]any{"keys": keys, "values": values, "size": m.Size(), "empty": m.Empty(), "get_a": func() int { v, _ := m.Get("a"); return v }()})
	}
	if kind == "linked" {
		m := linkedhashmap.New[string, int]()
		for _, item := range pairs {
			m.Put(item.Key, item.Value)
		}
		keys := m.Keys()
		values := m.Values()
		return encode(map[string]any{"keys": keys, "values": values, "size": m.Size(), "empty": m.Empty()})
	}
	return invalid(fmt.Errorf("unknown map kind"))
}

func treeMapCall(args []json.RawMessage) response {
	var pairs []intPair
	var query []int
	if err := decode(args, 0, &pairs); err != nil {
		return invalid(err)
	}
	if err := decode(args, 1, &query); err != nil {
		return invalid(err)
	}
	if len(pairs) > maxItems || len(query) > maxItems {
		return invalid(fmt.Errorf("tree map request exceeds item limit"))
	}
	m := treemap.New[int, int]()
	for _, item := range pairs {
		m.Put(item.Key, item.Value)
	}
	minKey, minValue, minOK := m.Min()
	maxKey, maxValue, maxOK := m.Max()
	ranges := make([]map[string]any, 0, len(query))
	for _, key := range query {
		floorKey, floorValue, floorOK := m.Floor(key)
		ceilingKey, ceilingValue, ceilingOK := m.Ceiling(key)
		ranges = append(ranges, map[string]any{"floor": []any{floorKey, floorValue, floorOK}, "ceiling": []any{ceilingKey, ceilingValue, ceilingOK}})
	}
	return encode(map[string]any{"keys": m.Keys(), "values": m.Values(), "min": []any{minKey, minValue, minOK}, "max": []any{maxKey, maxValue, maxOK}, "ranges": ranges})
}

func setCall(args []json.RawMessage) response {
	var kind string
	var values []int
	var other []int
	if err := decode(args, 0, &kind); err != nil {
		return invalid(err)
	}
	if err := decode(args, 1, &values); err != nil {
		return invalid(err)
	}
	if err := decode(args, 2, &other); err != nil {
		return invalid(err)
	}
	if len(values) > maxItems || len(other) > maxItems {
		return invalid(fmt.Errorf("set request exceeds item limit"))
	}
	if kind == "hash" {
		left, right := hashset.New(values...), hashset.New(other...)
		all := left.Values()
		sort.Ints(all)
		intersection := left.Intersection(right).Values()
		sort.Ints(intersection)
		union := left.Union(right).Values()
		sort.Ints(union)
		difference := left.Difference(right).Values()
		sort.Ints(difference)
		return encode(map[string]any{"values": all, "intersection": intersection, "union": union, "difference": difference, "contains": left.Contains(values...), "size": left.Size()})
	}
	if kind == "tree" {
		left, right := treeset.New(values...), treeset.New(other...)
		return encode(map[string]any{"values": left.Values(), "intersection": left.Intersection(right).Values(), "union": left.Union(right).Values(), "difference": left.Difference(right).Values(), "contains": left.Contains(values...), "size": left.Size()})
	}
	return invalid(fmt.Errorf("unknown set kind"))
}

func heapCall(args []json.RawMessage) response {
	var values []int
	if err := decode(args, 0, &values); err != nil {
		return invalid(err)
	}
	if len(values) > maxItems {
		return invalid(fmt.Errorf("heap request exceeds item limit"))
	}
	heap := binaryheap.New[int]()
	heap.Push(values...)
	peek, peekOK := heap.Peek()
	ordered := make([]int, 0, heap.Size())
	for !heap.Empty() {
		value, _ := heap.Pop()
		ordered = append(ordered, value)
	}
	return encode(map[string]any{"peek": peek, "peek_ok": peekOK, "pop_order": ordered, "empty": heap.Empty()})
}

func serializationCall(args []json.RawMessage) response {
	var kind string
	var values []int
	if err := decode(args, 0, &kind); err != nil {
		return invalid(err)
	}
	if err := decode(args, 1, &values); err != nil {
		return invalid(err)
	}
	if len(values) > maxItems {
		return invalid(fmt.Errorf("serialization request exceeds item limit"))
	}
	var data []byte
	var err error
	var restored []int
	switch kind {
	case "list":
		value := arraylist.New(values...)
		data, err = value.ToJSON()
		restoredValue := arraylist.New[int]()
		if err == nil {
			err = restoredValue.FromJSON(data)
			restored = restoredValue.Values()
		}
	case "tree-set":
		value := treeset.New(values...)
		data, err = value.ToJSON()
		restoredValue := treeset.New[int]()
		if err == nil {
			err = restoredValue.FromJSON(data)
			restored = restoredValue.Values()
		}
	default:
		return invalid(fmt.Errorf("unknown serialization kind"))
	}
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return encode(map[string]any{"json": string(data), "restored": restored})
}

func call(input request) response {
	switch input.Operation {
	case "list":
		return listCall(input.Args)
	case "stack":
		return stackCall(input.Args)
	case "queue":
		return queueCall(input.Args)
	case "circular":
		return circularCall(input.Args)
	case "map":
		return hashmapCall(input.Args)
	case "tree_map":
		return treeMapCall(input.Args)
	case "set":
		return setCall(input.Args)
	case "heap":
		return heapCall(input.Args)
	case "serialization":
		return serializationCall(input.Args)
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
