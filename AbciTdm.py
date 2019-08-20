import requests
import sys
import json
from web3.auto import w3
from ethereum import utils

import rlp
from rlp.sedes import List, CountableList

from threading import Thread

from abci import (
    ABCIServer,
    BaseApplication,
    ResponseInfo,
    ResponseInitChain,
    ResponseCheckTx, ResponseDeliverTx,
    ResponseQuery,
    ResponseCommit,
    CodeTypeOk,
)

operator_key = '0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448'
operator_normalize_key = utils.normalize_key(operator_key)
authority = utils.privtoaddr(operator_key)
authority_address = w3.toChecksumAddress('0x' + authority.hex())
f = open('config.json', 'r')
config = json.load(f)
f.close()

class RequestFailedException(Exception):
    """request failed without success http status"""


def request(end_point, method, params=None, data=None, headers=None):
    url = 'http://{}:{}'.format(config['chain_IP'], config['child_chain']) + end_point

    response = requests.request(
        method=method,
        url=url,
        params=params,
        data=data,
        headers=headers,
    )

    if response.ok:
        return response
    else:
        raise RequestFailedException(
            'failed reason: {}, text: {}'.format(response.reason, response.text)
        )


def sign_apphash(apphash):
    sedes = CountableList(List([rlp.sedes.binary,
                                rlp.sedes.big_endian_int,
                                rlp.sedes.big_endian_int,
                                rlp.sedes.binary,
                                rlp.sedes.binary]))

    decoded = rlp.decode(bytes.fromhex(apphash), sedes)

    for i in decoded:
        data = list(i)
        data[2] = bool(data[2])
        msg_hash = w3.soliditySha3(['bytes32', 'uint256', 'bool', 'bytes', 'bytes'], data).hex()[2:]
        signed = utils.ecsign(bytes.fromhex(msg_hash), operator_normalize_key)
        tx = '1{0:0{1}X}{2:0{3}X}{4:0{5}X}{6:X}'.format(signed[1], 64,
                signed[2], 64, signed[0], 2, data[1])
        requests.get('http://{}:{}/broadcast_tx_async?tx="{}"'.format(config['tdm_IP'], config['tdm_RPC'], tx))


class PlasmaCash(BaseApplication):
    def info(self, req) -> ResponseInfo:
        r = ResponseInfo()
        r.version = "1.0"
        r.last_block_height = 0
        r.last_block_app_hash = b''
        return r

    def init_chain(self, req) -> ResponseInitChain:
        self.last_block_height = 0
        return ResponseInitChain()

    def check_tx(self, tx) -> ResponseCheckTx:
        end_point = '/check_tx'
        data = {'tx': tx}
        try:
            request(end_point, 'POST', data=data)
            return ResponseCheckTx(code=CodeTypeOk)
        except Exception as e:
            print(e)
            return ResponseCheckTx(code=1)

    def deliver_tx(self, tx) -> ResponseDeliverTx:
        end_point = '/send_tx'
        data = {'tx': tx}
        try:
            request(end_point, 'POST', data=data)
            return ResponseDeliverTx(code=CodeTypeOk)
        except Exception as e:
            print(e)
            return ResponseDeliverTx(code=1)

    def query(self, req) -> ResponseQuery:
        return ResponseQuery(code=CodeTypeOk, value='0', height=self.last_block_height)

    def commit(self) -> ResponseCommit:
        end_point = '/operator/commit'
        ret = request(end_point, 'POST')
        print(ret.text)
        worker = Thread(target=sign_apphash, args=[ret.text])
        worker.start()
        return ResponseCommit(data=bytes.fromhex(ret.text))


if __name__ == '__main__':
    port = int(config['tdm_ABCI'])
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    app = ABCIServer(port=port, app=PlasmaCash())
    print("Tendermint ABCI @ {}".format(port))
    app.run()
