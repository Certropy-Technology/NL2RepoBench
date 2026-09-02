package main

import (
	"bufio"
	"database/sql"
	"database/sql/driver"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"strings"

	sqlmock "github.com/DATA-DOG/go-sqlmock"
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

type queryRequest struct {
	Query        string              `json:"query"`
	Actual       string              `json:"actual"`
	Matcher      string              `json:"matcher"`
	Columns      []string            `json:"columns"`
	Rows         [][]json.RawMessage `json:"rows"`
	Args         []json.RawMessage   `json:"args"`
	WithoutArgs  bool                `json:"without_args"`
	CloseRows    bool                `json:"close_rows"`
	CSV          string              `json:"csv"`
}

type resultRequest struct {
	LastInsertID int64 `json:"last_insert_id"`
	RowsAffected int64 `json:"rows_affected"`
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(response{ErrorType: "InvalidInput", Message: err.Error()})
			continue
		}
		_ = encoder.Encode(run(input))
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func run(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = response{ErrorType: "Panic", Message: fmt.Sprint(recovered)}
		}
	}()
	value, err := dispatch(input)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: value}
}

func dispatch(input request) (any, error) {
	switch input.Operation {
	case "query":
		return query(input.Args)
	case "exec":
		return exec(input.Args)
	case "transaction":
		return transaction(input.Args)
	case "prepare":
		return prepare(input.Args)
	case "matcher":
		return matcher(input.Args)
	case "result":
		return result(input.Args)
	case "column":
		return column(input.Args)
	case "any_arg":
		return anyArg(input.Args)
	default:
		return nil, errors.New("unknown operation")
	}
}

func decode[T any](args []json.RawMessage) (T, error) {
	var value T
	if len(args) != 1 {
		return value, errors.New("exactly one argument is required")
	}
	if err := json.Unmarshal(args[0], &value); err != nil {
		return value, err
	}
	return value, nil
}

func decodeValue(raw json.RawMessage) (driver.Value, error) {
	decoder := json.NewDecoder(strings.NewReader(string(raw)))
	decoder.UseNumber()
	var value any
	if err := decoder.Decode(&value); err != nil {
		return nil, err
	}
	switch typed := value.(type) {
	case nil, string, bool:
		return typed, nil
	case json.Number:
		if strings.ContainsAny(string(typed), ".eE") {
			return typed.Float64()
		}
		return typed.Int64()
	default:
		return nil, errors.New("driver values must be scalar JSON values")
	}
}

func decodeValues(raws []json.RawMessage) ([]driver.Value, error) {
	values := make([]driver.Value, 0, len(raws))
	for _, raw := range raws {
		value, err := decodeValue(raw)
		if err != nil {
			return nil, err
		}
		values = append(values, value)
	}
	return values, nil
}

func makeRows(spec queryRequest) (rows *sqlmock.Rows, err error) {
	defer func() {
		if recovered := recover(); recovered != nil {
			rows = nil
			err = fmt.Errorf("invalid rows: %v", recovered)
		}
	}()
	rows = sqlmock.NewRows(spec.Columns)
	if spec.CSV != "" {
		return rows.FromCSVString(spec.CSV), nil
	}
	for _, rawRow := range spec.Rows {
		values, decodeErr := decodeValues(rawRow)
		if decodeErr != nil {
			return nil, decodeErr
		}
		rows.AddRow(values...)
	}
	return rows, nil
}

func openMock(spec queryRequest) (*sql.DB, sqlmock.Sqlmock, error) {
	options := make([]sqlmock.SqlMockOption, 0, 1)
	if spec.Matcher == "equal" {
		options = append(options, sqlmock.QueryMatcherOption(sqlmock.QueryMatcherEqual))
	}
	db, mock, err := sqlmock.New(options...)
	if err != nil {
		return nil, nil, err
	}
	return db, mock, nil
}

