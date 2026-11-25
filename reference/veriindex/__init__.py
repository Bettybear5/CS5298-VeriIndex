"""VeriIndex reference implementation.

This package is a deterministic, offline reference for the Lyquid indexer.
It is used by the tests and by the evaluation script. It is not the
production Lyquid adapter.
"""

from .canonical import canonical_json, result_hash
from .metrics import METRICS, compute_metric
from .quorum import quorum

__all__ = ["canonical_json", "result_hash", "METRICS", "compute_metric", "quorum"]
