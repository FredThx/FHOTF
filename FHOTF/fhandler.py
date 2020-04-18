#!/usr/bin/env python
# -*- coding:utf-8 -*

import sys, os
import re
import time
import logging

from watchdog.events import PatternMatchingEventHandler


class FHandler(PatternMatchingEventHandler):
    '''Gestionnaire d'evenements
    avec
        - des fichier ignorés
    '''
    # Les fichiers ignorés par defaut
    _ignored = ['*.crdownload', 'thumbs.db']

    def __init__(self, ignored = None, only = None):
        '''
            only        :   None ou list de pattern à ignorer
            ignored     :   si None : les valeurs par default, sinon list de pattern à ignorer
        '''
        ignored = self.arrange_pattern(ignored, self._ignored)
        only = self.arrange_pattern(only)
        logging.debug(f"Create PatternMatchingEventHandler with only = {only} and ignored = {ignored}")
        PatternMatchingEventHandler.__init__(self, patterns = only, ignore_patterns = ignored, ignore_directories = True)

    @staticmethod
    def arrange_pattern(pattern, default = None):
        if pattern is None:
            pattern = []
        elif type(pattern)!=list:
            pattern = [pattern]
        if default:
            pattern += default
        if len(pattern) > 0:
            return  ["*/" + i for i in pattern]
        else:
            return None


class FDebounceHandler(FHandler):
    '''Gestionnaire d'evenements
    avec
        - des fichier ignorés
        - un système qui vérifie que les fichiers sont bien terminés
    '''
    # Une extension pour renommer le fichier
    _ = "_$8$_"

    def __init__(self, actions = None, delay = 15, timeout = 600, ignored = None, only = None):
        '''
            actions    :   function callback(filename) or listof
            delay       :   temps (second) entre chaque test
            timeout     :   temps (second) entre la creation et l'abandon de l'action
            ignored     :   si None : les valeurs par default, sinon list des expressions régulière à ignorer
        '''
        self.delay = delay
        self.timeout = timeout
        self.actions = []
        if actions:
            if type(actions) == list:
                self.actions += actions
            else:
                self.action.append(actions)
        FHandler.__init__(self, ignored, only)

    def on_created(self, event):
        logging.info(event)
        self.do_action(event.src_path)

    def on_moved(self, event):
        if not (event.dest_path.endswith(self._) or event.src_path.endswith(self._)):
            logging.info(event)
            self.do_action(event.dest_path)

    def add_action(self, callback):
        '''Add a new action
        '''
        self.actions.append(callback)

    def do_action(self, filename):
        '''Quand creation
        '''
        logging.debug(f"do_action('{filename}')")
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
            logging.debug(f"Check file status in {self.delay} seconds")
            time.sleep(self.delay)
            try:
                new_size = os.path.getsize(filename)
                logging.debug(f"new_size : {new_size}")
            except OSError:
                file_abort = True
                break
            size_change = size != new_size
            if size_change:
                size = new_size
                logging.debug(f"File size change : {size}")
            else:
                try:
                    os.rename(filename, filename_)
                    os.rename(filename_, filename)
                    file_lock = False
                except OSError:
                    logging.debug("File lock.")
        if file_abort:
            logging.debug("The file has disappeared!")
        elif file_lock and size_change:
            logging.debug("Timeout expected.")
        else:
            logging.debug(f"Creation of {filename} id valid.")
            for callback in self.actions:
                callback(filename)

class FSysHandler(FHandler):
    ''' Gestionnaire d'evenements lié à la modif des fichiers '.hotfolder'
    '''
    def __init__(self, only, callback):
        '''Initlialisation
        - only      :   ".hotfolder" par exemple
        - callback
        '''
        self.callback = callback
        FHandler.__init__(self, only = only)

    def on_any_event(self, event):
        logging.info("A modification on a .hotfolder file was detected.")
        self.callback()
