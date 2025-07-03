from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.switch import Switch
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivy.lang import Builder
from kivy.factory import Factory

class ColorCard(MDCard, RoundedRectangularElevationBehavior):
    def __init__(self, color_name, color_code, kivymd_name, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = color_code
        self.size_hint = (None, None)
        self.size = (dp(60), dp(60))
        self.radius = [dp(30)]
        self.elevation = 2
        self.color_name = color_name
        self.kivymd_name = kivymd_name  # The actual KivyMD palette name
        self.on_select = on_select
        self.bind(on_release=self.select_color)
        
    def select_color(self, *args):
        if self.on_select:
            self.on_select(self.kivymd_name, self.color_name)

class SettingsScreen(MDScreen):
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.app = app
        self.theme_dialog = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = MDBoxLayout(orientation="vertical")
        
        # Modern Toolbar
        toolbar = MDTopAppBar(
            title="Settings",
            elevation=1,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["information-outline", lambda x: self.show_about()]],
        )
        layout.add_widget(toolbar)
        
        # Scrollable Content
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical", 
            adaptive_height=True, 
            padding=dp(16), 
            spacing=dp(12)
        )
        
        # App Information Section
        content.add_widget(self.create_app_info_section())

        
        # Appearance Section
        content.add_widget(self.create_appearance_section())

        
        # Preferences Section
        content.add_widget(self.create_preferences_section())

        
        # About Section
        content.add_widget(self.create_about_section())
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def create_app_info_section(self):
        """Create app information section"""
        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(8),
            elevation=1,
            radius=[dp(12)]
        )
        
        # Section Header
        header = MDLabel(
            text="App Information",
            font_style="H6",
            theme_text_color="Primary",
            adaptive_height=True
        )
        card.add_widget(header)
        
        # App Version
        version_item = TwoLineAvatarIconListItem(
            text="Version",
            secondary_text="v1.0.2 (Build 2025.1)",
            theme_text_color="Primary"
        )
        version_item.add_widget(IconLeftWidget(icon="information-outline"))
        card.add_widget(version_item)
        
        return card
    
    def create_appearance_section(self):
        """Create appearance customization section"""
        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(8),
            elevation=1,
            radius=[dp(12)]
        )
        
        # Section Header
        header = MDLabel(
            text="Appearance",
            font_style="H6",
            theme_text_color="Primary",
            adaptive_height=True
        )
        card.add_widget(header)
        
        # Theme Color Selection
        theme_item = TwoLineAvatarIconListItem(
            text="Theme Color",
            secondary_text="Tap to change app theme",
            on_release=self.show_theme_dialog
        )
        theme_item.add_widget(IconLeftWidget(icon="palette"))
        theme_item.add_widget(IconRightWidget(icon="chevron-right"))
        card.add_widget(theme_item)
        
        # Dark Mode Toggle
        dark_mode_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[0, dp(8)],
            spacing=dp(16)
        )
        
        dark_mode_info = MDBoxLayout(orientation="vertical", adaptive_height=True)
        dark_mode_info.add_widget(MDLabel(
            text="Dark Mode",
            font_style="Body1",
            theme_text_color="Primary",
            adaptive_height=True
        ))
        dark_mode_info.add_widget(MDLabel(
            text="Switch between light and dark themes",
            font_style="Caption",
            theme_text_color="Secondary",
            adaptive_height=True
        ))
        
        dark_mode_switch = Switch(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_y": 0.5},
            on_active=self.toggle_dark_mode
        )
        
        dark_mode_layout.add_widget(IconLeftWidget(icon="weather-night"))
        dark_mode_layout.add_widget(dark_mode_info)
        dark_mode_layout.add_widget(dark_mode_switch)
        card.add_widget(dark_mode_layout)
        
        return card
    
    def create_preferences_section(self):
        """Create user preferences section"""
        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(8),
            elevation=1,
            radius=[dp(12)]
        )
        
        # Section Header
        header = MDLabel(
            text="Preferences",
            font_style="H6",
            theme_text_color="Primary",
            adaptive_height=True
        )
        card.add_widget(header)
        
        # Notifications
        notif_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[0, dp(8)],
            spacing=dp(16)
        )
        
        notif_info = MDBoxLayout(orientation="vertical", adaptive_height=True)
        notif_info.add_widget(MDLabel(
            text="Push Notifications",
            font_style="Body1",
            theme_text_color="Primary",
            adaptive_height=True
        ))
        notif_info.add_widget(MDLabel(
            text="Receive app notifications",
            font_style="Caption",
            theme_text_color="Secondary",
            adaptive_height=True
        ))
        
        notif_switch = Switch(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_y": 0.5},
            active=True,
            on_active=self.toggle_notifications
        )
        
        notif_layout.add_widget(IconLeftWidget(icon="bell"))
        notif_layout.add_widget(notif_info)
        notif_layout.add_widget(notif_switch)
        card.add_widget(notif_layout)
        
        # Auto-sync
        sync_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[0, dp(8)],
            spacing=dp(16)
        )
        
        sync_info = MDBoxLayout(orientation="vertical", adaptive_height=True)
        sync_info.add_widget(MDLabel(
            text="Auto-sync",
            font_style="Body1",
            theme_text_color="Primary",
            adaptive_height=True
        ))
        sync_info.add_widget(MDLabel(
            text="Automatically sync data",
            font_style="Caption",
            theme_text_color="Secondary",
            adaptive_height=True
        ))
        
        sync_switch = Switch(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            pos_hint={"center_y": 0.5},
            active=True,
            on_active=self.toggle_auto_sync
        )
        
        sync_layout.add_widget(IconLeftWidget(icon="sync"))
        sync_layout.add_widget(sync_info)
        sync_layout.add_widget(sync_switch)
        card.add_widget(sync_layout)
        
        return card
    
    def create_about_section(self):
        """Create about section with additional options"""
        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(8),
            elevation=1,
            radius=[dp(12)]
        )
        
        # Section Header
        header = MDLabel(
            text="About",
            font_style="H6",
            theme_text_color="Primary",
            adaptive_height=True
        )
        card.add_widget(header)
        
        # Help & Support
        help_item = OneLineAvatarIconListItem(
            text="Help & Support",
            on_release=self.show_help
        )
        help_item.add_widget(IconLeftWidget(icon="help-circle"))
        help_item.add_widget(IconRightWidget(icon="chevron-right"))
        card.add_widget(help_item)
        
        # Privacy Policy
        privacy_item = OneLineAvatarIconListItem(
            text="Privacy Policy",
            on_release=self.show_privacy
        )
        privacy_item.add_widget(IconLeftWidget(icon="shield-check"))
        privacy_item.add_widget(IconRightWidget(icon="chevron-right"))
        card.add_widget(privacy_item)
        
        # Rate App
        rate_item = OneLineAvatarIconListItem(
            text="Rate This App",
            on_release=self.rate_app
        )
        rate_item.add_widget(IconLeftWidget(icon="star"))
        rate_item.add_widget(IconRightWidget(icon="chevron-right"))
        card.add_widget(rate_item)
        
        return card
    
    def show_theme_dialog(self, *args):
        """Show theme color selection dialog"""
        if not self.theme_dialog:
            # Color palette with KivyMD-compatible names
            # Format: (Display Name, Color Code, KivyMD Palette Name)
            colors = [
                ("Red", "#F44336", "Red"),
                ("Pink", "#E91E63", "Pink"), 
                ("Purple", "#9C27B0", "Purple"),
                ("Deep Purple", "#673AB7", "DeepPurple"),
                ("Indigo", "#3F51B5", "Indigo"),
                ("Blue", "#2196F3", "Blue"),
                ("Light Blue", "#03A9F4", "LightBlue"),
                ("Cyan", "#00BCD4", "Cyan"),
                ("Teal", "#009688", "Teal"),
                ("Green", "#4CAF50", "Green"),
                ("Light Green", "#8BC34A", "LightGreen"),
                ("Lime", "#CDDC39", "Lime"),
                ("Yellow", "#FFEB3B", "Yellow"),
                ("Amber", "#FFC107", "Amber"),
                ("Orange", "#FF9800", "Orange"),
                ("Deep Orange", "#FF5722", "DeepOrange"),
                ("Brown", "#795548", "Brown"),
                ("Blue Gray", "#607D8B", "BlueGray")
            ]
            
            # Create color grid
            color_grid = MDGridLayout(
                cols=6,
                adaptive_height=True,
                spacing=dp(8),
                size_hint_y=None,
                height=dp(200)
            )
            
            for display_name, color_code, kivymd_name in colors:
                color_card = ColorCard(
                    color_name=display_name,
                    color_code=color_code,
                    kivymd_name=kivymd_name,
                    on_select=self.change_theme
                )
                color_grid.add_widget(color_card)
            
            self.theme_dialog = MDDialog(
                title="Choose Theme Color",
                type="custom",
                content_cls=color_grid,
                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        on_release=self.close_theme_dialog
                    )
                ]
            )
        
        self.theme_dialog.open()
    
    def close_theme_dialog(self, *args):
        """Close theme selection dialog"""
        if self.theme_dialog:
            self.theme_dialog.dismiss()
    
    def change_theme(self, kivymd_name, display_name):
        """Change app theme color"""
        if self.app:
            self.app.change_theme(kivymd_name)  # Use the KivyMD-compatible name
        self.close_theme_dialog()
        
        # Show confirmation with display name
        self.show_snackbar(f"Theme changed to {display_name}")
    
    def toggle_dark_mode(self, switch, active):
        """Toggle dark mode"""
        if self.app:
            # Implement dark mode toggle in your app
            self.app.toggle_dark_mode(active)
        self.show_snackbar("Dark mode " + ("enabled" if active else "disabled"))
    
    def toggle_notifications(self, switch, active):
        """Toggle notifications"""
        self.show_snackbar("Notifications " + ("enabled" if active else "disabled"))
    
    def toggle_auto_sync(self, switch, active):
        """Toggle auto-sync"""
        self.show_snackbar("Auto-sync " + ("enabled" if active else "disabled"))
    
    def show_about(self, *args):
        """Show about dialog"""
        dialog = MDDialog(
            title="About This App",
            text="A modern, Material Design application built with KivyMD.\n\nVersion: 1.0.2\nBuild: 2025.1\n\nDeveloped with ❤️",
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_help(self, *args):
        """Show help section"""
        self.show_snackbar("Opening help & support...")
    
    def show_privacy(self, *args):
        """Show privacy policy"""
        self.show_snackbar("Opening privacy policy...")
    
    def rate_app(self, *args):
        """Rate app functionality"""
        self.show_snackbar("Opening app store for rating...")
    
    def show_snackbar(self, message):
        """Show snackbar message"""
        if self.app and hasattr(self.app, 'show_snackbar'):
            self.app.show_snackbar(message)
    
    def go_back(self):
        """Navigate back to main screen"""
        self.manager.current = "main"
        self.manager.transition.direction = "right"