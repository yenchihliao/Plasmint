import requests
import json

f = open('config.json', 'r')
config = json.load(f)
f.close()

class TendermintClient(object):
    def __init__(self):
        self.rpc_addr = 'http://{}:{}'.format(config['tdm_IP'], config['tdm_RPC'])

    def broadcast_tx_sync(self, tx):
        ret = requests.get('{}/broadcast_tx_sync?tx="{}"'.format(self.rpc_addr, tx))
        return ret.text

    def broadcast_tx_commit(self, tx):
        ret = requests.get('{}/broadcast_tx_commit?tx="{}"'.format(self.rpc_addr, tx))
        return ret.text
