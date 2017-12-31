#########################################################################
# File Name: http.sh
# Author: ma6174
# mail: ma6174@163.com
# Created Time: Fri 29 Dec 2017 11:24:07 AM CST
#########################################################################
#!/bin/bash
PORT=`python -c 'import conf;print conf.HTTP_PORT'`
cd html
nohup python3 -m http.server --cgi $PORT > ../logs/webserver.out 2> ../logs/webserver.err &
