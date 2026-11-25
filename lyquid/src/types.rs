use serde::{Deserialize, Serialize};

use crate::metrics::MetricResult;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct IndexRequest {
    pub contract: String,
    pub metric: String,
    pub from_block: u64,
    pub to_block: u64,
}

impl IndexRequest {
    pub fn key(&self) -> String {
        format!(
            "{}:{}:{}:{}",
            self.metric, self.contract, self.from_block, self.to_block
        )
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Proposal {
    pub request: IndexRequest,
    pub result: MetricResult,
    pub result_hash: String,
    pub node_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FinalizedResult {
    pub request: IndexRequest,
    pub result: MetricResult,
    pub result_hash: String,
    pub signers: Vec<String>,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ResultRecord {
    pub result_hash: String,
    pub contract: String,
    pub metric: String,
    pub from_block: u64,
    pub to_block: u64,
    pub event_count: u64,
    pub value: String,
    pub quorum: u16,
    pub timestamp: u64,
    pub signers: Vec<String>,
}

impl ResultRecord {
    pub fn key(metric: &str, contract: &str, from_block: u64, to_block: u64) -> String {
        format!("{metric}:{contract}:{from_block}:{to_block}")
    }
}
