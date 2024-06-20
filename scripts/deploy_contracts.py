from brownie import (
    MoralisGovernor,
    TimeLock,
    Box,
    GovernanceToken,
    network,
    config,
)
from scripts.helpful_scripts import get_account
from web3 import Web3

initial_supply = Web3.toWei(100, "ether")

QUORUM_PERCENTAGE = 4  # %
VOTING_PERIOD = 50  # 10 minutes
VOTING_DELAY = 1  # 1 block

# TimeLock
MIN_DELAY = 5  # Seconds

# Address 0
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

def deploy_contracts():
    account = get_account()

    # Deploy Governance Token
    try:
        governance_token = GovernanceToken.deploy(
            2,
            {"from": account},
            publish_source=config["networks"][network.show_active()].get("verify", False),
        )
        print(f"Governance Token deployed at: {governance_token.address}")
    except Exception as e:
        print(f"Error deploying Governance Token: {e}")
        print(f"Error type: {type(e)}")
        return

    # Try delegation with a higher gas limit
    try:
        tx = governance_token.delegate(account, {"from": account, "gas_limit": 3000000})
        tx.wait(1)
        print(f"Number of CheckPoints: {governance_token.numCheckpoints(account)}")
    except Exception as e:
        print(f"Error delegating Governance Token: {e}")
        return

    # Deploy TimeLock
    try:
        governance_time_lock = TimeLock.deploy(
            MIN_DELAY,
            [],
            [],
            account,
            {"from": account},
            publish_source=config["networks"][network.show_active()].get("verify", False),
        )
        print(f"Governance TimeLock deployed at: {governance_time_lock.address}")
    except Exception as e:
        print(f"Error deploying Governance TimeLock: {e}")
        print(f"Error type: {type(e)}")
        return

    # Deploy Moralis Governor
    try:
        governor = MoralisGovernor.deploy(
            governance_token.address,
            governance_time_lock.address,
            QUORUM_PERCENTAGE,
            VOTING_PERIOD,
            VOTING_DELAY,
            {"from": account},
            publish_source=config["networks"][network.show_active()].get("verify", False),
        )
        print(f"Governor deployed at: {governor.address}")
    except Exception as e:
        print(f"Error deploying Governor: {e}")
        print(f"Error type: {type(e)}")
        return

    # Setting Up the Roles
    try:
        proposer_role = governance_time_lock.PROPOSER_ROLE()
        executor_role = governance_time_lock.EXECUTOR_ROLE()
        timelock_admin_role = governance_time_lock.TIMELOCK_ADMIN_ROLE()
        governance_time_lock.grantRole(proposer_role, governor.address, {"from": account})
        governance_time_lock.grantRole(executor_role, ZERO_ADDRESS, {"from": account})
        governance_time_lock.grantRole(timelock_admin_role, account, {"from": account})
        print("Roles set up successfully.")
    except Exception as e:
        print(f"Error setting up roles: {e}")
        return

    # Deploying Contract to be Governed
    try:
        box = Box.deploy({"from": account})
        tx = box.transferOwnership(TimeLock[-1], {"from": account})
        tx.wait(1)
        print(f"Box deployed at: {box.address} and ownership transferred to TimeLock.")
    except Exception as e:
        print(f"Error deploying Box or transferring ownership: {e}")
        return

def main():
    deploy_contracts()
