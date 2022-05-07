# FHOTF
Python scripts to create hotfolders.
(windows or linux system)

Detect files creation (or move) on folders
##### Possibles actions
- start os command (before)
- copy file to destination
- send file by email
- move file to destination
- delete (optionnaly do a backup)
- start os command (after)

##### optionnal :
- system tray icon UI
- autosave parameters and credentials (keyring)

## Installation

Need python >= 3.6

from sources

pip install -r requirements.txt

## Usage

### Configuration

In each folder you want to make an hotfolder: create a .hotfolder file

```toml
# Configuration file for FHOTF
#
# This file should be named '.hotfolder'
# It is applied to itself
#
# Syntax : TOML
#

title = "Hotfolder"

#General information
[hotfolder]
delay = 15
timeout = 600
ignored = ['*.tmp']
only = ['*.txt']
no_empty_file = true
module = "mymodule.py"

#Actions
[actions]

  [actions.before]
  cmd = 'my_script'
  or
  [actions.before.cmd]
    function = "my_python_function_with_None_return_in_mymodule"
    args = ["{filename}"]

  [actions.copy]
  destination = '/home/destination/'

  [actions.email]
  no_empty_file = true
  txt2pdf = true
  to = "fredthx@gmail.com"
  subject = "Hotfolder a détecté un nouveau fichier : {filename}"
  body ='''
  Un nouveau fichier {name} est arrivé sur le hotfolder{path}.
  Ci-joint ce fichier {suffix}.

  Nom du fichier sans l'extention : {basename}

  Salut.'''

  [actions.move]
  txt2pdf = true
  [actions.move.destination]
    function = "get_dest_path"
    args = ["{filename}"]


  [actions.delete]
  backup = true
  backup_folder = './sav/'
  add_date = true

  [actions.after]
  cmd = 'my_script2'
```
Strings can be formated with Literal String interpolation with

```python
{
     'filename' : str(filename),
     'name' : filename.name,
     'suffix' : filename.suffix,
     'path' : filename.drive+filename.stem,
     'basename' : filename.stem,
     'path_basename' : filename.parent/filename.stem
     }
```

All properties can be a python function :
- in the hotfolder, create a python script (ex : mymodule.py)

```python
#! /usr/bin/env python
# -*- coding: utf-8 -*-

def get_dest_path(filename, suffix):
    if suffix == ".txt":
        return './txt/'
    else:
        return './olfa/'

def get_cmd(filename):
    return f"notepad {filename}"

def get_destination_path_for_copy(filename):
    return './olfa/'

def get_txt2pdf(filename):
    return False

def get_dest_path(filename, suffix):
    if suffix == ".txt":
        return './txt/'
    else:
        return './olfa/'

def get_cmd(filename):
    return f"notepad {filename}"

def get_destination_path_for_copy(filename):
    return './olfa/'

def get_txt2pdf(filename):
    return filename == "mon_fichier.txt"
```

### Command

Next, you can execute the command :

```
usage: python fhotf.py [-h] [-o HOST] [-p PORT] [-u USER] [-w PASSWORD]
                       [-f PATH] [-v] [-n] [-k SETTINGSKEY] [-s] [-d]

Find .hotfolder files and manage hotfolders.

optional arguments:
  -h, --help            show this help message and exit
  -o HOST, --host HOST  SMTP host
  -p PORT, --port PORT  SMTP port (default=587)
  -u USER, --user USER  SMTP user
  -w PASSWORD, --password PASSWORD
                        SMTP password
  -f PATH, --path PATH  Root path for hotfolders
  -v, --verbose         Debug mode
  -n, --nogui           no systray
  -k SETTINGSKEY, --settingskey SETTINGSKEY
                        a key for settings
  -s, --store           store command line parameters
  -d, --delete          delete all saved parameters
  -a  --nostarttls      not use starttls
```
Or for a gui system just execute ```python fhotf.py``` and do the configuration with the SystemTray icon.

For command line, execute the command with all parameters for the first time with ```--store``` argument and for the next time only execute ```python fhotf.py``` is needed.


## license
[CeCILL-fr](https://cecill.info/licences/Licence_CeCILL_V2.1-fr.html)
[CeCILL](https://cecill.info/licences/Licence_CeCILL_V2.1-en.html)
