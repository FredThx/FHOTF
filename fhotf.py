#!/usr/bin/env python
# -*- coding:utf-8 -*
'''
Main program

'''
import argparse
from FUTIL.my_logging import *

from FHOTF.smtp import Smtp, NoneSmtp
from FHOTF.hotfolders import Hotfolders

parser = argparse.ArgumentParser(
            prog='python fhotf.py',
            description = 'Find .hotfolder files and manage hotfolders.',
            epilog = 'Please visit https://github.com/FredThx/FHOTF to see more.')
parser.add_argument("-o","--host", help="SMTP host", action="store")
parser.add_argument("-p","--port", help="SMTP port (default=587)", action="store", default = 587)
parser.add_argument("-u","--user", help="SMTP user", action="store")
parser.add_argument("-w","--password", help = "SMTP password", action="store")
parser.add_argument("-f","--path", help = "Root path for hotfolders", action="store", default = '.')
parser.add_argument("-v","--verbose", help = "Debug mode", action="store_true")
args = parser.parse_args()

if args.verbose:
    my_logging(console_level = DEBUG, logfile_level = INFO, details = False)
else:
    my_logging(console_level = INFO, logfile_level = INFO, details = False)

if not args.host or not args.user or not args.password:
    print("Smtp params not valid (need host, user, password) : a NoneSmtp is used.\n Please read help (--help).")
    smtp = NoneSmtp()
else:
    smtp = Smtp(args.host, args.port, args.user, args.password)

hotfolders = Hotfolders(args.path, smtp)

hotfolders.run()
