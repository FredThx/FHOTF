# FHOTF
Python scripts to create hotfolders.
(windows or linux system)

Currently :
- detect creation or move of files
- send file by email (or not)
- delete or backup file (or not)

## Installation

TODO

## Usage

### Configuration

In each folder you want to make an hotfolder : a .hotfolder file

```toml
title = "Hotfolder"

#Général information
[hotfolder]
recursive = false
delay = 15
timeout = 600
ignored = ['.*\.tmp'] # regex expression

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

Next, you can execute the script :

```python

from FHOTF.smtp import Smtp
from FHOTF.hotfolders import Hotfolders

smtp = Smtp('smtp.domain.com', 587, 'sender@domain.com', "*******")

hotfolders = Hotfolders('.', smtp)

hotfolders.run()
```

## license
[CeCILL-fr](https://cecill.info/licences/Licence_CeCILL_V2.1-fr.html)
[CeCILL](https://cecill.info/licences/Licence_CeCILL_V2.1-en.html)
