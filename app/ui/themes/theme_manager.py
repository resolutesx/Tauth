import os
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.theme_store = None
        self.theme_pref_path = None
        self._init_theme_store()

    @property
    def user_data_dir(self):
        if platform == "android":
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            return PythonActivity.getAppContext().getFilesDir().getAbsolutePath()
        elif platform == "ios":
            from os.path import expanduser
            return expanduser('~/Documents')
        else:
            return self.app.user_data_dir

    def _init_theme_store(self):
        if self.theme_store is not None:
            return
        try:
            base_dir = self.user_data_dir
        except AttributeError:
            base_dir = os.path.expanduser("~/.authenticator")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
        self.theme_pref_path = os.path.join(base_dir, "theme_prefs.json")
        self.theme_store = JsonStore(self.theme_pref_path)

    def load_theme_prefs(self):
        if self.theme_store and self.theme_store.exists('theme'):
            theme = self.theme_store.get('theme')
            self.app.theme_cls.primary_palette = theme.get('primary_palette', 'DeepOrange')
            self.app.theme_cls.theme_style = theme.get('theme_style', 'Light')
        else:
            self.app.theme_cls.primary_palette = 'DeepOrange'
            self.app.theme_cls.theme_style = 'Light'
            self.save_theme_prefs()

    def save_theme_prefs(self):
        if self.theme_store is not None:
            self.theme_store.put('theme',
                primary_palette=self.app.theme_cls.primary_palette,
                theme_style=self.app.theme_cls.theme_style)
