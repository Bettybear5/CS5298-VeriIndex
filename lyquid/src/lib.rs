//! VeriIndex Lyquid: verifiable historical event indexing on Lyquor.
//!
//! The Lyquid uses the oracle two-phase group to collect independent indexer
//! proposals, aggregate a quorum, and write a certified result into network
//! state. The on-chain (Lyquor network) record stores only the canonical result
//! hash and metadata; full logs and per-node proposals stay off chain.

pub mod canonical;
pub mod metrics;
pub mod rpc;
pub mod types;

use lyquid::prelude::*;
use serde::Serialize;

use crate::types::{FinalizedResult, IndexRequest, Proposal, ResultRecord};

const DEFAULT_RPC_URL: &str = "https://ethereum-sepolia-rpc.publicnode.com";

state! {
    network initializer: Address = Address::ZERO;
    network oracle veriindex_oracle;
    network results: HashMap<String, ResultRecord> = new_hashmap();
    network result_count: u64 = 0;
    instance rpc_url: String = String::new();
    instance min_proposals: u16 = 2;
}

#[method::network(export = eth)]
fn constructor(ctx: &mut _) {
    *ctx.network.initializer = ctx.caller;
}

#[method::network(export = eth)]
fn configure_committee(ctx: &mut _, node_ids: Vec<NodeID>) -> LyquidResult<bool> {
    if ctx.caller != *ctx.network.initializer {
        return Err(LyquidError::LyquorRuntime(
            "only initializer can configure committee".into(),
        ));
    }
    if node_ids.is_empty() {
        return Err(LyquidError::LyquorRuntime("committee cannot be empty".into()));
    }

    let target = OracleTarget {
        seq_id: lyquor_api::sequence_backend_id()?,
        target: OracleServiceTarget::LVM(ctx.lyquid_id),
    };
    let threshold = u16::try_from(node_ids.len() / 2 + 1)
        .map_err(|_| LyquidError::LyquorRuntime("committee threshold overflow".into()))?;

    if !ctx
        .network
        .veriindex_oracle
        .clone()
        .initialize(&mut ctx, target, node_ids, threshold)
    {
        return Err(LyquidError::LyquorRuntime(
            "oracle committee initialization failed".into(),
        ));
    }

    Ok(true)
}

#[method::instance(export = eth)]
fn set_rpc_url(ctx: &mut _, url: String) -> LyquidResult<bool> {
    if !url.starts_with("http://") && !url.starts_with("https://") {
        return Err(LyquidError::LyquorRuntime(
            "rpc url must start with http:// or https://".into(),
        ));
    }
    *ctx.instance.rpc_url.write() = url;
    Ok(true)
}

#[method::instance(export = eth)]
fn get_rpc_url(ctx: &_) -> LyquidResult<String> {
    let configured = (*ctx.instance.rpc_url.read()).clone();
    if configured.is_empty() {
        Ok(DEFAULT_RPC_URL.to_string())
    } else {
        Ok(configured)
    }
}

#[method::instance(export = eth)]
fn set_min_proposals(ctx: &mut _, value: u16) -> LyquidResult<bool> {
    if value == 0 {
        return Err(LyquidError::LyquorRuntime(
            "min_proposals must be greater than zero".into(),
        ));
    }
    *ctx.instance.min_proposals.write() = value;
    Ok(true)
}

#[method::instance(export = eth)]
fn get_min_proposals(ctx: &_) -> LyquidResult<u16> {
    Ok(*ctx.instance.min_proposals.read())
}


#[method::instance(export = eth)]
fn index_local(
    ctx: &mut _,
    contract: String,
    metric: String,
    from_block: u64,
    to_block: u64,
) -> LyquidResult<String> {
    let configured = (*ctx.instance.rpc_url.read()).clone();
    let rpc_url = if configured.is_empty() {
        DEFAULT_RPC_URL.to_string()
    } else {
        configured
    };
    let request = IndexRequest {
        contract: contract.to_lowercase(),
        metric,
        from_block,
        to_block,
    };
    let node_id = ctx.node_id.to_string();
    let proposal = rpc::index_request(&rpc_url, &request, &node_id)?;
    let payload = serde_json::json!({
        "proposal": proposal,
        "canonical_hash": proposal.result_hash,
    });
    serde_json::to_string(&payload)
        .map_err(|error| LyquidError::LyquorRuntime(format!("JSON encode failed: {error}")))
}

