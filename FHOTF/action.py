#!/usr/bin/env python
# -*- coding:utf-8 -*

import logging, os, pathlib, datetime
import FHOTF.txt2pdf as TXT2PDF

import FHOTF.utils as utils

class Action(object):
    '''Une classe action
    qui va permettre de générer des actions pour fhandler
    à partir d'actions lues dans .hotfolder
    '''
    keys_needed = []
    def __init__(self, config_actions):
        '''Initialisation
        config_action  :   dict issu de toml
        '''
        self.config = {}
        for k,v in config_actions.items():
            self.config[k] = v

    def get_action(self):
        ''' Return the action for fhandler
        '''
        try:
            for key_needed in self.keys_needed:
                assert key_needed in self.config,f"key error ({key_needed} is require in .hotfolder file : {self.config}"
            return self._get_action()
        except AssertionError:
            pass

class EmailAction(Action):
    ''' Subclass for email action
    '''
    keys_needed = ['to']
    default_subject = "Hotfolder alert."
    default_pdf_params = {'font_size' : 7.0, 'margin_left' : 0.5, 'margin_right' : 0.0}

    def __init__(self, config_actions, smtp):
        '''Initialisation
            config_actions  :   dict issu de toml
            smtp            :   a Smtp instance
        '''
        self.smtp = smtp
        super().__init__(config_actions)

    def _get_action(self):
        ''' Return the email action
        '''
        to = self.config.get('to')
        subject = self.config.get('subject',self.default_subject)
        body = self.config.get('body')
        txt2pdf = self.config.get('txt2pdf', False)
        def f_email(filename):
            if txt2pdf and filename[-4:]==".txt":
                pdf_creator = TXT2PDF.PDFCreator(**self.default_pdf_params)
                pdf_filename = pdf_creator.generate(filename)
                logging.debug(f"Envoie email...to{to}, subject:{subject},pdf_filename:{pdf_filename}")
                self.smtp.send(to, subject, body, pdf_filename)
                os.remove(pdf_filename) # A améliorer car ca génère une detection de nouveau fichier.... qui n'aboutie pas
            else:
                self.smtp.send(to, subject, body, filename)
        logging.debug(f"Crt action email (subject:'{subject}')")
        return f_email

class DeleteAction(Action):
    '''Subclass for delete action
    '''

    def __init__(self, config_actions, root):
        '''Initialisation
            config_actions  :   dict issu de toml
            root            :      the root path
        '''
        self.root = root
        super().__init__(config_actions)

    def _get_action(self):
        '''return the delete action
        '''
        if self.config.get('backup'):
            backup_folder = self.root / pathlib.Path(self.config.get('backup_folder'))
            add_date = self.config.get('add_date')
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
            logging.debug("Crt action delete")
            return f_move
        else:
            return lambda filename : os.remove(filename)
