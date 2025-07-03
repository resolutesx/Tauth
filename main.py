from app_gui import ModernAuthenticatorApp
from key_manager import KeyManager
from kivy.lang import Builder
import os
from kivy.storage.jsonstore import JsonStore


Builder.load_string('''
<CustomSwitch@MDSwitch>:
''')

if __name__ == '__main__':
    ModernAuthenticatorApp().run()

