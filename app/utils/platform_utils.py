import os
from kivy.utils import platform

def get_user_data_dir():
    if platform == "android":
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        return PythonActivity.getAppContext().getFilesDir().getAbsolutePath()
    elif platform == "ios":
        from os.path import expanduser
        return expanduser('~/Documents')
    else:
        home = os.path.expanduser("~")
        if platform == "win":
            base = os.getenv("APPDATA", home)
            return os.path.join(base, "Tautth")
        elif platform == "macosx":
            return os.path.join(home, "Library", "Application Support", "Tautth")
        else:
            return os.path.join(home, ".local", "share", "Tautth")
