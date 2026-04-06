import json
import os

class LanguageManager:
    def __init__(self):
        self.current_lang = "en"
        self.translations = {}

        # Path to languages folder
        self.base_path = os.path.join(os.path.dirname(__file__), "languages")

    # Load selected language
    def load_language(self, lang_code):
        file_path = os.path.join(self.base_path, f"{lang_code}.json")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
            self.current_lang = lang_code
        except FileNotFoundError:
            print(f"❌ Language file not found: {file_path}")
            self.translations = {}

    # Main method (recommended)
    def get(self, key):
        return self.translations.get(key, key)

    # Alias method (for compatibility with your old code)
    def t(self, key):
        return self.get(key)

    # Optional: formatted text support
    def format(self, key, **kwargs):
        text = self.get(key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    # Optional: check if key exists
    def has_key(self, key):
        return key in self.translations

    # Optional: fallback language support
    def set_fallback(self, fallback_lang="en"):
        fallback_path = os.path.join(self.base_path, f"{fallback_lang}.json")
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                self.fallback_translations = json.load(f)
        except:
            self.fallback_translations = {}

    def get_with_fallback(self, key):
        if key in self.translations:
            return self.translations[key]
        return getattr(self, "fallback_translations", {}).get(key, key)