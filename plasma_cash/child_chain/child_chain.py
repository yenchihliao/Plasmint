import time
from threading import Thread

import rlp
from ethereum import utils

from plasma_cash.utils.utils import sign
from plasma_cash.tendermint.client import TendermintClient

from .block import Block
from .event import emit
from .exceptions import (DepositAlreadyAppliedException, InvalidBlockNumException,
                         InvalidBlockSignatureException, InvalidTxSignatureException,
                         PreviousTxNotFoundException, TxAlreadySpentException,
                         TxAmountMismatchException, TxWithSameUidAlreadyExists)
from .transaction import Transaction


class ChildChain(object):

    def __init__(self, key, root_chain, db):
        self.key = utils.normalize_key(key)
        self.authority = utils.privtoaddr(self.key)
        self.root_chain = root_chain
        self.db = db
        self.current_block = Block()
        self.current_block_number = self.db.get_current_block_num()
        self.deposit = set()
        self.tmclient = TendermintClient()
        self.db.save_block(Block(), 0)

        """
        TODO: should be removed as there's operator cron job that's doing the job
        here. Temperary keep this to not break integration test.
        """
        deposit_filter = self.root_chain.eventFilter('Deposit', {'fromBlock': 0})
        worker = Thread(target=self.log_loop, args=(deposit_filter, 0.1), daemon=True)
        worker.start()

    def log_loop(self, event_filter, poll_interval):
        """
        TODO: should be removed as there's operator cron job that's doing the job
        here. Temperary keep this to not break integration test.
        """
        while True:
            for event in event_filter.get_new_entries():
                depositor = event['args']['depositor']
                amount = event['args']['amount']
                uid = event['args']['uid']
                new_owner = utils.normalize_address(depositor)
                deposit_tx = Transaction(0, uid, amount, new_owner)
                encoded_tx = '0' + rlp.encode(deposit_tx, Transaction).hex()
                ret = self.tmclient.broadcast_tx_sync(encoded_tx)
                print(ret)
            time.sleep(poll_interval)

    def apply_deposit(self, depositor, amount, uid):
        new_owner = utils.normalize_address(depositor)

        if not self.current_block.get_tx_by_uid(uid):
            deposit_tx = Transaction(0, uid, amount, new_owner)
            self.current_block.add_tx(deposit_tx)
            sig = sign(self.current_block.hash, self.key)
            self.submit_block(sig.hex(), True, uid)
            return deposit_tx.hash

        err_msg = 'deposit of uid: {} is already applied previously'.format(uid)
        raise DepositAlreadyAppliedException(err_msg)

    def commit(self):
        result = []
        for transaction in self.deposit:
            tx = rlp.decode(utils.decode_hex(transaction[1:]), Transaction)
            block = Block()
            block.add_tx(tx)
            merkle_hash = block.merklize_transaction_set()
            print('submit deposit block', self.current_block_number, merkle_hash.hex())
            print('uid', tx.uid)
            result.append(self.get_app_hash(block, True, tx.uid))
        self.deposit = set()

        merkle_hash = self.current_block.merklize_transaction_set()
        print('submit_block', self.current_block_number, merkle_hash.hex())
        result.append(self.get_app_hash(self.current_block))
        self.current_block = Block()
        return rlp.encode(result).hex()

    def get_app_hash(self, block, isDepositBlock=False, uid=None):
        merkle_hash = block.merklize_transaction_set()
        deposit_tx, deposit_tx_proof = b'', b''
        if uid is not None:
            deposit_tx = block.get_tx_by_uid(uid)
            deposit_tx_proof = block.merkle.create_merkle_proof(uid)

        self.db.save_block(block, self.current_block_number)
        self.current_block_number = self.db.increment_current_block_num()
        return [merkle_hash, self.current_block_number - 1, isDepositBlock,
                rlp.encode(deposit_tx), deposit_tx_proof]

    def submit_block(self, sig, isDepositBlock=False, uid=None):
        merkle_hash = self.current_block.merklize_transaction_set()
        print('submit_block', self.current_block_number, merkle_hash.hex())
        emit('chain.block', self.current_block_number)
        self.db.save_block(self.current_block, self.current_block_number)
        self.current_block_number = self.db.increment_current_block_num()
        self.current_block = Block()
        return merkle_hash.hex()

    def check_transaction(self, transaction):

        if transaction[0] == '1':
            return ''

        print('transaction', transaction)
        tx = rlp.decode(utils.decode_hex(transaction[1:]), Transaction)
        if tx.prev_block == 0:
            return ''
        else:
            prev_tx = self.db.get_block(tx.prev_block).get_tx_by_uid(tx.uid)
            if prev_tx is None:
                raise PreviousTxNotFoundException('failed to apply transaction')
            if prev_tx.spent:
                raise TxAlreadySpentException('failed to apply transaction')
            if prev_tx.amount != tx.amount:
                raise TxAmountMismatchException('failed to apply transaction')
            if tx.sig == b'\x00' * 65 or tx.sender != prev_tx.new_owner:
                raise InvalidTxSignatureException('failed to apply transaction')
            if self.current_block.get_tx_by_uid(tx.uid):
                raise TxWithSameUidAlreadyExists('failed to apply transaction')
            return ''

    def apply_transaction(self, transaction):

        if transaction[0] == '1':
            return ''
        tx = rlp.decode(utils.decode_hex(transaction[1:]), Transaction)
        if tx.prev_block == 0:
            self.deposit.add(transaction)
            return tx.hash
        else:
            prev_tx = self.db.get_block(tx.prev_block).get_tx_by_uid(tx.uid)
            if prev_tx is None:
                raise PreviousTxNotFoundException('failed to apply transaction')
            if prev_tx.spent:
                raise TxAlreadySpentException('failed to apply transaction')
            if prev_tx.amount != tx.amount:
                raise TxAmountMismatchException('failed to apply transaction')
            if tx.sig == b'\x00' * 65 or tx.sender != prev_tx.new_owner:
                raise InvalidTxSignatureException('failed to apply transaction')
            if self.current_block.get_tx_by_uid(tx.uid):
                raise TxWithSameUidAlreadyExists('failed to apply transaction')

            prev_tx.spent = True  # Mark the previous tx as spent
            self.current_block.add_tx(tx)
            return tx.hash

    def get_current_block(self):
        return rlp.encode(self.current_block).hex()

    def get_block(self, blknum):
        if 0 < blknum < self.current_block_number:
            block = self.db.get_block(blknum)
        elif blknum == self.current_block_number:
            return self.get_current_block()
        else:
            raise InvalidBlockNumException(
                'current blockNum is {}, your requested blocknum does not exists'.format(
                    self.current_block_number))
        return rlp.encode(block).hex()

    def get_proof(self, blknum, uid):
        block = self.db.get_block(blknum)
        return block.merkle.create_merkle_proof(uid)
