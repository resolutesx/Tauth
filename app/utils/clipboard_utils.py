import platform
from kivy.core.clipboard import Clipboard
from kivy.utils import platform as kivy_platform

def copy_to_clipboard(text, app=None):
    """
    Copy text to clipboard with cross-platform support for Windows and Android.
    
    Args:
        text (str): Text to copy to clipboard
        app: The app instance to show snackbar feedback (optional)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use Kivy's clipboard implementation (works on Windows and Android)
        Clipboard.copy(text)
        
        # Show success feedback if app is provided
        if app and hasattr(app, 'show_snackbar'):
            app.show_snackbar(f"Copied Text")
        
        return True
        
    except Exception as e:
        # Show error feedback
        if app and hasattr(app, 'show_snackbar'):
            app.show_snackbar("Failed to copy to clipboard")
        
        return False

def get_clipboard_text():
    """
    Get text from clipboard with cross-platform support.
    
    Returns:
        str: Clipboard text or empty string if failed
    """
    try:
        return Clipboard.paste()
    except Exception:
        return ""

def is_clipboard_available():
    """
    Check if clipboard is available on the current platform.
    
    Returns:
        bool: True if clipboard is available
    """
    try:
        # Test if we can access clipboard
        test_text = "test"
        Clipboard.copy(test_text)
        retrieved = Clipboard.paste()
        return retrieved == test_text
    except Exception:
        return False 