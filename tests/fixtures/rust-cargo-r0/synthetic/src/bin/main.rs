fn main() {
    let values: Vec<i64> = std::env::args()
        .skip(1)
        .map(|value| value.parse().expect("arguments must be integers"))
        .collect();
    let (count, total) = nl2repo_rust_synthetic::summarize(&values);
    println!("{count}:{total}");
}
