# FHOTF
Python scripts to create hotfolders.
(windows or linux system)

Currently :
- detect creation or move of files
- send file by email (or not)
- delete or backup file (or not)

optionnal :
- system tray icon UI
- autosave parameters and credentials (keyring)

## Installation

Need python >= 3.6

from sources

pip install -r requirements.txt

## Usage

### Configuration

In each folder you want to make an hotfolder : a .hotfolder file

```toml
# Fichier de configuration pour FHOTF
#
# Ce fichier doit être nommé '.hotfolder'
# Il s'applique au repertoir dans lequel il est présent
#
# Syntaxe : TOML
#

title = "Hotfolder"

#Général information
[hotfolder]
delay = 15
timeout = 600
ignored = ['*.tmp']
only = ['*.txt']
no_empty_file = true

#Actions générées
[actions]

  [actions.before]
  cmd = 'my_script'

  [actions.copy]
  destination = '/home/destination/'

  [actions.email]
  no_empty_file = true
  txt2pdf = true
  to = "fredthx@gmail.com"
  subject = "Hotfolder detect a new file : {filename}"
  body ='''
  Un nouveau fichier {name} est arrivé sur le hotfolder{path}.
  Ci-joint ce fichier {suffix}.

  Nom du fichier sans l'extention : {basename}

  Salut.'''

  [actions.move]
  destination = 'c:\temp'

  [actions.delete]
  backup = true
  backup_folder = './sav/'
  add_date = true

  [actions.after]
  cmd = 'my_script2'


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

```
or
For a gui system just ```python fhotf.py``` and do the configuration with the SystemTray icon.

For command line, execute the command with all parameters a first time with ```--store``` argument. The next time only ```python fhotf.py``` is needed.


## license
[CeCILL-fr](https://cecill.info/licences/Licence_CeCILL_V2.1-fr.html)
[CeCILL](https://cecill.info/licences/Licence_CeCILL_V2.1-en.html)
