import json
import os
import logging
from config_manager import ConfigManager

class LanguageManager:
    def __init__(self):
        self.translations = {}
        self.config_manager = ConfigManager()
        self.current_language = self.config_manager.get_language()
        self.languages = {
            'en': 'English',
            'fr': 'Français',
            'es': 'Español',
            'de': 'Deutsch'
        }
        self.observers = {}
        self.load_translations()

    def load_translations(self):
        logging.info(f"Current working directory: {os.getcwd()}")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for lang_code in self.languages.keys():
            file_path = os.path.join(current_dir, 'languages', f'{lang_code}.json')
            logging.info(f"Attempting to load translation file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.translations[lang_code] = json.load(file)
                    logging.info(f"Successfully loaded translation file for {lang_code}")
            except FileNotFoundError:
                logging.warning(f"Warning: Translation file for {lang_code} not found. Full path: {file_path}")
            except json.JSONDecodeError:
                logging.error(f"Error: Invalid JSON in translation file for {lang_code}")

    def get_translated_text(self, key):
        return self.translations.get(self.current_language, {}).get(key, key)

    def get_languages(self):
        return self.languages

    def get_current_language(self):
        return self.current_language

    def set_language(self, lang_code):
        if lang_code in self.languages:
            self.current_language = lang_code
            self.config_manager.set_language(lang_code) 
            self.notify_observers()
        else:
            logging.error(f"Error: Language code '{lang_code}' not supported.")

    def add_observer(self, name, callback):
        self.observers[name] = callback

    def remove_observer(self, name):
        if name in self.observers:
            del self.observers[name]

    def notify_observers(self):
        for callback in self.observers.values():
            try:
                callback(self.current_language)
            except Exception as e:
                logging.error(f"Error notifying observer: {e}", exc_info=True)

    def translate(self, key, *args):
        translation = self.translations.get(self.current_language, {}).get(key, key)
        if args:
            return translation.format(*args)
        return translation

language_manager = LanguageManager()