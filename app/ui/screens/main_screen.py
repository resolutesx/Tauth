from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.menu import MDDropdownMenu
from app.ui.components.custom_widgets import CustomOneLineIconListItem

class MainScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.name = "main"
        self.layout = MDBoxLayout(orientation="vertical")
        
        self.toolbar = MDTopAppBar(
            title="Tautth",
            md_bg_color=self.app.theme_cls.primary_color,
            elevation=0,
            anchor_title="left",
            right_action_items=[
                ["plus-circle", lambda x: self.app.show_add_dialog()],
                ["menu", lambda x: self.show_menu(x)]
            ]
        )
        
        self.scroll = MDScrollView(
            md_bg_color=(0, 0, 0, 0),
            bar_color=self.app.theme_cls.primary_color,
            bar_inactive_color=(*self.app.theme_cls.primary_color[:3], 0.3)
        )
        
        self.accounts_layout = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(16),
            padding=[dp(20), dp(24), dp(20), dp(24)]
        )
        
        self.scroll.add_widget(self.accounts_layout)
        
        self.layout.add_widget(self.toolbar)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)

        self.overlay = FloatLayout()
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
        self.overlay.add_widget(version_label)
        self.add_widget(self.overlay)

        # Initialize empty message layout and its labels
        self.empty_message_layout = MDBoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(dp(280), dp(120)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=dp(5),
            md_bg_color=[0, 0, 0, 0]
        )

        self.empty_message_label_1 = MDLabel(
            text="No accounts yet",
            theme_text_color="Primary",
            font_style="H5",
            halign="center",
            font_size=dp(24)
        )
        self.empty_message_label_2 = MDLabel(
            text="Tap the plus button to add your first account",
            theme_text_color="Secondary",
            font_style="Body1",
            halign="center",
            font_size=dp(16)
        )
            
        self.empty_message_layout.add_widget(self.empty_message_label_1)
        self.empty_message_layout.add_widget(self.empty_message_label_2)
        self.overlay.add_widget(self.empty_message_layout)
        self.empty_message_layout.opacity = 0 # Start hidden
        self.empty_message_layout.height = 0 # Start with no height
        self.empty_message_layout.disabled = True # Disable interaction

    def show_menu(self, instance):
        # Determine icon color and background color based on theme
        if self.app and self.app.theme_cls:
            if self.app.theme_cls.theme_style == "Dark":
                icon_color = [1, 1, 1, 1]  # White for dark theme
                bg_color = [0.2, 0.2, 0.2, 1]  # Dark gray for dark theme
            else:
                icon_color = [0, 0, 0, 1]  # Black for light theme
                bg_color = [0.90, 0.90, 0.90, 1]  # Light gray for light theme (darker than pure white)
        else:
            icon_color = [0, 0, 0, 1]  # Default to black
            bg_color = [0.90, 0.90, 0.90, 1]  # Default to light gray
        
        menu_items = [
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Edit Selected",
                "icon": "pencil",
                "icon_color": icon_color,
                "on_release": lambda: self.app.menu_callback("edit"),
            },
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Remove Selected",
                "icon": "delete",
                "icon_color": icon_color,
                "on_release": lambda: self.app.menu_callback("remove"),
            },
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Backup Data",
                "icon": "content-save",
                "icon_color": icon_color,
                "on_release": lambda: self.app.menu_callback("backup"),
            },
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Restore Data",
                "icon": "folder",
                "icon_color": icon_color,
                "on_release": lambda: self.app.menu_callback("restore"),
            },
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Settings",
                "icon": "cog",
                "icon_color": icon_color,
                "on_release": lambda: self.app.menu_callback("settings"),
            },
            {
                "viewclass": "CustomOneLineIconListItem",
                "text": "Icon Preview",
                "icon": "eye",
                "icon_color": icon_color,
                "on_release": lambda: self.app.menu_callback("icon_preview"),
            },
        ]
        
        self.menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            elevation=0,
            md_bg_color=bg_color
        )
        self.menu.open()

    def show_empty_message(self):
        self.accounts_layout.clear_widgets()
        self.empty_message_layout.opacity = 1
        self.empty_message_layout.height = self.height # Make it visible and take up space
        self.empty_message_layout.disabled = False # Enable interaction if needed

    def hide_empty_message(self):
        self.empty_message_layout.opacity = 0
        self.empty_message_layout.height = 0 # Hide it and make it take no space
        self.empty_message_layout.disabled = True # Disable interaction
