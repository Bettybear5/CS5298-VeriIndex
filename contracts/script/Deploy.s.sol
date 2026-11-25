// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Script} from "forge-std/Script.sol";
import {EventSource} from "../src/EventSource.sol";
import {ResultRegistry} from "../src/ResultRegistry.sol";

contract Deploy is Script {
    function run() external returns (EventSource source, ResultRegistry registry) {
        uint256 key = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(key);

        source = new EventSource();
        registry = new ResultRegistry();

        vm.stopBroadcast();
    }
}
