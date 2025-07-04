from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty
from kivymd.uix.list import OneLineIconListItem

Builder.load_string("""
<CustomOneLineIconListItem>:
    IconLeftWidget:
        icon: root.icon
        theme_text_color: "Custom"
        text_color: root.icon_color
""")

class CustomOneLineIconListItem(OneLineIconListItem):
    icon = StringProperty()
    icon_color = ListProperty([0, 0, 0, 1])