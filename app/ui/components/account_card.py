from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.progressbar import ProgressBar
from kivymd.uix.snackbar import MDSnackbar
import pyperclip

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
        
        top_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(24))
        info_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(4))
        
        account_name = name
        if ":" in name:
            issuer, account_name = name.split(":", 1)
            self.issuer_label = MDLabel(
                text=issuer.upper(),
                font_style="Caption",
                adaptive_height=True,
                font_size=dp(12),
                bold=True
            )
            info_layout.add_widget(self.issuer_label)
            
        self.name_label = MDLabel(
            text=account_name,
            font_style="H6",
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
        
        self.progress_bar = ProgressBar(
            value=ttl / 30 * 100, 
            size_hint_y=None, 
            height=dp(4)
        )
        
        self.ttl_label = MDLabel(
            text=f"{ttl}s",
            font_style="Body2",
            adaptive_size=True,
            font_size=dp(14),
            bold=True
        )
        
        bottom_layout.add_widget(self.progress_bar)
        bottom_layout.add_widget(self.ttl_label)
        
        self.add_widget(top_layout)
        self.add_widget(bottom_layout)
        
        self.bind(on_touch_down=self._on_touch_down, on_touch_up=self._on_touch_up)
        self.update_theme_colors()
        self.update_selected_visual()
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
        
        top_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(24))
        info_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(4))
        
        account_name = name
        if ":" in name:
            issuer, account_name = name.split(":", 1)
            self.issuer_label = MDLabel(
                text=issuer.upper(),
                font_style="Caption",
                adaptive_height=True,
                font_size=dp(12),
                bold=True
            )
            info_layout.add_widget(self.issuer_label)
            
        self.name_label = MDLabel(
            text=account_name,
            font_style="H6",
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
        
        self.progress_bar = ProgressBar(
            value=ttl / 30 * 100, 
            size_hint_y=None, 
            height=dp(4)
        )
        
        self.ttl_label = MDLabel(
            text=f"{ttl}s",
            font_style="Body2",
            adaptive_size=True,
            font_size=dp(14),
            bold=True
        )
        
        bottom_layout.add_widget(self.progress_bar)
        bottom_layout.add_widget(self.ttl_label)
        
        self.add_widget(top_layout)
        self.add_widget(bottom_layout)
        
        self.bind(on_touch_down=self._on_touch_down, on_touch_up=self._on_touch_up)
        self.update_theme_colors()
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
            MDSnackbar(
                MDLabel(
                    text=f"Copied {self.raw_code}",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                )
            ).open()
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

    def update_theme_colors(self, *args):
        self.md_bg_color = self.theme_cls.bg_normal
        self.line_color = (*self.theme_cls.divider_color[:3], 0.3)
        if hasattr(self, 'issuer_label'):
            self.issuer_label.theme_text_color = "Secondary"
        self.name_label.theme_text_color = "Primary"
        self.code_label.theme_text_color = "Primary"
        self.ttl_label.theme_text_color = "Secondary"
        self.progress_bar.back_color = (*self.theme_cls.divider_color[:3], 0.4)
        self.update_selected_visual()
