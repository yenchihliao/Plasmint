import pytest
from ethereum.utils import sha3

from plasma_cash.utils.merkle.sparse_merkle_tree import SparseMerkleTree


class TestSparseMerkleTree(object):

    def test_all_leaves_with_val(self):
        dummy_val = b'\x01' * 32
        leaves = {0: dummy_val, 1: dummy_val, 2: dummy_val, 3: dummy_val}
        tree = SparseMerkleTree(depth=3, leaves=leaves)
        mid_level_val = sha3(dummy_val + dummy_val)
        assert tree.root == sha3(mid_level_val + mid_level_val)

    def test_empty_leaves(self):
        tree = SparseMerkleTree(depth=3)
        empty_val = b'\x00' * 32
        mid_level_val = sha3(empty_val + empty_val)
        assert tree.root == sha3(mid_level_val + mid_level_val)

    def test_empty_left_leave(self):
        empty_val = b'\x00' * 32
        dummy_val = b'\x01' * 32
        leaves = {1: dummy_val, 2: dummy_val, 3: dummy_val}
        tree = SparseMerkleTree(depth=3, leaves=leaves)
        mid_left_val = sha3(empty_val + dummy_val)
        mid_right_val = sha3(dummy_val + dummy_val)
        assert tree.root == sha3(mid_left_val + mid_right_val)

    def test_empty_right_leave(self):
        empty_val = b'\x00' * 32
        dummy_val = b'\x01' * 32
        leaves = {0: dummy_val, 2: dummy_val, 3: dummy_val}
        tree = SparseMerkleTree(depth=3, leaves=leaves)
        mid_left_val = sha3(dummy_val + empty_val)
        mid_right_val = sha3(dummy_val + dummy_val)
        assert tree.root == sha3(mid_left_val + mid_right_val)

    def test_exceed_tree_size(self):
        with pytest.raises(SparseMerkleTree.TreeSizeExceededException):
            SparseMerkleTree(depth=1, leaves={0: '0', 1: '1'})

    def test_create_merkle_proof(self):
        empty_val = b'\x00' * 32
        dummy_val = b'\x01' * 32
        leaves = {0: dummy_val, 2: dummy_val, 3: dummy_val}
        tree = SparseMerkleTree(depth=3, leaves=leaves)
        mid_left_val = sha3(dummy_val + empty_val)
        mid_right_val = sha3(dummy_val + dummy_val)
        assert tree.create_merkle_proof(0) == empty_val + mid_right_val
        assert tree.create_merkle_proof(1) == dummy_val + mid_right_val
        assert tree.create_merkle_proof(2) == dummy_val + mid_left_val
        assert tree.create_merkle_proof(3) == dummy_val + mid_left_val
