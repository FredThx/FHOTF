#!/usr/bin/env python
# -*- coding:utf-8 -*

import sys, os
import re
import time
import logging

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver



class handler(FileSystemEventHandler):
    '''Gestionnaire d'evenements
    '''
    _ = "_$8$_"
    _ignored = ['.*\.crdownload', 'thumbs.db']

    def __init__(self, delay = 15, timeout = 600, ignored = None):
        '''
            delay       :   temps (second) entre chaque test
            timeout     :   temps (second) entre la creation et l'abandon de l'action
            ignored     :   si None : les valeurs par default, sinon list des expressions régulière à ignorer
        '''
        self.delay = delay
        self.timeout = timeout
        if ignored is None:
            ignored = self._ignored
        self.ignored = re.compile("|".join(ignored))
        super().__init__()

    def on_created(self, event):
        logging.info(event)
        self.do_action(event.src_path)

    def on_moved(self, event):
        if not (event.dest_path.endswith(self._) or event.src_path.endswith(self._)):
            logging.info(event)
            self.do_action(event.dest_path)

    def do_action(self, filename):
        '''Quand creation
        '''
        if self.ignored.fullmatch(filename)==None:
            logging.debug("do_action('%s')"%filename)
            timeout = time.time() + self.timeout
            filename_ = filename + self._
            file_lock = True
            size_change = True
            file_abort = False
            try:
                size = os.path.getsize(filename)
            except OSError:
                file_abort = True
                size = -1
            while (size_change or file_lock) and time.time() < timeout and (not file_abort):
                logging.debug("Check file status in %s seconds"%self.delay)
                time.sleep(self.delay)
                try:
                    new_size = os.path.getsize(filename)
                except OSError:
                    file_abort = True
                    break
                size_change = size != new_size
                if size_change:
                    size = new_size
                    logging.debug("File size change : %s"%size)
                else:
                    try:
                        os.rename(filename, filename_)
                        os.rename(filename_, filename)
                        file_lock = False
                    except OSError:
                        logging.debug("File lock.")
            if file_abort:
                logging.debug("Le fichier a disparu!")
            elif file_lock and size_change:
                logging.debug("Timeout expected.")
            else:
                logging.debug("Creation of %s finish!"%filename)
                #TODO : faire quelque chose
        else:
            logging.debug("%s ignored."%filename)


class WatchdogService:
    '''Notre chien de garde
    '''

    def __init__(self):
        '''Initlialisation
        '''
        self.observer = PollingObserver()
        logging.info("WatchdogService Initlialised")

    def add_schedule(self, event_handler, path, recursive=False):
        '''Add a new schedule
            event       :   a handler
            path        :   path of the folder
            recursive   :   default = True
        '''
        self.observer.schedule(event_handler, path, recursive=recursive)
        logging.info("path = %s surveillé."%path)

    def run(self):
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()





if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = handler()
    service = WatchdogService()
    service.add_schedule(event_handler, path)
    service.run()
