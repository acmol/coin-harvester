#!/bin/env python
#fileencoding:utf-8
print("Content-Type:text/html\n")
import sys
sys.path.append('..')
import conf
import json
print json.dumps({'OPEN_RATES': conf.OPEN_RATES ,
	   'CLOSE_RATES': conf.CLOSE_RATES,
	   'ADJUST_VALUES': conf.ADJUST_VALUES,
       'SUPPORT_COIN_TYPES': conf.SUPPORT_COIN_TYPES,
       'WORKING_CONTRACT_TYPE': conf.WORKING_CONTRACT_TYPE
       })