#[method::instance(group = oracle::two_phase::veriindex_oracle)]
fn propose(
    ctx: &mut _,
    contract: String,
    metric: String,
    from_block: u64,
    to_block: u64,
    _target: OracleTarget,
) -> LyquidResult<Proposal> {
    let configured = (*ctx.instance.rpc_url.read()).clone();
    let rpc_url = if configured.is_empty() {
        DEFAULT_RPC_URL.to_string()
    } else {
        configured
    };
    let request = IndexRequest {
        contract: contract.to_lowercase(),
        metric,
        from_block,
        to_block,
    };
    let node_id = ctx.node_id.to_string();
    rpc::index_request(&rpc_url, &request, &node_id)
}

#[method::instance(group = oracle::two_phase::veriindex_oracle)]
fn aggregate(ctx: &_) -> LyquidResult<Option<CertifiedCallParams>> {
    let init = decode_by_fields!(
        ctx.init,
        contract: String,
        metric: String,
        from_block: u64,
        to_block: u64,
        threshold: u16,
        target: OracleTarget
    )
    .ok_or_else(|| LyquidError::LyquorRuntime("failed to decode init params".into()))?;

    if init.target.seq_id != lyquor_api::sequence_backend_id()? {
        return Ok(None);
    }
    if ctx.inputs.len() < init.threshold as usize {
        return Ok(None);
    }

    let mut groups: HashMap<String, Vec<Proposal>> = new_hashmap();
    for input in ctx.inputs {
        if let Some(proposal) = lyquor_primitives::decode_object::<Proposal>(&input.input) {
            if proposal.result_hash.is_empty() {
                continue;
            }
            groups
                .entry(proposal.result_hash.clone())
                .or_default()
                .push(proposal);
        }
    }

    let mut best: Option<(String, Vec<Proposal>)> = None;
    let mut tied = false;
    for (hash, group) in groups {
        match &best {
            None => best = Some((hash, group)),
            Some((_, current)) if group.len() > current.len() => {
                best = Some((hash, group));
                tied = false;
            }
            Some((_, current)) if group.len() == current.len() => {
                tied = true;
            }
            Some(_) => {}
        }
    }

    if tied {
        return Ok(None);
    }
    let Some((hash, group)) = best else {
        return Ok(None);
    };
    if group.len() < init.threshold as usize {
        return Ok(None);
    }

    let first = &group[0];
    if first.request.contract != init.contract
        || first.request.metric != init.metric
        || first.request.from_block != init.from_block
        || first.request.to_block != init.to_block
    {
        return Ok(None);
    }

    let finalized = FinalizedResult {
        request: first.request.clone(),
        result: first.result.clone(),
        result_hash: hash,
        signers: group.iter().map(|proposal| proposal.node_id.clone()).collect(),
    };
    let input = encode_by_fields!(finalized: FinalizedResult = finalized).into();

    Ok(Some(CertifiedCallParams {
        origin: Address::ZERO,
        method: "update".into(),
        input,
        target: init.target,
    }))
}

#[method::network(group = oracle::certified::veriindex_oracle::two_phase)]
fn update(ctx: &mut _, finalized: FinalizedResult) -> LyquidResult<bool> {
    if finalized.signers.is_empty() {
        return Err(LyquidError::LyquorRuntime(
            "certified result has no signers".into(),
        ));
    }

    let key = ResultRecord::key(
        &finalized.request.metric,
        &finalized.request.contract,
        finalized.request.from_block,
        finalized.request.to_block,
    );
    let record = ResultRecord {
        result_hash: finalized.result_hash,
        contract: finalized.request.contract,
        metric: finalized.request.metric,
        from_block: finalized.request.from_block,
        to_block: finalized.request.to_block,
        event_count: finalized.result.event_count,
        value: finalized.result.value,
        quorum: finalized.signers.len() as u16,
        timestamp: lyquor_api::chain_pos()?.block(),
        signers: finalized.signers,
    };

    ctx.network.results.insert(key, record);
    *ctx.network.result_count += 1;
    Ok(true)
}

