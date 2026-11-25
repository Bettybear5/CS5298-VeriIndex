"""Attestation signing and verification.

The reference implementation uses Ethereum message signing so that a
signature can be recovered without a shared secret. The production Lyquid
adapter should use the host's key facility instead of embedding a key in the
service.
"""

from __future__ import annotations

from typing import Any

from eth_account import Account
from eth_account.messages import encode_defunct

from .canonical import result_hash


def address_for_key(private_key: str) -> str:
    """Return the lowercase Ethereum address for a private key."""
    return Account.from_key(private_key).address.lower()


def sign_result(result: dict[str, Any], private_key: str) -> dict[str, Any]:
    """Sign a result and return an attestation object."""
    digest = result_hash(result)
    account = Account.from_key(private_key)
    signed = Account.sign_message(encode_defunct(text=digest), private_key=account.key)
    return {
        "node_id": account.address.lower(),
        "result": result,
        "result_hash": digest,
        "signature": signed.signature.hex(),
    }


def verify_attestation(attestation: dict[str, Any]) -> bool:
    """Verify the hash and signature of an attestation.

    Raises:
        ValueError: if a field is missing or the hash/signature is invalid.
    """
    for field in ("node_id", "result", "result_hash", "signature"):
        if field not in attestation:
            raise ValueError(f"missing field: {field}")

    result = attestation["result"]
    if not isinstance(result, dict):
        raise ValueError("result must be an object")

    expected_hash = result_hash(result)
    if expected_hash.lower() != str(attestation["result_hash"]).lower():
        raise ValueError("result hash mismatch")

    try:
        recovered = Account.recover_message(
            encode_defunct(text=expected_hash),
            signature=attestation["signature"],
        )
    except Exception as exc:  # eth-account raises several exception types
        raise ValueError(f"signature verification failed: {exc}") from exc

    if recovered.lower() != str(attestation["node_id"]).lower():
        raise ValueError("signature does not match node_id")

    return True
