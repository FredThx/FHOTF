#!/usr/bin/env python
# -*- coding:utf-8 -*

import logging, os, pathlib, datetime, subprocess, shutil, importlib
import FHOTF.txt2pdf as TXT2PDF

import FHOTF.utils as utils

class Action(object):
    '''Une classe action
    qui va permettre de générer des actions pour fhandler
    à partir d'actions lues dans .hotfolder
    '''
    keys_needed = []
    MODULE_NAME = "$$MODULE_NAME$$"
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
            def f_action(filename):
                if not self.config.get('no_empty_file') or os.path.getsize(filename) > 0:
                    self._get_action()(filename)
                else:
                    logging.debug(f"File is empty : cancel action {self}")
            return f_action
        except AssertionError:
            pass

    def get_function(self, function_name):
        '''Return a function named function_name from module
        '''
        if self.config.get('module'):
            module_path = pathlib.Path(self.config.get('module'))
            if not module_path.is_absolute():
                module_path = self.root / module_path
            spec = importlib.util.spec_from_file_location(self.MODULE_NAME,module_path )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, function_name)

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
            backup_folder = pathlib.Path(self.config.get('backup_folder'))
            if not backup_folder.is_absolute():
                backup_folder = self.root / backup_folder
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

class MoveAction(Action):
    '''Subclass for move action
    '''
    keys_needed = ['destination']
    def __init__(self, config_actions, root):
        '''Initialisation
            config_actions  :   dict issu de toml
            root            :      the root path
        '''
        self.root = root
        super().__init__(config_actions)

    def _get_action(self):
        '''Return the move action
        '''
        destination = self.config.get('destination')
        if isinstance(destination,dict):
            the_function = self.get_function(destination.get('function'))
            destination = lambda *args : pathlib.Path(the_function(*args))
        else :
            destination = pathlib.Path(destination)
        def f_move(filename):
            filename = pathlib.Path(filename)
            if callable(destination):
                args = []
                logging.debug("Arguments for lambda fonction")
                for arg in self.config.get("destination").get('args'):
                     args.append(arg.format(**utils.dict_file(filename)))
                logging.debug(args)
                _destination = destination(*args)
            if not _destination.is_absolute():
                _destination = self.root / _destination
            target = _destination / (filename.stem + filename.suffix)
            logging.debug(f"Move file {filename} to {target}")
            try:
                os.rename(filename, target)
            except OSError:
                shutil.move(filename,target)
        logging.debug("Crt action move")
        return f_move

class CopyAction(Action):
    '''Sub class copy action
    '''
    keys_needed = ['destination']
    def __init__(self, config_actions, root):
        '''Initialisation
            config_actions  :   dict issu de toml
            root            :      the root path
        '''
        self.root = root
        super().__init__(config_actions)

    def _get_action(self):
        '''Return the copy action
        '''
        destination = pathlib.Path(self.config.get('destination'))
        if not destination.is_absolute():
            destination = self.root / destination
        def f_copy(filename):
            filename = pathlib.Path(filename)
            target = destination / (filename.stem + filename.suffix)
            logging.debug(f"Copy file {filename} to {target}")
            shutil.copyfile(filename,target)
        logging.debug("Crt action copy")
        return f_copy

class CmdAction(Action):
    '''Sub class execute cmd action
    '''
    key_needed = ['cmd']

    def _get_action(self):
        '''Return the cmd action
        '''
        cmd = self.config.get('cmd')
        def f_cmd(filename):
            _cmd = cmd.format(**utils.dict_file(filename))
            logging.debug(f"Cmd start : {_cmd}")
            completed_process = subprocess.run(_cmd)
            if completed_process.returncode == 0:
                logging.debug(f"Cmd ok : {completed_process.stdout}")
            else:
                logging.error("Cmd error : {completed_process.stderr}")
        return f_cmd
