import os
from kivy.utils import platform

def get_user_data_dir():
    """Return a directory path for storing user data, platform-appropriately."""
    if platform == "android":
        try:
            from android.storage import app_storage_path
            return app_storage_path()
        except ImportError:
            # In case 'android' module isn't available
            return os.path.join(os.path.expanduser("~"), ".local", "share", "Tautth")
    elif platform == "ios":
        return os.path.expanduser("~/Documents")
    else:
        home = os.path.expanduser("~")
        if platform == "win":
            base = os.getenv("APPDATA", home)
            return os.path.join(base, "Tautth")
        elif platform == "macosx":
            return os.path.join(home, "Library", "Application Support", "Tautth")
        else:
            return os.path.join(home, ".local", "share", "Tautth")