func query(args []json.RawMessage) (any, error) {
	spec, err := decode[queryRequest](args)
	if err != nil {
		return nil, err
	}
	db, mock, err := openMock(spec)
	if err != nil {
		return nil, err
	}
	defer db.Close()
	rows, err := makeRows(spec)
	if err != nil {
		return nil, err
	}
	expectation := mock.ExpectQuery(spec.Query)
	if spec.WithoutArgs {
		expectation.WithoutArgs()
	} else if len(spec.Args) > 0 {
		values, decodeErr := decodeValues(spec.Args)
		if decodeErr != nil {
			return nil, decodeErr
		}
		expectation.WithArgs(values...)
	}
	if spec.CloseRows {
		expectation.RowsWillBeClosed()
	}
	expectation.WillReturnRows(rows)
	actualQuery := spec.Actual
	if actualQuery == "" {
		actualQuery = spec.Query
	}
	var argsForQuery []any
	if len(spec.Args) > 0 {
		values, decodeErr := decodeValues(spec.Args)
		if decodeErr != nil {
			return nil, decodeErr
		}
		argsForQuery = make([]any, len(values))
		for index, value := range values {
			argsForQuery[index] = value
		}
	}
	dbRows, err := db.Query(actualQuery, argsForQuery...)
	if err != nil {
		return nil, err
	}
	columns, err := dbRows.Columns()
	if err != nil {
		return nil, err
	}
	resultRows := make([][]any, 0, len(spec.Rows))
	for dbRows.Next() {
		values := make([]any, len(columns))
		dest := make([]any, len(columns))
		for index := range values {
			dest[index] = &values[index]
		}
		if err := dbRows.Scan(dest...); err != nil {
			return nil, err
		}
		for index, value := range values {
			if bytes, ok := value.([]byte); ok {
				values[index] = string(bytes)
			}
		}
		resultRows = append(resultRows, values)
	}
	if err := dbRows.Close(); err != nil {
		return nil, err
	}
	if err := dbRows.Err(); err != nil {
		return nil, err
	}
	if err := mock.ExpectationsWereMet(); err != nil {
		return nil, err
	}
	return map[string]any{"columns": columns, "rows": resultRows}, nil
}

func exec(args []json.RawMessage) (any, error) {
	spec, err := decode[queryRequest](args)
	if err != nil {
		return nil, err
	}
	db, mock, err := openMock(spec)
	if err != nil {
		return nil, err
	}
	defer db.Close()
	expectation := mock.ExpectExec(spec.Query)
	values, err := decodeValues(spec.Args)
	if err != nil {
		return nil, err
	}
	if spec.WithoutArgs {
		expectation.WithoutArgs()
	} else if len(values) > 0 {
		expectation.WithArgs(values...)
	}
	expectation.WillReturnResult(sqlmock.NewResult(17, int64(len(values)+1)))
	result, err := db.Exec(spec.Query, valuesToAny(values)...)
	if err != nil {
		return nil, err
	}
	lastID, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}
	affected, err := result.RowsAffected()
	if err != nil {
		return nil, err
	}
	if err := mock.ExpectationsWereMet(); err != nil {
		return nil, err
	}
	return map[string]any{"last_insert_id": lastID, "rows_affected": affected}, nil
}

func transaction(args []json.RawMessage) (any, error) {
	spec, err := decode[queryRequest](args)
	if err != nil {
		return nil, err
	}
	db, mock, err := openMock(spec)
	if err != nil {
		return nil, err
	}
	defer db.Close()
	mock.ExpectBegin()
	mock.ExpectExec(spec.Query).WithArgs(1).WillReturnResult(sqlmock.NewResult(1, 1))
	mock.ExpectCommit()
	tx, err := db.Begin()
	if err != nil {
		return nil, err
	}
	if _, err := tx.Exec(spec.Query, 1); err != nil {
		return nil, err
	}
	if err := tx.Commit(); err != nil {
		return nil, err
	}
	if err := mock.ExpectationsWereMet(); err != nil {
		return nil, err
	}
	return map[string]any{"committed": true}, nil
}

