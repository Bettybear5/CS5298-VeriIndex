use serde::{Deserialize, Serialize};
use serde_json::Value;
use thiserror::Error;

pub const METRICS: [&str; 5] = [
    "event_count",
    "deposit_total",
    "withdraw_total",
    "swap_volume",
    "unique_senders",
];

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct EventLog {
    #[serde(rename = "blockNumber")]
    pub block_number: u64,
    #[serde(rename = "transactionHash")]
    pub transaction_hash: String,
    #[serde(rename = "logIndex")]
    pub log_index: u64,
    pub address: String,
    pub event: String,
    pub args: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct MetricResult {
    pub schema_version: u8,
    pub chain_id: u64,
    pub contract: String,
    pub metric: String,
    pub from_block: u64,
    pub to_block: u64,
    pub event_count: u64,
    pub value: String,
}

#[derive(Debug, Error)]
pub enum MetricError {
    #[error("unknown metric: {0}")]
    UnknownMetric(String),
    #[error("from_block must be <= to_block")]
    InvalidRange,
    #[error("invalid integer in event args")]
    InvalidInteger,
}

fn parse_int(value: Option<&Value>) -> Result<u64, MetricError> {
    match value {
        Some(Value::String(raw)) => raw
            .parse::<u64>()
            .map_err(|_| MetricError::InvalidInteger),
        Some(Value::Number(number)) => number
            .as_u64()
            .ok_or(MetricError::InvalidInteger),
        _ => Ok(0),
    }
}

fn dedupe(logs: &[EventLog]) -> Vec<&EventLog> {
    let mut seen = std::collections::BTreeSet::new();
    let mut out = Vec::new();
    for log in logs {
        let key = (log.transaction_hash.to_lowercase(), log.log_index);
        if seen.insert(key) {
            out.push(log);
        }
    }
    out
}

pub fn filter_logs<'a>(
    logs: &'a [EventLog],
    contract: &str,
    from_block: u64,
    to_block: u64,
) -> Result<Vec<&'a EventLog>, MetricError> {
    if from_block > to_block {
        return Err(MetricError::InvalidRange);
    }
    let target = contract.to_lowercase();
    Ok(logs
        .iter()
        .filter(|log| {
            log.address.to_lowercase() == target
                && from_block <= log.block_number
                && log.block_number <= to_block
        })
        .collect())
}

pub fn compute_metric(logs: &[EventLog], metric: &str) -> Result<u64, MetricError> {
    if !METRICS.contains(&metric) {
        return Err(MetricError::UnknownMetric(metric.to_string()));
    }
    let unique = dedupe(logs);
    match metric {
        "event_count" => Ok(unique.len() as u64),
        "deposit_total" => {
            let mut total = 0u64;
            for log in unique.iter().filter(|log| log.event == "Deposit") {
                total += parse_int(log.args.get("amount"))?;
            }
            Ok(total)
        }
        "withdraw_total" => {
            let mut total = 0u64;
            for log in unique.iter().filter(|log| log.event == "Withdraw") {
                total += parse_int(log.args.get("amount"))?;
            }
            Ok(total)
        }
        "swap_volume" => {
            let mut total = 0u64;
            for log in unique.iter().filter(|log| log.event == "Swap") {
                total += parse_int(log.args.get("amountIn"))?;
            }
            Ok(total)
        }
        "unique_senders" => {
            let senders: std::collections::BTreeSet<String> = unique
                .iter()
                .filter_map(|log| log.args.get("from"))
                .filter_map(|value| value.as_str())
                .map(|value| value.to_lowercase())
                .collect();
            Ok(senders.len() as u64)
        }
        _ => Err(MetricError::UnknownMetric(metric.to_string())),
    }
}

pub fn build_result(
    logs: &[EventLog],
    metric: &str,
    contract: &str,
    from_block: u64,
    to_block: u64,
    chain_id: u64,
) -> Result<MetricResult, MetricError> {
    let filtered = filter_logs(logs, contract, from_block, to_block)?;
    let value = compute_metric(
        &filtered.iter().map(|log| (*log).clone()).collect::<Vec<_>>(),
        metric,
    )?;
    let event_count = compute_metric(
        &filtered.iter().map(|log| (*log).clone()).collect::<Vec<_>>(),
        "event_count",
    )?;
    Ok(MetricResult {
        schema_version: 1,
        chain_id,
        contract: contract.to_lowercase(),
        metric: metric.to_string(),
        from_block,
        to_block,
        event_count,
        value: value.to_string(),
    })
}
