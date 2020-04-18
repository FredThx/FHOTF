# FHOTF
Python scripts to create hotfolders.
(windows or linux system)

Currently :
- detect creation or move of files
- send file by email (or not)
- delete or backup file (or not)

## Installation

### On linux

#### from sources

```bash
sudo python3 setup.py install
```

Change /opt/FHOTF/fhotf.service with your config

```bash
sudo systemctl enable /opt/FHOTF/fhotf.service
sudo systemctl start fhotf.service
```
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

### Deamon

Next, you can execute the command :

```
usage: python fhotf.py [-h] [-o HOST] [-p PORT] [-u USER] [-w PASSWORD] [-f PATH] [-v]
```

## license
[CeCILL-fr](https://cecill.info/licences/Licence_CeCILL_V2.1-fr.html)
[CeCILL](https://cecill.info/licences/Licence_CeCILL_V2.1-en.html)
