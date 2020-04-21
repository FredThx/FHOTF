import logging
import toml

try:
    import keyring
except:
    pass


class FSettings:
    '''A class to store settings
    '''
    pass

class IniFSetting(FSettings):
    '''A toml file class settings
    '''
    def __init__(self, filename):
        self.filename = filename


    def get(self, keys = None):
        '''restore the settings
        keys    :   a list of key or a key
        return a dict
        '''
        try:
            settings = toml.load(self.filename)
        except FileNotFoundError:
            logging.warning(f"{settings_filename} not present.")
        else:
            if keys:
                if type(keys) != list:
                    keys = [keys]
                return {k:v for k,v in settings.items() if k in keys}
            else:
                return settings


    def set(self, settings):
        '''Store the settings
        return True if done
        '''
        try:
            with open(self.filename, 'w') as settings_file:
                toml.dump(settings, settings_file)
            return True
        except (OSError, IOError):
            logging.error("Unable to save settings.")


class KeyFSettings(FSettings):
    '''A keyring based class settings
    '''
    def __init__(self, service_name = 'KeyFSettings'):
        '''Initialisation
        key         :       a magic-key (string)
        '''
        self.service_name = service_name


    def set(self, settings):
        '''Store the settings
        settings    :   a dict {'key':values}
        '''
        try:
            for k,v in settings.items():
                keyring.set_password(self.service_name, k, v)
            return True
        except Exception as e:
            logging.error(e)

    def delete(self, keys):
        '''Delete the saved settings
        keys    :   a list of key or a key
        '''
        if type(keys) != list:
            keys = [keys]
        for key in keys:
            keyring.delete_password(self.service_name, key)

    def get(self, keys):
        '''restore the settings
        keys    :   a list of key or a key
        return a dict
        '''
        if type(keys) != list:
            keys = [keys]
        result = {}
        try:
            for key in keys:
                result[key] = keyring.get_password(self.service_name, key)
            return result
        except:
            return None
