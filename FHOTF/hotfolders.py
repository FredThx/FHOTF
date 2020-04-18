#!/usr/bin/env python
# -*- coding:utf-8 -*


import os, pathlib, datetime, logging, time

import toml

from watchdog.observers.polling import PollingObserver
from FHOTF.fhandler import *
from FHOTF.smtp import Smtp



class Hotfolders:
    '''Une arborescences de hotfodders
    ie :
        des repertoirs dans lequel il existe des fichiers .hotfolder
        qui vont générer des actions à la création de nouveaux fichiers
    '''

    config_file_name = '.hotfolder'
    default_subject = "Hotfolder alert."

    def __init__(self, path, smtp = None):
        '''
        path    :   root path
        smtp    :   Smtp (FHOTF.smtp) instance
        '''
        self.path = path
        self.observer = PollingObserver()
        self.sys_observer = PollingObserver()
        logging.info("WatchdogServices Initialised")
        self.smtp = smtp
        self.scan()
        self.crt_sys_deamon()

    def start(self):
        '''Start th deamons
        '''
        self.observer.start()
        self.sys_observer.start()

    def run(self):
        '''Run forever
        '''
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.sys_observer.stop()
            self.observer.stop()
        self.sys_observer.join()
        self.observer.join()


    def scan(self):
        '''Scan all the hotfolders
        '''
        logging.info("\n(Ré)Initilisation des deamons et scanne du repertoire.\n")
        # Supprime tous les anciens programmes
        self.observer.unschedule_all()
        for root, dirs, files in os.walk(self.path):
            root = pathlib.Path(root)
            if self.config_file_name in files:
                logging.debug(f"{self.config_file_name} found in {root}")
                config_file = root / pathlib.Path(self.config_file_name)
                try:
                    config=toml.load(config_file)
                    config_hotfolder=config['hotfolder']
                    config_actions = config['actions']
                except toml.decoder.TomlDecodeError:
                    logging.error(f"Error parsing {config_file}")
                except keyError:
                    logging.error(f"key error in .hotfolder file : {config_file}")
                else:
                    recursive = False#config_hotfolder.get('recursive')
                    delay = config_hotfolder.get('delay')
                    timeout = config_hotfolder.get('timeout')
                    ignored = config_hotfolder.get('ignored', [])
                    only = config_hotfolder.get('only', [])
                    ignored.append(self.config_file_name) # TODO.....quand modif de ce fichier.
                    actions = list()
                    #Email action
                    if 'email' in config_actions:
                        #Pour isoler les variables locales!
                        def inner():
                            try:
                                to = config_actions['email']['to']
                            except keyError:
                                logging.error(f"key error (email) in .hotfolder file : {config_file}")
                            else:
                                subject = config_actions['email'].get('subject',self.default_subject)
                                body = config_actions['email'].get('body')
                                def f_email(filename):
                                    self.smtp.send(to, subject, body, filename)
                                actions.append(f_email)
                                logging.debug(f"Crt action email (subject:'{subject}')")
                        inner()
                    if 'delete' in config_actions:
                        if config_actions['delete'].get('backup'):
                            #Pour isoler les variables locales!
                            def inner():
                                backup_folder = root / pathlib.Path(config_actions['delete'].get('backup_folder'))
                                add_date = config_actions['delete'].get('add_date')
                                #création si besoin du repertoir backup
                                try:
                                    os.mkdir(backup_folder)
                                except FileExistsError:
                                    pass
                                def f_move(filename):
                                    filename = pathlib.Path(filename)
                                    if add_date:
                                        date = datetime.datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")
                                    else:
                                        date = ""
                                    target = backup_folder / (filename.stem + date + filename.suffix)
                                    logging.debug(f"Move file {filename} to {target}")
                                    os.rename(filename, target)
                                actions.append(f_move)
                                logging.debug("Crt action delete")
                            inner()
                        else:
                            actions.append(lambda filename : os.remove(filename))
                    handler = FDebounceHandler(actions, delay, timeout, ignored, only)
                    self.observer.schedule(handler, root, recursive)
        logging.info("\nScan finished.\n")

    def crt_sys_deamon(self):
        ''' Va créer un observer pour la détection des changements dans les fichiers '.hotfolder'
        '''
        sys_handler = FSysHandler(only=self.config_file_name, callback = self.scan)
        self.sys_observer.schedule(sys_handler, self.path, True)
