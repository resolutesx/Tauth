from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivymd.icon_definitions import md_icons
from kivymd.uix.label import MDIcon
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar


class IconPreviewScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "icon_preview"
        layout = BoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(
            title="Icon Preview",
            elevation=0,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
        )
        scroll = ScrollView()
        grid = GridLayout(cols=5, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for icon_name in list(md_icons.keys())[:500]:  # Limit to 500 icons for performance
            icon_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=100)
            icon_layout.add_widget(MDIcon(icon=icon_name, halign="center"))
            icon_layout.add_widget(Label(text=icon_name, size_hint_y=None, height=20))
            grid.add_widget(icon_layout)
        scroll.add_widget(grid)
        layout.add_widget(toolbar)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def go_back(self):
        self.manager.current = "main"
        self.manager.transition.direction = "right"