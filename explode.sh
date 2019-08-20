ganache-cli -m=plasma_cash &
sleep 3
python3 deployment.py 
python3 -m plasma_cash.child_chain &
python3 AbciTdm.py &
