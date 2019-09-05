from gevent import monkey
monkey.patch_all()
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from web3.auto import w3
from plasma_cash.client.client import Client
from plasma_cash.dependency_config import container

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <body>

    <b>GetBalance</b>
    <form action="/getBalance">
    account: <input type="text" name="account" value="0xb83e232458a092696be9717045d9a605fb0fec2b"><br>
    <input type="submit" value="Submit">
    </form><br><br>

    <b>Deposit</b>
    <form action="/deposit">
    key: <input type="text" name="key" value="0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b"><br>
    amount: <input type="text" name="amount" value="10"><br>
    <input type="submit" value="Submit">
    </form><br><br>

    <b>SendTransaction</b>
    <form action="/sendTransaction">
    key: <input type="text" name="key" value="0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b"><br>
    <!--preBlock: <input type="text" name="preBlock" value=""><br>-->
    uid: <input type="text" name="uid" value="1693390459388381052156419331572168595237271043726428428352746834777341368960"><br>
    amount: <input type="text" name="amount" value="10"><br>
    receiver: <input type="text" name="receiver" value="0x08d92dca9038ea9433254996a2d4f08d43be8227"><br>
    <input type="submit" value="Submit">
    </form><br><br>

    <b>StartExit</b>
    <form action="/startExit">
    key: <input type="text" name="key" value="0xee092298d0c0db61969cc4466d57571cf3ca36ca62db94273d5c1513312aeb30"><br>
    uid: <input type="text" name="uid" value="1693390459388381052156419331572168595237271043726428428352746834777341368960"><br>
    block1: <input type="text" name="block1" value=""><br>
    block2: <input type="text" name="block2" value=""><br>
    <input type="submit" value="Submit">
    </form><br><br>
    
    <b>IncreaseTime</b>
    <form action="/increaseTime">
    time: <input type="text" name="time" value="1209600"><br>
    <input type="submit" value="Submit">
    </form><br><br>
    
    <b>FinalizeExit</b>
    <form action="/finalizeExit">
    key: <input type="text" name="key" value="0xee092298d0c0db61969cc4466d57571cf3ca36ca62db94273d5c1513312aeb30"><br>
    uid: <input type="text" name="uid" value="1693390459388381052156419331572168595237271043726428428352746834777341368960"><br>
    <input type="submit" value="Submit">
    </form><br><br>

    </body>
    </html>
    '''

#account    : eth account
@app.route('/getBalance')
def getBalance():
    print('getBalance')
    account = request.args.get('account')
    print(account)
    balance = w3.eth.getBalance(w3.toChecksumAddress(account))
    return str(balance)

#key	    : account private key
#amount     : amount to deposit
@app.route('/deposit')
def deposit():
    print(deposit)
    #TODO
    userA = Client(container.get_root_chain(), container.get_child_chain_client(), request.args.get('key'))
    userA.deposit(int(request.args.get('amount')), '0x0000000000000000000000000000000000000000')
    return '0'

#key	    : account private key
#preBlock   : block of previous utxo 
#uid        : uid
#amount     : amount to send
#receiver   : receiver
@app.route('/sendTransaction')
def sendTransaction():
    print('sendTransaction')
    #TODO
    userA = Client(container.get_root_chain(), container.get_child_chain_client()    , request.args.get('key'))
    preblock = requests.post("http://127.0.0.1:26657/status").json()['result']['sync_info']['latest_block_height']
    userA.send_transaction(int(preblock), int(request.args.get('uid')), int(request.args.get('amount')), request.args.get('receiver'))
    return '0'

#key        : account private key
#uid        : uid
#block1     : 
#block2     :
@app.route('/startExit')
def startExit():
    print('startExit')
    #TODO
    userB = Client(container.get_root_chain(), container.get_child_chain_client(), request.args.get('key'))
    userB.start_exit(int(request.args.get('uid')), int(request.args.get('block1')), int(request.args.get('block2')))
    return '0'

#time        : time
@app.route('/increaseTime')
def increaseTime():
    print('increaseTime')
    #TODO
    w3.providers[0].make_request('evm_increaseTime', int(request.args.get('time')))
    return '0'

#key        : account private key
#uid        : uid
@app.route('/finalizeExit')
def finalizeExit():
    print('finalizeExit')
    #TODO
    userB = Client(container.get_root_chain(), container.get_child_chain_client(), request.args.get('key'))
    userB.finalize_exit(int(request.args.get('uid')))
    return '0'

if __name__ == '__main__':
    print('Serving on port 5000')
    server = WSGIServer(('127.0.0.1', 5000), app)
    server.serve_forever()
