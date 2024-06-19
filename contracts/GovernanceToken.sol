//SPDX-License-Identifier: MIT

import "@openzeppelin/contracts/token/ERC20/Extensions/ERC20Votes.sol";

pragma solidity ^0.8.7;

contract GovernanceToken is ERC20Votes {

    event TokenTransfered(
        address indexed from,
        address indexed to,
        uint256 amount
    );

    event TokenMinted(address indexed to, uint256 amount );
    event TokenBurned(address indexed from, uint256 amount);

    uint256 constant TOKENS_PER_USER = 1000;
    uint256 constant TOTAL_SUPPLY = 1000000 * 10**18;

    mapping(address => bool) public s_claimedTokens;

    address[] public s_holders;

    constructor(uint256 _keepPercentage) ERC20("MoralisToken", "MRST") ERC20Permit("MoralisToken") {
        uint256 keepAmount = (TOTAL_SUPPLY * _keepPercentage) / 100;
        _mint(msg.sender, TOTAL_SUPPLY);
        _transfer(msg.sender, address(this), TOTAL_SUPPLY - keepAmount);
        s_holders.push(msg.sender);
    }

    function claimTokens() external {
        require(!s_claimedTokens[msg.sender], "Already claimed Tokens");
        s_claimedTokens[msg.sender] = true;
        _transfer(address(this), msg.sender, TOKENS_PER_USER * 10**18);
        s_holders.push(msg.sender);

    }
}

// Hot Proposal Coming up => Buy a ton of tokens and dump them after voting is over
// We need to prevent that by setting a Snapshop of tokens at a certain block.
