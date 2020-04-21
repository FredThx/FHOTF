#!/usr/bin/env python
# -*- coding:utf-8 -*
'''
Main program

'''
import argparse
from FUTIL.my_logging import *

from FHOTF.hotfolders import Hotfolders

parser = argparse.ArgumentParser(
            prog='python fhotf.py',
            description = 'Find .hotfolder files and manage hotfolders.',
            epilog = 'Please visit https://github.com/FredThx/FHOTF to see more.')
parser.add_argument("-o","--host", help="SMTP host", action="store")
parser.add_argument("-p","--port", help="SMTP port (default=587)", action="store", default = 587)
parser.add_argument("-u","--user", help="SMTP user", action="store")
parser.add_argument("-w","--password", help = "SMTP password", action="store")
parser.add_argument("-f","--path", help = "Root path for hotfolders", action="store")
parser.add_argument("-v","--verbose", help = "Debug mode", action="store_true")
parser.add_argument("-n","--nogui", help = "no systray", action="store_true")
parser.add_argument("-k","--settingskey", help = "a key for settings", action="store")
parser.add_argument("-s","--store", help = "store command line parameters", action="store_true")
parser.add_argument("-d","--delete", help = "delete all saved parameters", action="store_true")

args = parser.parse_args()

if args.verbose:
    my_logging(console_level = DEBUG, logfile_level = INFO, details = False)
else:
    my_logging(console_level = INFO, logfile_level = INFO, details = False)

hotfolders = Hotfolders(args.path, args.host, args.port, args.user, args.password, gui = not args.nogui, settings_key = args.settingskey, settings_store = args.store, settings_delete = args.delete)

hotfolders.run()
