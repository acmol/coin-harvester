#########################################################################
# File Name: stop.sh
# Author: ma6174
# mail: ma6174@163.com
# Created Time: Wed 27 Dec 2017 09:58:26 PM CST
#)########################################################################
#!/bin/bash
ps ux | grep $PWD | grep trading.py | grep -v grep | awk '{print $2}' | xargs kill
