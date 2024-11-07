import json
import os
import locale
import logging

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser('~'), '.imagemap_config.json')
        self.config = self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving config: {e}")

    def get_language(self):
        if 'language' in self.config:
            return self.config['language']
        
        try:
            system_lang = locale.getdefaultlocale()[0]
            if system_lang:
                lang_code = system_lang.split('_')[0].lower()
                return lang_code
        except Exception as e:
            logging.error(f"Error getting system language: {e}")
        
        return 'en' 

    def set_language(self, language):
        self.config['language'] = language
        self.save_config()