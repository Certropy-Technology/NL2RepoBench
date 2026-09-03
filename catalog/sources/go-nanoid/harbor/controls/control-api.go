package gonanoid

var AlphaNum = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
var Alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
var AlphaLowerNum = "abcdefghijklmnopqrstuvwxyz0123456789"
var AlphaUpperNum = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
var AlphaLower = "abcdefghijklmnopqrstuvwxyz"
var AlphaUpper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
var Numeric = "0123456789"
var CrockfordBase32Upper = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
var CrockfordBase32Lower = "0123456789abcdefghjkmnpqrstvwxyz"

func Generate(string, int) (string, error) { return "", nil }
func MustGenerate(string, int) string { return "" }
func New(...int) (string, error) { return "", nil }
func Must(...int) string { return "" }
