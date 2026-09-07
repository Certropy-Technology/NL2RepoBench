// Candidate-linked adapter. Reads numeric operation codes on stdin and writes
// one line of hex-encoded observations per code. It contains no expected values.
use semver::{BuildMetadata, Comparator, Op, Prerelease, Version, VersionReq};
use std::io::{self, BufRead, Write};
use std::panic::{catch_unwind, AssertUnwindSafe};

const MAX_VALUE_BYTES: usize = 8 * 1024;

fn hex(s: &[u8]) -> String {
    s.iter().map(|b| format!("{b:02x}")).collect()
}

fn emit(values: &[String]) {
    let mut line = String::from("ok");
    for v in values {
        if v.len() > MAX_VALUE_BYTES {
            println!("truncated");
            let _ = io::stdout().flush();
            return;
        }
        let encoded = hex(v.as_bytes());
        if line.len() + encoded.len() + 1 > MAX_VALUE_BYTES {
            println!("truncated");
            let _ = io::stdout().flush();
            return;
        }
        line.push('|');
        line.push_str(&encoded);
    }
    line.push('\n');
    print!("{line}");
    let _ = io::stdout().flush();
}

fn p(text: &str) -> String {
    match Version::parse(text) {
        Ok(v) => format!("{v}"),
        Err(e) => format!("ERR:{e}"),
    }
}

fn q(text: &str) -> String {
    match VersionReq::parse(text) {
        Ok(r) => format!("{r}"),
        Err(e) => format!("ERR:{e}"),
    }
}

fn cmp_text(a: &str, b: &str) -> String {
    let x = Version::parse(a).unwrap();
    let y = Version::parse(b).unwrap();
    let ord = match x.cmp(&y) {
        std::cmp::Ordering::Less => "lt",
        std::cmp::Ordering::Equal => "eq",
        std::cmp::Ordering::Greater => "gt",
    };
    let prec = match x.cmp_precedence(&y) {
        std::cmp::Ordering::Less => "lt",
        std::cmp::Ordering::Equal => "eq",
        std::cmp::Ordering::Greater => "gt",
    };
    format!("{ord}/{prec}/{}", x == y)
}

fn matches(req: &str, ver: &str) -> String {
    match (VersionReq::parse(req), Version::parse(ver)) {
        (Ok(r), Ok(v)) => format!("{}", r.matches(&v)),
        (Err(e), _) => format!("ERR:{e}"),
        (_, Err(e)) => format!("ERR:{e}"),
    }
}

fn ident(text: &str) -> String {
    let pre = match Prerelease::new(text) {
        Ok(v) => format!("{}|{}|{}", v, v.as_str(), v.is_empty()),
        Err(e) => format!("ERR:{e}"),
    };
    let build = match BuildMetadata::new(text) {
        Ok(v) => format!("{}|{}|{}", v, v.as_str(), v.is_empty()),
        Err(e) => format!("ERR:{e}"),
    };
    format!("{pre}###{build}")
}

fn cmp_matches(text: &str, ver: &str) -> String {
    match (Comparator::parse(text), Version::parse(ver)) {
        (Ok(c), Ok(v)) => format!("{}", c.matches(&v)),
        (Err(e), _) => format!("ERR:{e}"),
        (_, Err(e)) => format!("ERR:{e}"),
    }
}

fn req_parts(text: &str) -> String {
    match VersionReq::parse(text) {
        Ok(r) => r
            .comparators
            .iter()
            .map(|c| {
                let op = match c.op {
                    Op::Exact => "Exact",
                    Op::Greater => "Greater",
                    Op::GreaterEq => "GreaterEq",
                    Op::Less => "Less",
                    Op::LessEq => "LessEq",
                    Op::Tilde => "Tilde",
                    Op::Caret => "Caret",
                    Op::Wildcard => "Wildcard",
                    _ => "Other",
                };
                format!(
                    "{}:{}:{:?}:{:?}:{}",
                    op,
                    c.major,
                    c.minor,
                    c.patch,
                    c.pre
                )
            })
            .collect::<Vec<_>>()
            .join(","),
        Err(e) => format!("ERR:{e}"),
    }
}

