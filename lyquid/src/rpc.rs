//! Minimal Ethereum JSON-RPC log fetcher and event decoder.
//!
//! The decoder handles the three events emitted by `EventSource.sol`. It
//! intentionally avoids an ABI dependency so the Lyquid crate stays small and
//! deterministic. Topic hashes are keccak256 of the canonical event signatures.

use lyquid::http::{Header, Method, Request, RequestOptions};
use lyquid::prelude::*;
use serde_json::{json, Value};

use crate::canonical::result_hash;
use crate::metrics::{build_result, EventLog};
use crate::types::{IndexRequest, Proposal};

const TOPIC_DEPOSIT: &str = "0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c";
const TOPIC_WITHDRAW: &str = "0x884edad9ce6fa2440d8a54cc123490eb96d2768479d49ff9c7366125a9424364";
const TOPIC_SWAP: &str = "0xcd3829a3813dc3cdd188fd3d01dcf3268c16be2fdd2dd21d0665418816e46062";

fn rpc(rpc_url: &str, method: &str, params: Value) -> LyquidResult<Value> {
    let body = json!({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    });
    let request = Request {
        method: Method::Post,
        url: rpc_url.to_string(),
        headers: vec![Header {
            name: "content-type".into(),
            value: b"application/json".to_vec(),
        }],
        body: Some(
            serde_json::to_vec(&body)
                .map_err(|error| LyquidError::LyquorRuntime(format!("JSON encode failed: {error}")))?,
        ),
    };
    let response = lyquor_api::http_request(
        request,
        Some(RequestOptions {
            timeout_ms: Some(10_000),
        }),
    )?;
    if response.status != 200 {
        return Err(LyquidError::LyquorRuntime(format!(
            "RPC HTTP status {}",
            response.status
        )));
    }
    let value: Value = serde_json::from_slice(&response.body)
        .map_err(|error| LyquidError::LyquorRuntime(format!("RPC JSON decode failed: {error}")))?;
    if let Some(error) = value.get("error") {
        return Err(LyquidError::LyquorRuntime(format!("RPC error: {error}")));
    }
    Ok(value.get("result").cloned().unwrap_or(Value::Null))
}

fn parse_hex_u64(value: &Value) -> LyquidResult<u64> {
    let raw = value
        .as_str()
        .ok_or_else(|| LyquidError::LyquorRuntime("expected hex string".into()))?;
    let trimmed = raw.strip_prefix("0x").unwrap_or(raw);
    u64::from_str_radix(trimmed, 16)
        .map_err(|error| LyquidError::LyquorRuntime(format!("invalid hex integer: {error}")))
}

fn hex_bytes(value: &Value) -> LyquidResult<Vec<u8>> {
    let raw = value
        .as_str()
        .ok_or_else(|| LyquidError::LyquorRuntime("expected hex string".into()))?;
    let trimmed = raw.strip_prefix("0x").unwrap_or(raw);
    hex::decode(trimmed)
        .map_err(|error| LyquidError::LyquorRuntime(format!("invalid hex bytes: {error}")))
}

fn word(data: &[u8], index: usize) -> u64 {
    let start = index * 32;
    if data.len() < start + 32 {
        return 0;
    }
    let mut bytes = [0u8; 8];
    bytes.copy_from_slice(&data[start + 24..start + 32]);
    u64::from_be_bytes(bytes)
}

fn address_from_topic(topic: &Value) -> LyquidResult<String> {
    let bytes = hex_bytes(topic)?;
    if bytes.len() < 20 {
        return Err(LyquidError::LyquorRuntime("topic shorter than address".into()));
    }
    Ok(format!("0x{}", hex::encode(&bytes[bytes.len() - 20..])))
}

fn parse_log(log: &Value) -> LyquidResult<Option<EventLog>> {
    let topics = log
        .get("topics")
        .and_then(Value::as_array)
        .ok_or_else(|| LyquidError::LyquorRuntime("log has no topics".into()))?;
    let Some(topic0) = topics.first() else {
        return Ok(None);
    };
    let topic0 = topic0.as_str().unwrap_or_default().to_lowercase();
    let data = hex_bytes(log.get("data").unwrap_or(&Value::Null))?;

    let (event, args) = match topic0.as_str() {
        TOPIC_DEPOSIT => {
            if topics.len() < 2 {
                return Ok(None);
            }
            (
                "Deposit",
                json!({
                    "from": address_from_topic(&topics[1])?,
                    "amount": word(&data, 0).to_string(),
                }),
            )
        }
        TOPIC_WITHDRAW => {
            if topics.len() < 2 {
                return Ok(None);
            }
            (
                "Withdraw",
                json!({
                    "from": address_from_topic(&topics[1])?,
                    "amount": word(&data, 0).to_string(),
                }),
            )
        }
        TOPIC_SWAP => {
            if topics.len() < 4 {
                return Ok(None);
            }
            (
                "Swap",
                json!({
                    "from": address_from_topic(&topics[1])?,
                    "tokenIn": address_from_topic(&topics[2])?,
                    "tokenOut": address_from_topic(&topics[3])?,
                    "amountIn": word(&data, 0).to_string(),
                    "amountOut": word(&data, 1).to_string(),
                }),
            )
        }
        _ => return Ok(None),
    };

    Ok(Some(EventLog {
        block_number: parse_hex_u64(log.get("blockNumber").unwrap_or(&Value::Null))?,
        transaction_hash: log
            .get("transactionHash")
            .and_then(Value::as_str)
            .unwrap_or_default()
            .to_string(),
        log_index: parse_hex_u64(log.get("logIndex").unwrap_or(&Value::Null))?,
        address: log
            .get("address")
            .and_then(Value::as_str)
            .unwrap_or_default()
            .to_string(),
        event: event.to_string(),
        args,
    }))
}

pub fn fetch_logs(rpc_url: &str, request: &IndexRequest) -> LyquidResult<Vec<EventLog>> {
    let params = json!([{
        "address": request.contract,
        "fromBlock": format!("0x{:x}", request.from_block),
        "toBlock": format!("0x{:x}", request.to_block),
    }]);
    let result = rpc(rpc_url, "eth_getLogs", params)?;
    let logs = result
        .as_array()
        .ok_or_else(|| LyquidError::LyquorRuntime("eth_getLogs result is not an array".into()))?;

    let mut parsed = Vec::new();
    for log in logs {
        if let Some(event) = parse_log(log)? {
            parsed.push(event);
        }
    }
    Ok(parsed)
}

pub fn index_request(
    rpc_url: &str,
    request: &IndexRequest,
    node_id: &str,
) -> LyquidResult<Proposal> {
    let logs = fetch_logs(rpc_url, request)?;
    let result = build_result(
        &logs,
        &request.metric,
        &request.contract,
        request.from_block,
        request.to_block,
        11_155_111,
    )
    .map_err(|error| LyquidError::LyquorRuntime(error.to_string()))?;
    let hash = result_hash(&result)
        .map_err(|error| LyquidError::LyquorRuntime(format!("canonicalization failed: {error}")))?;
    Ok(Proposal {
        request: request.clone(),
        result,
        result_hash: hash,
        node_id: node_id.to_string(),
    })
}
