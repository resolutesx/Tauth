from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.spinner import MDSpinner
from kivy.metrics import dp

class LoadingScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "loading"
        
        layout = MDBoxLayout(
            orientation="vertical",
            adaptive_size=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=dp(20)
        )
        
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            active=True
        )
        
        layout.add_widget(spinner)
        self.add_widget(layout)
