echo "tendermint init"
#tendermint --home "$1" init
tendermint --home "$1" init
echo "tendermint reset"
#tendermint --home "$1" unsafe_reset_all
tendermint --home "$1" unsafe_reset_all
echo "tendermint node"
#tendermint --home "$1" node 
tendermint --home "$1" node
