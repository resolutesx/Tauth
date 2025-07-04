from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDSwitch

class MainApp(MDApp):
    def build(self):
        box = MDBoxLayout(orientation="vertical")
        switch = MDSwitch()
        box.add_widget(switch)
        return box

MainApp().run()
