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
    date_format = "_%Y-%m-%d_%H-%M-%S"

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
            #Look for function options
            for key, value in self.config.items():
                if isinstance(value,dict):
                    try:
                        the_function = getattr(self.config.get('module'), value.get('function'))
                        value['function'] = lambda *args : the_function(*args)
                    except:
                        logging.warning(f'Error creating function {value}')
                        self.config[key] = None
            def f_action(filename):
                if not self.config.get('no_empty_file') or os.path.getsize(filename) > 0:
                    try:
                        self._get_action()(filename)
                    except Exception as e:
                        logging.error(f"Error during action {self} with file : {filename}:\n {e}")
                else:
                    logging.debug(f"File is empty : cancel action {self}")
            return f_action
        except AssertionError:
            pass

    def get_config(self, key, filename, default = None):
        '''Return the value of the property.
        If is is a function, call it and return the value
        '''
        if isinstance(self.config.get(key), dict):
            _function = self.config.get(key).get('function')
            _args = self.config.get(key).get('args')
            if callable(_function):
                args = []
                for arg in _args:
                    args.append(arg.format(**utils.dict_file(filename)))
                try:
                    value = _function(*args)
                except Exception as e:
                    logging.warning(f"Error in user_function {key}: {e}")
                    value = None
        else:
            value = self.config.get(key)
        logging.debug(f"get_config({key},{repr(filename)},{default}) = '{repr(value)}'")
        return value or default

class EmailAction(Action):
    ''' Subclass for email action
    keys of config:
        - to (needed)   str or function
        - subject       str or subject
        - body          str or subject
        - txt2pdf       boolean or subject
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
        def f_email(filename):
            to = self.get_config('to', filename)
            subject = self.get_config('subject',filename, self.default_subject)
            body = self.get_config('body', filename)
            txt2pdf = self.get_config('txt2pdf', filename, False)
            if txt2pdf and filename[-4:]==".txt":
                pdf_creator = TXT2PDF.PDFCreator(**self.default_pdf_params)
                pdf_filename = pdf_creator.generate(filename)
                logging.debug(f"Envoie email...to{to}, subject:{subject},pdf_filename:{pdf_filename}")
                self.smtp.send(to, subject, body, pdf_filename)
                os.remove(pdf_filename) # A améliorer car ca génère une detection de nouveau fichier.... qui n'aboutie pas
            else:
                self.smtp.send(to, subject, body, filename)
        logging.debug(f"Crt action email")
        return f_email

class DeleteAction(Action):
    '''Subclass for delete action
    keys of config:
        - backup            boolean or function
        - backup_folder     str (a path) or function
        - add_date          boolean or function
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
        def f_move(filename):
            filename = pathlib.Path(filename)
            backup = self.get_config('backup',filename,False)
            if backup:
                backup_folder = pathlib.Path(self.get_config('backup_folder',filename))
                if not backup_folder.is_absolute():
                    backup_folder = self.root / backup_folder
                add_date = self.get_config('add_date', filename, False)
                try:
                    os.mkdir(backup_folder)
                except FileExistsError:
                    pass
                if add_date:
                    date = datetime.datetime.now().strftime(self.date_format)
                else:
                    date = ""
                target = backup_folder / (filename.stem + date + filename.suffix)
                logging.debug(f"Move file {filename} to {target}")
                os.rename(filename, target)
            else:
                os.remove(filename)
        return f_move

class MoveAction(Action):
    '''Subclass for move action
    keys of config:
        - destination (str or function)
        - txt2pdf (TODO)
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
        def f_move(filename):
            filename = pathlib.Path(filename)
            destination = pathlib.Path(self.get_config('destination', filename))
            if not destination.is_absolute():
                destination = self.root / destination
            target = destination / (filename.stem + filename.suffix)
            logging.debug(f"Move file {filename} to {target}")
            try:
                os.rename(filename, target)
            except OSError:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.move(filename,target)
        logging.debug("Crt action move")
        return f_move

class CopyAction(Action):
    '''Sub class copy action
    keys of config:
        - destination (needed) str or function
        - txt2pdf (TODO)
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
        def f_copy(filename):
            filename = pathlib.Path(filename)
            destination = pathlib.Path(self.get_config('destination', filename))
            if destination:
                if not destination.is_absolute():
                    destination = self.root / destination
                target = destination / (filename.stem + filename.suffix)
                logging.debug(f"Copy file {filename} to {target}")
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copyfile(filename,target)
        logging.debug("Crt action copy")
        return f_copy

class CmdAction(Action):
    '''Sub class execute cmd action
    keys of config:
        - cmd   (needed) str or function
    '''
    key_needed = ['cmd']

    def _get_action(self):
        '''Return the cmd action
        '''
        def f_cmd(filename):
            cmd = self.get_config('cmd', filename)
            if cmd:
                logging.debug(f"cmd : {repr(cmd)}, filename : {repr(filename)}")
                _cmd = cmd.format(**utils.dict_file(filename))
                logging.debug(f"Cmd start : {_cmd}")
                completed_process = subprocess.run(_cmd)
                if completed_process.returncode == 0:
                    logging.debug(f"Cmd ok : {completed_process.stdout}")
                else:
                    logging.error("Cmd error : {completed_process.stderr}")
        return f_cmd
