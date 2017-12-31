#########################################################################
# File Name: start_monitor.sh
# Author: ma6174
# mail: ma6174@163.com
# Created Time: Sat 30 Dec 2017 06:27:57 PM CST
#########################################################################
#!/bin/bash

sh stop_monitor.sh 2> log/stop_monitor.err
nohup python3 $PWD/monitor.py > log/monitor.out 2> ./log/monitor.err &

