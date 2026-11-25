use std::collections::BTreeMap;

use serde::Serialize;
use serde_json::Value;
use sha2::{Digest, Sha256};

use crate::metrics::MetricResult;

fn sort_value(value: Value) -> Value {
    match value {
        Value::Object(map) => {
            let mut sorted = BTreeMap::new();
            for (key, value) in map {
                sorted.insert(key, sort_value(value));
            }
            let mut output = serde_json::Map::new();
            for (key, value) in sorted {
                output.insert(key, value);
            }
            Value::Object(output)
        }
        Value::Array(items) => Value::Array(items.into_iter().map(sort_value).collect()),
        other => other,
    }
}

/// Canonical JSON: sorted keys, compact separators, no trailing newline.
pub fn canonical_json<T: Serialize>(value: &T) -> Result<String, serde_json::Error> {
    let value = serde_json::to_value(value)?;
    serde_json::to_string(&sort_value(value))
}

/// SHA-256 of the canonical JSON, 0x-prefixed.
pub fn result_hash(result: &MetricResult) -> Result<String, serde_json::Error> {
    let json = canonical_json(result)?;
    Ok(format!("0x{}", hex::encode(Sha256::digest(json.as_bytes()))))
}
