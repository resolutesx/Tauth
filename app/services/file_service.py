import os
from kivy.utils import platform
try:
    from plyer import storagepath
except ImportError:
    storagepath = None

class FileService:
    def __init__(self, user_data_dir):
        self.user_data_dir = user_data_dir

    def get_backup_dir(self):
        if platform == 'android' and storagepath is not None:
            get_docs = getattr(storagepath, 'get_documents_dir', None)
            get_ext = getattr(storagepath, 'get_external_storage_dir', None)
            start_dir = None
            if callable(get_docs):
                start_dir = get_docs()
            if not start_dir and callable(get_ext):
                start_dir = get_ext()
            if not start_dir:
                start_dir = "/sdcard"
            return start_dir
        else:
            return self.user_data_dir
