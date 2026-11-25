// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {ResultRegistry} from "../src/ResultRegistry.sol";

contract ResultRegistryTest is Test {
    ResultRegistry private registry;

    address private owner = address(this);
    address private submitter = address(0xA11CE);
    address private stranger = address(0xB0B);

    bytes32 private constant METRIC = keccak256("deposit_total");
    uint64 private constant FROM = 5_000_000;
    uint64 private constant TO = 5_010_000;

    function setUp() public {
        registry = new ResultRegistry();
        registry.setAuthorized(submitter, true);
    }

    function testSubmitAndRead() public {
        bytes32 hash = keccak256("result");
        vm.prank(submitter);
        registry.submitResult(hash, METRIC, FROM, TO, 2);

        ResultRegistry.Result memory result = registry.getResult(METRIC, FROM, TO);
        assertTrue(result.exists);
        assertEq(result.resultHash, hash);
        assertEq(result.metricId, METRIC);
        assertEq(result.fromBlock, FROM);
        assertEq(result.toBlock, TO);
        assertEq(result.quorum, 2);
        assertEq(result.submitter, submitter);
    }

    function testUnauthorizedReverts() public {
        vm.prank(stranger);
        vm.expectRevert("NOT_AUTHORIZED");
        registry.submitResult(keccak256("result"), METRIC, FROM, TO, 2);
    }

    function testInvalidRangeReverts() public {
        vm.prank(submitter);
        vm.expectRevert("INVALID_RANGE");
        registry.submitResult(keccak256("result"), METRIC, TO, FROM, 2);
    }

    function testEmptyHashReverts() public {
        vm.prank(submitter);
        vm.expectRevert("EMPTY_RESULT_HASH");
        registry.submitResult(bytes32(0), METRIC, FROM, TO, 2);
    }

    function testResubmitUpdatesAndEmits() public {
        bytes32 first = keccak256("first");
        bytes32 second = keccak256("second");

        vm.prank(submitter);
        registry.submitResult(first, METRIC, FROM, TO, 2);

        vm.expectEmit(true, true, true, true);
        emit ResultRegistry.ResultUpdated(
            registry.resultKey(METRIC, FROM, TO),
            first,
            second,
            submitter
        );
        vm.prank(submitter);
        registry.submitResult(second, METRIC, FROM, TO, 2);

        assertEq(registry.getResult(METRIC, FROM, TO).resultHash, second);
    }

    function testMissingResultReverts() public {
        vm.expectRevert("RESULT_NOT_FOUND");
        registry.getResult(METRIC, FROM, TO);
    }

    function testOwnerCanRevoke() public {
        registry.setAuthorized(submitter, false);
        vm.prank(submitter);
        vm.expectRevert("NOT_AUTHORIZED");
        registry.submitResult(keccak256("result"), METRIC, FROM, TO, 2);
    }
}
