// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {EventSource} from "../src/EventSource.sol";

contract EventSourceTest is Test {
    EventSource private source;

    event Deposit(address indexed from, uint256 amount);

    function setUp() public {
        source = new EventSource();
        vm.deal(address(this), 10 ether);
    }

    function testDepositEmits() public {
        vm.expectEmit(true, false, false, true);
        emit Deposit(address(this), 1 ether);
        source.deposit{value: 1 ether}();
        assertEq(address(source).balance, 1 ether);
    }

    function testZeroDepositReverts() public {
        vm.expectRevert("ZERO_AMOUNT");
        source.deposit{value: 0}();
    }

    function testRecordSwapEmits() public {
        source.recordSwap(
            address(0x1),
            address(0x2),
            100,
            90
        );
    }

    function testSameTokenReverts() public {
        vm.expectRevert("SAME_TOKEN");
        source.recordSwap(address(0x1), address(0x1), 100, 90);
    }
}
