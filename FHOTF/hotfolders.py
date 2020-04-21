#!/usr/bin/env python
# -*- coding:utf-8 -*


import os, pathlib, datetime, logging, time

import toml

from watchdog.observers.polling import PollingObserver
from FHOTF.fhandler import *
from FHOTF.smtp import Smtp, NoneSmtp
from FHOTF.systray import Fsystray
from FHOTF.settings import KeyFSettings

class Hotfolders:
    '''Une arborescences de hotfodders
    ie :
        des repertoirs dans lequel il existe des fichiers .hotfolder
        qui vont générer des actions à la création de nouveaux fichiers
    '''

    config_file_name = '.hotfolder'
    default_subject = "Hotfolder alert."
    default_settings_key = 'FHOTKEY'
    saved_properties = ['path','smtp_host', 'smtp_port', 'smtp_user', 'smtp_password']

    def __init__(self, path = None, smtp_host = None, smtp_port = None, smtp_user = None, smtp_password = None, gui = False, settings_key = None, settings_store = False,settings_delete = False):
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
        if smtp_user:
            self.smtp_user = smtp_user
        if smtp_password:
            self.smtp_password = smtp_password
        if self.smtp_host:
            self.smtp = Smtp(self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password)
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
        settings['smtp_password']="*******"
        logging.info(f"Settings change (from systray) : {settings}")
        # TODO : faire un peu de vérification
        self.__dict__.update(settings)
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
