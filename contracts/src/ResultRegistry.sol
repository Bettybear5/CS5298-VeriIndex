// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ResultRegistry
/// @notice Stores quorum-backed historical index results on chain.
/// @dev The registry stores only a hash and metadata. The full result stays
///      off chain and can be checked against the stored hash.
contract ResultRegistry {
    struct Result {
        bytes32 resultHash;
        bytes32 metricId;
        uint64 fromBlock;
        uint64 toBlock;
        uint8 quorum;
        uint64 timestamp;
        address submitter;
        bool exists;
    }

    address public owner;
    mapping(address => bool) public authorized;

    mapping(bytes32 => Result) private _results;

    event ResultSubmitted(
        bytes32 indexed key,
        bytes32 indexed metricId,
        bytes32 resultHash,
        uint64 fromBlock,
        uint64 toBlock,
        uint8 quorum,
        address indexed submitter
    );

    event ResultUpdated(
        bytes32 indexed key,
        bytes32 oldResultHash,
        bytes32 newResultHash,
        address indexed submitter
    );

    event AuthorizationChanged(address indexed account, bool allowed);

    modifier onlyOwner() {
        require(msg.sender == owner, "NOT_OWNER");
        _;
    }

    modifier onlyAuthorized() {
        require(authorized[msg.sender], "NOT_AUTHORIZED");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorized[msg.sender] = true;
        emit AuthorizationChanged(msg.sender, true);
    }

    /// @notice Allow or revoke a result submitter.
    function setAuthorized(address account, bool allowed) external onlyOwner {
        require(account != address(0), "ZERO_ADDRESS");
        authorized[account] = allowed;
        emit AuthorizationChanged(account, allowed);
    }

    /// @notice Store a result for (metricId, fromBlock, toBlock).
    /// @dev Re-submission overwrites the record and emits both events for audit.
    function submitResult(
        bytes32 resultHash,
        bytes32 metricId,
        uint64 fromBlock,
        uint64 toBlock,
        uint8 quorum
    ) external onlyAuthorized {
        require(resultHash != bytes32(0), "EMPTY_RESULT_HASH");
        require(metricId != bytes32(0), "EMPTY_METRIC");
        require(fromBlock <= toBlock, "INVALID_RANGE");
        require(quorum > 0, "INVALID_QUORUM");

        bytes32 key = resultKey(metricId, fromBlock, toBlock);
        Result storage previous = _results[key];
        bytes32 oldHash = previous.resultHash;

        _results[key] = Result({
            resultHash: resultHash,
            metricId: metricId,
            fromBlock: fromBlock,
            toBlock: toBlock,
            quorum: quorum,
            timestamp: uint64(block.timestamp),
            submitter: msg.sender,
            exists: true
        });

        emit ResultSubmitted(
            key,
            metricId,
            resultHash,
            fromBlock,
            toBlock,
            quorum,
            msg.sender
        );

        if (oldHash != bytes32(0)) {
            emit ResultUpdated(key, oldHash, resultHash, msg.sender);
        }
    }

    /// @notice Read a result. Reverts if the key has never been submitted.
    function getResult(
        bytes32 metricId,
        uint64 fromBlock,
        uint64 toBlock
    ) external view returns (Result memory) {
        bytes32 key = resultKey(metricId, fromBlock, toBlock);
        Result memory result = _results[key];
        require(result.exists, "RESULT_NOT_FOUND");
        return result;
    }

    /// @notice Check whether a result exists for a key.
    function hasResult(
        bytes32 metricId,
        uint64 fromBlock,
        uint64 toBlock
    ) external view returns (bool) {
        return _results[resultKey(metricId, fromBlock, toBlock)].exists;
    }

    /// @notice Compute the registry key for a query.
    function resultKey(
        bytes32 metricId,
        uint64 fromBlock,
        uint64 toBlock
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(metricId, fromBlock, toBlock));
    }
}
