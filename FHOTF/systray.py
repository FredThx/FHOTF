try:
    import PySimpleGUIQt as sg #Utilisation de Qt car la version TkInter place l'icone au dessus de la barre des taches sous windows!
    #A tester plus tard > avril 2020 si pb corrigé......
    NO_GUI=False
except:
    NO_GUI=True


import os
import logging
logging.getLogger("PIL").setLevel(logging.ERROR)

class Fsystray:
    ''' Une interface à base de systray pour piloter Hotfolder
    '''

    title = "Hotfolders"

    def __init__(self, hotfolders):
        '''
        Hotfolders      :   une instance de Hotfolders
        '''
        self.hotfolders = hotfolders
        if not NO_GUI:
            menu_def = ['BLANK', ['&Open hotfolder::open', '&Change hotfolder::change', '&Help::help', '&Quit::quit']]
            self.tray = sg.SystemTray(menu=menu_def, filename=r'hotfolder.png', tooltip = 'fhotf')
            logging.info("systray initialised.")
        else:
            logging.warning("systray not initialised.")


    def open_hotfolder(self):
        '''Open the hotfolder (not tested on linux gui)
        '''
        os.startfile(self.hotfolders.path)

    def change_hotfolder_path(self):
        '''Une une fenêtre pour changer le hotfolder
        '''
        rep = sg.popup_get_folder("Select the new hotfolder root :",self.title , self.hotfolders.path)
        if rep:
            self.hotfolders.change_path(rep)

    def help(self):
        '''Help link
        '''
        sg.popup('Please visit : https://github.com/FredThx/FHOTF', title=self.title)

    def run(self):
        '''run forever the systray
        '''
        assert not NO_GUI, "Error gui not possible."
        logging.info("Systray is running.")
        while True:
            menu_item = self.tray.read() .split('::')[-1]
            logging.debug(f"SystemTray read {menu_item}.")
            if menu_item == "open":
                self.open_hotfolder()
            elif menu_item == "change":
                self.change_hotfolder_path()
            elif menu_item == "help":
                self.help()
            elif menu_item == "quit":
                break

    def show_message(self, message):
        '''Show a ballon message on the systray
        '''
        self.tray.Showmessage(self.title, message)

if __name__ == "__main__":
    from FUTIL.my_logging import *
    my_logging(console_level = DEBUG, logfile_level = INFO, details = False)
    systray = Fsystray(None)
    systray.run()
