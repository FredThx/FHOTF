#!/usr/bin/env python
# -*- coding:utf-8 -*


import toml
import os, pathlib, datetime, logging

from FHOTF.fhotf import FDebounceHandler
from FHOTF.fhotf import FWatchdogService
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
        self.service = FWatchdogService()
        self.smtp = smtp
        self.scan()

    def run(self):
        self.service.run()

    def scan(self):
        '''Scan all the hotfolders
        '''
        for root, dirs, files in os.walk(self.path):
            root = pathlib.Path(root)
            if self.config_file_name in files:
                logging.debug("%s found in %s"%(self.config_file_name, root))
                config_file = root / pathlib.Path(self.config_file_name)
                try:
                    config=toml.load(config_file)
                    config_hotfolder=config['hotfolder']
                    config_actions = config['actions']
                except toml.decoder.TomlDecodeError:
                    logging.error("Error parsing %s"%config_file)
                except keyError:
                    logging.error("key error in .hotfolder file : %s"%config_file)
                else:
                    recursive = config_hotfolder.get('recursive')
                    delay = config_hotfolder.get('delay')
                    timeout = config_hotfolder.get('timeout')
                    ignored = config_hotfolder.get('ignored', [])
                    ignored.append(self.config_file_name) # TODO.....
                    actions = list()
                    #Email action
                    if 'email' in config_actions:
                        #Pour isoler les variables locales!
                        def inner():
                            try:
                                to = config_actions['email']['to']
                            except keyError:
                                logging.error("key error (email) in .hotfolder file : %s"%config_file)
                            else:
                                subject = config_actions['email'].get('subject',self.default_subject)
                                body = config_actions['email'].get('body')
                                def f_email(filename):
                                    logging.debug("Send Email %s"%subject)
                                    self.smtp.send(to, subject.format(filename=filename), body.format(filename=filename), filename)
                                actions.append(f_email)
                                logging.debug("Crt action email (subject:%s)"%subject)
                        inner()
                    if 'delete' in config_actions:
                        if config_actions['delete'].get('backup'):
                            #Pour isoler les variables locales!
                            def inner():
                                backup_folder = root / pathlib.Path(config_actions['delete'].get('backup_folder'))
                                add_date = config_actions['delete'].get('add_date')
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
                                    logging.debug("Move file %s to %s"%(filename, target))
                                    os.rename(filename, target)
                                actions.append(f_move)
                            inner()
                        else:
                            actions.append(lambda filename : os.remove(filename))
                    handler = FDebounceHandler(actions, delay, timeout, ignored)
                    self.service.add_schedule(handler, root, recursive)
