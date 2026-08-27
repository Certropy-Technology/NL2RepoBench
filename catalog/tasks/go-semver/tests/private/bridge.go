package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"

	semver "github.com/Masterminds/semver/v3"
)

const maxSortVersions = 64

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     any    `json:"value,omitempty"`
	ErrorType string `json:"error_type,omitempty"`
	Message   string `json:"message,omitempty"`
}

type versionValue struct {
	String     string `json:"string"`
	Original   string `json:"original"`
	Major      uint64 `json:"major"`
	Minor      uint64 `json:"minor"`
	Patch      uint64 `json:"patch"`
	Prerelease string `json:"prerelease"`
	Metadata   string `json:"metadata"`
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 64*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			writeResponse(encoder, response{ErrorType: "InvalidInput", Message: err.Error()})
			continue
		}
		writeResponse(encoder, handle(input))
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func handle(input request) response {
	switch input.Operation {
	case "parse":
		var value string
		var strict bool
		if err := decodeArgs(input.Args, &value, &strict); err != nil {
			return invalidInput(err)
		}
		parsed, err := parseVersion(value, strict)
		if err != nil {
			return callFailed(err)
		}
		return response{Value: snapshot(parsed)}
	case "compare":
		var left string
		var right string
		if err := decodeArgs(input.Args, &left, &right); err != nil {
			return invalidInput(err)
		}
		leftVersion, err := parseVersion(left, false)
		if err != nil {
			return callFailed(err)
		}
		rightVersion, err := parseVersion(right, false)
		if err != nil {
			return callFailed(err)
		}
		return response{Value: leftVersion.Compare(rightVersion)}
	case "increment":
		var value string
		var component string
		if err := decodeArgs(input.Args, &value, &component); err != nil {
			return invalidInput(err)
		}
		parsed, err := parseVersion(value, false)
		if err != nil {
			return callFailed(err)
		}
		incremented, err := increment(*parsed, component)
		if err != nil {
			return callFailed(err)
		}
		return response{Value: snapshot(&incremented)}
	case "set_prerelease":
		return setPrerelease(input.Args)
	case "set_metadata":
		return setMetadata(input.Args)
	case "constraint_check":
		var constraintText string
		var versionText string
		if err := decodeArgs(input.Args, &constraintText, &versionText); err != nil {
			return invalidInput(err)
		}
		constraint, err := parseConstraint(constraintText)
		if err != nil {
			return callFailed(err)
		}
		version, err := parseVersion(versionText, false)
		if err != nil {
			return callFailed(err)
		}
		return response{Value: constraint.Check(version)}
	case "sort":
		return sortVersions(input.Args)
	default:
		return response{ErrorType: "InvalidInput", Message: "unknown operation"}
	}
}

func decodeArgs(raw []json.RawMessage, values ...any) error {
	if len(raw) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for index, value := range values {
		if err := json.Unmarshal(raw[index], value); err != nil {
			return fmt.Errorf("argument %d: %w", index, err)
		}
	}
	return nil
}

func parseVersion(value string, strict bool) (*semver.Version, error) {
	if len(value) > semver.MaxVersionLen {
		return nil, semver.ErrVersionTooLong
	}
	if strict {
		return semver.StrictNewVersion(value)
	}
	return semver.NewVersion(value)
}

func parseConstraint(value string) (*semver.Constraints, error) {
	if len(value) > semver.MaxConstraintLen {
		return nil, semver.ErrConstraintTooLong
	}
	return semver.NewConstraint(value)
}

func increment(value semver.Version, component string) (semver.Version, error) {
	switch component {
	case "major":
		return value.IncMajorE()
	case "minor":
		return value.IncMinorE()
	case "patch":
		return value.IncPatchE()
	default:
		return semver.Version{}, fmt.Errorf("unknown component %q", component)
	}
}

func setPrerelease(args []json.RawMessage) response {
	var versionText string
	var prerelease string
	if err := decodeArgs(args, &versionText, &prerelease); err != nil {
		return invalidInput(err)
	}
	version, err := parseVersion(versionText, false)
	if err != nil {
		return callFailed(err)
	}
	changed, err := version.SetPrerelease(prerelease)
	if err != nil {
		return callFailed(err)
	}
	return response{Value: snapshot(&changed)}
}

func setMetadata(args []json.RawMessage) response {
	var versionText string
	var metadata string
	if err := decodeArgs(args, &versionText, &metadata); err != nil {
		return invalidInput(err)
	}
	version, err := parseVersion(versionText, false)
	if err != nil {
		return callFailed(err)
	}
	changed, err := version.SetMetadata(metadata)
	if err != nil {
		return callFailed(err)
	}
	return response{Value: snapshot(&changed)}
}

func sortVersions(args []json.RawMessage) response {
	var values []string
	if err := decodeArgs(args, &values); err != nil {
		return invalidInput(err)
	}
	if len(values) > maxSortVersions {
		return invalidInput(fmt.Errorf("too many versions"))
	}
	versions := make(semver.Collection, 0, len(values))
	for _, value := range values {
		parsed, err := parseVersion(value, false)
		if err != nil {
			return callFailed(err)
		}
		versions = append(versions, parsed)
	}
	sort.Sort(versions)
	result := make([]string, 0, len(versions))
	for _, version := range versions {
		result = append(result, version.String())
	}
	return response{Value: result}
}

func snapshot(value *semver.Version) versionValue {
	return versionValue{
		String:     value.String(),
		Original:   value.Original(),
		Major:      value.Major(),
		Minor:      value.Minor(),
		Patch:      value.Patch(),
		Prerelease: value.Prerelease(),
		Metadata:   value.Metadata(),
	}
}

func invalidInput(err error) response {
	return response{ErrorType: "InvalidInput", Message: err.Error()}
}

func callFailed(err error) response {
	return response{ErrorType: "CallFailed", Message: err.Error()}
}

func writeResponse(encoder *json.Encoder, output response) {
	if err := encoder.Encode(output); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
