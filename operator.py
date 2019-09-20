import requests
import json
import base64
import rlp
from rlp.sedes import List, CountableList

from web3.auto import w3
from plasma_cash.client.client import Client
from plasma_cash.dependency_config import container
from plasma_cash.utils.utils import sign
from plasma_cash.root_chain.deployer import Deployer

from ethereum import utils
import time

last_block = 1
plasma_latest_block = 0
last_submit_block = 0

f = open('config.json', 'r')
config = json.load(f)
f.close()
operator_key = config['op_Key']
authority = utils.privtoaddr(operator_key)
authority_address = w3.toChecksumAddress('0x' + authority.hex())
root_chain = Deployer().get_contract('RootChain/RootChainSimple.sol')

twothirds = 1


class Block(object):
    '''
    def __init__(self, blkRoot, blkNum, isDepositBlock, depositTx, depositTxProof):
        self.blkRoot = blkRoot
        self.blkNum = blkNum
        self.isDepositBlock = isDepositBlock
        self.depositTx = depositTx
        self.depositTxProof = depositTxProof
        self.signature = set()
    '''
    def __init__(self, apphash):
        self.hash = apphash
    '''
    def add_signature(self, signature):
        self.signature.add(signature)

    def check_signature_num(self):
        if len(self.signature) >= twothirds:
            return True
        return False
    '''
    def submit(self):
        #siglist = list(self.signature)
        tx = root_chain.functions.submitBlock(
            self.hash
        #    self.blkRoot,
        #    self.blkNum,
        #    self.isDepositBlock,
        #    self.depositTx,
        #    self.depositTxProof,
        #    [int(siglist[0][128:130], 16)],
        #    [bytes.fromhex(siglist[0][0:64])],
        #    [bytes.fromhex(siglist[0][64:128])]
        
        ).buildTransaction({
            'from': authority_address,
            'nonce': w3.eth.getTransactionCount(authority_address, 'pending')
        })
        print('submiting block of', self.hash)
        signed = w3.eth.account.signTransaction(tx, operator_key)
        w3.eth.sendRawTransaction(signed.rawTransaction)


def tendermint_latest_block():
    ret = requests.get('http://{}:{}/status'.format(config['tdm_IP'], config['tdm_RPC']))
    j = json.loads(ret.text)
    return int(j['result']['sync_info']['latest_block_height'])


def get_tendermint_block(block):
    ret = requests.get('http://{}:{}/block?height={}'.format(config['tdm_IP'], config['tdm_RPC'], block))
    j = json.loads(ret.text)
    return j


if __name__ == '__main__':
    block = {}
    while True:
        latest = tendermint_latest_block()
        for blk in range(last_block + 1, latest + 1):
            print('blk', blk)
            tdm_block = get_tendermint_block(blk)
            apphash = tdm_block['result']['block_meta']['header']['app_hash']

            Block(apphash).submit();
            '''
            sedes = CountableList(List([rlp.sedes.binary,
                rlp.sedes.big_endian_int,
                rlp.sedes.big_endian_int,
                rlp.sedes.binary,
                rlp.sedes.binary]))
            d = rlp.decode(bytes.fromhex(apphash), sedes)
            for i in d:
                block[i[1]] = Block(i[0], i[1], bool(i[2]), i[3], i[4])
                plasma_latest_block = i[1]
            txs = tdm_block['result']['block']['data']['txs']
            for tx in txs:
                decoded_tx = base64.b64decode(tx).decode()
                if decoded_tx[0] == '1':
                    decoded_tx = decoded_tx[1:]
                    sig = decoded_tx[:130]
                    blkNum = int(decoded_tx[130:], 16)
                    block[blkNum].add_signature(sig)
                # block[i[1]].submit()
            '''
        last_block = latest
        '''
        for blk in range(last_submit_block + 1, plasma_latest_block + 1):
            if block[blk].check_signature_num():
                block[blk].submit()
                last_submit_block = blk
            else:
                break
        '''
        time.sleep(5)
