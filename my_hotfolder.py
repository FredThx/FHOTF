#!/usr/bin/env python
# -*- coding:utf-8 -*

from FUTIL.my_logging import *
from FHOTF.fhotf import FDebounceHandler
from FHOTF.fhotf import FWatchdogService
from FHOTF.smtp import Smtp

my_logging(console_level = DEBUG, logfile_level = INFO, details = False)

smtp = Smtp('smtp.gmail.com', 587, 'fredthxdev@gmail.com', "555dcfg8***")
service = FWatchdogService()

text = '''
Bonjour,

Un nouveau fichier est arrivé sur le hotfolder.
voir ci_joint.

bye
'''

sendmail_to_me = FDebounceHandler(lambda filename : smtp.send('fredthx@gmail.com', filename, text, filename))

service.add_schedule(sendmail_to_me, './hotfolder')
service.run()
