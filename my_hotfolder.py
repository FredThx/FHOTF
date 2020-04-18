#!/usr/bin/env python
# -*- coding:utf-8 -*

from FUTIL.my_logging import *

from FHOTF.smtp import Smtp
from FHOTF.hotfolders import Hotfolders

my_logging(console_level = DEBUG, logfile_level = INFO, details = False)

smtp = Smtp('smtp.gmail.com', 587, 'fredthxdev@gmail.com', "555dcfg8***")

path = sys.argv[1] if len(sys.argv) > 1 else '/mnt/e/Hotfolder/'
hotfolders = Hotfolders(path, smtp)

hotfolders.run()