/// Direct registry write for single-node CI/testing. The multi-node path is
/// `report_result`, which requires an oracle committee.
#[method::network(export = eth)]
fn submit_result(
    ctx: &mut _,
    contract: String,
    metric: String,
    from_block: u64,
    to_block: u64,
    result_hash: String,
    value: String,
    event_count: u64,
    quorum: u16,
) -> LyquidResult<bool> {
    if result_hash.is_empty() {
        return Err(LyquidError::LyquorRuntime("empty result hash".into()));
    }
    if quorum == 0 {
        return Err(LyquidError::LyquorRuntime("quorum must be positive".into()));
    }
    let contract = contract.to_lowercase();
    let key = ResultRecord::key(&metric, &contract, from_block, to_block);
    let record = ResultRecord {
        result_hash,
        contract,
        metric,
        from_block,
        to_block,
        event_count,
        value,
        quorum,
        timestamp: lyquor_api::chain_pos()?.block(),
        signers: Vec::new(),
    };
    ctx.network.results.insert(key, record);
    *ctx.network.result_count += 1;
    Ok(true)
}

/// Schedule `report_result` after the current network slot commits.
/// `TriggerMode::Commit` is only valid from network functions.
#[method::network(export = eth)]
fn trigger_report_result(
    ctx: &mut _,
    contract: String,
    metric: String,
    from_block: u64,
    to_block: u64,
) -> LyquidResult<bool> {
    let _ = ctx;
    trigger!(
        report_result(
            contract: String,
            metric: String,
            from_block: u64,
            to_block: u64
        ),
        TriggerMode::Commit
    );
    Ok(true)
}

#[method::instance(export = eth)]
fn report_result(
    ctx: &mut _,
    contract: String,
    metric: String,
    from_block: u64,
    to_block: u64,
) -> LyquidResult<bool> {
    let threshold = *ctx.instance.min_proposals.read();
    let target = OracleTarget {
        target: OracleServiceTarget::LVM(ctx.lyquid_id),
        seq_id: lyquor_api::sequence_backend_id()?,
    };
    let oracle = ctx.network.veriindex_oracle.clone();
    let init = encode_by_fields!(
        contract: String = contract.to_lowercase(),
        metric: String = metric,
        from_block: u64 = from_block,
        to_block: u64 = to_block,
        threshold: u16 = threshold,
        target: OracleTarget = target
    )
    .into();

    let call = oracle.propose_and_certify(&mut ctx, target, init, None, None)?;
    if let Some(call) = call {
        let _ = submit_certified_call!(call)?;
        Ok(true)
    } else {
        Ok(false)
    }
}

#[method::network(export = eth)]
fn get_result(
    ctx: &_,
    contract: String,
    metric: String,
    from_block: u64,
    to_block: u64,
) -> LyquidResult<String> {
    let key = ResultRecord::key(&metric, &contract.to_lowercase(), from_block, to_block);
    let record = ctx
        .network
        .results
        .get(&key)
        .ok_or_else(|| LyquidError::LyquorRuntime("RESULT_NOT_FOUND".into()))?;
    serde_json::to_string(record)
        .map_err(|error| LyquidError::LyquorRuntime(format!("JSON encode failed: {error}")))
}

#[method::instance(export = eth)]
fn get_node_ids(ctx: &_) -> LyquidResult<Vec<String>> {
    let target = OracleTarget {
        seq_id: lyquor_api::sequence_backend_id()?,
        target: OracleServiceTarget::LVM(ctx.lyquid_id),
    };
    Ok(ctx
        .network
        .veriindex_oracle
        .config_current(&ctx, target)
        .committee
        .keys()
        .map(std::string::ToString::to_string)
        .collect())
}

#[method::network(export = eth)]
fn get_result_count(ctx: &_) -> LyquidResult<u64> {
    Ok(*ctx.network.result_count)
}

#[method::network(export = eth)]
fn has_result(
    ctx: &_,
    contract: String,
    metric: String,
    from_block: u64,
    to_block: u64,
) -> LyquidResult<bool> {
    let key = ResultRecord::key(&metric, &contract.to_lowercase(), from_block, to_block);
    Ok(ctx.network.results.contains_key(&key))
}

#[allow(dead_code)]
fn to_json<T: Serialize>(value: &T) -> LyquidResult<String> {
    serde_json::to_string(value)
        .map_err(|error| LyquidError::LyquorRuntime(format!("JSON encode failed: {error}")))
}
