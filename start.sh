#########################################################################
# File Name: start.sh
# Author: ma6174
# mail: ma6174@163.com
# Created Time: Wed 27 Dec 2017 09:57:21 PM CST
#########################################################################
#!/bin/bash
sh stop.sh 2> logs/stop.err
nohup python3 $PWD/trading.py > log/trading.out 2> log/trading.err &
sh start_monitor.sh
