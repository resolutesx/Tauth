import sys
import time
import pyotp
from pathlib import Path
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
try:
    from plyer import storagepath
except ImportError:
    storagepath = None

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
from kivymd.uix.label import MDIcon
import pyperclip
from kivymd.uix.list import OneLineIconListItem
from kivy.properties import StringProperty
from kivymd.uix.list import IconLeftWidget
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.storage.jsonstore import JsonStore
import os

from key_manager import KeyManager
from settings_gui import SettingsScreen

Builder.load_string("""
<CustomOneLineIconListItem>:
    IconLeftWidget:
        icon: root.icon
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1
""")

class CustomOneLineIconListItem(OneLineIconListItem):
    icon = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(IconLeftWidget(icon=self.icon, theme_text_color="Custom", text_color=(0, 0, 0, 1)))

class AccountCard(MDCard, ThemableBehavior):
    def __init__(self, name, code="------", ttl=30, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.raw_code = code
        self.on_select = on_select
        self.orientation = "vertical"
        self.elevation = 1
        self.padding = (dp(24), dp(20), dp(24), dp(20))
        self.size_hint_y = None
        self.height = dp(120)
        self.radius = [dp(16)]
        self.ripple_behavior = True
        self.selected = False
        self.long_press_time = 1.5
        self._long_press_event = None
        self._touch_in_progress = False
        self._was_long_press = False
        
        self.md_bg_color = self.theme_cls.bg_normal
        self.line_color = (*self.theme_cls.divider_color[:3], 0.3)

        top_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(24))
        info_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(4))
        
        account_name = name
        if ":" in name:
            issuer, account_name = name.split(":", 1)
            self.issuer_label = MDLabel(
                text=issuer.upper(),
                font_style="Caption",
                theme_text_color="Secondary",
                adaptive_height=True,
                font_size=dp(12),
                bold=True
            )
            info_layout.add_widget(self.issuer_label)
            
        self.name_label = MDLabel(
            text=account_name,
            font_style="H6",
            theme_text_color="Primary",
            adaptive_height=True,
            font_size=dp(18),
            bold=True,
            size_hint_x=1,
            shorten=False,
            max_lines=2,
        )
        info_layout.add_widget(self.name_label)
        
        self.code_label = MDLabel(
            text=self.format_code(code),
            font_style="H4",
            theme_text_color="Primary",
            adaptive_size=True,
            font_size=dp(32),
            bold=True,
            size_hint_x=None,
            width=dp(180),
            halign="right",
        )
        
        top_layout.add_widget(info_layout)
        top_layout.add_widget(Widget())
        top_layout.add_widget(self.code_label)
        
        bottom_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(16),
            padding=(0, dp(16), 0, 0),
        )
        
        self.progress_bar = MDProgressBar(
            value=ttl / 30 * 100, 
            size_hint_y=None, 
            height=dp(4),
            color=self.theme_cls.primary_color,
            back_color=(*self.theme_cls.divider_color[:3], 0.4)
        )
        self.progress_bar.radius = [dp(2)]
        
        self.ttl_label = MDLabel(
            text=f"{ttl}s",
            font_style="Body2",
            theme_text_color="Secondary",
            adaptive_size=True,
            font_size=dp(14),
            bold=True
        )
        
        bottom_layout.add_widget(self.progress_bar)
        bottom_layout.add_widget(self.ttl_label)
        
        self.add_widget(top_layout)
        self.add_widget(bottom_layout)
        
        self.bind(on_touch_down=self._on_touch_down, on_touch_up=self._on_touch_up)
        self.update_selected_visual()

    def format_code(self, code):
        if len(code) == 6 and code.isdigit():
            return f"{code[:3]} {code[3:]}"
        return code
    
    def _on_touch_down(self, instance, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._touch_in_progress = True
            self._was_long_press = False
            anim = Animation(elevation=4, md_bg_color=self.theme_cls.bg_light, duration=0.1)
            anim.start(self)
            self._long_press_event = Clock.schedule_once(lambda dt: self._on_long_press(touch), self.long_press_time)
            return True
        return super().on_touch_down(touch)

    def _on_touch_up(self, instance, touch):
        if self.collide_point(*touch.pos):
            if not self.selected:
                anim = Animation(elevation=1, md_bg_color=self.theme_cls.bg_normal, duration=0.2)
                anim.start(self)
            if touch.grab_current is self:
                touch.ungrab(self)
            if self._long_press_event:
                if self._long_press_event.is_triggered:
                    self._long_press_event = None
                    self._touch_in_progress = False
                    self._was_long_press = False
                    return True
                self._long_press_event.cancel()
                self._long_press_event = None
            if not self._was_long_press and self.on_select and self.collide_point(*touch.pos):
                self.on_select(self.name)
            self._touch_in_progress = False
            self._was_long_press = False
            return True
        return super().on_touch_up(touch)

    def _on_long_press(self, touch):
        if getattr(self, '_touch_in_progress', False):
            pyperclip.copy(self.raw_code)
            toast(f"Copied {self.raw_code}")
            self._was_long_press = True
            original_color = self.md_bg_color
            anim = Animation(md_bg_color=(*self.theme_cls.accent_color[:3], 0.3), duration=0.1) + \
                   Animation(md_bg_color=original_color, duration=0.3)
            anim.start(self)
        self._long_press_event = None
        self._touch_in_progress = False

    def set_selected(self, selected):
        self.selected = selected
        self.update_selected_visual()

    def update_selected_visual(self):
        if self.selected:
            primary_color = self.theme_cls.primary_color
            self.md_bg_color = (*primary_color[:3], 0.2)
            self.elevation = 6
            self.line_color = (*self.theme_cls.primary_color[:3], 0.8)
        else:
            self.md_bg_color = self.theme_cls.bg_normal
            self.elevation = 1
            self.line_color = (*self.theme_cls.divider_color[:3], 0.3)

    def update_code(self, code, ttl):
        self.raw_code = code
        self.code_label.text = self.format_code(code)
        self.ttl_label.text = f"{ttl}s"
        
        progress_value = ttl / 30 * 100
        self.progress_bar.value = progress_value
        
        if ttl > 15:
            self.progress_bar.color = self.theme_cls.primary_color
        elif ttl > 8:
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
        from kivy.uix.screenmanager import ScreenManager
        self.screen_manager = ScreenManager()
        # Theme persistence
        self.theme_store = None
        self.theme_pref_path = None

    @property
    def user_data_dir(self):
        import os
        if platform == "android":
            return super().user_data_dir
        home = os.path.expanduser("~")
        if platform == "win":
            base = os.getenv("APPDATA", home)
            return os.path.join(base, "Tautth")
        elif platform == "macosx":
            return os.path.join(home, "Library", "Application Support", "Tautth")
        else:
            return os.path.join(home, ".local", "share", "Tautth")

    def _init_theme_store(self):
        if self.theme_store is not None:
            return  # Already initialized
        try:
            base_dir = self.user_data_dir
            print(f"[ThemeStore] Using user_data_dir: {base_dir}")
        except AttributeError:
            base_dir = os.path.expanduser("~/.authenticator")
            print(f"[ThemeStore] Using fallback dir: {base_dir}")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
            print(f"[ThemeStore] Created directory: {base_dir}")
        self.theme_pref_path = os.path.join(base_dir, "theme_prefs.json")
        print(f"[ThemeStore] Theme preference path: {self.theme_pref_path}")
        self.theme_store = JsonStore(self.theme_pref_path)
        print(f"[ThemeStore] JsonStore initialized: {self.theme_store}")

    def load_theme_prefs(self):
        self._init_theme_store()  # Ensure store is initialized
        if self.theme_store and self.theme_store.exists('theme'):
            theme = self.theme_store.get('theme')
            print(f"[ThemeStore] Loaded theme from store: {theme}")
            self.theme_cls.primary_palette = theme.get('primary_palette', 'DeepOrange')
            self.theme_cls.theme_style = theme.get('theme_style', 'Light')
        else:
            print("[ThemeStore] No theme found in store, using defaults.")
            self.theme_cls.primary_palette = 'DeepOrange'
            self.theme_cls.theme_style = 'Light'
            self.save_theme_prefs()
        print(f"[ThemeStore] Theme after load: palette={self.theme_cls.primary_palette}, style={self.theme_cls.theme_style}")

    def save_theme_prefs(self):
        self._init_theme_store()  # Ensure store is initialized
        print(f"[ThemeStore] save_theme_prefs called, self id: {id(self)}, theme_store: {self.theme_store}")
        if self.theme_store is not None:
            self.theme_store.put('theme',
                primary_palette=self.theme_cls.primary_palette,
                theme_style=self.theme_cls.theme_style)
            print(f"[ThemeStore] Saved theme: palette={self.theme_cls.primary_palette}, style={self.theme_cls.theme_style}")
        else:
            print("[ThemeStore] ERROR: theme_store is not initialized after _init_theme_store!")

    def build(self):
        self._init_theme_store()
        self.load_theme_prefs()
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.accent_hue = "400"
        self.theme_cls.material_style = "M3"
        
        self.title = "Tautth"
        
        Window.clearcolor = self.theme_cls.bg_darkest
        
        self.screen_manager = ScreenManager()
        
        # Main screen
        main_screen = Screen(name="main")
        main_layout = MDBoxLayout(orientation="vertical")
        
        self.toolbar = MDTopAppBar(
            title="Tautth",
            md_bg_color=self.theme_cls.primary_color,
            elevation=0,
            anchor_title="left",
            right_action_items=[
                ["plus-circle", lambda x: self.show_add_dialog()],
                ["menu", lambda x: self.show_menu(x)]
            ]
        )
        
        self.scroll = MDScrollView(
            md_bg_color=(0, 0, 0, 0),
            bar_color=self.theme_cls.primary_color,
            bar_inactive_color=(*self.theme_cls.primary_color[:3], 0.3)
        )
        
        self.accounts_layout = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(16),
            padding=[dp(20), dp(24), dp(20), dp(24)]
        )
        
        self.scroll.add_widget(self.accounts_layout)
        
        main_layout.add_widget(self.toolbar)
        main_layout.add_widget(self.scroll)
        
        main_screen.add_widget(main_layout)

        overlay = FloatLayout()
        version_label = MDLabel(
            text="V0.1 Alpha",
            halign="right",
            valign="bottom",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 0.3),
            font_style="Caption",
            size_hint=(None, None),
            size=(dp(80), dp(24)),
            pos_hint={"right": 1.0, "y": 0.0},
            padding=(0, dp(2))
        )
        overlay.add_widget(version_label)
        main_screen.add_widget(overlay)
        
        self.screen_manager.add_widget(main_screen)
        
        # Settings screen
        settings_screen = SettingsScreen(name="settings", app=self)
        self.screen_manager.add_widget(settings_screen)
        
        self.refresh_accounts()
        self.start_timer()
        
        return self.screen_manager
    
    def show_menu(self, instance):
        menu_items = [
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Edit Selected",
                "icon": "pencil",
                "on_release": lambda: self.menu_callback("edit"),
            },
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Remove Selected",
                "icon": "delete",
                "on_release": lambda: self.menu_callback("remove"),
            },
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Backup Data",
                "icon": "content-save",
                "on_release": lambda: self.menu_callback("backup"),
            },
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Restore Data",
                "icon": "folder",
                "on_release": lambda: self.menu_callback("restore"),
            },
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Settings",
                "icon": "cog",
                "on_release": lambda: self.menu_callback("settings"),
            },
        ]
        
        self.menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            elevation=0
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
        elif action == "settings":
            self.show_settings()
    
    def show_settings(self):
        self.screen_manager.current = "settings"
        self.screen_manager.transition.direction = "left"

    def change_theme(self, color):
        self.theme_cls.primary_palette = color
        self.toolbar.md_bg_color = self.theme_cls.primary_color
        for card in self.account_cards.values():
            card.update_selected_visual()
            card.progress_bar.color = self.theme_cls.primary_color
        self.save_theme_prefs()
        print(f"[ThemeStore] change_theme called: palette={color}")
    
    def start_timer(self):
        Clock.schedule_interval(self.update_codes, 1)
    
    def show_snackbar(self, message):
        toast(message)
    
    def show_add_dialog(self):
        content = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(20), 
            adaptive_height=True,
            padding=[dp(4), dp(8)]
        )
        
        self.name_field = MDTextField(
            hint_text="Account name (e.g., Google, GitHub)",
            required=True,
            helper_text_mode="on_error",
            helper_text="This field is required",
            line_color_focus=self.theme_cls.primary_color,
        )
        
        self.secret_field = MDTextField(
            hint_text="TOTP secret key",
            required=True,
            helper_text_mode="on_error",
            helper_text="Enter the secret key from your service",
            line_color_focus=self.theme_cls.primary_color,
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
                    text_color=self.theme_cls.disabled_hint_text_color,
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="ADD",
                    md_bg_color=self.theme_cls.primary_color,
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
            orientation="vertical", 
            spacing=dp(20), 
            adaptive_height=True,
            padding=[dp(4), dp(8)]
        )
        
        self.edit_secret_field = MDTextField(
            hint_text="New TOTP secret key",
            required=True,
            helper_text_mode="on_error",
            helper_text="Enter the new secret key",
            line_color_focus=self.theme_cls.primary_color,
        )
        
        self.dialog_content.add_widget(MDLabel(
            text=f"Updating: {self.selected_account}", 
            theme_text_color="Secondary",
            font_style="Body2"
        ))
        self.dialog_content.add_widget(self.edit_secret_field)
        
        self.dialog = MDDialog(
            title="Edit Account",
            type="custom",
            content_cls=self.dialog_content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.disabled_hint_text_color,
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="UPDATE",
                    md_bg_color=self.theme_cls.primary_color,
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
        else:
            start_dir = self.user_data_dir
        self.file_manager.show(str(start_dir))
        self.backup_mode = True
    
    def restore(self):
        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.select_restore_path,
            )
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
        else:
            start_dir = self.user_data_dir
        self.file_manager.show(str(start_dir))
        self.backup_mode = False
    
    def exit_file_manager(self, *args):
        if self.file_manager:
            self.file_manager.close()
        self.file_manager = None
    
    def select_backup_path(self, path):
        self.exit_file_manager()
        self.show_backup_dialog(path)
    
    def show_backup_dialog(self, directory):
        content = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(20), 
            adaptive_height=True,
            padding=[dp(4), dp(8)]
        )
        
        self.backup_filename_field = MDTextField(
            hint_text="Backup filename",
            text="authenticator_backup.bak",
            line_color_focus=self.theme_cls.primary_color,
        )
        
        self.backup_password_field = MDTextField(
            hint_text="Backup password",
            password=True,
            required=True,
            helper_text_mode="on_error",
            helper_text="Password is required for encryption",
            line_color_focus=self.theme_cls.primary_color,
        )
        
        content.add_widget(MDLabel(
            text=f"Location: {directory}", 
            theme_text_color="Secondary",
            font_style="Body2"
        ))
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
                    text_color=self.theme_cls.disabled_hint_text_color,
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="BACKUP",
                    md_bg_color=self.theme_cls.primary_color,
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
                    md_bg_color=self.theme_cls.error_color,
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
            empty_layout = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                spacing=dp(20),
                padding=[dp(40), dp(80)]
            )
            

            
            empty_layout.add_widget(MDLabel(
                text="No accounts yet",
                theme_text_color="Primary",
                font_style="H5",
                halign="center",
                font_size=dp(24)
            ))
            
            empty_layout.add_widget(MDLabel(
                text="Tap the plus button to add your first account",
                theme_text_color="Secondary",
                font_style="Body1",
                halign="center",
                font_size=dp(16)
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
        content = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(20), 
            adaptive_height=True,
            padding=[dp(4), dp(8)]
        )
        
        self.restore_password_field = MDTextField(
            hint_text="Backup password",
            password=True,
            required=True,
            helper_text_mode="on_error",
            helper_text="Enter the password used for encryption",
            line_color_focus=self.theme_cls.primary_color,
        )
        
        content.add_widget(MDLabel(
            text=f"File: {Path(filepath).name}", 
            theme_text_color="Secondary",
            font_style="Body2"
        ))
        content.add_widget(self.restore_password_field)
        
        self.dialog = MDDialog(
            title="Restore Backup",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.disabled_hint_text_color,
                    on_release=self.close_dialog
                ),
                MDRaisedButton(
                    text="RESTORE",
                    md_bg_color=self.theme_cls.primary_color,
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

    def toggle_dark_mode(self, active):
        self.theme_cls.theme_style = 'Dark' if active else 'Light'
        self.save_theme_prefs()
        print(f"[ThemeStore] toggle_dark_mode called: style={'Dark' if active else 'Light'}")

if __name__ == '__main__':
    ModernAuthenticatorApp().run()