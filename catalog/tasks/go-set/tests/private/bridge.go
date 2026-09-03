package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"sync"

	mapset "github.com/deckarep/golang-set/v2"
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

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func failed(message string) response {
	return response{ErrorType: "CallFailed", Message: message}
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

func sortedStrings(values []string) []string {
	result := append([]string(nil), values...)
	sort.Strings(result)
	return result
}

func sortedInts(values []int) []int {
	result := append([]int(nil), values...)
	sort.Ints(result)
	return result
}

func call(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = failed(fmt.Sprintf("candidate call panicked: %v", recovered))
		}
	}()

	switch input.Operation {
	case "basic":
		s := mapset.NewSet("alpha", "beta", "alpha")
		return response{Value: map[string]any{
			"cardinality":   s.Cardinality(),
			"contains_all":  s.Contains("alpha", "beta"),
			"contains_none": s.Contains(),
			"sorted":        sortedStrings(s.ToSlice()),
		}}

	case "mutate":
		s := mapset.NewSet("a", "b")
		first := s.Add("c")
		second := s.Add("c")
		appended := s.Append("d", "a")
		s.Remove("b")
		s.RemoveAll("missing", "d")
		beforeClear := sortedStrings(s.ToSlice())
		s.Clear()
		return response{Value: map[string]any{
			"first_add":           first,
			"second_add":          second,
			"appended":            appended,
			"before_clear":        beforeClear,
			"empty_after_clear":   s.IsEmpty(),
			"cardinality_cleared": s.Cardinality(),
		}}

	case "append_from":
		target := mapset.NewSet("a", "b")
		added := target.AppendFrom(mapset.NewSet("b", "c", "d"))
		unsafeTarget := mapset.NewThreadUnsafeSet(1, 2)
		unsafeAdded := unsafeTarget.AppendFrom(mapset.NewThreadUnsafeSet(2, 3))
		return response{Value: map[string]any{
			"added":         added,
			"values":        sortedStrings(target.ToSlice()),
			"unsafe_added":  unsafeAdded,
			"unsafe_values": sortedInts(unsafeTarget.ToSlice()),
		}}

	case "algebra":
		left := mapset.NewSet("a", "b", "c")
		right := mapset.NewSet("b", "c", "d")
		union := left.Union(right)
		intersection := left.Intersect(right)
		difference := left.Difference(right)
		symmetric := left.SymmetricDifference(right)
		return response{Value: map[string]any{
			"union":           sortedStrings(union.ToSlice()),
			"intersection":    sortedStrings(intersection.ToSlice()),
			"difference":      sortedStrings(difference.ToSlice()),
			"symmetric":       sortedStrings(symmetric.ToSlice()),
			"left_unchanged":  sortedStrings(left.ToSlice()),
			"right_unchanged": sortedStrings(right.ToSlice()),
		}}

	case "predicates":
		small := mapset.NewSet("a", "b")
		large := mapset.NewSet("a", "b", "c")
		return response{Value: map[string]any{
			"subset":               small.IsSubset(large),
			"proper_subset":        small.IsProperSubset(large),
			"not_proper_equal":     small.IsProperSubset(mapset.NewSet("b", "a")),
			"superset":             large.IsSuperset(small),
			"proper_superset":      large.IsProperSuperset(small),
			"equal":                small.Equal(mapset.NewSet("b", "a")),
			"not_equal":            small.Equal(large),
			"contains_one":         large.ContainsOne("c"),
			"contains_all":         large.Contains("a", "c"),
			"contains_any":         large.ContainsAny("missing", "b"),
			"contains_any_element": large.ContainsAnyElement(mapset.NewSet("x", "c")),
			"contains_any_empty":   large.ContainsAny(),
		}}

	case "clone":
		original := mapset.NewSet("keep", "remove")
		clone := original.Clone()
		clone.Remove("remove")
		return response{Value: map[string]any{
			"original": sortedStrings(original.ToSlice()),
			"clone":    sortedStrings(clone.ToSlice()),
		}}

	case "each_filter":
		s := mapset.NewSet(1, 2, 3)
		sum := 0
		s.Each(func(value int) bool {
			sum += value
			return false
		})
		visitsBeforeStop := 0
		s.Each(func(value int) bool {
			visitsBeforeStop++
			return true
		})
		filtered := s.Filter(func(value int) bool { return value%2 == 1 })
		return response{Value: map[string]any{
			"sum":                sum,
			"visits_before_stop": visitsBeforeStop,
			"filtered":           sortedInts(filtered.ToSlice()),
			"original":           sortedInts(s.ToSlice()),
		}}

	case "pop":
		s := mapset.NewSet(1, 2, 3, 4)
		removed, count := s.PopN(2)
		removedSet := mapset.NewSet(removed...)
		remainingSet := mapset.NewSet(s.ToSlice()...)
		first, firstOK := s.Pop()
		_, secondOK := s.Pop()
		zero, emptyOK := s.Pop()
		emptyN, emptyCount := s.PopN(10)
		bounded := mapset.NewSet(7, 8)
		nonPositive, nonPositiveCount := bounded.PopN(0)
		return response{Value: map[string]any{
			"removed_count":       count,
			"removed_unique":      removedSet.Cardinality(),
			"removed_disjoint":    !remainingSet.ContainsAnyElement(removedSet),
			"first_ok":            firstOK,
			"first_was_remaining": remainingSet.ContainsOne(first),
			"second_ok":           secondOK,
			"empty_ok":            emptyOK,
			"empty_zero":          zero,
			"empty_n":             emptyN,
			"empty_count":         emptyCount,
			"non_positive":        nonPositive,
			"non_positive_count":  nonPositiveCount,
			"bounded_unchanged":   sortedInts(bounded.ToSlice()),
		}}

	case "map_constructor":
		s := mapset.NewSetFromMapKeys(map[string]int{"x": 1, "y": 2})
		unsafe := mapset.NewThreadUnsafeSet("b", "a", "b")
		emptySafe := mapset.NewSetWithSize[string](8)
		emptyUnsafe := mapset.NewThreadUnsafeSetWithSize[string](8)
		return response{Value: map[string]any{
			"cardinality":  s.Cardinality(),
			"sorted":       sortedStrings(s.ToSlice()),
			"unsafe":       sortedStrings(unsafe.ToSlice()),
			"empty_safe":   emptySafe.IsEmpty(),
			"empty_unsafe": emptyUnsafe.IsEmpty(),
		}}

	case "concurrent":
		s := mapset.NewSet[int]()
		var group sync.WaitGroup
		for worker := 0; worker < 8; worker++ {
			group.Add(1)
			go func(worker int) {
				defer group.Done()
				for value := 0; value < 100; value++ {
					s.Add(worker*100 + value)
				}
			}(worker)
		}
		group.Wait()
		return response{Value: map[string]any{
			"cardinality":    s.Cardinality(),
			"contains_edges": s.Contains(0, 99, 700, 799),
		}}

	case "invalid":
		return invalid("known bridge operation has invalid request")
	default:
		return invalid("unknown operation")
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
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
