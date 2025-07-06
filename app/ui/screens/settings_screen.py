from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    IRightBodyTouch,
    IconLeftWidget,
    IconRightWidget,
    OneLineAvatarIconListItem,
    TwoLineAvatarIconListItem,
)
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarActionButton
from kivymd.uix.toolbar import MDTopAppBar

class ColorCard(MDCard):
    def __init__(self, color_name, color_code, kivymd_name, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = color_code
        self.size_hint = (None, None)
        self.size = (dp(60), dp(60))
        self.radius = [dp(30)]
        self.elevation = 0  # No shadow
        self.color_name = color_name
        self.kivymd_name = kivymd_name  # The actual KivyMD palette name
        self.on_select = on_select
        self.bind(on_release=self.select_color)
        
    def select_color(self, *args):
        if self.on_select:
            self.on_select(self.kivymd_name, self.color_name)

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass


class SettingsScreen(MDScreen):
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.app = app
        self.theme_dialog = None
        self.is_ui_setup = False
        self.is_initializing = False
        
    def setup_ui(self):
        if self.is_ui_setup:
            return
            
        layout = MDBoxLayout(orientation="vertical")
        
        # Modern Toolbar
        toolbar = MDTopAppBar(
            title="Settings",
            elevation=1,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            anchor_title="left",
        )
        
        # Add custom title label positioned as far left as possible
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
        self.is_ui_setup = True
    
    def create_app_info_section(self):
        """Create app information section"""
        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(8),
            elevation=0,
            radius=[dp(12)],
            md_bg_color=[0, 0, 0, 0]  # Transparent background
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
        self.version_item = TwoLineAvatarIconListItem(
            text="Version",
            secondary_text=getattr(getattr(self.app, "app_config", None), "VERSION", "Unknown"),
            theme_text_color="Primary"
        )
        self.version_item.add_widget(IconLeftWidget(icon="information-outline"))
        card.add_widget(self.version_item)
        
        return card
    
    def create_appearance_section(self):
        """Create appearance customization section"""
        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(8),
            elevation=0,
            radius=[dp(12)],
            md_bg_color=[0, 0, 0, 0]  # Transparent background
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
        dark_mode_item = TwoLineAvatarIconListItem(
            text="Dark Mode",
            secondary_text="Switch between light and dark themes",
        )
        dark_mode_item.add_widget(IconLeftWidget(icon="weather-night"))

        self.dark_mode_checkbox = RightCheckbox()
        self.dark_mode_checkbox.bind(active=self.toggle_dark_mode)
        dark_mode_item.add_widget(self.dark_mode_checkbox)
        card.add_widget(dark_mode_item)
        
        return card
    
    def create_preferences_section(self):
        """Create user preferences section"""
        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(8),
            elevation=0,
            radius=[dp(12)],
            md_bg_color=[0, 0, 0, 0]  # Transparent background
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
        notif_item = TwoLineAvatarIconListItem(
            text="Push Notifications",
            secondary_text="Receive app notifications (NOT WORKING)"
        )
        notif_item.add_widget(IconLeftWidget(icon="bell"))
        self.notif_checkbox = RightCheckbox()
        self.notif_checkbox.bind(active=self.toggle_notifications)
        notif_item.add_widget(self.notif_checkbox)
        card.add_widget(notif_item)
        
        # Auto-sync
        sync_item = TwoLineAvatarIconListItem(
            text="Auto-sync",
            secondary_text="Automatically sync data (NOT WORKING)"
        )
        sync_item.add_widget(IconLeftWidget(icon="sync"))
        self.sync_checkbox = RightCheckbox()
        self.sync_checkbox.bind(active=self.toggle_auto_sync)
        sync_item.add_widget(self.sync_checkbox)
        card.add_widget(sync_item)
        
        return card
    
    def create_about_section(self):
        """Create about section with additional options"""
        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(8),
            elevation=0,
            radius=[dp(12)],
            md_bg_color=[0, 0, 0, 0]  # Transparent background
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
        """Show theme color selection dialog (mobile‐friendly, no shadows, selectable without close)"""
        if not self.theme_dialog:
            # Color palette
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

            # Grid of swatches
            color_grid = MDGridLayout(
                cols=4,
                adaptive_height=True,
                padding=dp(8),
                spacing=dp(8),
            )
            color_grid.children = [
                ColorCard(
                    color_name=display_name,
                    color_code=color_code,
                    kivymd_name=kivymd_name,
                    size_hint=(1, None),
                    height=dp(56),
                    elevation=0,
                    radius=[0],
                    on_select=self.change_theme,
                )
                for display_name, color_code, kivymd_name in colors
            ]

            # Scrollable container
            scroll = MDScrollView(
                size_hint=(1, None),
                height=dp(240),
            )
            scroll.add_widget(color_grid)

            # Build dialog
            self.theme_dialog = MDDialog(
                title="Choose Theme Color",
                type="custom",
                content_cls=scroll,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=self.close_theme_dialog
                    )
                ],
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
        
        # Show confirmation with display name
        self.show_snackbar(f"Theme changed to {display_name}")
    
    def toggle_dark_mode(self, checkbox, active):
        """Toggle dark mode"""
        if self.app:
            # Implement dark mode toggle in your app
            self.app.toggle_dark_mode(active)
        if not self.is_initializing:
            self.show_snackbar("Dark mode " + ("enabled" if active else "disabled"))
    
    def toggle_notifications(self, checkbox, active):
        """Toggle notifications"""
        if not self.is_initializing:
            self.show_snackbar("Notifications " + ("enabled" if active else "disabled"))
    
    def toggle_auto_sync(self, checkbox, active):
        """Toggle auto-sync"""
        if not self.is_initializing:
            self.show_snackbar("Auto-sync " + ("enabled" if active else "disabled"))
    
    def show_about(self, *args):
        """Show about dialog"""
        dialog = MDDialog(
            title="About This App",
            text=f"A modern, Material Design application built with KivyMD.\n\nVersion: {getattr(getattr(self.app, 'app_config', None), 'VERSION', 'Unknown')}\n\nDeveloped with ❤️",
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
    
    def show_snackbar(self, message, action_text=None, action_callback=None):
        """Show snackbar message with optional action button and theme-aware background."""
        # Determine background color based on theme
        if self.app and hasattr(self.app, "theme_cls"):
            if self.app.theme_cls.theme_style == "Dark":
                bg_color = "#2A2A2A"  # Lighter dark
            else:
                bg_color = "#F5F5F5"  # Darker white
        else:
            bg_color = "#F5F5F5"

        # Prepare snackbar content
        # Determine text color based on theme
        if self.app and hasattr(self.app, "theme_cls"):
            if self.app.theme_cls.theme_style == "Dark":
                text_color = "#FFFFFF"  # White text for dark background
            else:
                text_color = "#000000"  # Black text for light background
        else:
            text_color = "#000000"  # Default to black
            
        label = MDLabel(
            text=message,
            theme_text_color="Custom",
            text_color=text_color,
        )
        label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        content = [label]
        if action_text:
            content.append(
                MDSnackbarActionButton(
                    text=action_text,
                    theme_text_color="Custom",
                    text_color="#8E353C",
                    on_release=action_callback if action_callback else lambda x: None,
                )
            )

        MDSnackbar(
            *content,
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            md_bg_color=bg_color,
        ).open()
    
    def on_pre_enter(self, *args):
        """Event fired when the screen is about to be displayed."""
        self.setup_ui()
        Clock.schedule_once(self.update_checkbox_states, 0)

    def update_checkbox_states(self, *args):
        """Update the state of the checkboxes after the screen transition."""
        # Set flag to prevent snackbar triggers during initialization
        self.is_initializing = True
        
        # Update checkbox states
        if self.app and self.app.theme_cls:
            self.dark_mode_checkbox.active = self.app.theme_cls.theme_style == "Dark"
        
        # Set other checkboxes' initial states here if needed
        self.notif_checkbox.active = True
        self.sync_checkbox.active = True
        
        # Reset flag after initialization
        self.is_initializing = False

    def go_back(self):
        """Navigate back to main screen"""
        self.manager.current = "main"
        self.manager.transition.direction = "right"
