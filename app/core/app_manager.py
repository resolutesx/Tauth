import time
import pyotp
from pathlib import Path
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.filemanager import MDFileManager
from app.core.config import AppConfig
from app.services.storage_service import StorageService
from app.services.auth_service import AuthService
from app.ui.screens.main_screen import MainScreen
from app.ui.screens.settings_screen import SettingsScreen
from app.ui.screens.icon_preview_screen import IconPreviewScreen
from app.ui.components.dialogs import (
    AddAccountDialog,
    EditAccountDialog,
    BackupDialog,
    RestoreDialog,
    ErrorDialog,
    ConfirmDialog,
)
from app.ui.themes.theme_manager import ThemeManager
from app.utils.platform_utils import get_user_data_dir
from kivymd.uix.label import MDIcon
from app.ui.components.custom_widgets import CustomOneLineIconListItem

class ModernAuthenticatorApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_config = AppConfig()
        self.storage = StorageService(get_user_data_dir())
        self.auth = AuthService(self.storage)
        self.theme_manager = ThemeManager(self)
        
        self.selected_account = None
        self.account_cards = {}
        self.dialog = None
        self.file_manager = None

    def build(self):
        self.theme_manager.load_theme_prefs()
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.accent_hue = "400"
        self.theme_cls.material_style = "M3"
        
        self.title = self.app_config.APP_NAME
        
        self.screen_manager = ScreenManager()
        
        self.main_screen = MainScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.icon_preview_screen = IconPreviewScreen()
        
        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.settings_screen)
        self.screen_manager.add_widget(self.icon_preview_screen)
        
        self.refresh_accounts()
        self.start_timer()
        
        return self.screen_manager

    def start_timer(self):
        Clock.schedule_interval(self.update_codes, 1)

    def update_codes(self, dt):
        rem = 30 - (int(time.time()) % 30)
        for name, card in self.account_cards.items():
            try:
                code = self.auth.get_otp(name)
                card.update_code(code, rem)
            except Exception:
                card.update_code('ERROR', rem)

    def refresh_accounts(self):
        self.main_screen.accounts_layout.clear_widgets()
        self.account_cards.clear()
        self.selected_account = None
        
        keys = self.auth.get_all_keys()
        if not keys:
            self.main_screen.show_empty_message()
            return
        
        for name in keys:
            card = self.app_config.ACCOUNT_CARD_CLASS(name, on_select=self.on_account_select)
            self.account_cards[name] = card
            self.main_screen.accounts_layout.add_widget(card)

    def on_account_select(self, name):
        if self.selected_account == name:
            self.selected_account = None
        else:
            self.selected_account = name
        
        for card_name, card in self.account_cards.items():
            card.set_selected(card_name == self.selected_account)

    def menu_callback(self, action):
        if hasattr(self.main_screen, 'menu') and self.main_screen.menu:
            self.main_screen.menu.dismiss()
        
        if action == "edit":
            self.show_edit_dialog()
        elif action == "remove":
            self.show_confirm_remove_dialog()
        elif action == "backup":
            self.backup()
        elif action == "restore":
            self.restore()
        elif action == "settings":
            self.show_settings()
        elif action == "icon_preview":
            self.show_icon_preview()

    def show_add_dialog(self):
        self.dialog = AddAccountDialog(self, self.add_account)
        self.dialog.show()

    def add_account(self, name, secret):
        try:
            self.auth.add_key(name, secret)
            self.show_snackbar(f"Added {name}")
            self.refresh_accounts()
        except Exception as e:
            self.show_error_dialog(str(e))

    def show_edit_dialog(self):
        if not self.selected_account:
            self.show_snackbar("Please select an account to edit.")
            return
        self.dialog = EditAccountDialog(self, self.selected_account, self.edit_account)
        self.dialog.show()

    def edit_account(self, name, secret):
        try:
            self.auth.update_key(name, secret)
            self.show_snackbar(f"Updated {name}")
            self.refresh_accounts()
        except Exception as e:
            self.show_error_dialog(str(e))

    def show_confirm_remove_dialog(self):
        if not self.selected_account:
            self.show_snackbar("Please select an account to remove.")
            return
        self.dialog = ConfirmDialog(
            self,
            "Remove Account",
            f"Are you sure you want to remove {self.selected_account}?",
            self.remove_account
        )
        self.dialog.show()

    def remove_account(self):
        if self.selected_account:
            self.auth.remove_key(self.selected_account)
            self.selected_account = None
            self.refresh_accounts()
            self.show_snackbar("Account removed.")

    def backup(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_backup_path,
        )
        self.file_manager.show(get_user_data_dir())

    def select_backup_path(self, path):
        self.exit_file_manager()
        self.dialog = BackupDialog(self, path, self.create_backup)
        self.dialog.show()

    def create_backup(self, directory, filename, password):
        try:
            path = Path(directory) / filename
            self.auth.backup(path, password)
            self.show_snackbar("Backup created successfully")
        except Exception as e:
            self.show_error_dialog(str(e))

    def restore(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_restore_path,
        )
        self.file_manager.show(get_user_data_dir())

    def select_restore_path(self, path):
        self.exit_file_manager()
        if not path.endswith('.bak'):
            self.show_snackbar('Please select a .bak file')
            return
        self.dialog = RestoreDialog(self, path, self.restore_backup)
        self.dialog.show()

    def restore_backup(self, filepath, password):
        try:
            self.auth.restore(Path(filepath), password)
            self.show_snackbar("Backup restored successfully")
            self.refresh_accounts()
        except Exception as e:
            self.show_error_dialog("Failed to restore - check password and file")

    def exit_file_manager(self, *args):
        if self.file_manager:
            self.file_manager.close()
        self.file_manager = None

    def show_error_dialog(self, message):
        if self.dialog:
            self.dialog.close()
        self.dialog = ErrorDialog(self, message)
        self.dialog.show()

    def show_settings(self):
        self.screen_manager.current = "settings"
        self.screen_manager.transition.direction = "left"

    def show_icon_preview(self):
        self.screen_manager.current = "icon_preview"
        self.screen_manager.transition.direction = "left"

    def toggle_dark_mode(self, active):
        self.theme_cls.theme_style = 'Dark' if active else 'Light'
        self.theme_manager.save_theme_prefs()
        for card in self.account_cards.values():
            card.update_theme_colors()

    def change_theme(self, color_name):
        self.theme_cls.primary_palette = color_name
        self.theme_manager.save_theme_prefs()
        self.main_screen.toolbar.md_bg_color = self.theme_cls.primary_color
        for card in self.account_cards.values():
            card.update_theme_colors()
            card.progress_bar.color = self.theme_cls.primary_color

    def show_snackbar(self, text):
        snackbar = MDSnackbar()
        snackbar.text = text
        snackbar.open()