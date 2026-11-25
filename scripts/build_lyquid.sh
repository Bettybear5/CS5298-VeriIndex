#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/lyquid"

# Requires the Rust toolchain pinned in rust-toolchain.toml and the
# wasm32-unknown-unknown target.
rustup target add wasm32-unknown-unknown
cargo build --release --target wasm32-unknown-unknown
