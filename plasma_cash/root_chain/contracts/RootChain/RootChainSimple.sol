pragma solidity ^0.4.18;

contract RootChain {
	mapping(bytes32 => int) private hashIndex;
	bytes32[] public apphash;
	int count;
	address private authority;


	constructor() public {
		authority = msg.sender;
		count = 0;
	}

	modifier isAuthority() {
		require(msg.sender == authority);
		_;
	}

	function getIndexByHash(bytes32 hash) view public returns(int) {
		require(hashIndex[hash] != 0);
		return hashIndex[hash] - 1;
	}


	function submitBlock(bytes32 hash) public isAuthority {
		require(hashIndex[hash] == 0);
		apphash.push(hash);
		hashIndex[hash] = count + 1;
		count += 1;
	}

}