func prepare(args []json.RawMessage) (any, error) {
	spec, err := decode[queryRequest](args)
	if err != nil {
		return nil, err
	}
	db, mock, err := openMock(spec)
	if err != nil {
		return nil, err
	}
	defer db.Close()
	rows, err := makeRows(spec)
	if err != nil {
		return nil, err
	}
	mock.ExpectPrepare(spec.Query).ExpectQuery().WithArgs(1).WillReturnRows(rows)
	stmt, err := db.Prepare(spec.Query)
	if err != nil {
		return nil, err
	}
	defer stmt.Close()
	dbRows, err := stmt.Query(1)
	if err != nil {
		return nil, err
	}
	defer dbRows.Close()
	if !dbRows.Next() {
		return nil, errors.New("prepared query returned no row")
	}
	values := make([]any, len(spec.Columns))
	dest := make([]any, len(values))
	for index := range values {
		dest[index] = &values[index]
	}
	if err := dbRows.Scan(dest...); err != nil {
		return nil, err
	}
	if err := mock.ExpectationsWereMet(); err != nil {
		return nil, err
	}
	return map[string]any{"columns": spec.Columns, "first_row": values}, nil
}

func matcher(args []json.RawMessage) (any, error) {
	spec, err := decode[queryRequest](args)
	if err != nil {
		return nil, err
	}
	var queryMatcher sqlmock.QueryMatcher
	if spec.Matcher == "equal" {
		queryMatcher = sqlmock.QueryMatcherEqual
	} else {
		queryMatcher = sqlmock.QueryMatcherRegexp
	}
	actual := spec.Actual
	if actual == "" {
		actual = spec.Query
	}
	matchErr := queryMatcher.Match(spec.Query, actual)
	result := map[string]any{"matched": matchErr == nil}
	if matchErr != nil {
		result["error"] = matchErr.Error()
	}
	return result, nil
}

func result(args []json.RawMessage) (any, error) {
	spec, err := decode[resultRequest](args)
	if err != nil {
		return nil, err
	}
	valid := sqlmock.NewResult(spec.LastInsertID, spec.RowsAffected)
	lastID, err := valid.LastInsertId()
	if err != nil {
		return nil, err
	}
	affected, err := valid.RowsAffected()
	if err != nil {
		return nil, err
	}
	failing := sqlmock.NewErrorResult(errors.New("driver failure"))
	_, lastErr := failing.LastInsertId()
	_, affectedErr := failing.RowsAffected()
	return map[string]any{
		"last_insert_id": lastID,
		"rows_affected":  affected,
		"error_result":   lastErr != nil && affectedErr != nil,
	}, nil
}

func column(args []json.RawMessage) (any, error) {
	var name string
	if len(args) != 1 || json.Unmarshal(args[0], &name) != nil || name == "" {
		return nil, errors.New("column name must be a non-empty string")
	}
	value := sqlmock.NewColumn(name).
		OfType("DECIMAL", float64(0)).
		Nullable(true).
		WithLength(32).
		WithPrecisionAndScale(10, 2)
	length, lengthOK := value.Length()
	nullable, nullableOK := value.IsNullable()
	precision, scale, precisionOK := value.PrecisionScale()
	return map[string]any{
		"name":             value.Name(),
		"db_type":          value.DbType(),
		"scan_type":        value.ScanType().String(),
		"length":           length,
		"length_ok":        lengthOK,
		"nullable":         nullable,
		"nullable_ok":      nullableOK,
		"precision":        precision,
		"scale":            scale,
		"precision_ok":     precisionOK,
	}, nil
}

func anyArg(args []json.RawMessage) (any, error) {
	values, err := decode[[]json.RawMessage](args)
	if err != nil {
		return nil, err
	}
	matcher := sqlmock.AnyArg()
	matched := make([]bool, 0, len(values))
	for _, raw := range values {
		value, decodeErr := decodeValue(raw)
		if decodeErr != nil {
			return nil, decodeErr
		}
		matched = append(matched, matcher.Match(value))
	}
	return matched, nil
}

func valuesToAny(values []driver.Value) []any {
	result := make([]any, len(values))
	for index, value := range values {
		result[index] = value
	}
	return result
}
