try:
    import pystray
    from PIL import Image, ImageDraw
    import easygui
    NO_GUI=False
except:
    NO_GUI=True

import logging
logging.getLogger("PIL").setLevel(logging.ERROR)

class Fsystray:
    ''' Une interface à base de systray pour piloter Hotfolder
    '''
    def __init__(self, hotfolders):
        '''
        Hotfolders      :   une instance de Hotfolders
        '''
        if not NO_GUI:
            self.hotfolders = hotfolders
            self.icon = pystray.Icon('Hotfolders')
            self.icon.icon = self.create_image()
            self.icon.menu=pystray.Menu(
                pystray.MenuItem(
                    'Ouvrir le hotfolder',
                    self.open_hotfolder),
                pystray.MenuItem(
                    'Changer de hotfolder',
                    self.change_hotfolder_path),
                pystray.MenuItem(
                    'Aide',
                    self.help),
                pystray.MenuItem(
                    'Quitter',
                    self.icon.stop))
            logging.info("systray initialised.")
        else:
            logging.warning("systray not initialised.")

    def create_image(self, width = 32, height = 32, color1 = 'red', color2 = 'blue'):
        # Generate an image and draw a pattern
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 2, 0, width, height // 2),
            fill=color2)
        dc.rectangle(
            (0, height // 2, width // 2, height),
            fill=color2)
        return image

    def open_hotfolder(self):
        pass

    def change_hotfolder_path(self):
        '''Une une fenètre pour changer le hotfolder
        '''
        rep = easygui.diropenbox("Selectionner le repertoire","Hotfolders", "e:\\Hotfolder")
        if rep:
            self.hotfolders.change_path(rep)

    def help(self):
        '''Help link
        '''
        easygui.textbox(msg='https://github.com/FredThx/FHOTF', title='Hotfolders')

    def run(self):
        '''run forever the systray
        '''
        assert not NO_GUI, "Error gui not possible."
        logging.info("Systray is running.")
        self.icon.run()
