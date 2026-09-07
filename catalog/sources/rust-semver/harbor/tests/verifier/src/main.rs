// Root-only hidden checker for the rust-semver task. Compiled WITHOUT the
// candidate library: it owns every expected observation and drives the
// candidate-linked adapter over a bounded pipe protocol, so hidden assertions
// never enter any candidate-visible file.
use std::io::{BufReader, Read, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::{env, format};

const NAMES: [&str; 25] = [
    "version-parse-canonical",
    "version-leading-zero-and-structure-errors",
    "version-whitespace-and-empty-segment-errors",
    "version-overflow-and-charset-errors",
    "prerelease-and-build-metadata-acceptance",
    "ord-versus-precedence-with-build",
    "semver-precedence-chain",
    "constructors-traits-and-debug",
    "requirement-parse-canonical",
    "requirement-parse-errors",
    "comparator-normalization-projection",
    "caret-semantics",
    "tilde-semantics",
    "wildcard-and-exact-semantics",
    "comparison-operators-and-intersection",
    "prerelease-matching-rule",
    "build-metadata-ignored-in-matching",
    "prerelease-validation",
    "build-metadata-validation",
    "requirement-default-and-star",
    "error-trait-contract",
    "display-roundtrip-stability",
    "auto-trait-surface",
    "identifier-ordering",
    "comparator-level-matching",
];

const EXPECTED: [&[&str]; 25] = [
    &["1.2.3", "0.0.0", "18446744073709551615.0.1", "1.0.0-alpha", "1.0.0-alpha.1+build.4", "1.2.3+meta"],
    &["ERR:invalid leading zero in minor version number", "ERR:invalid leading zero in patch version number", "ERR:invalid leading zero in major version number", "ERR:unexpected end of input while parsing minor version number", "ERR:unexpected character '.' after patch version number", "ERR:unexpected character 'v' while parsing major version number", "ERR:empty string, expected a semver version"],
    &["ERR:unexpected character ' ' while parsing major version number", "ERR:unexpected character ' ' after patch version number", "ERR:unexpected character ' ' while parsing minor version number", "ERR:empty identifier segment in pre-release identifier", "ERR:empty identifier segment in build metadata", "ERR:empty identifier segment in pre-release identifier", "ERR:unexpected character '_' after pre-release identifier"],
    &["ERR:value of major version number exceeds u64::MAX", "ERR:unexpected character 'x' while parsing minor version number", "ERR:unexpected character 'z' while parsing patch version number"],
    &["1.0.0-0", "1.0.0-0a", "ERR:invalid leading zero in pre-release identifier", "1.0.0-alpha.beta.1", "1.0.0+build.007", "ERR:unexpected character '_' after build metadata"],
    &["lt/eq/false", "lt/lt/false", "lt/eq/false", "lt/lt/false", "lt/lt/false"],
    &["lt/lt/false", "lt/lt/false", "lt/lt/false", "lt/lt/false", "lt/lt/false", "gt/gt/false", "lt/lt/false"],
    &["1.2.3|1.2.3|true", "Version { major: 1, minor: 2, patch: 3, pre: Prerelease(\u{0022}a\u{0022}), build: BuildMetadata(\u{0022}b\u{0022}) }", "true", "true|true"],
    &["*", "^1.2", "^1.2.3", "~1.2.3", ">=1.0.0, <2.0.0", "=1.2.3", "1.*", ">=1.2.3"],
    &["ERR:unexpected character 'b' while parsing major version number", "ERR:unexpected character after wildcard in version req", "ERR:unexpected character 'x' while parsing major version number", "ERR:expected comma after patch version number, found '.'", "ERR:empty identifier segment in pre-release identifier", "ERR:unexpected end of input while parsing major version number", "^1.2.3-x", "ERR:unexpected character '>' while parsing major version number"],
    &["", "Caret:1:Some(2):None:", "Wildcard:1:None:None:", "Caret:1:Some(2):Some(3):", "Tilde:1:Some(2):Some(3):", "GreaterEq:1:Some(0):Some(0):,Less:2:Some(0):Some(0):", "Exact:1:Some(2):Some(3):", "Caret:1:Some(2):Some(3):"],
    &["true", "false", "true", "false", "false", "true", "false"],
    &["true", "true", "false", "false", "false", "true", "false"],
    &["true", "true", "true", "false", "true", "false", "true", "false"],
    &["true", "false", "true", "true", "false", "true", "true", "false", "false"],
    &["false", "true", "true", "false", "false", "false"],
    &["true", "true", ">=1.2.3", "^1.2", "true", ">=1.2.3"],
    &["alpha.1|alpha.1|false###alpha.1|alpha.1|false", "0|0|false###0|0|false", "ERR:invalid leading zero in pre-release identifier###00|00|false", "||true###||true"],
    &["ERR:invalid leading zero in pre-release identifier###build.007|build.007|false", "x-1|x-1|false###x-1|x-1|false", "ERR:unexpected character in pre-release identifier###ERR:unexpected character in build metadata", "ERR:empty identifier segment in pre-release identifier###ERR:empty identifier segment in build metadata", "-|-|false###-|-|false"],
    &["*|true", "*|0|true", "ERR:unexpected end of input while parsing major version number"],
    &["true", "true", "true", "true", "true"],
    &["0.0.4|true|true", "1.2.3-alpha.1|true|true", "9.9.9+meta|true|true", "1.0.0-beta.1+2.3|true|true"],
    &["traits-ok"],
    &["true|true", "false", "true|0", "false|alpha.1"],
    &["true", "true", "false", "true", "true", "true", "false", "ERR:unexpected character 'b' while parsing major version number"]
];

const MAX_LINE_BYTES: usize = 64 * 1024;
const LEAF_COUNT: usize = 26;


fn quote_char() -> char {
    0x22u8 as char
}

fn backslash_char() -> char {
    0x5cu8 as char
}

fn obj_open() -> char {
    0x7bu8 as char
}

fn obj_close() -> char {
    0x7du8 as char
}

fn arr_open() -> char {
    0x5bu8 as char
}

fn arr_close() -> char {
    0x5du8 as char
}

/// Serialises a JSON string using numeric escapes only, so no embedded quote or
/// backslash literal can desynchronise this file's own lexer.
fn json_string(value: &str) -> String {
    let quote = quote_char();
    let backslash = backslash_char();
    let mut out = String::new();
    out.push(quote);
    for ch in value.chars() {
        if ch == quote || ch == backslash {
            out.push(backslash);
            out.push(ch);
        } else if (ch as u32) < 0x20 {
            out.push(' ');
        } else {
            out.push(ch);
        }
    }
    out.push(quote);
    out
}

fn pair(key: &str, value: &str) -> String {
    json_string(key) + ":" + &json_string(value)
}

fn leaf_json(id: &str, status: &str, message: Option<&str>) -> String {
    let mut parts = vec![pair("id", id), pair("status", status)];
    if let Some(text) = message {
        parts.push(pair("message", text));
    }
    obj_open().to_string() + &parts.join(",") + &obj_close().to_string()
}

struct Adapter {
    child: Child,
    stdin: ChildStdin,
    stdout: BufReader<ChildStdout>,
}

impl Adapter {
    fn start() -> Result<Self, String> {
        let path = env::var("NL2REPO_RUST_ADAPTER").map_err(|e| e.to_string())?;
        let mut child = Command::new("runuser")
            .args(["-u", "candidate", "--", &path])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .map_err(|e| e.to_string())?;
        let stdin = child.stdin.take().ok_or("adapter stdin unavailable")?;
        let stdout = child.stdout.take().ok_or("adapter stdout unavailable")?;
        Ok(Self {
            child,
            stdin,
            stdout: BufReader::new(stdout),
        })
    }

    /// Reads exactly one newline-terminated response and refuses to grow past a
    /// fixed bound, so a hostile adapter cannot exhaust the checker.
    fn call(&mut self, code: u8) -> Result<Vec<String>, String> {
        writeln!(self.stdin, "{}", code).map_err(|e| e.to_string())?;
        self.stdin.flush().map_err(|e| e.to_string())?;
        let mut line = Vec::new();
        loop {
            let mut byte = [0u8; 1];
            let read = self.stdout.read(&mut byte).map_err(|e| e.to_string())?;
            if read == 0 {
                return Err("adapter closed the response stream".into());
            }
            if byte[0] == b'\n' {
                break;
            }
            line.push(byte[0]);
            if line.len() > MAX_LINE_BYTES {
                return Err("adapter response exceeded the bound".into());
            }
        }
        let text = String::from_utf8(line).map_err(|e| e.to_string())?;
        let mut parts = text.trim_end_matches('\r').split('|');
        if parts.next() != Some("ok") {
            return Err("adapter reported a failure".into());
        }
        parts
            .map(|field| {
                if field.len() % 2 != 0 {
                    return Err("odd-length hex field".into());
                }
                let bytes = (0..field.len())
                    .step_by(2)
                    .map(|index| {
                        u8::from_str_radix(&field[index..index + 2], 16)
                            .map_err(|e| e.to_string())
                    })
                    .collect::<Result<Vec<_>, _>>()?;
                String::from_utf8(bytes).map_err(|e| e.to_string())
            })
            .collect()
    }
}

impl Drop for Adapter {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

fn evaluate(adapter: &mut Adapter) -> Vec<Result<(), String>> {
    let mut results = Vec::with_capacity(NAMES.len());
    for code in 1..=NAMES.len() as u8 {
        let expected = EXPECTED[(code - 1) as usize];
        results.push(
            adapter
                .call(code)
                .and_then(|observed| {
                    if observed.len() != expected.len() {
                        return Err(format!(
                            "expected {} observations, received {}",
                            expected.len(),
                            observed.len()
                        ));
                    }
                    for (index, (got, want)) in observed.iter().zip(expected.iter()).enumerate() {
                        if got != want {
                            return Err(format!("observation {} differs from the expected value", index));
                        }
                    }
                    Ok(())
                }),
        );
    }
    results
}

fn emit(results: &[Result<(), String>]) {
    let mut out = String::new();
    out.push(obj_open());
    out.push_str(&pair("schema_version", "1.0"));
    out.push(',');
    out.push_str(&pair("framework", "rust"));
    out.push(',');
    out.push_str(&pair("report_format", "rust-semver-bridge-v1"));
    out.push(',');
    out.push_str(&json_string("leaves"));
    out.push(':');
    out.push(arr_open());
    // Always report the full frozen denominator, even when the adapter died
    // early: unscored leaves become explicit failures.
    for index in 0..LEAF_COUNT {
        if index > 0 {
            out.push(',');
        }
        if index < NAMES.len() {
            let id = format!("semver.{}", NAMES[index]);
            match results.get(index) {
                Some(Ok(())) => out.push_str(&leaf_json(&id, "passed", None)),
                Some(Err(message)) => {
                    let trimmed: String = message.chars().take(200).collect();
                    out.push_str(&leaf_json(&id, "failed", Some(&trimmed)));
                }
                None => {
                    out.push_str(&leaf_json(&id, "failed", Some("scenario not evaluated")));
                }
            }
        } else {
            // The no-std feature leaf is re-decided by run.py from its own
            // offline cargo check; this placeholder cannot raise a score.
            out.push_str(&leaf_json("semver.feature-compatibility", "failed", None));
        }
    }
    out.push(arr_close());
    out.push(obj_close());
    println!("{}", out);
}

fn main() {
    match Adapter::start() {
        Ok(mut adapter) => {
            let results = evaluate(&mut adapter);
            emit(&results);
        }
        Err(error) => {
            eprintln!("adapter launch failed");
            let trimmed: String = error.chars().take(200).collect();
            let results = vec![Err(trimmed); NAMES.len()];
            emit(&results);
        }
    }
}
