import sys
import time
import pyotp
from pathlib import Path
from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.list import MDList
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast
from kivymd.color_definitions import colors
from kivymd.theming import ThemableBehavior

from key_manager import KeyManager

class AccountCard(MDCard, ThemableBehavior):
    def __init__(self, name, code="------", ttl=30, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.raw_code = code
        self.on_select = on_select
        self.orientation = "vertical"
        self.elevation = 2
        self.padding = (dp(16), dp(12), dp(16), dp(12))
        self.size_hint_y = None
        self.height = dp(95)
        self.radius = [dp(16)]
        self.ripple_behavior = True
        self.selected = False
        self.long_press_time = 2  # seconds
        self._long_press_event = None
        self.md_bg_color = self.theme_cls.bg_normal
        self._touch_in_progress = False
        self._was_long_press = False

        # Top part: Account info and code
        top_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(16))
        
        info_layout = MDBoxLayout(orientation="vertical", adaptive_height=True)

        account_name = name
        if ":" in name:
            issuer, account_name = name.split(":", 1)
            self.issuer_label = MDLabel(
                text=issuer.upper(),
                font_style="Overline",
                theme_text_color="Secondary",
                adaptive_height=True,
            )
            info_layout.add_widget(self.issuer_label)

        self.name_label = MDLabel(
            text=account_name,
            font_style="Subtitle1",
            theme_text_color="Primary",
            adaptive_height=True,
        )
        info_layout.add_widget(self.name_label)

        self.code_label = MDLabel(
            text=self.format_code(code),
            font_style="H3",
            theme_text_color="Primary",
            adaptive_size=True,
        )

        top_layout.add_widget(info_layout)
        top_layout.add_widget(Widget())  # Spacer
        top_layout.add_widget(self.code_label)

        # Bottom part: Progress bar and TTL
        bottom_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(8),
            padding=(0, dp(8), 0, 0),
        )

        self.progress_bar = MDProgressBar(value=ttl / 30 * 100, size_hint_y=None, height=dp(5))

        self.ttl_label = MDLabel(
            text=f"{ttl}s",
            font_style="Body2",
            theme_text_color="Secondary",
            adaptive_size=True,
        )
        
        bottom_layout.add_widget(self.progress_bar)
        bottom_layout.add_widget(self.ttl_label)
        
        self.add_widget(top_layout)
        self.add_widget(bottom_layout)
        
        # Touch handling for tap/long-press
        self.bind(on_touch_down=self._on_touch_down, on_touch_up=self._on_touch_up)
        self.update_selected_visual()

    def format_code(self, code):
        """Format 6-digit code with space in middle"""
        if len(code) == 6 and code.isdigit():
            return f"{code[:3]} {code[3:]}"
        return code
    
    def _on_touch_down(self, instance, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._touch_in_progress = True
            self._was_long_press = False
            self._long_press_event = Clock.schedule_once(lambda dt: self._on_long_press(touch), self.long_press_time)
        return super().on_touch_down(touch)

    def _on_touch_up(self, instance, touch):
        try:
            if touch.grab_current is self and self in touch.grab_list:
                touch.ungrab(self)
        except ValueError:
            pass
        if self._long_press_event:
            if self._long_press_event.is_triggered:
                self._long_press_event = None
                self._touch_in_progress = False
                self._was_long_press = False
                return super().on_touch_up(touch)
            self._long_press_event.cancel()
            self._long_press_event = None
        # Only toggle selection if this was NOT a long-press
        if not self._was_long_press and self.on_select and self.collide_point(*touch.pos):
            self.on_select(self.name)
        self._touch_in_progress = False
        self._was_long_press = False
        return super().on_touch_up(touch)

    def _on_long_press(self, touch):
        if getattr(self, '_touch_in_progress', False):
            Clipboard.copy(self.raw_code)
            toast(f"Copied code for {self.name}")
            self._was_long_press = True
        self._long_press_event = None
        self._touch_in_progress = False

    def set_selected(self, selected):
        self.selected = selected
        self.update_selected_visual()

    def update_selected_visual(self):
        if self.selected:
            # Use a much darker blue (Blue 900 or custom dark blue)
            self.md_bg_color = (0.07, 0.18, 0.36, 1)  # Custom dark blue RGBA
            self.name_label.theme_text_color = "Custom"
            self.name_label.text_color = (1, 1, 1, 1)
            if hasattr(self, 'issuer_label'):
                self.issuer_label.theme_text_color = "Custom"
                self.issuer_label.text_color = (0.8, 0.9, 1, 1)
            self.code_label.theme_text_color = "Custom"
            self.code_label.text_color = (1, 1, 1, 1)
        else:
            self.md_bg_color = self.theme_cls.bg_normal
            self.name_label.theme_text_color = "Primary"
            if hasattr(self, 'issuer_label'):
                self.issuer_label.theme_text_color = "Secondary"
            self.code_label.theme_text_color = "Primary"

    def update_code(self, code, ttl):
        self.raw_code = code
        self.code_label.text = self.format_code(code)
        self.ttl_label.text = f"{ttl}s"
        
        # Update progress bar value and color
        progress_value = ttl / 30 * 100
        self.progress_bar.value = progress_value
        
        # Change color based on time remaining
        if ttl > 10:
            self.progress_bar.color = self.theme_cls.primary_color
        elif ttl > 5:
            self.progress_bar.color = self.theme_cls.accent_color
        else:
            self.progress_bar.color = self.theme_cls.error_color

class ModernAuthenticatorApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.km = KeyManager()
        self.selected_account = None
        self.account_cards = {}
        self.dialog = None
        self.file_manager = None
        
        # Theme configuration
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Orange"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"

    def build(self):
        self.title = "Authenticator"
        
        # Main screen
        screen = MDScreen()
        
        # Main layout
        main_layout = MDBoxLayout(orientation="vertical")
        
        # Top app bar
        self.toolbar = MDTopAppBar(
            title="Authenticator",
            md_bg_color=self.theme_cls.primary_color,
            specific_text_color="#FFFFFF",
            right_action_items=[
                ["plus", lambda x: self.show_add_dialog()],
                ["dots-vertical", lambda x: self.show_menu(x)]
            ]
        )
        
        # Scrollable content
        self.scroll = MDScrollView()
        self.accounts_layout = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(12),
            padding=[dp(16), dp(16)]
        )
        
        self.scroll.add_widget(self.accounts_layout)
        
        main_layout.add_widget(self.toolbar)
        main_layout.add_widget(self.scroll)
        
        screen.add_widget(main_layout)
        
        # Initialize
        self.refresh_accounts()
        self.start_timer()
        
        return screen
    
    def show_menu(self, instance):
        menu_items = [
            {
                "text": "Edit Selected",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.menu_callback("edit"),
            },
            {
                "text": "Remove Selected",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.menu_callback("remove"),
            },
            {
                "text": "Backup Data",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.menu_callback("backup"),
            },
            {
                "text": "Restore Data",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.menu_callback("restore"),
            },
        ]
        
        self.menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()
    
    def menu_callback(self, action):
        self.menu.dismiss()
        
        if action == "edit":
            self.edit_key()
        elif action == "remove":
            self.remove_key()
        elif action == "backup":
            self.backup()
        elif action == "restore":
            self.restore()
    
    def start_timer(self):
        Clock.schedule_interval(self.update_codes, 1)
    
    def show_snackbar(self, message):
        toast(message)
    
    def show_add_dialog(self):
        content = MDBoxLayout(orientation="vertical", spacing=dp(16), adaptive_height=True)
        
        self.name_field = MDTextField(
            hint_text="Account name (e.g., Google, GitHub)",
            required=True,
            helper_text_mode="on_error",
            helper_text="This field is required"
        )
        
        self.secret_field = MDTextField(
            hint_text="TOTP secret key",
            required=True,
            helper_text_mode="on_error",
            helper_text="Enter the secret key from your service"
        )
        
        content.add_widget(self.name_field)
        content.add_widget(self.secret_field)
        
        self.dialog = MDDialog(
            title="Add New Account",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="ADD",
                    on_release=self.add_account
                ),
            ],
        )
        self.dialog.open()
    
    def add_account(self, instance):
        name = self.name_field.text.strip()
        secret = self.secret_field.text.strip()
        
        if not name or not secret:
            self.name_field.error = not name
            self.secret_field.error = not secret
            return
        
        try:
            self.km.add_key(name, secret)
            self.show_snackbar(f"Added {name}")
            self.refresh_accounts()
            self.close_dialog()
        except Exception as e:
            self.show_error_dialog(str(e))
    
    def edit_key(self):
        if not self.selected_account:
            self.show_snackbar("Please select an account to edit.")
            return

        all_keys = self.km.get_keys()
        key_data = all_keys.get(self.selected_account)

        if key_data is None:
            self.show_snackbar(f"Could not find data for {self.selected_account}")
            return

        self.dialog_content = MDBoxLayout(
            orientation="vertical", spacing=dp(16), adaptive_height=True
        )
        
        self.edit_secret_field = MDTextField(
            hint_text="New TOTP secret key",
            required=True,
            helper_text_mode="on_error",
            helper_text="Enter the new secret key"
        )
        
        self.dialog_content.add_widget(MDLabel(text=f"Updating: {self.selected_account}", theme_text_color="Secondary"))
        self.dialog_content.add_widget(self.edit_secret_field)
        
        self.dialog = MDDialog(
            title="Edit Account",
            type="custom",
            content_cls=self.dialog_content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="UPDATE",
                    on_release=self.update_account
                ),
            ],
        )
        self.dialog.open()
    
    def update_account(self, instance):
        if not self.selected_account:
            self.show_snackbar("No account selected to update.")
            self.close_dialog()
            return

        new_secret = self.edit_secret_field.text.strip()
        if not new_secret:
            self.edit_secret_field.error = True
            return
        
        try:
            # Validate the new secret before updating
            pyotp.TOTP(new_secret).now()
            self.km.update_key(self.selected_account, new_secret)
            self.show_snackbar(f"Updated {self.selected_account}")
            self.refresh_accounts()
            self.close_dialog()
        except Exception as e:
            self.show_error_dialog(str(e))
    
    def remove_key(self):
        if not self.selected_account:
            self.show_snackbar("Please select an account to remove.")
            return

        self.km.remove_key(self.selected_account)
        self.selected_account = None
        self.refresh_accounts()
        self.show_snackbar("Account removed.")
    
    def confirm_remove(self, instance):
        if self.selected_account:
            self.km.remove_key(self.selected_account)
            self.selected_account = None
            self.refresh_accounts()
            self.show_snackbar("Account removed.")
        self.close_dialog()
    
    def backup(self):
        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.select_backup_path,
            )
        self.file_manager.show(str(Path.home()))
        self.backup_mode = True
    
    def restore(self):
        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.select_restore_path,
            )
        self.file_manager.show(str(Path.home()))
        self.backup_mode = False
    
    def exit_file_manager(self, *args):
        if self.file_manager:
            self.file_manager.close()
        self.file_manager = None
    
    def select_backup_path(self, path):
        self.exit_file_manager()
        self.show_backup_dialog(path)
    
    def show_backup_dialog(self, directory):
        content = MDBoxLayout(orientation="vertical", spacing=dp(16), adaptive_height=True)
        
        self.backup_filename_field = MDTextField(
            hint_text="Backup filename",
            text="authenticator_backup.bak"
        )
        
        self.backup_password_field = MDTextField(
            hint_text="Backup password",
            password=True,
            required=True,
            helper_text_mode="on_error",
            helper_text="Password is required for encryption"
        )
        
        content.add_widget(MDLabel(text=f"Location: {directory}", theme_text_color="Secondary"))
        content.add_widget(self.backup_filename_field)
        content.add_widget(self.backup_password_field)
        
        self.dialog = MDDialog(
            title="Create Backup",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="BACKUP",
                    on_release=lambda x: self.create_backup(directory)
                ),
            ],
        )
        self.dialog.open()
    
    def create_backup(self, directory):
        filename = self.backup_filename_field.text.strip()
        password = self.backup_password_field.text.strip()
        
        if not password:
            self.backup_password_field.error = True
            return
        
        if not filename:
            filename = "authenticator_backup.bak"
        
        try:
            path = Path(directory) / filename
            self.km.backup(path, password)
            self.show_snackbar("Backup created successfully")
            self.close_dialog()
        except Exception as e:
            self.show_error_dialog(str(e))
    
    def show_error_dialog(self, message):
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=colors["Red"]["500"],
                    on_release=self.close_dialog
                ),
            ],
        )
        self.dialog.open()
    
    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
    
    def on_account_select(self, name):
        # If already selected, unselect
        if self.selected_account == name:
            self.selected_account = None
            for card in self.account_cards.values():
                card.set_selected(False)
            return
        self.selected_account = name
        for card_name, card in self.account_cards.items():
            card.set_selected(card_name == name)

    def refresh_accounts(self):
        self.accounts_layout.clear_widgets()
        self.account_cards.clear()
        self.selected_account = None
        
        keys = self.km.get_keys()
        if not keys:
            # Empty state
            empty_layout = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                spacing=dp(16),
                padding=[dp(32), dp(64)]
            )
            
            empty_layout.add_widget(MDLabel(
                text="No accounts yet",
                theme_text_color="Secondary",
                font_style="H5",
                halign="center"
            ))
            
            empty_layout.add_widget(MDLabel(
                text="Tap the + button to add your first account",
                theme_text_color="Secondary",
                halign="center"
            ))
            
            self.accounts_layout.add_widget(empty_layout)
            return
        
        for name in keys:
            card = AccountCard(name, "------", 30, on_select=self.on_account_select)
            self.account_cards[name] = card
            self.accounts_layout.add_widget(card)
    
    def update_codes(self, dt):
        rem = 30 - (int(time.time()) % 30)
        
        for name, card in self.account_cards.items():
            secret = self.km.get_keys().get(name, '')
            try:
                code = pyotp.TOTP(secret).now()
            except:
                code = 'ERROR'
            
            card.update_code(code, rem)

    def select_restore_path(self, path):
        self.exit_file_manager()
        if not path.endswith('.bak'):
            self.show_snackbar('Please select a .bak file')
            return
        self.show_restore_dialog(path)

    def show_restore_dialog(self, filepath):
        content = MDBoxLayout(orientation="vertical", spacing=dp(16), adaptive_height=True)
        self.restore_password_field = MDTextField(
            hint_text="Backup password",
            password=True,
            required=True,
            helper_text_mode="on_error",
            helper_text="Enter the password used for encryption"
        )
        content.add_widget(MDLabel(text=f"File: {Path(filepath).name}", theme_text_color="Secondary"))
        content.add_widget(self.restore_password_field)
        self.dialog = MDDialog(
            title="Restore Backup",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="RESTORE",
                    on_release=lambda x: self.restore_backup(filepath)
                ),
            ],
        )
        self.dialog.open()

    def restore_backup(self, filepath):
        password = self.restore_password_field.text.strip()
        if not password:
            self.restore_password_field.error = True
            return
        try:
            self.km.restore(Path(filepath), password)
            self.show_snackbar("Backup restored successfully")
            self.refresh_accounts()
            self.close_dialog()
        except Exception:
            self.show_error_dialog("Failed to restore - check password and file")

if __name__ == '__main__':
    ModernAuthenticatorApp().run()