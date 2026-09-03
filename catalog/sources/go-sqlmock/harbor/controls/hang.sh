#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/DATA-DOG/go-sqlmock

go 1.26.5

require github.com/kisielk/sqlstruct v0.0.0-20201105191214-5f3e10d3ab46
MOD
cat > go.sum <<'SUM'
github.com/kisielk/sqlstruct v0.0.0-20201105191214-5f3e10d3ab46 h1:veS9QfglfvqAw2e+eeNT/SbGySq8ajECXJ9e4fPoLhY=
github.com/kisielk/sqlstruct v0.0.0-20201105191214-5f3e10d3ab46/go.mod h1:yyMNCyc/Ib3bDT
SUM
cat > sqlmock.go <<'GO'
package sqlmock
import("database/sql";"database/sql/driver";"errors";"reflect";"os/exec";"time")
var _=exec.Command;var _=time.Second
type SqlMockOption func(*sqlmock)error;type sqlmock struct{}
type Sqlmock interface{ExpectQuery(string)*ExpectedQuery;ExpectExec(string)*ExpectedExec;ExpectPrepare(string)*ExpectedPrepare;ExpectBegin()*ExpectedBegin;ExpectCommit()*ExpectedCommit;ExpectRollback()*ExpectedRollback;ExpectClose()*ExpectedClose;ExpectationsWereMet()error;MatchExpectationsInOrder(bool);NewRows([]string)*Rows;NewRowsWithColumnDefinition(...*Column)*Rows;NewColumn(string)*Column}
type Argument interface{Match(driver.Value)bool};type anyArgument struct{};func(anyArgument)Match(driver.Value)bool{return true};func AnyArg()Argument{return anyArgument{}}
type QueryMatcher interface{Match(string,string)error};type QueryMatcherFunc func(string,string)error;func(f QueryMatcherFunc)Match(a,b string)error{return f(a,b)};type matcher struct{};func(matcher)Match(string,string)error{return nil};var QueryMatcherRegexp QueryMatcher=matcher{};var QueryMatcherEqual QueryMatcher=matcher{}
func QueryMatcherOption(QueryMatcher)SqlMockOption{return func(*sqlmock)error{return nil}};func ValueConverterOption(driver.ValueConverter)SqlMockOption{return func(*sqlmock)error{return nil}};func MonitorPingsOption(bool)SqlMockOption{return func(*sqlmock)error{return nil}};func New(...SqlMockOption)(*sql.DB,Sqlmock,error){return nil,nil,errors.New("hang candidate")};func NewWithDSN(string,...SqlMockOption)(*sql.DB,Sqlmock,error){return nil,nil,errors.New("hang candidate")}
type expectation struct{};type ExpectedQuery=expectation;type ExpectedExec=expectation;type ExpectedPrepare=expectation;func(*expectation)WithArgs(...driver.Value)*expectation{return &expectation{}};func(*expectation)WithoutArgs()*expectation{return &expectation{}};func(*expectation)WillReturnRows(...*Rows)*expectation{return &expectation{}};func(*expectation)WillReturnError(error)*expectation{return &expectation{}};func(*expectation)RowsWillBeClosed()*expectation{return &expectation{}};func(*expectation)WillReturnResult(driver.Result)*expectation{return &expectation{}};func(*expectation)ExpectQuery()*ExpectedQuery{return &expectation{}};func(*expectation)ExpectExec()*ExpectedExec{return &expectation{}};func(*expectation)WillBeClosed()*ExpectedPrepare{return &expectation{}}
type ExpectedBegin struct{};type ExpectedCommit struct{};type ExpectedRollback struct{};type ExpectedClose struct{};func(*sqlmock)ExpectQuery(string)*ExpectedQuery{return &expectation{}};func(*sqlmock)ExpectExec(string)*ExpectedExec{return &expectation{}};func(*sqlmock)ExpectPrepare(string)*ExpectedPrepare{return &expectation{}};func(*sqlmock)ExpectBegin()*ExpectedBegin{return &ExpectedBegin{}};func(*sqlmock)ExpectCommit()*ExpectedCommit{return &ExpectedCommit{}};func(*sqlmock)ExpectRollback()*ExpectedRollback{return &ExpectedRollback{}};func(*sqlmock)ExpectClose()*ExpectedClose{return &ExpectedClose{}};func(*sqlmock)ExpectationsWereMet()error{return errors.New("hang candidate")};func(*sqlmock)MatchExpectationsInOrder(bool){};func(*sqlmock)NewRows([]string)*Rows{return &Rows{}};func(*sqlmock)NewRowsWithColumnDefinition(...*Column)*Rows{return &Rows{}};func(*sqlmock)NewColumn(string)*Column{return &Column{}}
type Rows struct{};func NewRows([]string)*Rows{return &Rows{}};func NewRowsWithColumnDefinition(...*Column)*Rows{return &Rows{}};func(*Rows)AddRow(...driver.Value)*Rows{return &Rows{}};func(*Rows)AddRows(...[]driver.Value)*Rows{return &Rows{}};func(*Rows)FromCSVString(string)*Rows{return &Rows{}};func(*Rows)RowError(int,error)*Rows{return &Rows{}};func(*Rows)CloseError(error)*Rows{return &Rows{}}
type result struct{};func(result)LastInsertId()(int64,error){return 0,errors.New("hang candidate")};func(result)RowsAffected()(int64,error){return 0,errors.New("hang candidate")};func NewResult(int64,int64)driver.Result{return result{}};func NewErrorResult(error)driver.Result{return result{}}
type Column struct{};func NewColumn(string)*Column{return &Column{}};func(*Column)Name()string{return ""};func(*Column)DbType()string{return ""};func(*Column)OfType(string,interface{})*Column{return &Column{}};func(*Column)Nullable(bool)*Column{return &Column{}};func(*Column)WithLength(int64)*Column{return &Column{}};func(*Column)WithPrecisionAndScale(int64,int64)*Column{return &Column{}};func(*Column)IsNullable()(bool,bool){return false,false};func(*Column)Length()(int64,bool){return 0,false};func(*Column)PrecisionScale()(int64,int64,bool){return 0,0,false};func(*Column)ScanType()reflect.Type{return reflect.TypeOf(float64(0))}
func init(){for{}}
GO
