#!/usr/bin/env python
# -*- coding:utf-8 -*


import os, pathlib, datetime, logging, time, subprocess

import toml

from watchdog.observers.polling import PollingObserver
from FHOTF.fhandler import *
from FHOTF.smtp import Smtp, NoneSmtp
from FHOTF.systray import Fsystray
from FHOTF.settings import KeyFSettings
from FHOTF.action import *
from FHOTF.__init__ import __version__

import FHOTF.utils as utils

class Hotfolders:
    '''Une arborescences de hotfodders
    ie :
        des repertoirs dans lequel il existe des fichiers .hotfolder
        qui vont générer des actions à la création de nouveaux fichiers
    '''

    config_file_name = '.hotfolder'
    default_settings_key = 'FHOTKEY'
    saved_properties = ['path','smtp_host', 'smtp_port', 'smtp_user_addr', 'smtp_user', 'smtp_password']

    def __init__(self, path = None, smtp_host = None, smtp_port = None, smtp_user_addr = None, smtp_user = None, smtp_password = None, gui = False, settings_key = None, settings_store = False,settings_delete = False, starttls = True):
        '''
        path    :   root path
        smtp    :   Smtp (FHOTF.smtp) instance
        '''

        self.settings = KeyFSettings(settings_key or self.default_settings_key)
        self.restore_settings()
        if path:
            self.path = path
        if smtp_host:
            self.smtp_host = smtp_host
        if smtp_port:
            self.smtp_port = smtp_port
        if smtp_user_addr:
            self.smtp_user_addr = smtp_user
        if smtp_user:
            self.smtp_user = smtp_user
        if smtp_password:
            self.smtp_password = smtp_password
        if self.smtp_host:
            self.smtp = Smtp(self.smtp_host, self.smtp_port, self.smtp_user_addr, self.smtp_user, self.smtp_password, starttls)
        else:
            self.smtp = NoneSmtp()
        self.gui = gui
        if not self.path:
            self.path = '.'
        if settings_store:
            self.store_settings()
        if settings_delete:
            self.delete_settings()
        self.observer = PollingObserver()
        self.sys_observer = PollingObserver()
        logging.info("WatchdogServices Initialised")
        self.scan()
        self.crt_sys_deamon()

    def restore_settings(self):
        '''Restore settings from keyring
        '''
        settings = self.settings.get(self.saved_properties)
        if settings:
            self.__dict__.update(settings)

    def store_settings(self):
        '''Store settings on keyring
        '''
        self.settings.set({k:v for k,v in self.__dict__.items() if k in self.saved_properties})

    def delete_settings(self):
        '''Delete settings on keyring
        '''
        self.settings.delete(self.saved_properties)

    def change_settings(self, settings):
        '''Change the settings (from systray)
        '''
        # TODO : faire un peu de vérification
        self.__dict__.update(settings)
        settings['smtp_password']="*******"
        logging.info(f"Settings change (from systray) : {settings}")
        self.store_settings()
        self.smtp = Smtp(self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password)
        self.scan()

    def start(self):
        '''Start the deamons
        '''
        logging.info("Start Holfoders.")
        self.observer.start()
        self.sys_observer.start()

    def stop(self):
        '''Stop all
        '''
        logging.info("Stop Holfoders.")
        self.sys_observer.stop()
        self.observer.stop()
        self.sys_observer.join()
        self.observer.join()

    def run(self):
        '''Run forever
        '''
        self.start()
        if self.gui:
            try:
                Fsystray(self).run()
            except AssertionError:
                logging.warning("Systray cannot be laught. No gui available. Remove the --gui option or install pystray and easygui and use a os with gui.")
        else:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        self.stop


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
                    logging.debug("config : %s"%config)
                except toml.decoder.TomlDecodeError:
                    logging.error(f"Error parsing {config_file}")
                except KeyError:
                    logging.error(f"key error in .hotfolder file : {config_file}")
                except Exception as e:
                    logging.error(f"Unknow Error on {config_file} : {e}")
                else:
                    recursive = False#config_hotfolder.get('recursive')
                    delay = config_hotfolder.get('delay')
                    timeout = config_hotfolder.get('timeout')
                    ignored = config_hotfolder.get('ignored', [])
                    only = config_hotfolder.get('only', [])
                    ignored.append(self.config_file_name) # TODO.....quand modif de ce fichier.
                    no_empty_file = config_hotfolder.get('no_empty_file')
                    actions = list()
                    #Before command
                    if 'before' in config_actions:
                        def inner(): #Pour isoler les variables locales!
                            try:
                                cmd = config_actions['before']['cmd']
                            except KeyError:
                                logging.error(f"key error (before) in .hotfolder file : {config_file}")
                            else:
                                def f_cmd(filename):
                                    logging.debug(f"Cmd start : {cmd}")
                                    _cmd = cmd.format(**utils.dict_file(filename))
                                    logging.debug(utils.dict_file(filename))
                                    logging.debug(_cmd)
                                    completed_process = subprocess.run(_cmd)
                                    if completed_process.returncode == 0:
                                        logging.debug(f"Cmd ok : {completed_process.stdout}")
                                    else:
                                        logging.error("Cmd error : {completed_process.stderr}")
                                actions.append(f_cmd)
                        inner()
                    #Email action
                    if 'email' in config_actions:
                        action = EmailAction(config_actions['email'], self.smtp)
                        if action:
                            actions.append(action.get_action())
                    #Delete action
                    if 'delete' in config_actions:
                        action = DeleteAction(config_actions['delete'], root)
                        if action:
                            actions.append(action.get_action())
                    handler = FDebounceHandler(actions, delay, timeout, ignored, only,no_empty_file)
                    self.observer.schedule(handler, root, recursive)
        logging.info("\nScan finished.\n")

    def version(self):
        return __version__

    def crt_sys_deamon(self):
        ''' Va créer un observer pour la détection des changements dans les fichiers '.hotfolder'
        '''
        sys_handler = FSysHandler(only=self.config_file_name, callback = self.scan)
        self.sys_observer.schedule(sys_handler, self.path, True)
