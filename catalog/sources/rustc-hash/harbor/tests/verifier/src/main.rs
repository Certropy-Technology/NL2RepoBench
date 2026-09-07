use std::io::{BufRead, BufReader, Write};
use std::process::{Command, Stdio};

const NAMES: [&str; 24] = [
    "default-hasher-bytes", "typed-integer-hashing", "signed-integer-hashing",
    "empty-and-unicode-bytes", "seeded-hasher", "build-hasher-determinism",
    "map-insertion-lookup", "map-replacement-removal", "set-insertion",
    "set-membership-removal", "map-iteration", "set-iteration", "clone-seeded-state",
    "different-seeds", "u8-u16-widths", "u32-u64-widths", "u128-usize-widths",
    "repeated-finish", "hasher-independence", "default-aliases", "seeded-aliases",
    "no-std-feature", "hash-trait-use", "stable-report-collection",
];

fn main() {
    let adapter = std::env::var("NL2REPO_RUST_ADAPTER").expect("adapter path");
    let mut child = Command::new(adapter).stdin(Stdio::piped()).stdout(Stdio::piped()).spawn().expect("adapter");
    let mut input = child.stdin.take().unwrap();
    for i in 1..=24 { writeln!(input, "{i}").unwrap(); }
    drop(input);
    let output = child.wait_with_output().expect("adapter output");
    let lines: Vec<_> = BufReader::new(output.stdout.as_slice()).lines().collect::<Result<_, _>>().unwrap();
    let mut out = String::from("{\"schema_version\":\"1.0\",\"framework\":\"rust-harness\",\"report_format\":\"rust-bridge-json-v1\",\"collected\":24,\"leaves\":[");
    for (i, name) in NAMES.iter().enumerate() {
        if i > 0 { out.push(','); }
        let passed = lines.get(i).map(|x| x == "ok").unwrap_or(false);
        out.push_str(&format!("{{\"leaf_id\":\"rustc-hash.{name}\",\"status\":\"{}\",\"duration_ms\":0.0,\"details\":null}}", if passed { "passed" } else { "failed" }));
    }
    out.push_str("],\"collection_errors\":[],\"runner_exit_code\":0}");
    println!("{out}");
}
