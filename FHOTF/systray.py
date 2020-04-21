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
            menu_def = ['BLANK', ['&Open hotfolder::open', '&Configuration::config', '&Help::help', '&Quit::quit']]
            self.tray = sg.SystemTray(menu=menu_def, filename=r'icone.ico', tooltip = 'fhotf')
            logging.info("systray initialised.")
        else:
            logging.warning("systray not initialised.")


    def open_hotfolder(self):
        '''Open the hotfolder (not tested on linux gui)
        '''
        os.startfile(self.hotfolders.path)

    def change_config(self):
        '''Une une fenêtre pour changer les paramètres
        '''
        window = sg.Window(self.title, [
            [sg.Text("Hotfolder path : "), sg.InputText(key='path',default_text = self.hotfolders.path),sg.FolderBrowse(initial_folder = self.hotfolders.path)],
            [sg.Text("Smtp :")],
            [sg.Text('   Host : '), sg.InputText(key = 'smtp_host', default_text = self.hotfolders.smtp_host)],
            [sg.Text('   Port :'),sg.InputText(key = 'smtp_port', default_text = self.hotfolders.smtp_port)],
            [sg.Text('   Sender :'), sg.InputText(key = 'smtp_user', default_text = self.hotfolders.smtp_user)],
            [sg.Text('   Password :'), sg.InputText(key='smtp_password', password_char="*", default_text = self.hotfolders.smtp_password)],
            [sg.Cancel(),sg.OK()] ])
        event, values = window.Read()
        if event == 'OK':
            self.hotfolders.change_settings(values)
        window.close()

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
            elif menu_item == "config":
                self.change_config()
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
