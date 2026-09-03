package govalidator

type Validator func(string) bool

func IsEmail(string) bool                          { return false }
func IsURL(string) bool                            { return false }
func IsRequestURL(string) bool                     { return false }
func IsRequestURI(string) bool                     { return false }
func IsAlpha(string) bool                          { return false }
func IsUTFLetter(string) bool                      { return false }
func IsAlphanumeric(string) bool                   { return false }
func IsUTFLetterNumeric(string) bool               { return false }
func IsNumeric(string) bool                        { return false }
func IsUTFNumeric(string) bool                     { return false }
func IsUTFDigit(string) bool                       { return false }
func IsInt(string) bool                            { return false }
func IsFloat(string) bool                          { return false }
func IsNull(string) bool                           { return false }
func IsNotNull(string) bool                        { return false }
func IsASCII(string) bool                          { return false }
func IsPrintableASCII(string) bool                 { return false }
func IsBase64(string) bool                         { return false }
func IsDNSName(string) bool                        { return false }
func IsIP(string) bool                             { return false }
func IsIPv4(string) bool                           { return false }
func IsIPv6(string) bool                           { return false }
func IsPort(string) bool                           { return false }
func IsMAC(string) bool                            { return false }
func IsHost(string) bool                           { return false }
func IsUUID(string) bool                           { return false }
func IsUUIDv3(string) bool                         { return false }
func IsUUIDv4(string) bool                         { return false }
func IsUUIDv5(string) bool                         { return false }
func IsJSON(string) bool                           { return false }
func IsHexadecimal(string) bool                    { return false }
func IsHexcolor(string) bool                       { return false }
func IsRGBcolor(string) bool                       { return false }
func IsLatitude(string) bool                       { return false }
func IsLongitude(string) bool                      { return false }
func Contains(string, string) bool                 { return false }
func Matches(string, string) bool                  { return false }
func Trim(string, string) string                   { return "" }
func LeftTrim(string, string) string               { return "" }
func RightTrim(string, string) string              { return "" }
func BlackList(string, string) string              { return "" }
func WhiteList(string, string) string              { return "" }
func StripLow(string, bool) string                 { return "" }
func ReplacePattern(string, string, string) string { return "" }
func CamelCaseToUnderscore(string) string          { return "" }
func UnderscoreToCamelCase(string) string          { return "" }
func Reverse(string) string                        { return "" }
func SafeFileName(string) string                   { return "" }
func NormalizeEmail(string) (string, error)        { return "", nil }
func GetLines(string) []string                     { return nil }
func GetLine(string, int) (string, error)          { return "", nil }
func ToString(any) string                          { return "" }
func ToJSON(any) (string, error)                   { return "", nil }
func ToFloat(any) (float64, error)                 { return 0, nil }
func ToInt(any) (int64, error)                     { return 0, nil }
func ToBoolean(string) (bool, error)               { return false, nil }
