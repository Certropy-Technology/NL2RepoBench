pub fn summarize(values: &[i64]) -> (usize, i64) {
    (values.len(), values.iter().sum())
}

pub async fn normalize_async(values: Vec<String>) -> Vec<String> {
    values
        .into_iter()
        .map(|value| value.trim().to_lowercase())
        .collect()
}

#[cfg(test)]
mod tests {
    use super::summarize;

    #[test]
    fn summarizes_values() {
        assert_eq!(summarize(&[2, 3, 5]), (3, 10));
    }
}
