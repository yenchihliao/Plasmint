import json
import os

from solc import compile_standard
from web3.auto import w3
from web3 import Web3
from ethereum import utils

# from plasma_cash.config import plasma_config
import json
import sys

OWN_DIR = os.path.dirname(os.path.realpath(__file__))
f = open(OWN_DIR+'/../../config.json', 'r')
config = json.load(f)
f.close()
www = Web3(w3.HTTPProvider("http://{}:{}".format(config['root_addr'], config['root_IP'])))
contractAddr = ''


class Deployer(object):

    def get_dirs(self, path):
        abs_contract_path = os.path.realpath(os.path.join(OWN_DIR, 'contracts'))

        extra_args = []
        for r, d, f in os.walk(abs_contract_path):
            for file in f:
                extra_args.append([file, [os.path.realpath(os.path.join(r, file))]])
                #print("extra_args, ", [file, [os.path.realpath(os.path.join(r, file))]])

        contracts = {}
        for contract in extra_args:
            contracts[contract[0]] = {'urls': contract[1]}
        path = '{}/{}'.format(abs_contract_path, path)
        sys.stdout.flush()
        return path, contracts

    def compile_contract(self, path, args=()):
        file_name = path.split('/')[1]
        contract_name = file_name.split('.')[0]
        path, contracts = self.get_dirs(path)
        #print({**{path.split('/')[-1]: {'urls': [path]}}, **contracts})
        compiled_sol = compile_standard({
            'language': 'Solidity',
            'sources': {**{path.split('/')[-1]: {'urls': [path]}}, **contracts},
            'settings': {'outputSelection': {"*": {"*": ['abi', 'metadata', 'evm.bytecode']}}}
        }, allow_paths=OWN_DIR + "/contracts")
        abi = compiled_sol['contracts'][file_name][contract_name]['abi']
        bytecode = compiled_sol['contracts'][file_name][contract_name]['evm']['bytecode']['object']

        # Create the contract_data folder if it doesn't already exist
        os.makedirs('contract_data', exist_ok=True)

        contract_file = open('contract_data/%s.json' % (file_name.split('.')[0]), "w+")
        json.dump(abi, contract_file)
        contract_file.close()
        return abi, bytecode, contract_name

    def deploy_contract(self, path, args=(), gas=4410000):
        abi, bytecode, contract_name = self.compile_contract(path, args)
        contract = www.eth.contract(abi=abi, bytecode=bytecode)

        key = bytes.fromhex(config['op_Key'][2:])
        address = www.toChecksumAddress(utils.privtoaddr(key))
        tx = contract.constructor().buildTransaction({
            'from': address,
            'nonce': www.eth.getTransactionCount(address, 'pending')
        })
        signed = www.eth.account.signTransaction(tx, key)
        tx_hash = www.eth.sendRawTransaction(signed.rawTransaction)
        tx_receipt = www.eth.waitForTransactionReceipt(tx_hash)

        contractAddr = tx_receipt.contractAddress
        f = open('addr.txt', 'w')
        f.write(contractAddr)
        f.close()
        print('Successfully deployed {} contract with tx hash {} in contract address {}!'.format(
            contract_name, tx_hash.hex(), tx_receipt.contractAddress))

    def get_contract(self, path):
        file_name = path.split('/')[1]
        abi = json.load(open('contract_data/%s.json' % (file_name.split('.')[0])))
        f = open('addr.txt', 'r')
        contractAddr = f.read()
        f.close()
        print('contractAddr: ', type(contractAddr), contractAddr)
        contract = www.eth.contract(
            address=www.toChecksumAddress(contractAddr),
            abi=abi
        )
        return contract
