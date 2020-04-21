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

### On linux

#### with systemd

from sources
```bash
sudo python3 setup.py install
```

Change /opt/FHOTF/fhotf.service with your config

```bash
sudo systemctl enable /opt/FHOTF/fhotf.service
sudo systemctl start fhotf.service
```

####

### On windows

(...)

## Usage

### Configuration

In each folder you want to make an hotfolder : a .hotfolder file

```toml
title = "Hotfolder"

#Général information
[hotfolder]
delay = 15
timeout = 600
ignored = ['*.tmp']

#Actions générées
[actions]

  [actions.email]
  to = "fredthx@gmail.com"
  subject = "Hotfolder detect a new file"
  body ='''
  Un nouveau fichier {filename} est arrivé sur le hotfolder.
  Ci-joint ce fichier.

  Salut.'''

  [actions.delete]
  backup = true
  backup_folder = './backup/'
  add_date = true

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

## license
[CeCILL-fr](https://cecill.info/licences/Licence_CeCILL_V2.1-fr.html)
[CeCILL](https://cecill.info/licences/Licence_CeCILL_V2.1-en.html)
