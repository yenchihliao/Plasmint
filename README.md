# Dependency Prerequisite
Solidity 0.4.24
Python 3.6+
ganache-cli 6.1.2+
Install requirements:
```
pip install -r requirements.txt
```
# Config
There are multiple ports that are needed for a single Plasmint node. Use `lsof -i:[port]` command to make sure these ports aren't occupied:

	* A blockchain service(e.g. ganache-cli take 8545)

The followings need an additional port if new node is added on the same device:

	* child-chain server(e.g. 8546)
	* tendermint ABCI(e.g. 26658)
	* tendermint RPC(e.g. 26657)
	* tendermint p2p(e.g. 26656)

To customize these ports, modify config.json and your Tendermint config file counterpart.

# Run

**Python used below are all python3.6+**

1. Ganache-cli command to start a simulated chain:
```bash
ganache-cli -m=plasma_cash
```
2. Deploy plasma contract:
```bash
python deployment.py
```
3. Run child chain Server:
```
python -m plasma_cash.child_chain
```
4. Run app for ABCI:
```
python AbciTdm.py
```
5. Start Tendermint Node 
```bash
./NodeTdm.sh [TendermintConfigDirectory]
```
6. Submit Block to mainchain
```bash
python operator.py
```

7. (Optional) For demo:
```bash
python server.py
```
