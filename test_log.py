#!/usr/bin/env python
# -*- coding:utf-8 -*
'''
Main program

'''

from FUTIL.my_logging import *

my_logging(console_level = DEBUG, logfile_level = INFO, details = True,name_logfile = "c:\\temp\\test.log")

logging.info(f"sys.argv[0]:{sys.argv[0]}")
logging.info(os.path.splitext(sys.argv[0])[0] + '.log')
