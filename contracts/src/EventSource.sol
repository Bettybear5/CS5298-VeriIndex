// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title EventSource
/// @notice A minimal event emitter used as the indexing target for VeriIndex.
/// @dev This contract is intentionally small. It is not a production vault.
contract EventSource {
    event Deposit(address indexed from, uint256 amount);
    event Withdraw(address indexed from, uint256 amount);
    event Swap(
        address indexed from,
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );

    /// @notice Deposit Ether and emit a Deposit event.
    function deposit() external payable {
        require(msg.value > 0, "ZERO_AMOUNT");
        emit Deposit(msg.sender, msg.value);
    }

    /// @notice Withdraw Ether and emit a Withdraw event.
    function withdraw(uint256 amount) external {
        require(amount > 0, "ZERO_AMOUNT");
        require(address(this).balance >= amount, "INSUFFICIENT_BALANCE");
        (bool ok, ) = payable(msg.sender).call{value: amount}("");
        require(ok, "TRANSFER_FAILED");
        emit Withdraw(msg.sender, amount);
    }

    /// @notice Record a swap that happened elsewhere.
    /// @dev No token transfer is performed; this is an event fixture.
    function recordSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOut
    ) external {
        require(tokenIn != address(0), "ZERO_TOKEN_IN");
        require(tokenOut != address(0), "ZERO_TOKEN_OUT");
        require(tokenIn != tokenOut, "SAME_TOKEN");
        require(amountIn > 0 && amountOut > 0, "ZERO_AMOUNT");
        emit Swap(msg.sender, tokenIn, tokenOut, amountIn, amountOut);
    }
}