fn op_code(n: u8) -> Result<Vec<String>, String> {
    Ok(match n {
        // Version parse and canonical display.
        1 => vec![
            p("1.2.3"),
            p("0.0.0"),
            p("18446744073709551615.0.1"),
            p("1.0.0-alpha"),
            p("1.0.0-alpha.1+build.4"),
            p("1.2.3+meta"),
        ],
        // Version parse rejection: numeric/leading-zero/structural.
        2 => vec![
            p("1.02.3"),
            p("1.2.03"),
            p("01.2.3"),
            p("1.2"),
            p("1.2.3.4"),
            p("v1.2.3"),
            p(""),
        ],
        // Version parse rejection: whitespace, charset, empty identifiers.
        3 => vec![
            p(" 1.2.3"),
            p("1.2.3 "),
            p("1. 2.3"),
            p("1.2.3-"),
            p("1.2.3+"),
            p("1.2.3-alpha..1"),
            p("1.2.3-al_pha"),
        ],
        // Numeric overflow and non-numeric component.
        4 => vec![
            p("18446744073709551616.0.0"),
            p("1.x.3"),
            p("1.2.z"),
        ],
        // Prerelease and build metadata parsing rules.
        5 => vec![
            p("1.0.0-0"),
            p("1.0.0-0a"),
            p("1.0.0-00"),
            p("1.0.0-alpha.beta.1"),
            p("1.0.0+build.007"),
            p("1.0.0+build-1_x"),
        ],
        // Ordering: build ignored by Ord, prerelease before release.
        6 => vec![
            cmp_text("1.0.0", "1.0.0+build"),
            cmp_text("1.0.0-alpha", "1.0.0"),
            cmp_text("1.0.0-alpha", "1.0.0-alpha+meta"),
            cmp_text("1.0.0-alpha.2", "1.0.0-alpha.10"),
            cmp_text("1.0.0-alpha.1", "1.0.0-alpha.1.0"),
        ],
        // Precedence chain and release-field ordering.
        7 => vec![
            cmp_text("1.0.0-alpha", "1.0.0-alpha.1"),
            cmp_text("1.0.0-alpha.1", "1.0.0-alpha.beta"),
            cmp_text("1.0.0-alpha.beta", "1.0.0-beta"),
            cmp_text("1.0.0-beta.2", "1.0.0-beta.11"),
            cmp_text("1.0.0-beta.11", "1.0.0-rc.1"),
            cmp_text("2.0.0", "1.99.99"),
            cmp_text("1.0.0", "1.0.1"),
        ],
        // Version::new, Display/Debug/FromStr, hashing equality.
        8 => {
            let v = Version::new(1, 2, 3);
            let a: Version = "1.2.3".parse().unwrap();
            let mut h1 = std::collections::hash_map::DefaultHasher::default();
            let mut h2 = std::collections::hash_map::DefaultHasher::default();
            use std::hash::{Hash, Hasher};
            v.hash(&mut h1);
            a.hash(&mut h2);
            vec![
                format!("{v}|{a}|{}", v == a),
                format!("{:?}", Version::parse("1.2.3-a+b").unwrap()),
                format!("{}", h1.finish() == h2.finish()),
                format!("{}|{}", v.pre.is_empty(), v.build.is_empty()),
            ]
        }
        // Requirement parsing and canonical display.
        9 => vec![
            q("*"),
            q("1.2"),
            q("^1.2.3"),
            q("~1.2.3"),
            q(">=1.0.0, <2.0.0"),
            q("=1.2.3"),
            q("1.x"),
            q(">= 1.2.3"),
        ],
        // Requirement parse rejection.
        10 => vec![
            q("bad"),
            q("**"),
            q(">=x"),
            q("1.2.3.4"),
            q("<1.0.0-"),
            q("^"),
            q("1.2.3-x"),
            q("=>1.2.3"),
        ],
        // Comparator field projection after normalization.
        11 => vec![
            req_parts("*"),
            req_parts("1.2"),
            req_parts("1.x"),
            req_parts("^1.2.3"),
            req_parts("~1.2.3"),
            req_parts(">=1.0.0, <2.0.0"),
            req_parts("=1.2.3"),
            req_parts("1.2.3"),
        ],
        // Caret semantics.
        12 => vec![
            matches("^1.2.3", "1.2.3"),
            matches("^1.2.3", "1.2.2"),
            matches("^1.2.3", "1.9.0"),
            matches("^1.2.3", "2.0.0"),
            matches("^0.2.3", "0.3.0"),
            matches("^0.2.3", "0.2.9"),
            matches("^0.0.3", "0.0.4"),
        ],
        // Tilde semantics.
        13 => vec![
            matches("~1.2.3", "1.2.3"),
            matches("~1.2.3", "1.2.9"),
            matches("~1.2.3", "1.3.0"),
            matches("~1.2", "1.9.9"),
            matches("~1.2", "2.0.0"),
            matches("~1", "1.9.9"),
            matches("~1", "2.0.0"),
        ],
        // Wildcard and exact semantics.
        14 => vec![
            matches("*", "0.0.0"),
            matches("*", "99.0.0"),
            matches("1.x", "1.9.9"),
            matches("1.x", "2.0.0"),
            matches("1.2.x", "1.2.9"),
            matches("1.2.x", "1.3.0"),
            matches("=1.2.3", "1.2.3"),
            matches("=1.2.3", "1.2.4"),
        ],
        // Comparison operators and intersections.
        15 => vec![
            matches(">1.2.3", "1.2.4"),
            matches(">1.2.3", "1.2.3"),
            matches(">=1.2.3", "1.2.3"),
            matches("<1.2.3", "1.2.2"),
            matches("<1.2.3", "1.2.3"),
            matches("<=1.2.3", "1.2.3"),
            matches(">=1.0.0, <2.0.0", "1.5.0"),
            matches(">=1.0.0, <2.0.0", "2.0.0"),
            matches(">=1.0.0, <1.0.0", "1.0.0"),
        ],
        // Prerelease matching rule against requirements.
        16 => vec![
            matches("^1.2.3", "1.2.3-alpha"),
            matches("^1.2.3-alpha", "1.2.3-beta"),
            matches("^1.2.3-alpha", "1.2.4"),
            matches(">=1.0.0", "1.0.1-alpha"),
            matches(">=1.0.0-alpha", "1.0.1-beta"),
            matches("*", "1.0.0-alpha"),
        ],
        // Build metadata ignored by matching; comparator Display.
        17 => vec![
            matches("^1.2.3", "1.2.3+build"),
            matches("=1.2.3", "1.2.3+meta"),
            format!("{}", Comparator::parse(">=1.2.3").unwrap()),
            format!("{}", Comparator::parse("^1.2").unwrap()),
            matches(">=1.2.3+bld", "1.2.4"),
            q(">=1.2.3+bld"),
        ],
        // Prerelease and BuildMetadata validation and Display.
        18 => vec![ident("alpha.1"), ident("0"), ident("00"), ident("")],
        19 => vec![
            ident("build.007"),
            ident("x-1"),
            ident("bad_char"),
            ident("alpha..1"),
            ident("-"),
        ],
        // VersionReq default, STAR, and empty-comparator behaviour.
        20 => {
            let star = VersionReq::STAR;
            let def = VersionReq::default();
            vec![
                format!("{star}|{}", star.matches(&Version::parse("7.7.7").unwrap())),
                format!("{def}|{}|{}", def.comparators.len(), def.matches(&Version::parse("1.0.0").unwrap())),
                format!("{}", VersionReq::parse("  ").map(|r| format!("ok:{}", r.matches(&Version::parse("1.0.0").unwrap()))).unwrap_or_else(|e| format!("ERR:{e}"))),
            ]
        }
        // Error Display text is stable and Clone/Eq usable.
        21 => {
            let e1 = Version::parse("1.2").unwrap_err();
            let e2 = Version::parse("1.2").unwrap_err();
            let disp = format!("{e1}");
            let dbg = format!("{e1:?}");
            vec![
                // Display is non-empty and deterministic across two parses.
                format!("{}", !disp.is_empty()),
                format!("{}", disp == format!("{e2}")),
                // Published invariant: Debug wraps the Display text.
                format!("{}", dbg == format!("Error(\"{disp}\")")),
                // std::error::Error is implemented with the std feature.
                {
                    let b: &dyn std::error::Error = &e1;
                    format!("{}", !b.to_string().is_empty())
                },
                format!("{}", VersionReq::parse("~").is_err()),
            ]
        }
        // Round-trip and inverse ordering consistency.
        22 => {
            let cases = ["0.0.4", "1.2.3-alpha.1", "9.9.9+meta", "1.0.0-beta.1+2.3"];
            cases
                .iter()
                .map(|t| {
                    let v = Version::parse(t).unwrap();
                    let back = Version::parse(&v.to_string()).unwrap();
                    format!("{v}|{}|{}", back == v, v.cmp(&back) == std::cmp::Ordering::Equal)
                })
                .collect()
        }
        // Public trait surface exposed by the candidate (Send/Sync/Unpin).
        23 => {
            fn assert_all<T: Send + Sync + Unpin + Clone + Eq + std::hash::Hash + core::fmt::Debug>() {}
            assert_all::<Version>();
            assert_all::<VersionReq>();
            assert_all::<Comparator>();
            assert_all::<Prerelease>();
            assert_all::<BuildMetadata>();
            assert_all::<Op>();
            vec![String::from("traits-ok")]
        }
        // Identifier module surface: PartialEq/Ord on Prerelease alone.
        24 => {
            let a = Prerelease::new("alpha.1").unwrap();
            let b = Prerelease::new("alpha.2").unwrap();
            let c = Prerelease::new("beta").unwrap();
            let z = Prerelease::EMPTY;
            vec![
                format!("{}|{}", a < b, b < c),
                format!("{}", a == c),
                format!("{}|{}", z.is_empty(), z.as_str().len()),
                format!("{}|{}", a.is_empty(), a.as_str()),
            ]
        }
        // Comparator-level matching: a distinct public path from VersionReq.
        25 => vec![
            cmp_matches(">=1.2.3", "1.2.4"),
            cmp_matches(">=1.2.3", "1.2.3"),
            cmp_matches("^1.2.3", "1.2.3-alpha"),
            cmp_matches("^1.2.3-alpha", "1.2.3-beta"),
            cmp_matches("=1.2.3", "1.2.3+meta"),
            cmp_matches("1.x", "1.9.9"),
            cmp_matches("1.x", "2.0.0"),
            cmp_matches("bad", "1.0.0"),
        ],
        _ => return Err("unknown operation".into()),
    })
}

fn main() {
    for line in io::stdin().lock().lines() {
        let code: Option<u8> = line.ok().and_then(|x| x.trim().parse().ok());
        match code {
            Some(n) => {
                let values = match catch_unwind(AssertUnwindSafe(|| op_code(n))) {
                    Ok(Ok(v)) => v,
                    Ok(Err(e)) => vec![format!("ERR:{e}")],
                    Err(_) => vec![String::from("PANIC")],
                };
                emit(&values);
            }
            None => emit(&[String::from("ERR:invalid operation")]),
        }
    }
}
