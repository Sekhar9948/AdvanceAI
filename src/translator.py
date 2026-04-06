import os
import json

class Translator:
    def __init__(self, lang="en"):
        self.lang = lang
        self.translations = {}
        self.load_language(lang)

    def load_language(self, lang):
        base_path = os.path.dirname(__file__)  # 👉 src folder
        path = os.path.join(base_path, "translations", f"{lang}.json")

        with open(path, "r", encoding="utf-8") as f:
            self.translations = json.load(f)

    def t(self, key):
        return self.translations.get(key, key)