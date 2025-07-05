from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.progressbar import ProgressBar
from kivymd.uix.snackbar.snackbar import MDSnackbar
from kivymd.app import MDApp
from app.utils.clipboard_utils import copy_to_clipboard

class AccountCard(MDCard, ThemableBehavior):
    def __init__(self, name, code="------", ttl=30, on_select=None, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize properties first
        self.name = name
        self.raw_code = code
        self.on_select = on_select
        self.selected = False
        self.long_press_time = 1.5
        self._long_press_event = None
        self._touch_in_progress = False
        self._was_long_press = False
        self._current_touch = None
        
        # Card properties
        self.orientation = "vertical"
        self.elevation = 0
        self.padding = (dp(24), dp(20), dp(24), dp(20))
        self.size_hint_y = None
        self.height = dp(120)
        self.radius = [dp(16)]
        self.ripple_behavior = True
        self.line_width = dp(2)
        
        # Build UI
        self._build_ui(name, code, ttl)
        
        # Set up touch handling
        self.bind(on_touch_down=self._on_touch_down, on_touch_up=self._on_touch_up)
        
        # Update visual state
        self.update_theme_colors()
        self.update_selected_visual()

    def _build_ui(self, name, code, ttl):
        """Build the user interface components"""
        # Top layout with account info and code
        top_layout = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(24))
        info_layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(4))
        
        # Parse account name and issuer
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
        
        # Assemble top layout
        top_layout.add_widget(info_layout)
        top_layout.add_widget(Widget())  # Spacer
        top_layout.add_widget(self.code_label)
        
        # Bottom layout with progress bar and TTL
        bottom_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(16),
            padding=(0, dp(16), 0, 0),
        )
        
        self.progress_bar = ProgressBar(
            value=max(0, min(100, ttl / 30 * 100)),  # Clamp between 0-100
            size_hint_y=None, 
            height=dp(4)
        )
        
        self.ttl_label = MDLabel(
            text=f"{max(0, ttl)}s",  # Ensure non-negative
            font_style="Body2",
            adaptive_size=True,
            font_size=dp(14),
            bold=True
        )
        
        bottom_layout.add_widget(self.progress_bar)
        bottom_layout.add_widget(self.ttl_label)
        
        # Add to main widget
        self.add_widget(top_layout)
        self.add_widget(bottom_layout)

    def format_code(self, code):
        """Format the authentication code for display"""
        if isinstance(code, str) and len(code) == 6 and code.isdigit():
            return f"{code[:3]} {code[3:]}"
        return str(code) if code is not None else "------"
    
    def _on_touch_down(self, instance, touch):
        """Handle touch down events"""
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        
        # Only handle if no other touch is in progress
        if self._touch_in_progress:
            return False
            
        # Claim the touch
        touch.grab(self)
        self._current_touch = touch
        self._touch_in_progress = True
        self._was_long_press = False
        
        # Schedule long press detection
        self._schedule_long_press()
        
        return True

    def _on_touch_up(self, instance, touch):
        """Handle touch up events"""
        # Only handle our own touch
        if touch.grab_current is not self or touch is not self._current_touch:
            return super().on_touch_up(touch)
        
        was_long_press = self._was_long_press  # snapshot before cleanup

        try:
            # Clean up touch state (but do NOT reset _was_long_press here)
            self._cleanup_touch(touch)
            
            # Handle tap if it wasn't a long press and touch is still on the card
            if not was_long_press and self.collide_point(*touch.pos):
                self._handle_tap()
                
        except Exception as e:
            # Ensure cleanup even if there's an error
            self._force_cleanup()
            print(f"Error in touch up: {e}")
        
        # Now reset _was_long_press at the very end
        self._was_long_press = False
        return True

    def _schedule_long_press(self):
        """Schedule the long press detection"""
        self._cancel_long_press()
        try:
            self._long_press_event = Clock.schedule_once(
                lambda dt: self._handle_long_press(), 
                self.long_press_time
            )
        except Exception as e:
            print(f"Error scheduling long press: {e}")

    def _cancel_long_press(self):
        """Cancel any pending long press event"""
        if self._long_press_event:
            try:
                self._long_press_event.cancel()
            except Exception as e:
                print(f"Error canceling long press: {e}")
            finally:
                self._long_press_event = None

    def _cleanup_touch(self, touch):
        """Clean up touch state"""
        if touch and touch.grab_current is self:
            touch.ungrab(self)
        
        self._cancel_long_press()
        self._touch_in_progress = False
        self._current_touch = None
        self._was_long_press = False

    def _force_cleanup(self):
        """Force cleanup of all touch state"""
        self._cancel_long_press()
        self._touch_in_progress = False
        self._current_touch = None
        self._was_long_press = False

    def _handle_tap(self):
        """Handle tap event"""
        try:
            if self.on_select and callable(self.on_select):
                self.on_select(self.name)
        except Exception as e:
            print(f"Error in tap handler: {e}")

    def _handle_long_press(self):
        """Handle long press event"""
        if not self._touch_in_progress:
            return
        
        self._was_long_press = True  # Set immediately!
        
        try:
            # Copy to clipboard
            self._copy_to_clipboard()
            
            # Visual feedback
            self._show_long_press_feedback()
            
        except Exception as e:
            print(f"Error in long press handler: {e}")
        finally:
            self._long_press_event = None

    def _copy_to_clipboard(self):
        """Copy the raw code to clipboard"""
        try:
            app = MDApp.get_running_app()
            if app and hasattr(app, 'copy_to_clipboard'):
                app.copy_to_clipboard(self.raw_code)
            else:
                copy_to_clipboard(self.raw_code, app)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")

    def _show_long_press_feedback(self):
        """Show visual feedback for long press"""
        try:
            original_color = self.md_bg_color
            accent_color = getattr(self.theme_cls, 'accent_color', [0.2, 0.6, 1.0, 1.0])
            
            # Create feedback animation
            feedback_color = (*accent_color[:3], 0.3)
            anim = (Animation(md_bg_color=feedback_color, duration=0.1) + 
                   Animation(md_bg_color=original_color, duration=0.3))
            anim.start(self)
        except Exception as e:
            print(f"Error showing long press feedback: {e}")

    def set_selected(self, selected):
        """Set the selected state of the card"""
        try:
            self.selected = bool(selected)
            self.update_selected_visual()
        except Exception as e:
            print(f"Error setting selected state: {e}")

    def update_selected_visual(self):
        """Update the visual appearance based on selected state"""
        try:
            self.md_bg_color = self.get_card_bg_color()
            self.elevation = 0
            
            if self.selected:
                target_color = getattr(self.theme_cls, 'primary_color', [0.2, 0.6, 1.0, 1.0])
            else:
                target_color = getattr(self.theme_cls, 'divider_color', [0.12, 0.12, 0.12, 1.0])
            
            anim = Animation(line_color=target_color, duration=0.2)
            anim.start(self)
        except Exception as e:
            print(f"Error updating selected visual: {e}")

    def update_code(self, code, ttl):
        """Update the displayed code and TTL"""
        try:
            self.raw_code = code
            self.code_label.text = self.format_code(code)
            self.ttl_label.text = f"{max(0, ttl)}s"
            
            # Update progress bar with bounds checking
            progress_value = max(0, min(100, ttl / 30 * 100))
            self.progress_bar.value = progress_value
            
        except Exception as e:
            print(f"Error updating code: {e}")

    def get_card_bg_color(self):
        """Get the background color for the card"""
        try:
            bg = getattr(self.theme_cls, 'bg_normal', [1.0, 1.0, 1.0, 1.0])
            style = getattr(self.theme_cls, 'theme_style', 'Light')
            
            # Ensure bg is a valid color tuple
            if not isinstance(bg, (list, tuple)) or len(bg) < 3:
                bg = [1.0, 1.0, 1.0, 1.0]
            
            r, g, b = bg[:3]
            a = bg[3] if len(bg) > 3 else 1.0
            
            # Adjust color based on theme
            if style == 'Light':
                factor = 0.9  # Slightly darker
            else:
                factor = 1.30  # Slightly lighter
            
            r = min(max(r * factor, 0), 1)
            g = min(max(g * factor, 0), 1)
            b = min(max(b * factor, 0), 1)
            
            return (r, g, b, a)
        except Exception as e:
            print(f"Error getting card bg color: {e}")
            return (1.0, 1.0, 1.0, 1.0)  # Default white

    def update_theme_colors(self, *args):
        """Update colors based on current theme"""
        try:
            self.md_bg_color = self.get_card_bg_color()
            self.line_color = getattr(self.theme_cls, 'divider_color', [0.12, 0.12, 0.12, 1.0])
            
            # Update label colors
            if hasattr(self, 'issuer_label'):
                self.issuer_label.theme_text_color = "Secondary"
            
            self.name_label.theme_text_color = "Primary"
            self.code_label.theme_text_color = "Primary"
            self.ttl_label.theme_text_color = "Secondary"
            
            self.update_selected_visual()
        except Exception as e:
            print(f"Error updating theme colors: {e}")

    def on_parent(self, instance, parent):
        """Handle parent changes"""
        if parent is None:
            # Widget is being removed, clean up any pending events
            self._force_cleanup()