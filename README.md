The backup project forked from omesigo/plasma_cash. The consensus part is modified to Tendermint.
# Dependency Prerequisite

* Solidity 0.4.24
* Python 3.6+ (Any insatllation problems with python and pip here has solution at [OSModuleinstall](https://github.com/yenchihliao/OSModuleInstall))
* ganache-cli 6.1.2+

## [LevelDB](https://github.com/google/leveldb)

* Mac:
```bash
$ brew install leveldb
```

* Linux:

LevelDB should be installed along with `plyvel` once you make the project later on.

* Windows:

First, install [vcpkg](https://github.com/Microsoft/vcpkg). Then,

```bash
> vcpkg install leveldb
```

## [Solidity 0.4.24](https://github.com/ethereum/solidity/releases/tag/v0.4.24)

* Mac:
```bash
$ brew update
$ brew upgrade
$ brew tap ethereum/ethereum
$ brew install solidity
```

* Linux:
```bash
$ wget https://github.com/ethereum/solidity/releases/download/v0.4.24/solc-static-linux
$ chmod +x ./solc-static-linux
$ sudo mv solc-static-linux /usr/bin/solc
```

* Windows:

Follow [this guide](https://solidity.readthedocs.io/en/v0.4.21/installing-solidity.html#prerequisites-windows).

## [ganache-cli 6.1.2+](https://github.com/trufflesuite/ganache-cli)

It's also recommended to run `ganache-cli` when developing, testing, or playing around. This will allow you to receive near instant feedback.

* Mac:
```bash
$ brew install node
$ npm install -g ganache-cli
```

* Linux:

Install [Node.js](https://nodejs.org/en/download/). Then,
```bash
$ npm install -g ganache-cli
```

## Python modules

* Install requirements:
```bash
pip install --user -r requirements.txt
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

1. RootChain:
If a rootchain of ganache-cli which is initilized with plasma_cash is not used, make sure to modify private key for operator(op_Key) in `config.json`.  
To interact with rootchain, use `geth attach http://127.0.0.1:8545`.
```bash
# ganache-cli simulates a root chain
ganache-cli -m=plasma_cash
# deploy plasma_cash contract on the root chain
python deployment.py
```
2. ChainChain:
```bash
# starts the child_chain node of plasma_cash
python -m plasma_cash.child_chain
```
3. Tendermint:
```bash
# starts ABCI for tendermint node
python Tendermint/AbciTdm.py
# initialize and run a tendermint node
./Tendermint/NodeTdm.sh [TendermintConfigDirectory]
```
4. Submit Block to mainchain
```bash
python operator.py
```

5. (Optional) For demo:
```bash
python server.py
```


