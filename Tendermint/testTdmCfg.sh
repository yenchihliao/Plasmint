#! /bin/bash
if [ $# -gt 0 ]
then
	cfg=$1
else
	cfg=CfgTdm
fi
echo "tendermint --home=\"$1\" init"
tendermint --home="$1" init
echo "tendermint --home=\"$1\" unsafe_reset_all"
tendermint --home="$1" unsafe_reset_all
echo "tendermint --home=\"$1\" node --proxy_app=kvstore"
tendermint --home="$1" node --proxy_app=kvstore
unset cfg
